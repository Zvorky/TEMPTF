# TEMPTF: Sistema de Sensoriamento de Temperatura Tolerante a Falhas
Este projeto foca no desenvolvimento de um **Sistema de Sensoriamento de Temperatura Tolerante a Falhas (TEMPTF)**. Ele simula um ambiente de monitoramento de alta confiabilidade para equipamentos usados no transporte de órgãos humanos para transplante. O sistema foi projetado para fornecer leituras de temperatura precisas por meio de redundância e de um mecanismo robusto de votação, garantindo a integridade dos dados mesmo em caso de falha de sensores.

[Read-me in English](README.md)

## Escopo do Repositório
Este repositório contém a implementação específica de um subconjunto do sistema distribuído:
 - [**Servidor Votador Central:**](server/LEIAME.md) Aplicação responsável por coletar dados via rede, executar a lógica de votação e gerenciar os estados de isolamento de sensores.
 - [**Módulo ESP32 (Framework Arduino):**](sensor/LEIAME.md) Código-fonte para a plataforma ESP32 usando o framework Arduino.
 - **Integração com Sensor LM35:** Lógica especializada para medição e validação de dados do sensor de temperatura LM35.

Scripts adicionais para testes e simulação estão incluídos em [`tools/`](tools/).

### Autores
 - [Cícero Pizetta Pizutti](https://github.com/ciceropizutti)
 - [Enzo Zavorski Delevatti](https://github.com/zvorky)
 - [Felipe Borges da Silva](https://github.com/znyctus)
 - [Thiago Reis Petereit Dos Santos](https://github.com/thiagopetereit)

## Especificações Técnicas e Lógica
_Prof. Dr. Marcelo Trindade Rebonatto_

### 1. Dispositivos Sensores
Cada unidade sensora deve seguir protocolos rigorosos de transmissão de dados e segurança:
 - **Frequência dos Dados:** Um único valor de temperatura deve ser transmitido a cada 5 segundos.
 - **Média Local:** O valor transmitido é a média de 10 leituras regulares realizadas dentro da janela de 5 segundos.
 - **Verificação de Segurança (Checkpoint):** Se o coeficiente de variação das 10 leituras ultrapassar 10%, o dispositivo deve voltar para a última medição calculada com sucesso (checkpoint) e monitorar leituras subsequentes até encontrar um valor estável.
 - **Formatação:** As leituras são transmitidas em Celsius com duas casas decimais.

### 2. Sistema Votador Central
O servidor processa os dados recebidos da rede de sensores para determinar a temperatura final do sistema:
 - **Consenso e Mascaramento:** Se todos os valores dos sensores estiverem dentro de 10% da média aritmética (x), o sistema exibe a menor temperatura como valor de consenso. Se um sensor divergir mais de 10% da média, isso indica um evento de "mascaramento de falha".
 - **Isolamento de Sensor:** Se um sensor específico permanecer divergente por 3 ciclos consecutivos, ele é sinalizado como comprometido e isolado do cálculo principal.
 - **Operação Degradada:** Após o isolamento, o sistema continua operando com os dois sensores restantes, sinalizando estado "degradado".
 - **Instabilidade do Sistema:** Se os dois sensores restantes divergirem mais de 10%, o sistema é declarado instável e exibe a última medição segura.
 - **Lógica de Recuperação:** Sensores isolados são monitorados continuamente. Eles são reintegrados se mostrarem concordância consistente (divergência menor que 10%) por 3 medições consecutivas.
<!-- - **Protocolo de Comunicação:** Aguardando outras equipes decidirem entre MQTT ou TCP/IP. -->
