# Regras gerais de comunicação MQTT

[Read-me in English](COMMUNICATION.md)

## 1. Conexão ao Broker MQTT
Como não conseguimos prever o endereço IP do servidor (Só sabemos que será um IPv4), é recomendado uma constante de fácil edição ou variável configurável durante a execução do dispositivo-sensor.

### Porta : `1883`
Usamos a porta padrão do Broker MQTT `:1883`.

### Parâmetros de publicação MQTT
- **QoS:** `0` (entrega no melhor esforço, sem confirmação).
- **Retain:** `false` (não manter última leitura no broker).
> *`0` e `false`, respectivamente, são os valores padrão na maioria das bibliotecas MQTT.*

Como as leituras são contínuas (a cada 5 segundos), esse modo evita acúmulo de mensagem retida e mantém o fluxo simples.

## 2. Tópico para *Publishing*
Cada dispositivo-sensor deve publicar suas leituras no tópico `sensors/{sensor_id}` a cada 5 segundos, onde `sensor_id` é o que distingue cada dispositivo-sensor. Pode ser o dispositivo+tecnologia, grupo ou o próprio sensor.

Qualquer mensagem em um tópico fora de um único nível após `sensors/` será ignorada pelo servidor.

Como estamos dividindo em subtópicos o client_id do seu dispositivo não importa. O servidor irá extrair o sensor_id do tópico e associar a leitura ao sensor correspondente.

### ✅ Corretos:
- `sensors/dht11`
- `sensors/esp32_micropython`
- `sensors/raspberry_pi`
- `sensors/marcos_joao`

### ❌ Incorretos:
- `sensors/`
- `sensors`
- `sensors/lm35/temperature`
- `leituras/lm35`

## 3. Formato da mensagem
As mensagens publicadas devem ser valores numéricos inteiros, em centésimos de graus Celsius, ou seja, a temperatura em Celsius multiplicada por 100. O servidor irá interpretar esses valores e convertê-los para o formato correto.

A mensagem deve ser apenas o int, sem unidades ou outros caracteres. O servidor irá processar a mensagem e formatá-la para exibição.

### Regras estritas do payload
- Codificação: **UTF-8**.
- Conteúdo: string contendo **apenas um inteiro decimal** em centésimos de grau Celsius.
- Sinal: permitido apenas `-` no início para valores negativos.
- Não usar: ponto, vírgula, unidade (`C`, `°C`), notação científica, texto adicional.

### ✅ Corretos:
Leitura (°C) | Mensagem MQTT | Leitura do Servidor |
---|---|---
23,45   | 2345  | 23.45°C  |
0,23    | 23    | 0.23°C   |
100,51  | 10051 | 100.51°C |
1,639   | 164   | 1.64°C   |
-0,69   | -69   | -0.69°C  |
-2,10   | -210  | -2.10°C  |

### ❌ Incorretos:
Leitura (°C) | Mensagem MQTT | Leitura do Servidor |
---|---|---
24,00   | 24     | 0.24°C       |
1,639   | 1639   | 16.39°C      |
23,45   | 23.45  | **Ignorada** |
24,12   | 2412°C | **Ignorada** |
0,23    | 0.23   | **Ignorada** |
-2,10   | -2.10  | **Ignorada** |

---

# Servidor MQTT de Teste
O servidor MQTT de teste ([`tools/test_mqtt_server.py`](tools/test_mqtt_server.py)) é uma implementação simples usando a biblioteca `paho-mqtt` em Python. Ele se conecta a um broker MQTT, assina o tópico `sensors/#` para receber mensagens de sensores e exibe as leituras formatadas no console com verificação do payload.

## Instalação e Uso
1. Certifique-se de ter Python 3 instalado.
2. Instale a biblioteca `paho-mqtt`:
    ```bash
    pip install paho-mqtt
    ```
3. Instale e Rode um broker MQTT local, como o Mosquitto:
    ### Linux 
    #### Debian/Ubuntu:
    ```bash
    sudo apt update
    sudo apt install mosquitto mosquitto-clients
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    ```
    #### Via Snap:
    ```bash
    sudo snap install mosquitto
    sudo snap start mosquitto
    ```
    #### Via Podman:
    ```bash
    podman run -d --name mosquitto -p 1883:1883 eclipse-mosquitto
    ```

    ### Windows:
    Baixe o instalador do Mosquitto em https://mosquitto.org/download/ e siga as instruções de instalação.
4. Execute o servidor MQTT de teste:
    ```bash
    python tools/test_mqtt_server.py
    ```
5. Conecte seu Dispositivo-Sensor ao mesmo broker MQTT e publique mensagens no tópico correto para validar a comunicação.
