

// WIFI and DHT11??




#include <Arduino.h>
#include <WiFiMulti.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 23

#define DHTTYPE DHT11

DHT_Unified dht(DHTPIN, DHTTYPE);

uint32_t delayMS;

#define WIFI_SSID "GiBWifi_EXT"
#define WIFI_PASSWORD "abcdefg1234"

WiFiMulti wifiMulti;



#define ledPin 2

void blink_led(unsigned int times, unsigned int duration){
  for (int i = 0; i < times; i++) {
    digitalWrite(ledPin, HIGH);
    delay(duration);
    digitalWrite(ledPin, LOW); 
    delay(200);
  }
}

void setup() {
  Serial.begin(921600);
  pinMode(LED_BUILTIN, OUTPUT);

  wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);

  while (wifiMulti.run() != WL_CONNECTED) {
    delay(100);
  }

  Serial.println("Connected");
  blink_led(10,200);
}

void loop() {
  //digitalWrite(LED_BUILTIN, WiFi.status() == WL_CONNECTED);
    // Delay between measurements.
  digitalWrite(LED_BUILTIN, HIGH);
  delay(delayMS);
  // Get temperature event and print its value.
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature!"));
  }
  else {
    Serial.print(F("Temperature: "));
    Serial.print(event.temperature);
    Serial.println(F("°C"));
  }
  // Get humidity event and print its value.
  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity!"));
  }
  else {
    Serial.print(F("Humidity: "));
    Serial.print(event.relative_humidity);
    Serial.println(F("%"));
  }
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}


















//dht11 not working



// #include <Arduino.h>
// // DHT Temperature & Humidity Sensor
// // Unified Sensor Library Example
// // Written by Tony DiCola for Adafruit Industries
// // Released under an MIT license.

// // REQUIRES the following Arduino libraries:
// // - DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library
// // - Adafruit Unified Sensor Lib: https://github.com/adafruit/Adafruit_Sensor

// #include <Adafruit_Sensor.h>
// #include <DHT.h>
// #include <DHT_U.h>

// #define DHTPIN 23     // Digital pin connected to the DHT sensor 
// // Feather HUZZAH ESP8266 note: use pins 3, 4, 5, 12, 13 or 14 --
// // Pin 15 can work but DHT must be disconnected during program upload.

// // Uncomment the type of sensor in use:
// #define DHTTYPE DHT11     // DHT 11
// //#define DHTTYPE    DHT22     // DHT 22 (AM2302)
// //#define DHTTYPE    DHT21     // DHT 21 (AM2301)

// // See guide for details on sensor wiring and usage:
// //   https://learn.adafruit.com/dht/overview

// DHT_Unified dht(DHTPIN, DHTTYPE);

// uint32_t delayMS;

// void setup() {
//   Serial.begin(9600);
//   // Initialize device.
//   dht.begin();
//   Serial.println(F("DHTxx Unified Sensor Example"));
//   // Print temperature sensor details.
//   sensor_t sensor;
//   dht.temperature().getSensor(&sensor);
//   Serial.println(F("------------------------------------"));
//   Serial.println(F("Temperature Sensor"));
//   Serial.print  (F("Sensor Type: ")); Serial.println(sensor.name);
//   Serial.print  (F("Driver Ver:  ")); Serial.println(sensor.version);
//   Serial.print  (F("Unique ID:   ")); Serial.println(sensor.sensor_id);
//   Serial.print  (F("Max Value:   ")); Serial.print(sensor.max_value); Serial.println(F("°C"));
//   Serial.print  (F("Min Value:   ")); Serial.print(sensor.min_value); Serial.println(F("°C"));
//   Serial.print  (F("Resolution:  ")); Serial.print(sensor.resolution); Serial.println(F("°C"));
//   Serial.println(F("------------------------------------"));
//   // Print humidity sensor details.
//   dht.humidity().getSensor(&sensor);
//   Serial.println(F("Humidity Sensor"));
//   Serial.print  (F("Sensor Type: ")); Serial.println(sensor.name);
//   Serial.print  (F("Driver Ver:  ")); Serial.println(sensor.version);
//   Serial.print  (F("Unique ID:   ")); Serial.println(sensor.sensor_id);
//   Serial.print  (F("Max Value:   ")); Serial.print(sensor.max_value); Serial.println(F("%"));
//   Serial.print  (F("Min Value:   ")); Serial.print(sensor.min_value); Serial.println(F("%"));
//   Serial.print  (F("Resolution:  ")); Serial.print(sensor.resolution); Serial.println(F("%"));
//   Serial.println(F("------------------------------------"));
//   // Set delay between sensor readings based on sensor details.
//   delayMS = sensor.min_delay / 1000;
// }

