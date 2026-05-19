# TEMPTF - Módulo Sensor (ESP32 - Framework Arduino)
Este módulo contém o código-fonte para a plataforma ESP32 usando o framework Arduino. Ele é responsável por se comunicar com o sensor de temperatura LM35, coletar dados de temperatura, aplicar média local e verificações de segurança, e transmitir as leituras processadas ao servidor votador central em intervalos regulares. O módulo garante que os dados sejam formatados corretamente e que sigam os protocolos especificados para uma comunicação confiável dentro do sistema TEMPTF.

[Read-me in English](README.md)

---

Veja o [LEIAME.md](../LEIAME.md) da raiz para uma visão geral do projeto completo e seus componentes.

## Montagem do Circuito

**Pinout do Sensor LM35:**
![LM35 Pinout](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fclubedomaker.com%2Fwp-content%2Fuploads%2F2026%2F01%2Fimagem_2026-01-05_224447026-768x315.png&f=1&nofb=1&ipt=7b2fded10111e792c8cf17502ca55a56a0a0da5f85643e53d30d63f1a7a68bfa)

**Ligação dos pinos:**

| LM35      | ESP32         |
|-----------|---------------|
| +Vs       | 3V3           |
| Vout      | GPIO ADC (ex: 34) |
| GND       | GND           |

> **Observações:**
> - Não é necessário resistor entre o LM35 e o ESP32.
> - Recomenda-se alimentar o LM35 com 3V3 para compatibilidade com o ADC do ESP32.
> - A saída Vout do LM35 deve ser conectada a um pino de entrada analógica (ADC) do ESP32, como o GPIO34, GPIO35, etc.