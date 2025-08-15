//Incluimos las librerias
#include "DHTesp.h"
//Decaramos el variable que almacena el pin a conectar el DHT11
int pinDHT = 15;
//Instanciamos el DHT
DHTesp dht;
void setup() {
  Serial.begin(115200);
  //Inicializamos el dht
  dht.setup(pinDHT, DHTesp::DHT11);
}
void loop() {
  //Obtenemos el arreglo de datos (humedad y temperatura)
  TempAndHumidity data = dht.getTempAndHumidity();
  //Mostramos los datos de la temperatura y humedad
  Serial.println("Temperatura: " + String(data.temperature, 2) + "°C");
  Serial.println("Humedad: " + String(data.humidity, 1) + "%");
  Serial.println("---");
  delay(1000);
}