// void loop() {
//   // Delay between measurements.
//   digitalWrite(LED_BUILTIN, HIGH);
//   delay(delayMS);
//   // Get temperature event and print its value.
//   sensors_event_t event;
//   dht.temperature().getEvent(&event);
//   if (isnan(event.temperature)) {
//     Serial.println(F("Error reading temperature!"));
//   }
//   else {
//     Serial.print(F("Temperature: "));
//     Serial.print(event.temperature);
//     Serial.println(F("°C"));
//   }
//   // Get humidity event and print its value.
//   dht.humidity().getEvent(&event);
//   if (isnan(event.relative_humidity)) {
//     Serial.println(F("Error reading humidity!"));
//   }
//   else {
//     Serial.print(F("Humidity: "));
//     Serial.print(event.relative_humidity);
//     Serial.println(F("%"));
//   }
//   delay(1000);
//   digitalWrite(LED_BUILTIN, LOW);
//   delay(1000);
// }








//not working: https://www.youtube.com/watch?v=rdUepNx1Rs4&t=326s

// #include <Arduino.h>
// #include <WiFiMulti.h>


// //Incluimos las librerias
// #include "DHTesp.h"
// //Decaramos el variable que almacena el pin a conectar el DHT11
// int pinDHT = 15;
// //Instanciamos el DHT
// DHTesp dht;

// void setup() {
//   Serial.begin(460800);
//   digitalWrite(LED_BUILTIN, HIGH);
//   //Inicializamos el dht
//   dht.setup(pinDHT, DHTesp::DHT11);
//   digitalWrite(LED_BUILTIN, HIGH);
// }
// void loop() {
//   //Obtenemos el arreglo de datos (humedad y temperatura)
//   digitalWrite(LED_BUILTIN, HIGH);
//   TempAndHumidity data = dht.getTempAndHumidity();
//   //Mostramos los datos de la temperatura y humedad
//   Serial.println("Temperatura: " + String(data.temperature, 2) + "°C");
//   Serial.println("Humedad: " + String(data.humidity, 1) + "%");
//   Serial.println("---");
//   delay(2000);
//   digitalWrite(LED_BUILTIN, LOW);
//   delay(2000);
// }













// /*********
//   Author: Jitesh Saini
//   This code is built upon the example code in pubsubclient library 
//   Complete project details at https://helloworld.co.in
// *********/

// #include <WiFi.h>
// #include <PubSubClient.h>


// // Replace the SSID/Password details as per your wifi router
// const char* ssid = "GiBWifi_EXT";
// const char* password = "8L4@xdJ$iAd$SQD4";

// // Replace your MQTT Broker IP address here:
// const char* mqtt_server = "192.168.3.100";

// WiFiClient espClient;
// PubSubClient client(espClient);

// long lastMsg = 0;

// #define ledPin 2

// void blink_led(unsigned int times, unsigned int duration){
//   for (int i = 0; i < times; i++) {
//     digitalWrite(ledPin, HIGH);
//     delay(duration);
//     digitalWrite(ledPin, LOW); 
//     delay(200);
//   }
// }

// void setup_wifi() {
//   delay(50);
//   Serial.println();
//   Serial.print("Connecting to ");
//   Serial.println(ssid);

//   WiFi.begin(ssid, password);

//   int c=0;
//   while (WiFi.status() != WL_CONNECTED) {
//     blink_led(5,200); //blink LED twice (for 200ms ON time) to indicate that wifi not connected
//     delay(1000); //
//     Serial.print(".");
//     c=c+1;
//     if(c>10){
//         ESP.restart(); //restart ESP after 10 seconds
//     }
//   }

