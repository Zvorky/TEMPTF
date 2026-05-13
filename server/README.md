# Projeto de Servidor MQTT com NMR

Este servidor Python atua como um cliente MQTT que recebe dados de múltiplos sensores, aplica uma lógica de Redundância por N Módulos (NMR) para determinar um valor confiável e exibe o resultado.

## 1. Preparando o Ambiente

Para executar o servidor, você precisa do Python instalado. Vamos criar um ambiente virtual (`venv`) para manter as dependências do projeto isoladas.

1.  **Abra o terminal** na pasta `server/`.
2.  **Crie o ambiente virtual** com o comando:
    ```bash
    python -m venv env
    ```
3.  **Ative o ambiente virtual**:
    *   **No Windows (PowerShell/CMD):**
        ```powershell
        .\env\Scripts\activate
        ```
    *   **No Linux ou macOS:**
        ```bash
        source env/bin/activate
        ```
    Depois de ativar, você verá `(env)` no início da linha do seu terminal.

## 2. Instalando as Dependências

Com o ambiente ativado, instale as bibliotecas necessárias que estão listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

## 3. Configurando o Broker MQTT (Mosquitto)

Para que os sensores e o servidor conversem, eles precisam de um "carteiro" no meio do caminho. Esse é o papel do broker MQTT. O Mosquitto é uma ótima opção.

1.  **Instale o Mosquitto**: Você pode baixá-lo no [site oficial](https://mosquitto.org/download/).
2.  **Inicie o Mosquitto**:
    *   Abra um **novo terminal** (não precisa ser na pasta do projeto).
    *   Execute o comando para iniciar o broker em modo "verbose", que mostra as mensagens de conexão e publicação. Isso é ótimo para testar.
        ```bash
        mosquitto -v
        ```
    *   Deixe este terminal aberto. Ele é o seu broker MQTT rodando.

## 4. Executando o Servidor

Agora que tudo está pronto, volte para o terminal onde você ativou o ambiente virtual (`env`) e inicie o servidor Python.

```bash
python main.py
```

O servidor irá se conectar ao broker Mosquitto e começará a aguardar mensagens dos sensores.

## 5. Testando com um Sensor (Publicando uma mensagem)

Para simular um sensor enviando uma temperatura, você pode usar o `mosquitto_pub`, uma ferramenta que vem com o Mosquitto.

1.  **Abra um terceiro terminal**.
2.  **Publique uma mensagem** para o tópico do sensor. O servidor está esperando no tópico `sensors/`. Vamos simular o sensor `lm35` enviando o valor `2500` (que o servidor interpretará como `25.00 °C`).

    ```bash
    mosquitto_pub -h localhost -t "sensors/lm35" -m "2500"
    ```

Ao executar o comando acima, você verá no terminal do **servidor** a temperatura final sendo calculada e exibida. No terminal do **Mosquitto**, você verá o log da mensagem sendo recebida e encaminhada.

Pronto! Agora seu ambiente está configurado e você sabe como testá-lo. Bom trabalho!