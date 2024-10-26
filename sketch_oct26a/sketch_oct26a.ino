#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";
const char* serverUrl = "http://<your_laptop_ip>:5000/data";  // Update with your laptop's IP address

#define LDR_PIN 34  // Analog pin for LDR
#define MIC_PIN 35  // Analog pin for Mic module
#define LED_PIN 2   // Digital pin for LED
#define TRIG_IN 26  // Ultrasonic IN trigger
#define ECHO_IN 27  // Ultrasonic IN echo
#define TRIG_OUT 32 // Ultrasonic OUT trigger
#define ECHO_OUT 33 // Ultrasonic OUT echo

int peopleCount = 0;
int peopleIn = 0;
int peopleOut = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(TRIG_IN, OUTPUT);
  pinMode(ECHO_IN, INPUT);
  pinMode(TRIG_OUT, OUTPUT);
  pinMode(ECHO_OUT, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  int ldrValue = analogRead(LDR_PIN);
  int micValue = analogRead(MIC_PIN);
  int distIn = measureDistance(TRIG_IN, ECHO_IN);
  int distOut = measureDistance(TRIG_OUT, ECHO_OUT);

  if (micValue > 3000) {
    Serial.println("Be Quiet!");
  }
  
  if (ldrValue < 1000) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  if (distIn < 50) {
    peopleCount++;
    peopleIn++;
    delay(500);
  }
  if (distOut < 50) {
    peopleCount--;
    peopleOut++;
    delay(500);
  }

  sendDataToServer(ldrValue, micValue, peopleIn, peopleOut, peopleCount);

  delay(1000);
}

int measureDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  return pulseIn(echoPin, HIGH) * 0.034 / 2;
}

void sendDataToServer(int ldr, int mic, int in, int out, int current) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{\"ldr\":" + String(ldr) + ",\"mic\":" + String(mic) + 
                      ",\"in\":" + String(in) + ",\"out\":" + String(out) +
                      ",\"current\":" + String(current) + "}";
    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response: " + response);
    } else {
      Serial.println("Error in sending POST: " + String(httpResponseCode));
    }
    http.end();
  }
}