//   Serial.println("");
//   Serial.println("WiFi connected");
//   Serial.println("IP address: ");
//   Serial.println(WiFi.localIP());

//   digitalWrite(ledPin, HIGH);
//   delay(500);
//   digitalWrite(ledPin, LOW); 
//   delay(200);
  
// }

// void connect_mqttServer() {
//   // Loop until we're reconnected
//   while (!client.connected()) {

//         //first check if connected to wifi
//         if(WiFi.status() != WL_CONNECTED){
//           //if not connected, then first connect to wifi
//           setup_wifi();
//         }

//         //now attemt to connect to MQTT server
//         Serial.print("Attempting MQTT connection...");
//         // Attempt to connect
//         if (client.connect("ESP32_client1")) { // Change the name of client here if multiple ESP32 are connected
//           //attempt successful
//           Serial.println("connected");
//           // Subscribe to topics here
//           client.subscribe("rpi/broadcast");
//           //client.subscribe("rpi/xyz"); //subscribe more topics here
          
//         } 
//         else {
//           //attempt not successful
//           Serial.print("failed, rc=");
//           Serial.print(client.state());
//           Serial.println(" trying again in 2 seconds");
    
//           blink_led(10,200); //blink LED three times (200ms on duration) to show that MQTT server connection attempt failed
//           // Wait 2 seconds before retrying
//           delay(2000);
//         }
//   }
  
// }

// //this function will be executed whenever there is data available on subscribed topics
// void callback(char* topic, byte* message, unsigned int length) {
//   Serial.print("Message arrived on topic: ");
//   Serial.print(topic);
//   Serial.print(". Message: ");
//   String messageTemp;
  
//   for (int i = 0; i < length; i++) {
//     Serial.print((char)message[i]);
//     messageTemp += (char)message[i];
//   }
//   Serial.println();

//   // Check if a message is received on the topic "rpi/broadcast"
//   if (String(topic) == "rpi/broadcast") {
//       if(messageTemp == "10"){
//         Serial.println("Action: blink LED");
//         blink_led(1,1250); //blink LED once (for 1250ms ON time)
//       }
//   }

//   //Similarly add more if statements to check for other subscribed topics 
// }

// void setup() {
//   pinMode(ledPin, OUTPUT);
//   Serial.begin(115200);

//   setup_wifi();
//   client.setServer(mqtt_server,1883); //1883 is the default port for MQTT server
//   client.setCallback(callback);
// }

// void loop() {
  
//   if (!client.connected()) {
//     connect_mqttServer();
//   }

//   client.loop();
  
//   long now = millis();
//   if (now - lastMsg > 4000) {
//     lastMsg = now;

//     client.publish("esp32/sensor1", "88"); //topic name (to which this ESP32 publishes its data). 88 is the dummy value.
    
//   }
  
// }






// OK!!!!!!!!!!!!!



// #include <Arduino.h>
// #include <WiFiMulti.h>

// #define WIFI_SSID "GiBWifi_EXT"
// #define WIFI_PASSWORD "8L4@xdJ$iAd$SQD4"

// WiFiMulti wifiMulti;

// void setup() {
//   Serial.begin(921600);
//   pinMode(LED_BUILTIN, OUTPUT);

//   wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);

//   while (wifiMulti.run() != WL_CONNECTED) {
//     delay(100);
//   }

//   Serial.println("Connected");
// }

// void loop() {
//   digitalWrite(LED_BUILTIN, WiFi.status() == WL_CONNECTED);
// }













// #include <Arduino.h>

// // put function declarations here:
// int myFunction(int, int);

// void setup() {
//   // put your setup code here, to run once:
//   //int result = myFunction(2, 3);

//   pinMode(LED_BUILTIN, OUTPUT);

//   Serial.begin(921600);
//   Serial.println("Hello from setup");
// }

// void loop() {
//   // put your main code here, to run repeatedly:
//   delay(1000); //in sec delay
//   digitalWrite(LED_BUILTIN, HIGH);
//   delay(1000);
//   digitalWrite(LED_BUILTIN, LOW);
// }

// put function definitions here:
// int myFunction(int x, int y) {
//   return x + y;
// }