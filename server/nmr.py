class NMR: # Essa classe aqui é o núcleo de todo o sistema, ela basicamente implementa o algoritmo de votação majoritária com isolamento e recuperação de sensores. Ela mantém um dicionário de sensores, onde cada sensor tem um valor, um contador de concordância e um status de isolamento
    def __init__(self, tolerancia=10, passos_isolamento=3, passos_recuperacao=3, valor_falha=None, verboso=False, logger=None):
        # o 'self' é um objeto que serve para acessar os atributos DA CLASSE. Ou seja, quando a gente faz 'self.sensores', a gente tá dizendo que o objeto que a gente tá criando vai ter um atributo chamado 'sensores'. E aí a gente pode acessar esse atributo em outros métodos da classe usando 'self.sensores'.
        self.sensores = {}  # Dicionário de sensores: {sensor_id: {"v": valor, "c": contador_concordancia, "iso": isolado}}
        self.tolerancia = tolerancia # Serve para defeinir a tolerância pra considerar um sensor 'concordante' com a média dos outros
        self.passos_isolamento = passos_isolamento # Serve para quanto de discordância um sensor precisa ter pra ser isolado
        self.passos_recuperacao = passos_recuperacao # Serve para quanto de concordância um sensor isolado precisa ter pra ser recuperado
        self.valor_falha = valor_falha # Serve para definir o valor de temperatura que o sistema vai retornar quando não tiver nenhum sensor confiável (todos isolados ou sem dados)
        self.ultimo_seguro = valor_falha # Serve para guardar o último valor de temperatura considerado seguro (com base nos sensores ativos), pra usar como fallback quando os sensores ficarem instáveis

    def update_sensor(self, sensor_id, value): # Função pra atualizar o valor de um sensor
        entry = self.sensores.get(sensor_id) # Tenta pegar a entrada do sensor no dicionário
        if not entry:
            self.sensores[sensor_id] = {"v": value, "c": 0, "iso": False} # Se o sensor não existir, cria uma nova entrada com o valor recebido, contador de concordância 0 e status de isolamento False
        else: 
            entry["v"] = value # Se o sensor existir, atualiza o valor do sensor com o valor recebido

    def _dentro_tolerancia(self, a, b) -> bool: # Função pra verificar se dois valores estão dentro da tolerância
        if b == 0: # Se for 0, pra não quebrar no meio...
            return a == 0 # o A também fica 0
        return abs(a - b) / abs(b) * 100 <= self.tolerancia # abs retorna a diferença entre os dois na divisão. A diferença de A para B, divido pelo resultado de B, vezes 100 pra transformar em porcentagem
        # Resultado: Se for menor ou igual à tolerância, retorna True (dentro da tolerância), senão retorna False (fora da tolerância)
        # Se for menor que a tolerância, quer dizer que os valores tão concordando, ou seja, os valores dos sensores tão bem próximos

    def evaluate(self): # Função pra avaliar o estado dos sensores e retornar a temperatura final e o estado do sistema
        if not self.sensores: # Se não tiver nenhum sensor... 
            return {"temperatura": self.valor_falha, "estado": "sem_dados"} # ... retorna o valor de falha e o estado "sem dados"

        ativos = {k: v for k, v in self.sensores.items() if not v.get("iso")} # Dicionário de sensores ativos (não isolados). Assim: {sensor_id: {"v": valor, "c": contador_concordancia, "iso": False}}
        vals = [v["v"] for v in (ativos.values() or self.sensores.values())] # Lista de valores dos sensores ativos. Se não tiver nenhum, pega o de todos. Assim: [valor1, valor2, ...]
        media = sum(vals) / len(vals) # Calcula a média dos valores desses sensores ativos (ou de todos, se não tiver nenhum ativo)

        for _, data in self.sensores.items(): # Para cada sensor no dic. de sensores...
            concorda = self._dentro_tolerancia(data["v"], media) # ... vê se o valor do sensor tá dentro da tolerância da média
            if concorda: # Se for...
                data["c"] = data["c"] + 1 if data["c"] > 0 else 1 # ... incrementa o contador em 1 se for maior que zero. Se não, seta pra 1
            else: # Se não for...
                data["c"] = data["c"] - 1 if data["c"] < 0 else -1 # ... decrementa o contador em 1 se for menor que zero. Se não, seta pra -1

            if not data.get("iso") and data["c"] <= -self.passos_isolamento: # Se não tiver isolado e o contador for menor ou igual ao negativo dos passos de isolamento...
                data["iso"] = True # ... isola o sensor
            if data.get("iso") and data["c"] >= self.passos_recuperacao: # Se tiver isolado e o contador for maior ou igual aos passos de recuperação...
                data["iso"] = False # ... recupera o sensor (tira do isolamento)

        ativos_vals = [d["v"] for d in self.sensores.values() if not d.get("iso")] # Lista de valores dos sensores ativos (não isolados)

        if not ativos_vals: # Se não tiver nenhum sensor ativo...
            return {"temperatura": self.ultimo_seguro or self.valor_falha, "estado": "instavel"} # Algo assim: "temperatura": último valor seguro ou valor de falha, "estado": "instável"
        if len(ativos_vals) == 1: # Se tiver só um sensor ativo...
            return {"temperatura": self.ultimo_seguro or ativos_vals[0], "estado": "instavel"} # Algo assim: "temperatura": último valor seguro ou valor do único sensor, "estado": "instável"
        if len(ativos_vals) == 2: # Se tiver dois sensores ativos...
            a, b = ativos_vals # Atribui os valores dos dois sensores: A e B
            if self._dentro_tolerancia(a, b): # Se os dois sensores tão dentro da tolerância um do outro...
                t = min(ativos_vals) # ... define a temperatura como o valor mínimo entre os dois sensores ...
                self.ultimo_seguro = t # ... atualiza o último valor seguro com esse valor ...
                return {"temperatura": t, "estado": "degradado"} # E devolve "temperatura": esse valor, "estado": "degradado"
            return {"temperatura": self.ultimo_seguro or min(ativos_vals), "estado": "instavel"} # Se os dois sensores não tão dentro da tolerância, devolve "temperatura": último valor seguro ou o valor mínimo entre os dois sensores, "estado": "instável"

        # 3+ sensores
        seguros = [v for v in ativos_vals if self._dentro_tolerancia(v, media)] # Lista de valores dos sensores ativos que tão dentro da tolerância da média
        t = min(seguros) if seguros else min(ativos_vals) # Se tiver algum sensor na tolerância, pega o valor mínimo entre eles. Se não, pega o valor mínimo entre os sensores ativos
        self.ultimo_seguro = t # Atualiza o último valor seguro com esse valor
        estado = "consenso" if len(seguros) == len(ativos_vals) else "falha_mascarada" # Se todos os sensores ativos tão na tolerância, o estado é "consenso". Se não, é "falha mascarada"
        return {"temperatura": t, "estado": estado} # Devolve "temperatura": esse valor, "estado": esse estado
    

"""
Pra quem não tá habituado, por ser feio, mas fazer 'data["c"] = data["c"] - 1 if data["c"] < 0 else -1' é a mesmíssima coisa que fazer:
if data["c"] < 0:
    data["c"] = data["c"] - 1
else:
    data["c"] = -1
"""