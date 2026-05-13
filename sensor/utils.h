#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <WiFi.h>

// Obtém uma entrada do usuário via Serial
String obter_entrada(String mensagem, bool ocultar = false);

// Conecta ao WiFi e retorna o status. Obtém ssid e senha da entrada do usuário por padrão.
wl_status_t configurar_wifi(String ssid = "", String senha = "", int tempo_limite = 5);

// Verdadeiro se a string for um número válido
bool e_numero(String str);

// Verdadeiro se a string for um endereço IP válido
bool e_endereco_ip(String str);

#endif