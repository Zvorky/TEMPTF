# TEMPTF - Servidor Votador Central
Este módulo implementa o servidor votador central para o sistema TEMPTF. Ele é responsável por receber dados de temperatura de múltiplos sensores, aplicar a lógica de votação para determinar a temperatura de consenso e gerenciar o isolamento de sensores com base no desempenho de cada um. O servidor opera em loop contínuo, processando os dados recebidos e atualizando o estado do sistema.

[Read-me in English](README.md)

---

Veja o [LEIAME.md](../LEIAME.md) da raiz para uma visão geral do projeto completo e seus componentes.

## TODO
- [x] **Recepção de Dados:** Escuta dados de temperatura recebidos de sensores conectados.
- [ ] **Lógica de Votação:** Implementa o algoritmo de consenso para determinar a leitura final de temperatura com base nos dados recebidos dos sensores.
- [ ] **Isolamento de Sensores:** Monitora o desempenho dos sensores e isola qualquer sensor que divergir de forma consistente do consenso.
- [ ] **Operação Degradada:** Continua operando com os sensores remanescentes se um sensor for isolado, e sinaliza estado degradado quando necessário.
- [ ] **Monitoramento de Estabilidade do Sistema:** Declara o sistema instável se os sensores remanescentes divergirem significativamente e exibe a última medição segura.
- [ ] **Mecanismo de Recuperação:** Monitora continuamente sensores isolados para possível reintegração com base no desempenho.

## Configuração e Execução
Este servidor usa MQTT em `localhost:1883` (tópico `sensors/{sensor_id}`).  
Veja [mosquitto.org/download](https://mosquitto.org/download/) para mais opções de instalação.

### Linux
1. Instale e inicie o broker Mosquitto

    #### **Debian/Ubuntu**:

    ```bash
    sudo apt update && sudo apt install -y mosquitto mosquitto-clients
    sudo systemctl enable --now mosquitto
    ```
    Verifique se o broker está em execução
    ```bash
    systemctl status mosquitto --no-pager
    ```

    #### **Alternativa com Snap**:

    ```bash
    sudo snap install mosquitto
    sudo snap start mosquitto
    ```
    Verifique se o broker está em execução
    ```bash
    snap services
    ```

    #### **Alternativa com Podman**:

    ```bash
    podman run -d --name mosquitto \
        -p 1883:1883 \
        -v mosquitto-data:/mosquitto/data \
        -v mosquitto-log:/mosquitto/log \
        docker.io/library/eclipse-mosquitto:2
    ```
    Verifique se o broker está em execução
    ```bash
    podman ps
    podman logs mosquitto --tail 50
    ```
    Opcional: gerar uma unidade systemd de usuário para auto-start
    ```bash
    podman generate systemd --name mosquitto --files --new
    ```

2. Crie e ative um ambiente virtual no diretório do servidor e instale as dependências:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Execute o servidor:

    ```bash
    python main.py
    ```

### Windows

1. Instale o Mosquitto com `winget` e inicie o serviço do broker (PowerShell como Administrador):

    ```powershell
    winget install EclipseMosquitto.Mosquitto
    net start mosquitto
    ```
    Verifique se o broker está em execução
    ```powershell
    Get-Service mosquitto
    ```

2. Crie e ative um ambiente virtual no diretório do servidor e instale as dependências:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

3. Execute o servidor:

    ```powershell
    python main.py
    ```
