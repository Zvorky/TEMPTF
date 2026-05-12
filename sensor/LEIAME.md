# TEMPTF - Módulo Sensor (ESP32 - Framework Arduino)
Este módulo contém o código-fonte para a plataforma ESP32 usando o framework Arduino. Ele é responsável por se comunicar com o sensor de temperatura LM35, coletar dados de temperatura, aplicar média local e verificações de segurança, e transmitir as leituras processadas ao servidor votador central em intervalos regulares. O módulo garante que os dados sejam formatados corretamente e que sigam os protocolos especificados para uma comunicação confiável dentro do sistema TEMPTF.

[Read-me in English](README.md)

---

Veja o [LEIAME.md](../LEIAME.md) da raiz para uma visão geral do projeto completo e seus componentes.

## TODO
- [ ] **Integração do Sensor LM35:** Lê dados do sensor LM35 e os processa de acordo com a lógica definida.
- [ ] **Média Local:** Calcula a média de 10 leituras regulares realizadas em uma janela de 5 segundos para garantir estabilidade dos dados.
- [ ] **Verificação de Segurança (Checkpoint):** Implementa um mecanismo para retornar à última medição bem-sucedida se o coeficiente de variação ultrapassar 10%, garantindo que apenas dados confiáveis sejam transmitidos.
- [ ] **Transmissão de Dados:** Transmite as leituras processadas ao servidor votador central a cada 5 segundos, em Celsius com duas casas decimais.
- [ ] **Tratamento de Erros:** Monitora o desempenho do sensor e lida com anomalias nas leituras para manter a integridade dos dados enviados ao servidor.
