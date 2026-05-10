#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <WiFi.h>

// Obtém entrada do usuário via Serial
String entrada_serial(String msg, bool esconder = false);

// Conecta ao WiFi e retorna status
wl_status_t configurar_wifi(String ssid = "", String senha = "", int tempo_limite = 5);

// Verifica se é número
bool eh_numero(String str);

// Verifica se é IP
bool eh_ip(String str);

#endif