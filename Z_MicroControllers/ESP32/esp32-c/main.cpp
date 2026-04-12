#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Data structure for managing various flags
typedef struct _vFlag
{
  // Flags for different functionalities
  uint8_t BTFlag = 0;
  uint8_t DC_Flag = 0;
  uint8_t CANFlag = 0;
  uint8_t I2C_Flag = 0;
  uint8_t BMP180Flag = 0;
  uint8_t DS18B20Flag = 0;
  uint8_t JSONFlag = 0;
  uint8_t Radar_L_Flag = 0;
  uint8_t Radar_R_Flag = 0;
  uint8_t sensor_Flag = 0;
  uint8_t sensor1_Flag = 0;
  uint8_t initial_Flag = 0;
  uint8_t Tone_Flag = -1;
  uint8_t IR_RECV_Flag = 0;
  uint8_t IR_SEND_Flag = 0;
  uint8_t FunctionFlag = 3;
  uint8_t SendFlag = 0;
  uint8_t BMPCnt = 0;
} vFlag;

vFlag *flag_Ptr;
vFlag flag;

// Function declarations
void processCommand(char *data);
void vDS18B20Task();

// Rest of your code...


// DS18B20 setup
#define DQ_Pin 4
OneWire oneWire(DQ_Pin);
DallasTemperature sensors(&oneWire);

byte data[12]; // Buffer for data
byte address[8]; // 64-bit device address

// UART setup
#define LINE_BUFFER_LENGTH 64

// Data structure for managing UART communication
typedef struct _vUart
{
  char c;
  int lineIndex = 0;
  int line1Index = 0;
  int BTlineIndex = 0;
  bool lineIsComment;
  bool lineSemiColon;
  char line[128];
  char BTline[20];
  String inputString;
  String BTinputString;
  String S1inputString;
  int V[16];
  char ctemp[30];
  char I2C_Data[80];
  int DC_Spped = 50;
  float Voltage[16];
  int Buffer[128];
  int StartCnt = 0;
  int ReadCnt = 0;
  int sensorValue = 0;
} vUart;

vUart *Uart_Ptr;
vUart Uart;

void setup()
{
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println(F("init"));

  // Search for DS18B20 temperature sensor on the OneWire bus
  if (oneWire.search(address))
  {
    Serial.println("Slave device found!");
    Serial.print("Device Address = ");
    Serial.println(address[0]);
  }
  else
  {
    Serial.println("Slave device not found!");
  }

  // Initialize DS18B20 sensor
  sensors.begin();
}

void loop()
{
  Serial.print(F("Main at core:"));
  Serial.println(xPortGetCoreID());

  while (1)
  {
    // Check for incoming serial data
    while (Serial.available() > 0)
    {
      Uart.c = Serial.read();

      if ((Uart.c == '\n') || (Uart.c == '\r'))
      {
        // End of line reached, process the command
        if (Uart.lineIndex > 0)
        {
          Uart.line[Uart.lineIndex] = '\0'; // Terminate string
          processCommand(Uart.line);
          Uart.lineIndex = 0;
          Uart.inputString = "";
        }
        else
        {
          // Empty or comment line, skip it.
        }
        Uart.lineIsComment = false;
        Uart.lineSemiColon = false;
        Serial.println(F("ok>"));
      }
      else
      {
        // Process characters in the current line
        if ((Uart.lineIsComment) || (Uart.lineSemiColon))
        {
          if (Uart.c == ')')
            Uart.lineIsComment = false; // End of comment. Resume line.
        }
        else
        {
          if (Uart.c == '/')
          {
            // Block delete not supported. Ignore character.
          }
          else if (Uart.c == '~')
          {
            // Enable comments flag and ignore characters until ')' or EOL.
            Uart.lineIsComment = true;
          }
          else if (Uart.c == ';')
          {
            Uart.lineSemiColon = true;
          }
          else if (Uart.lineIndex >= LINE_BUFFER_LENGTH - 1)
          {
            Serial.println("ERROR - lineBuffer overflow");
            Uart.lineIsComment = false;
            Uart.lineSemiColon = false;
          }
          else if (Uart.c >= 'a' && Uart.c <= 'z')
          {
            // Upcase lowercase characters
            Uart.line[Uart.lineIndex] = Uart.c - 'a' + 'A';
            Uart.lineIndex = Uart.lineIndex + 1;
            Uart.inputString += (char)(Uart.c - 'a' + 'A');
          }
          else
          {
            Uart.line[Uart.lineIndex] = Uart.c;
            Uart.lineIndex = Uart.lineIndex + 1;
            Uart.inputString += Uart.c;
          }
        }
      }
    }

    // If the DS18B20Flag is set, call the vDS18B20Task function
    if (flag.DS18B20Flag == 1)
    {
      vDS18B20Task();
    }
  }
}

void processCommand(char *data)
{
  // Process incoming commands
  int len, xlen, ylen, zlen, alen;
  int tempDIO;
  String stemp;

  len = Uart.inputString.length();

  if (strstr(data, "VER") != NULL)
  {
    Serial.println(F("ESP32_20230710"));
  }
  if (strstr(data, "DS18B20_ON") != NULL)
  {
    flag.DS18B20Flag = 1;
    Serial.println(F("DS18B20_ON"));
  }
  if (strstr(data, "DS18B20_OFF") != NULL)
  {
    flag.DS18B20Flag = 0;
    Serial.println(F("DS18B20_OFF"));
  }
}

void vDS18B20Task()
{
  // Request and print temperature from DS18B20 sensor
  Serial.print("Temperatures --> ");
  sensors.requestTemperatures();
  Serial.println(sensors.getTempCByIndex(0));
}
