#include "utils.h"

String entrada_serial(String msg, bool esconder) {
  Serial.print(msg);
  String s = "";
  char c;
  do {
    if (Serial.available()) {
      c = Serial.read();
      if (c == '\b') {
        if (s.length()) {
          s.remove(s.length()-1, 1);
          Serial.print("\b \b");
        }
      }
      else if (c != '\n' && c != '\r') {
        s += c;
        if (esconder) Serial.print('*');
        else Serial.print(c);
      }
    }
  } while (c != '\n');
  Serial.print('\n');
  return s;
}
  
wl_status_t configurar_wifi(String ssid, String senha, int tempo_limite) {
  WiFi.disconnect(true, true);
  WiFi.mode(WIFI_STA);
  
  while (ssid == "") {
    ssid = entrada_serial("\n\nSSID WiFi: ", false);
    senha = entrada_serial("Senha WiFi: ", true);
  }
  
  WiFi.begin(ssid, senha);
  
  Serial.print("\nConectando");
  for (int i = 0; i < tempo_limite and WiFi.status() != WL_CONNECTED; i++) {
    delay(1000);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado.");
    Serial.print("IP: "); 
    Serial.println(WiFi.localIP());
  } else {
    Serial.printf("\nErro ao conectar em \"%s\"!\n", ssid.c_str());
  }
  
  return WiFi.status();
}

bool eh_numero(String str) {
  bool ponto = false;
  if (str.length() == 0) return false;
  for (int i = 0; i < str.length(); i++) {
    if (str[i] == '.') {
      if (ponto) return false;
      ponto = true;
    } else if (!isdigit(str[i])) return false;
  }
  return true;
}

bool eh_ip(String str) {
  IPAddress ip;
  return ip.fromString(str);
}