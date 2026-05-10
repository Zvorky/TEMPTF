import time # Serve para lidar com o timeout dos sensores

class NMR: # Essa classe aqui é o núcleo de todo o sistema, ela basicamente implementa o algoritmo de votação majoritária com isolamento e recuperação de sensores. Ela mantém um dicionário de sensores, onde cada sensor tem um valor, um contador de concordância e um status de isolamento
    def __init__(self, tolerancia=10, passos_isolamento=3, passos_recuperacao=3, valor_falha=None, verboso=False, logger=None):
        # o 'self' é um objeto que serve para acessar os atributos DA CLASSE. Ou seja, quando a gente faz 'self.sensores', a gente tá dizendo que o objeto que a gente tá criando vai ter um atributo chamado 'sensores'. E aí a gente pode acessar esse atributo em outros métodos da classe usando 'self.sensores'.
        self.sensores = {}  # Dicionário de sensores: {sensor_id: {"v": valor, "c": contador_concordancia, "iso": isolado, "t": timestamp}}
        self.tolerancia = tolerancia # Serve para defeinir a tolerância pra considerar um sensor 'concordante' com a média dos outros
        self.passos_isolamento = passos_isolamento # Serve para quanto de discordância um sensor precisa ter pra ser isolado
        self.passos_recuperacao = passos_recuperacao # Serve para quanto de concordância um sensor isolado precisa ter pra ser recuperado
        self.valor_falha = valor_falha # Serve para definir o valor de temperatura que o sistema vai retornar quando não tiver nenhum sensor confiável (todos isolados ou sem dados)
        self.ultimo_seguro = valor_falha # Serve para guardar o último valor de temperatura considerado seguro (com base nos sensores ativos), pra usar como fallback quando os sensores ficarem instáveis

        # Contadores para os requisitos de recuperação de instabilidade (3 ciclos) estipulados no trabalho
        self.ciclos_concordancia_degradado = 3 # Inicializa em 3 pra já começar exibindo os dados se ligar direto com 2 sensores
        self.ciclos_concordancia_consenso = 3  # Inicializa em 3 pra já começar exibindo consenso se o sistema ligar com 3 sensores normais

    def update_sensor(self, sensor_id, value): # Função pra atualizar o valor de um sensor
        entry = self.sensores.get(sensor_id) # Tenta pegar a entrada do sensor no dicionário
        if not entry:
            # A chave "t" salva a hora exata que a leitura chegou
            self.sensores[sensor_id] = {"v": value, "c": 0, "iso": False, "t": time.time()} 
        else: 
            entry["v"] = value # Se o sensor existir, atualiza o valor do sensor com o valor recebido
            entry["t"] = time.time() # Atualiza a hora da última leitura recebida

    def _dentro_tolerancia(self, a, b) -> bool: # Função pra verificar se dois valores estão dentro da tolerância
        if b == 0: # Se for 0, pra não quebrar no meio...
            return a == 0 # o A também fica 0
        return abs(a - b) / abs(b) * 100 <= self.tolerancia # abs retorna a diferença entre os dois na divisão. A diferença de A para B, divido pelo resultado de B, vezes 100 pra transformar em porcentagem
        # Resultado: Se for menor ou igual à tolerância, retorna True (dentro da tolerância), senão retorna False (fora da tolerância)
        # Se for menor que a tolerância, quer dizer que os valores tão concordando, ou seja, os valores dos sensores tão bem próximos

    def evaluate(self): # Função pra avaliar o estado dos sensores e retornar a temperatura final e o estado do sistema
        agora = time.time()
        
        # Cria um dicionário temporário apenas com os sensores que enviaram dados nos últimos 12 segundos.
        # Se um sensor pifar e parar de enviar via MQTT, ele é ignorado automaticamente.
        sensores_vivos = {k: v for k, v in self.sensores.items() if (agora - v.get("t", 0)) < 12}

        if not sensores_vivos: # Se não tiver nenhum sensor vivo... 
            return {"temperatura": self.ultimo_seguro or self.valor_falha, "estado": "sem_dados"} # ... retorna o valor de falha e o estado "sem dados"

        ativos = {k: v for k, v in sensores_vivos.items() if not v.get("iso")} # Dicionário de sensores ativos (não isolados). Assim: {sensor_id: {"v": valor, "c": contador_concordancia, "iso": False}}
        vals = [v["v"] for v in (ativos.values() or sensores_vivos.values())] # Lista de valores dos sensores ativos. Se não tiver nenhum, pega o de todos. Assim: [valor1, valor2, ...]
        media = sum(vals) / len(vals) # Calcula a média dos valores desses sensores ativos (ou de todos, se não tiver nenhum ativo)

        for _, data in sensores_vivos.items(): # Para cada sensor no dic. de sensores VIVOS...
            concorda = self._dentro_tolerancia(data["v"], media) # ... vê se o valor do sensor tá dentro da tolerância da média
            if concorda: # Se for...
                data["c"] = data["c"] + 1 if data["c"] > 0 else 1 # ... incrementa o contador em 1 se for maior que zero. Se não, seta pra 1
            else: # Se não for...
                data["c"] = data["c"] - 1 if data["c"] < 0 else -1 # ... decrementa o contador em 1 se for menor que zero. Se não, seta pra -1

            if not data.get("iso") and data["c"] <= -self.passos_isolamento: # Se não tiver isolado e o contador for menor ou igual ao negativo dos passos de isolamento...
                data["iso"] = True # ... isola o sensor
            if data.get("iso") and data["c"] >= self.passos_recuperacao: # Se tiver isolado e o contador for maior ou igual aos passos de recuperação...
                data["iso"] = False # ... recupera o sensor (tira do isolamento)

        ativos_vals = [d["v"] for d in sensores_vivos.values() if not d.get("iso")] # Lista de valores dos sensores ativos (não isolados)

        if not ativos_vals: # Se não tiver nenhum sensor ativo...
            self.ciclos_concordancia_degradado = 0 # Reseta o contador
            return {"temperatura": self.ultimo_seguro or self.valor_falha, "estado": "instavel"} # Algo assim: "temperatura": último valor seguro ou valor de falha, "estado": "instável"
        
        if len(ativos_vals) == 1: # Se tiver só um sensor ativo...
            self.ciclos_concordancia_degradado = 0 # Reseta o contador
            return {"temperatura": self.ultimo_seguro or ativos_vals[0], "estado": "instavel"} # Algo assim: "temperatura": último valor seguro ou valor do único sensor, "estado": "instável"
        
        if len(ativos_vals) == 2: # Se tiver dois sensores ativos...
            a, b = ativos_vals # Atribui os valores dos dois sensores: A e B
            self.ciclos_concordancia_consenso = 0 # Como só tem 2 sensores, zera a contagem pro consenso de 3
            
            if self._dentro_tolerancia(a, b): # Se os dois sensores tão dentro da tolerância um do outro...
                self.ciclos_concordancia_degradado += 1 # Soma 1 ciclo de concordância
                t = min(ativos_vals) # ... define a temperatura como o valor mínimo entre os dois sensores ...
                
                # Só exibe o novo valor se eles concordarem por 3 ciclos consecutivos
                if self.ciclos_concordancia_degradado >= 3 or self.ultimo_seguro is None:
                    self.ultimo_seguro = t # ... atualiza o último valor seguro com esse valor ...
                    return {"temperatura": t, "estado": "degradado"} # E devolve "temperatura": esse valor, "estado": "degradado"
                else:
                    return {"temperatura": self.ultimo_seguro, "estado": f"recuperando_degradado ({self.ciclos_concordancia_degradado}/3)"}
            else:
                self.ciclos_concordancia_degradado = 0 # Eles discordaram, reseta o contador
                return {"temperatura": self.ultimo_seguro or min(ativos_vals), "estado": "instavel"} # Se os dois sensores não tão dentro da tolerância, devolve "temperatura": último valor seguro ou o valor mínimo entre os dois sensores, "estado": "instável"

        # 3+ sensores
        seguros = [v for v in ativos_vals if self._dentro_tolerancia(v, media)] # Lista de valores dos sensores ativos que tão dentro da tolerância da média
        t = min(seguros) if seguros else min(ativos_vals) # Se tiver algum sensor na tolerância, pega o valor mínimo entre eles. Se não, pega o valor mínimo entre os sensores ativos
        
        if len(seguros) == len(ativos_vals):
            # Todos os sensores ativos tão na tolerância
            self.ciclos_concordancia_consenso += 1
            self.ciclos_concordancia_degradado = 3 # Deixa armado, se cair um sensor, não precisa de 3 ciclos pra dizer que tá degradado
            
            if self.ciclos_concordancia_consenso >= 3 or self.ultimo_seguro is None:
                self.ultimo_seguro = t # Atualiza o último valor seguro com esse valor
                return {"temperatura": t, "estado": "consenso"}
            else:
                 # Esperando fechar 3 ciclos de consenso pra assumir de volta
                 self.ultimo_seguro = t 
                 return {"temperatura": t, "estado": f"recuperando_consenso ({self.ciclos_concordancia_consenso}/3)"}
        else:
            # Nem todos os sensores ativos tão na tolerância, tem pelo menos um discordante
            self.ciclos_concordancia_consenso = 0 # Reseta a contagem de consenso
            self.ultimo_seguro = t # Atualiza o último valor seguro com esse valor pra não ficar sem nenhum valor seguro caso os sensores fiquem instáveis
            return {"temperatura": t, "estado": "falha_mascarada"}


"""
Pra quem não tá habituado, pode ser feio, mas fazer 'data["c"] = data["c"] - 1 if data["c"] < 0 else -1' é a mesmíssima coisa que fazer:
if data["c"] < 0:
    data["c"] = data["c"] - 1
else:
    data["c"] = -1
"""
