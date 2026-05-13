#include "utils.h"

String obter_entrada(String mensagem, bool ocultar) { 
  Serial.print(mensagem);
  String s = "";
  char c;
  do {
    if (Serial.available()) {
      c = Serial.read();
      if (c == '\b') { // Backspace
        if (s.length()) {
          s.remove(s.length()-1, 1);
          Serial.print("\b \b");  // Move o cursor pra trás
        }
      }
      else if (c != '\n' && c != '\r') {
        s += c;
        if (ocultar) Serial.print('*');
        else Serial.print(c);
      }
    }
  } while (c != '\n');
  Serial.print('\n');
  return s;
}
  
wl_status_t configurar_wifi(String ssid, String senha, int tempo_limite) {
  WiFi.disconnect(true, true);       // O primeiro true desliga a conexão e o segundo apaga as redes salvas na flash
  WiFi.mode(WIFI_STA);

  while (ssid == "") {
    ssid = obter_entrada("\n\nSSID do WiFi: ", false);
    senha = obter_entrada("Senha do WiFi: ", true);
  }

  WiFi.begin(ssid.c_str(), senha.c_str());               // garante que as strings sejam convertidas para char*
  
  Serial.print("\nConectando");
  for (int i = 0; i < tempo_limite and WiFi.status() != WL_CONNECTED; i++) {
    delay(1000);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado.");
    Serial.print("\nIP:  ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC: ");
    Serial.println(WiFi.macAddress());
    Serial.println();
  }
  else Serial.printf("\nNao foi possivel conectar a \"%s\"!\n", ssid.c_str());

  return WiFi.status();
}

bool e_numero(String str) {
  bool ponto = false;
  if (str.length() == 0) return false;
  for (int i = 0; i < str.length(); i++) {
    if (str[i] == '.') {
      if (ponto) return false;
      ponto = true;
    } else if (!isdigit(str[i])) {           // se não for número (não pode nem ser negativo)
      return false;
    }
  }
  return true;
}

bool e_endereco_ip(String str) {
  IPAddress ip;
  return ip.fromString(str);
}