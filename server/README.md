# TEMPTF: Sistema de Sensor de Temperatura Tolerante a Falhas

Implementação de um **Sistema de Sensor de Temperatura Tolerante a Falhas (TEMPTF)** com redundância sensorial e votação majoritária robusta para garantir a integridade dos dados, mesmo em caso de falhas.

## Estrutura

Este servidor (Python) implementa o votador central (NMR):
- **`main.py`**: Aplicação MQTT que recebe dados dos sensores e executa a votação.
- **`nmr.py`**: Núcleo da lógica de votação (isolamento, recuperação, fallback).
- **`requirements.txt`**: Dependências do projeto.

Para o sensor ESP32, consulte [`../sensor/`](../sensor/).
Para ferramentas e simuladores, consulte [`../tools/`](../tools/).

### Autores
 - Cícero Pizetta Pizutti
 - [Enzo Zavorski Delevatti](https://github.com/zvorky)
 - Felipe Borges da Silva
 - [Thiago Reis Petereit Dos Santos](https://github.com/thiagopetereit)

## Especificações Técnicas

### 1. Dispositivos Sensores
Cada unidade sensora segue protocolos rigorosos de transmissão e segurança:
 - **Frequência de Dados:** Uma leitura de temperatura a cada 5 segundos.
 - **Média Local:** Valor transmitido é a média de 10 leituras em 5 segundos.
 - **Checkpoint:** Se o coeficiente de variação das 10 leituras exceder 10%, o dispositivo reverte ao último valor bem-sucedido.
 - **Formato:** Temperatura em centésimos de grau (ex.: 2345 = 23.45°C).
 - **Comunicação:** MQTT via tópico `sensors/{id}`.

### 2. Sistema Votador (NMR)
O servidor processa dados dos sensores e determina a temperatura final do sistema:
 - **Consenso & Falha Mascarada:** Se todos os sensores estão dentro de 10% da média, exibe o valor mínimo como consenso. Caso contrário, indica "falha mascarada".
 - **Isolamento:** Sensor que divergir por 3 ciclos consecutivos é isolado.
 - **Operação Degradada:** Sistema continua com 2 sensores ativos, sinalizando "degradado".
 - **Instabilidade:** Se 2 sensores divergirem por > 10%, sistema é "instável" e exibe o último valor seguro.
 - **Recuperação:** Sensores isolados são reintegrados após 3 leituras consistentes dentro da tolerância.

### Como Usar

**Requisitos:**
- Python 3.8+
- Broker MQTT (ex.: Mosquitto) em `localhost:1883`

**Recomendação:**
```bash
python -m venv env
env\Scripts\activate # no Windows
```

**Instalação:**
```bash
pip install -r requirements.txt
```

**Iniciar o servidor votador:**
```bash
python main.py
```

**Simular sensores (em outro terminal):**
```bash
python ../tools/simulate_sensor.py
```

