import time

class DadoSensor:
    def __init__(self, valor_bruto: int, fator: float = 1.0, ajuste: int = 0):
        self.fator = fator    
        self.ajuste = ajuste                # Ajuste para calibração do sensor. Ex: se o sensor sempre lê 5 graus a mais, coloque = -500 (porque o valor bruto é em centésimos)
        self.valor_bruto = valor_bruto
        self.ultima_atualizacao = time.time()
        self._isolado = False
        self._contagem_concordancia = 0

    def obter_valor(self) -> int:            # Equacão da reta: Corrige o erro de degrau
        return int(self.valor_bruto * self.fator + self.ajuste)

    def obter_contagem_concordancia(self) -> int:
        return self._contagem_concordancia

    def esta_isolado(self) -> bool:
        return self._isolado

    def atualizar(self, valor_bruto: int):
        self.valor_bruto = valor_bruto
        self.ultima_atualizacao = time.time()

    def calibrar(self, fator: float | None = None, ajuste: int | None = None):
        if fator is not None:
            self.fator = fator
        if ajuste is not None:
            self.ajuste = ajuste

    def atualizar_concordancia(self, concorda: bool):
        # Histerese: Se estava negativo e acertou, zera a ficha e exige provação
        if self._contagem_concordancia and concorda == (self._contagem_concordancia < 0):
            self._contagem_concordancia = 0
        self._contagem_concordancia += 1 if concorda else -1

    def isolar(self):
        self._isolado = True
        self._contagem_concordancia = 0

    def recuperar(self):
        self._isolado = False
        self._contagem_concordancia = 0


class NMR:
    def __init__(
        self,
        tolerancia: int = 10,
        passos_isolamento: int = 3,
        passos_recuperacao: int = 3,
        valor_falha: int | None = None,
        verboso: bool = False,
        tempo_limite_segundos: int = 12
    ):
        self.dados_sensores = {}
        self.tolerancia = tolerancia
        self.passos_isolamento = passos_isolamento
        self.passos_recuperacao = passos_recuperacao
        self.valor_falha = valor_falha
        self.verboso = verboso
        self.tempo_limite_segundos = tempo_limite_segundos
        self._estado = "NORMAL"
        self._ultimo_seguro = valor_falha
        self._ciclos_concordancia_degradado = 3
        self._ciclos_concordancia_consenso = 3

    def obter_estado(self) -> str:
        return self._estado

    def obter_ultimo_seguro(self) -> int | None:
        return self._ultimo_seguro

    def atualizar_sensor(self, id_sensor: str, valor_bruto: int):
        if id_sensor not in self.dados_sensores:
            self.dados_sensores[id_sensor] = DadoSensor(valor_bruto)
        else:
            self.dados_sensores[id_sensor].atualizar(valor_bruto)

    def _dentro_tolerancia(self, a: int, b: float) -> bool:
        if b == 0:
            return a == 0
        return abs(a - b) / abs(b) * 100 <= self.tolerancia

    def _sensores_vivos(self) -> dict[str, DadoSensor]:
        agora = time.time()
        return {
            id_sensor: dados
            for id_sensor, dados in self.dados_sensores.items()
            if (agora - dados.ultima_atualizacao) < self.tempo_limite_segundos
        }

    def _log_status_sensores(self, vivos: dict[str, DadoSensor]) -> None:
        if not self.verboso:
            return
        for id_sensor, dados in vivos.items():
            status = "ISOLADO" if dados.esta_isolado() else "ATIVO"
            print(f"Sensor {id_sensor} [{status}]: Valor={dados.obter_valor()} Contagem={dados.obter_contagem_concordancia()}")

    def avaliar(self) -> int | None:
        vivos = self._sensores_vivos()       # Dicionário de sensores dos últimos 12s
        self._log_status_sensores(vivos)

        if not vivos:
            self._estado = "SEM_DADOS"
            return self._ultimo_seguro if self._ultimo_seguro is not None else self.valor_falha

        ativos = {id_sensor: dados for id_sensor, dados in vivos.items() if not dados.esta_isolado()}
        valores_base = [d.obter_valor() for d in (ativos.values() or vivos.values())]
        media_base = sum(valores_base) / len(valores_base)

        for dados in vivos.values():
            concorda = self._dentro_tolerancia(dados.obter_valor(), media_base)
            dados.atualizar_concordancia(concorda)

            if not dados.esta_isolado() and dados.obter_contagem_concordancia() <= -self.passos_isolamento:
                dados.isolar()
            elif dados.esta_isolado() and dados.obter_contagem_concordancia() >= self.passos_recuperacao:
                dados.recuperar()

        valores_ativos = [d.obter_valor() for d in vivos.values() if not d.esta_isolado()]

        if not valores_ativos:
            self._ciclos_concordancia_degradado = 0
            self._estado = "INSTAVEL"
            return self._ultimo_seguro if self._ultimo_seguro is not None else self.valor_falha

        if len(valores_ativos) == 1:
            self._ciclos_concordancia_degradado = 0
            self._estado = "INSTAVEL"
            return self._ultimo_seguro if self._ultimo_seguro is not None else valores_ativos[0]

        if len(valores_ativos) == 2:
            self._ciclos_concordancia_consenso = 0
            a, b = valores_ativos

            if self._dentro_tolerancia(a, b):
                self._ciclos_concordancia_degradado += 1
                votado = min(valores_ativos)
                if self._ciclos_concordancia_degradado >= 3 or self._ultimo_seguro is None:
                    self._ultimo_seguro = votado
                    self._estado = "DEGRADADO"
                    return votado

                self._estado = "RECUPERANDO_DEGRADADO"
                return self._ultimo_seguro

            self._ciclos_concordancia_degradado = 0
            self._estado = "INSTAVEL"
            return self._ultimo_seguro if self._ultimo_seguro is not None else min(valores_ativos)

        valores_seguros = [v for v in valores_ativos if self._dentro_tolerancia(v, media_base)]
        votado = min(valores_seguros) if valores_seguros else min(valores_ativos)

        if len(valores_seguros) == len(valores_ativos):
            self._ciclos_concordancia_consenso += 1
            self._ciclos_concordancia_degradado = 3

            if self._ciclos_concordancia_consenso >= 3 or self._ultimo_seguro is None:
                self._ultimo_seguro = votado
                self._estado = "CONSENSO"
                return votado

            self._ultimo_seguro = votado
            self._estado = "RECUPERANDO_CONSENSO"
            return votado

        self._ciclos_concordancia_consenso = 0
        self._ultimo_seguro = votado
        self._estado = "FALHA_MASCARADA"
        return votado
