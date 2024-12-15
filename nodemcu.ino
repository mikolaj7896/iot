#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <vector>
#include <time.h>

// Zmienne dla sensora temperatury
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

LiquidCrystal_I2C lcd(0x27, 16, 2); 

// WiFi i MQTT
const char* ssid = "A54"; // wifi name
const char* password = "admin124"; // wifi pass
const char* mqtt_server = "y27feb91.ala.eu-central-1.emqxsl.com"; // mqtt broker server address
const int mqtt_port = 8883;
const char* mqtt_user = "student";
const char* mqtt_password = "admin1234";
const char* topic_temperature = "temperature"; // nowy temat do wysylania temperatury
const char* topic_whisper = "whisper"; // temat do odbierania wiadomosci
const char* topic_yolo = "object_recognition";

// Inicjalizacja klienta z certyfikatem
BearSSL::WiFiClientSecure espClient;
PubSubClient client(espClient);

// Certyfikat SSL brokera MQTT
static const char ca_cert[] PROGMEM = R"EOF(-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE-----)EOF";

// Bufor do przechowywania odebranych slow
std::vector<String> wordBuffer;
int currentIndex = 0;
long lastDisplayTime = 0;
const long displayInterval = 1200; // Interwal wyswietlania slow na ekranie

// Ustawienia NTP (do synchronizacji czasu)
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;
const int daylightOffset_sec = 3600;

void setup() {
  Serial.begin(9600);
  connectToWiFi();
  syncTime();
  sensors.begin();
  lcd.init();
  lcd.backlight();
  lcd.clear(); 
  espClient.setTrustAnchors(new BearSSL::X509List(ca_cert));
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  connectToMQTT();
}

void syncTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.print("Synchronizing time...");
  while (time(nullptr) < 24 * 3600) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Time synchronized");
}
void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void connectToMQTT() {
  while (!client.connected()) {
    String client_id = "ESP8266Client-" + String(WiFi.macAddress());
    Serial.printf("Connecting to MQTT Broker as %s...\n", client_id.c_str());
    if (client.connect(client_id.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("Connected to MQTT broker");
      client.subscribe(topic_whisper); // Subskrypcja tematu "whisper"
      client.subscribe(topic_yolo); // Subskrypcja tematu yolo
    } else {
      // Wypisanie szczegolowego bledu SSL
      char error_msg[128];
      espClient.getLastSSLError(error_msg, sizeof(error_msg));
      Serial.print("Failed to connect to MQTT broker, SSL error: ");
      Serial.println(error_msg);
      delay(5000); // Odczekaj 5 sekund przed ponowna proba
    }
  }
}
void clearBottomRow() {
  lcd.setCursor(0, 1);
  lcd.print("                ");
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.print(topic);
  Serial.print("]: ");
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  if (String(topic) == topic_whisper) {
    // Przetwarzanie wiadomości z tematu "whisper"
    wordBuffer.push_back(message);
    Serial.println("Added message to buffer for display on LCD.");
  } else if (String(topic) == topic_yolo) {
    clearBottomRow();
    lcd.setCursor(0, 1);
    lcd.print(message);
    Serial.println("Message displayed on LCD (bottom row).");
  } else {
    // Obsługa innych tematów
    Serial.println("Message received on an unknown topic.");
  }
}
void clearTopRow() {
  lcd.setCursor(0, 0);
  lcd.print("                ");
}

void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();

  // Aktualizacja i wysylanie temperatury co 5 sekund
  static long lastTempUpdate = 0;
  if (millis() - lastTempUpdate > 5000) {
    lastTempUpdate = millis();
    sensors.requestTemperatures();
    float temperature = sensors.getTempCByIndex(0);

    if (temperature != DEVICE_DISCONNECTED_C) {
      String message = String(temperature, 1);
      client.publish(topic_temperature, message.c_str()); // Wysylanie temperatury na temat "temperature"
      Serial.print("Temperature sent: ");
      Serial.println(message);
    } else {
      Serial.println("Failed to read temperature from DS18B20");
    }
  }

  // Wyswietlanie kolejnych slow na LCD
  long now = millis();
  if (now - lastDisplayTime > displayInterval && !wordBuffer.empty()) {
    lcd.clear();
    clearTopRow();
    lcd.setCursor(0, 0);
    lcd.print(wordBuffer[currentIndex]);

    // Aktualizacja wskaznika wyswietlanego slowa
    currentIndex = (currentIndex + 1) % wordBuffer.size();
    lastDisplayTime = now;
  }

  // Usuwanie przestarzalych slow, jesli bufor staje sie zbyt duzy
  if (wordBuffer.size() > 7) {
    wordBuffer.erase(wordBuffer.begin()); // Usuwanie najstarszego slowa
  }
}