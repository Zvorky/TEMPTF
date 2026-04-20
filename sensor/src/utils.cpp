// General Utils

/* ─                     · ─ +
 |  Enzo Zavorski Delevatti  |
 .  @Zvorky                  ·
             ___,
          .~´    `-,
         /  _    _ \.        .
        ,\`|_|''|_|´\
 .       /          /)       |
        (\  ,    , .\`
 |       `) ;`,; `,^,)
         ´,´  `,  `  `
        
 |__ _  September 2025    _  |
/                           */


#include "utils.h"


String input(String msg, bool hide) {
  Serial.print(msg);
  String s = "";
  char c;
  do {
    if (Serial.available()) {
      c = Serial.read();
      if (c == '\b') { // Backspace
        if (s.length()) {
          s.remove(s.length()-1, 1);
          Serial.print("\b \b");
        }
      }
      else if (c != '\n' && c != '\r') {
        s += c;
        if (hide) Serial.print('*');
        else Serial.print(c);
      }
    }
  } while (c != '\n');
  Serial.print('\n');
  return s;
}

  
wl_status_t setupWiFi(String ssid, String passwd, int timeout) {
  WiFi.disconnect(true, true);
  WiFi.mode(WIFI_STA);

  while (ssid == "") {
    ssid = input("\n\nWiFi SSID: ", false);
    passwd = input("WiFi Password: ", true);
  }

  WiFi.begin(ssid, passwd);
  
  Serial.print("\nConnecting");
  for (int i = 0; i < timeout and WiFi.status() != WL_CONNECTED; i++) {
    delay(1000);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected.");
    Serial.print("\nIP:  ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC: ");
    Serial.println(WiFi.macAddress());
  }
  else Serial.printf("\nCould not connect to \"%s\"!\n", ssid.c_str());

  return WiFi.status();
}


bool isNumber(String str) {
  bool dot = false;
  if (str.length() == 0) return false;
  for (int i = 0; i < str.length(); i++) {
    if (str[i] == '.') {
      if (dot) return false;
      dot = true;
    } else if (!isdigit(str[i])) {
      return false;
    }
  }
  return true;
}