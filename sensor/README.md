## Atualizações da Versão Final (Firmware Sensor A)

Em relação ao esqueleto inicial, a versão final do firmware conta com as seguintes adições e melhorias:

- **Leitura Real de Hardware:** Implementação da leitura analógica do LM35 (ou seja lá o sensor que formos usar, é só trocar ele na placa) com cálculo de conversão de tensão do ESP32.
- **Amostragem Temporizada:** Substituição do envio estático por um sistema de amostragem que armazena 10 leituras a cada janela de 5 segundos (1 leitura a cada 500ms), utilizando `millis()` para evitar bloqueios de processamento.
- **Filtro Estatístico e Checkpoint:** Adição do cálculo de Desvio Padrão Variação (CV). Implementada a regra de tolerância a falhas: se o CV > 10%, o sensor recorre ao último valor seguro (Checkpoint)..
- **Formatação de Payload (Acordo de Integração):** O valor final da temperatura agora é multiplicado por 100 e enviado como Inteiro via MQTT, conforme acordado com os demais grupos, garantindo que o Votador em Python receba os dados em centésimos de grau Celsius sem erros de flutuação.
- **Refatoração:** Padronização completa do código base (`main.cpp`, `utils.cpp` e `utils.h`) para o idioma pt-BR, para facilitar o estudo e apresentação até terça-feira.