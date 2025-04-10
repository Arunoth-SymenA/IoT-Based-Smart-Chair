#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Pin definitions
#define S0 25
#define S1 26
#define S2 27
#define S3 32
#define MUX_SIG 34
#define GREEN_LED 12
#define RED_LED 14
#define BUILTIN_LED 2

// DHT22
#define DHTPIN 4
#define DHTTYPE DHT22

// Threshold for pressure detection
#define PRESSURE_THRESHOLD 100

// WiFi credentials
const char* ssid = "******";
const char* password = "*******";

// Google Apps Script URL - REPLACE WITH YOUR ACTUAL URL
const char* googleScriptUrl = "https://script.google.com/macros/s/AKfycbwFf7epl4aLooQaQuwpO4kNYRSF6kAoNyJt2rCd3dNmlJ4ajh6qG7rEZkanURfMmF3PlQ/exec";

// Sensor objects
Adafruit_MPU6050 mpu;
DHT dht(DHTPIN, DHTTYPE);

void selectMuxChannel(byte channel) {
  digitalWrite(S0, bitRead(channel, 0));
  digitalWrite(S1, bitRead(channel, 1));
  digitalWrite(S2, bitRead(channel, 2));
  digitalWrite(S3, bitRead(channel, 3));
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  // Blink built-in LED while connecting
  pinMode(BUILTIN_LED, OUTPUT);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    digitalWrite(BUILTIN_LED, !digitalRead(BUILTIN_LED));
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(BUILTIN_LED, HIGH);
    Serial.println("");
    Serial.println("WiFi Connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("WiFi Connection Failed");
  }
}

void sendDataToGoogleSheets(String data) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    String fullUrl = String(googleScriptUrl) + "?" + data;
    Serial.println("Sending to URL: " + fullUrl);
    
    http.begin(fullUrl);
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    
    // Add headers
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Server Response: " + payload);
    } else {
      Serial.printf("HTTP Error: %d - %s\n", httpCode, http.errorToString(httpCode).c_str());
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected - Attempting to reconnect");
    connectToWiFi();
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  // Initialize pins
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(MUX_SIG, INPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  
  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, LOW);

  // Connect to WiFi
  connectToWiFi();

  // Initialize I2C
  Wire.begin(21, 22);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) delay(10);
  }
  Serial.println("MPU6050 Found!");
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  // Initialize DHT22
  dht.begin();
  Serial.println("DHT22 Initialized");
  
  // Initial delay for sensors to stabilize
  delay(2000);
}

void loop() {
  // Read FSR values
  String fsrData = "";
  int activeSensors = 0;
  
  for (int i = 0; i < 12; i++) {
    selectMuxChannel(i);
    delay(10); // Small delay for mux to settle
    int fsrValue = analogRead(MUX_SIG);
    
    if (fsrValue > PRESSURE_THRESHOLD) {
      activeSensors++;
    }
    
    fsrData += "fsr" + String(i) + "=" + String(fsrValue);
    if (i < 11) fsrData += "&";
    
    Serial.print("FSR");
    Serial.print(i);
    Serial.print(": ");
    Serial.print(fsrValue);
    Serial.print("\t");
  }
  Serial.println();

  // Read MPU6050
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Read DHT22 (with error checking)
  float humidity = dht.readHumidity();
  float dhtTemp = dht.readTemperature();
  
  if (isnan(humidity) || isnan(dhtTemp)) {
    Serial.println("Failed to read from DHT sensor!");
    humidity = -1;
    dhtTemp = -1;
  }

  // Prepare complete data string
  String postData = fsrData + 
                   "&active=" + String(activeSensors) +
                   "&accelX=" + String(a.acceleration.x, 2) +
                   "&accelY=" + String(a.acceleration.y, 2) +
                   "&accelZ=" + String(a.acceleration.z, 2) +
                   "&gyroX=" + String(g.gyro.x, 2) +
                   "&gyroY=" + String(g.gyro.y, 2) +
                   "&gyroZ=" + String(g.gyro.z, 2) +
                   "&mpuTemp=" + String(temp.temperature, 2) +
                   "&dhtHumidity=" + String(humidity, 2) +
                   "&dhtTemp=" + String(dhtTemp, 2);

  Serial.println("Complete Data: " + postData);
  
  // Send data to Google Sheets
  sendDataToGoogleSheets(postData);

  // Control LEDs based on active sensors
  digitalWrite(GREEN_LED, activeSensors > 4 ? HIGH : LOW);
  digitalWrite(RED_LED, activeSensors > 4 ? LOW : HIGH);

  delay(500); // 1 second delay between uploads
}
