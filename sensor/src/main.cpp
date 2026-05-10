/* TEMPTF - Módulo Sensor A (ESP32 + LM35)

Cícero Pizetta Pizutti          - 68612
Enzo Zavorski Delevatti         - 199575
Felipe Borges da Silva          - 184387
Thiago Reis Petereit Dos Santos - 198853
*/


#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFiClient.h>
#include "utils.h"

// ---[ DEFINIÇÕES ]---

#define PINO_LM35 34 // Pino analógico do LM35
#define PORTA_MQTT 1883
#define CLIENTE_MQTT "sensorA_grupo4"
#define TOPICO_MQTT "sensors/lm35"

#define INTERVALO_LEITURA 500      // 500ms para 10 leituras em 5s
#define INTERVALO_PUBLICACAO 5000  // Ciclo de 5 segundos

// ---[ CONFIGURAÇÕES ]---
const String ssid = "";
const String senha = "";
String ip_broker_mqtt = "";

// ---[ OBJETOS GLOBAIS ]---
WiFiClient espClient;
PubSubClient clienteMqtt(espClient);

unsigned long ultimo_tempo_leitura = 0;
unsigned long ultimo_tempo_publicacao = 0;

// Variáveis para a regra do Coeficiente de Variação (CV)
float leituras[10];
int indice_leitura = 0;
float ultimo_valor_seguro = -1.0; 
bool tem_valor_seguro = false;

// ---[ DECLARAÇÃO DE FUNÇÕES ]---
bool garantir_conexao_mqtt();
void publicar_dados(float temperatura);
float ler_lm35();

void setup() {
    Serial.begin(9600);
    delay(1000);

    pinMode(PINO_LM35, INPUT);

    // Conexão WiFi e Broker
    while (configurar_wifi(ssid, senha) != WL_CONNECTED) delay(1000);
    while (!eh_ip(ip_broker_mqtt)) ip_broker_mqtt = entrada_serial("IP do Broker MQTT: ");
    
    clienteMqtt.setServer((char*)ip_broker_mqtt.c_str(), PORTA_MQTT);
}

void loop() {
    garantir_conexao_mqtt();
    clienteMqtt.loop();

    unsigned long tempo_atual = millis();

    // 1. Amostragem (10 leituras em 5s)
    if (tempo_atual - ultimo_tempo_leitura >= INTERVALO_LEITURA) {
        if (indice_leitura < 10) {
            leituras[indice_leitura] = ler_lm35();
            indice_leitura++;
        }
        ultimo_tempo_leitura = tempo_atual;
    }

    // 2. Avaliação e Publicação (Intervalo de 5s)
    if (tempo_atual - ultimo_tempo_publicacao >= INTERVALO_PUBLICACAO) {
        if (indice_leitura == 10) {
            float soma = 0;
            for (int i = 0; i < 10; i++) soma += leituras[i];
            float media = soma / 10.0;

            float soma_variancia = 0;
            for (int i = 0; i < 10; i++) {
                soma_variancia += pow(leituras[i] - media, 2);
            }
            float desvio_padrao = sqrt(soma_variancia / 10.0);

            float cv = (media != 0) ? (desvio_padrao / media) * 100.0 : 0;

            Serial.printf("Media: %.2f | CV: %.2f%%\n", media, cv);

            if (cv > 10.0) {
                Serial.println("Aviso: CV > 10%! Medição instável.");
                if (tem_valor_seguro) {
                    Serial.println("Usando Checkpoint seguro.");
                    publicar_dados(ultimo_valor_seguro);
                }
            } else {
                ultimo_valor_seguro = media;
                tem_valor_seguro = true;
                publicar_dados(media);
            }
        }
        indice_leitura = 0;
        ultimo_tempo_publicacao = tempo_atual;
    }
}

bool garantir_conexao_mqtt() {
    if (clienteMqtt.connected()) return true;
    Serial.print("Conectando ao MQTT em ");
    Serial.println(ip_broker_mqtt);
    if (clienteMqtt.connect(CLIENTE_MQTT)) {
        Serial.println("Conectado!");
        return true;
    }
    Serial.print("Falha, rc=");
    Serial.println(clienteMqtt.state());
    return false;
}

void publicar_dados(float temperatura) {
    if (!garantir_conexao_mqtt()) return;
    int valor_inteiro = (int)(temperatura * 100);
    char payload[16];
    sprintf(payload, "%d", valor_inteiro);
    if (clienteMqtt.publish(TOPICO_MQTT, payload)) {
        Serial.printf("Publicado: %s\n", payload);
    }
}

float ler_lm35() {
    int cru = analogRead(PINO_LM35);
    float voltagem = cru * (3.3 / 4095.0);
    return voltagem * 100.0;
}