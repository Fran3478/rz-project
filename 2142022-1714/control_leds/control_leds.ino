#include <DHT.h>
#include <DHT_U.h>
#define DHTPIN 12
#define DHTTYPE DHT11
//Debe incluir las librerias: "Adafruit Unified Sensor" y "DHT sensor library" ambas de Adafruit

DHT dht(DHTPIN, DHTTYPE);
int blue1 = 11;
int red1 = 10;
int green1 = 9;
int blue2 = 6;
int red2 = 5;
int green2 = 3;
int cont = 60;
byte i = 0;
double data [] = {};
void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(red1, OUTPUT);
  pinMode(blue1, OUTPUT);
  pinMode(green1, OUTPUT);
  pinMode(red2, OUTPUT);
  pinMode(blue2, OUTPUT);
  pinMode(green2, OUTPUT);
}

void loop() {
  
  if (cont == 60) {
    cont = 0;
    if (i <= (sizeof(data) / sizeof(data[0]))) {
      int red = map(data[i], 0, 100, 0, 128);
      int blue = 128 - red;
      int green = 0;
      i += 1;
      analogWrite (blue2, blue);
      analogWrite (red2, red);
      analogWrite (green2, green);
    }
  }
  
  delay(2000);
  cont += 2;
  float humidity = dht.readHumidity();

  //Control de fallo al tomar medidas
  if (isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  int red = map(humidity, 0, 100, 0, 128);
  int blue = 128 - red;
  int green = 0;
  analogWrite (blue1, blue);
  analogWrite (red1, red);
  analogWrite (green1, green);

}
