# 1 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
/*

 * test_lcd.ino

 * Utiliser la bibliothèque LiquidCrystal pour faire afficher

 * des messages/données sur l'afficheur LCD.

 * 

 * L'afficheur LCD pourrait être intégré dans le projet IoT

 * de ce cours.

 * 

 * GPA788 - ETS

 * T. Wong

 * 08-2019

 * 08-2020

 * 

 * Ce programme est inspéré de l'exemple "Hello World!" de la page:

 * https://www.arduino.cc/en/Tutorial/HelloWorld. La classe LiquidCrystal()

 * et ses fonctions membres sont listées sur la page: 

 * https://www.arduino.cc/en/Reference/LiquidCrystal

 * Le branchement électrique est présenté d'une façon plus évidente dans le

 * protocole de laboratoire du cours. Finalement, la technique de lecture

 * de la température interne de l'ATmega328P est donnée dans les notes

 * de cours.

 */
# 23 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
// Classe pour afficher des caractères à l'aide du LCD
# 25 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 2
// Classe pour mesurer la température interne de l'ATmega328P 
# 27 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 2


/* ---------------------------------------------------------------

   Créer un objet (global) de type LiquidCrystal.

   Le constructeur utilisé est:

     LiquidCrystal(rs, enable, d4, d5, d6, d7)

     rs (register select): broche 12

     enable: broche 11

     d4: broche 5, d5: broche 4, d6: broche 3, d7: broche 2

   ---------------------------------------------------------------    

   Note: Les numéros de broches sont ceux du côté d'Arduino.   

         Brancher ces broches sur l'afficheur LCD selon le

         diagramme électrique donné sur le protocole de laboratoire.

   --------------------------------------------------------------- */
# 41 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
/* ---------------------------------------------------------------

   Créer un objet (global) de type ChipTemp.

   Le constructeur utilisé est:

     ChipTemp(float g, float d)

     g: gain de l'ajustement, d: décalage de l'ajustement

     

   Normalement le gain et le décalage sont des valeurs obtenues

   par une procédure de calibration. Dans ce laboratoire, on utilisera

   des constantes proposées par Albert van Daln, l'auteur du code

   original de ChipTemp.

   --------------------------------------------------------------- */
# 53 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
const float DECALAGE{316.0}; //332.70; //335.2; // Choisir la bonne...
const float GAIN{1.22}; //1.06154;              // Choisir la bonne...

/*---------------------------------------------*/
/* Constantes et variables globales */
/*---------------------------------------------*/

// Taux de transmission du port série
const int BAUD_RATE{9600};

// Créer un objet de type dht
dhtlib_gpa788 DHT(7);

void setup() {
// Initialiser la vitesse du port série
  Serial.begin(BAUD_RATE);

  lcd.begin(16,2);
  lcd.clear();
}

const int16_t NB_MSG_COUNT{2};
void loop() {

  static int16_t messageCount{0};
  static bool showingMessage{true};

  if (messageCount == 0) {
    lcd.clear();

    if (showingMessage) {
        showTemp(DHT, lcd);
    }
    else{
        welcome(lcd);
    }
  }

  if (messageCount++ > NB_MSG_COUNT) {
    messageCount = 0;
    showingMessage = !showingMessage;
  }

  // Faire clignoter lentement l'afficheur
  lcd.display();
  waitUntil(2000);
  lcd.noDisplay();
  waitUntil(1000);
}

/* ---------------------------------------------------------------

   Fonction pour créer un delai de w millisecondes

   

   La fonction delay() est utilisée dans bien des tutoriel pour

   créer un delai temporel. On peut aussi créer notre propre délai

   et utiliser une unité de temps à notre guise.

   --------------------------------------------------------------- */
# 110 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
void waitUntil(uint32_t w) {
  uint32_t t{millis()};
  // Attendre w millisecondes
  while (millis() < t + w) {}
}

/* ---------------------------------------------------------------

   Fonction pour afficher un message de bienvenue.

   ---------------------------------------------------------------

   Note: On aurait pu utiliser l'objet global lcd directement.

   --------------------------------------------------------------- */
# 121 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
void welcome(LiquidCrystal &l) {
  // D'abord le terminal série
  Serial.println((reinterpret_cast<const __FlashStringHelper *>(
# 123 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                (__extension__({static const char __c[] __attribute__((__progmem__)) = (
# 123 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                "Bienvenue au GPA788 OC/IoT"
# 123 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                ); &__c[0];}))
# 123 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                )));
  // Ensuite l'afficheur LCD
  l.setCursor(0, 0); // Cursuer à la 1ere colonne, 1ere ligne
  l.print("Bienvenue au"); // Afficher le texte...
  l.setCursor(0, 1); // Curseur à la 1ere colonne, 2e ligne
  l.print("GPA788 OC/IoT"); // Afficher le texte...}
}

/* ---------------------------------------------------------------

   Fonction pour afficher la température interne de l'ATmega328P.

   ---------------------------------------------------------------

   Note: On aurait pu utiliser l'objet global chipTemp directement.

   --------------------------------------------------------------- */
# 136 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
void showTemp(dhtlib_gpa788 &d, LiquidCrystal &l) {

  DHTLIB_ErrorCode chk = d.read11(d.getPin());

  // D'abord le terminal série
  if (chk == DHTLIB_ErrorCode::DHTLIB_OK) {
    Serial.print((reinterpret_cast<const __FlashStringHelper *>(
# 142 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                (__extension__({static const char __c[] __attribute__((__progmem__)) = (
# 142 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                "Température = "
# 142 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                ); &__c[0];}))
# 142 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                )));
    Serial.println(d.getTemperature());
    Serial.print((reinterpret_cast<const __FlashStringHelper *>(
# 144 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                (__extension__({static const char __c[] __attribute__((__progmem__)) = (
# 144 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                "Humidité = "
# 144 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino" 3
                ); &__c[0];}))
# 144 "/Users/samuellauzon/Sam/Ecole/AUT2021/GPA788/LAB1/ProjetIOT/ProjetIOT.ino"
                )));
    Serial.println(d.getHumidity());
    // Ensuite l'afficheur LCD
    l.setCursor(0,0); l.print("Temp: "); l.print(d.getTemperature()); l.print((char)223); l.print("C");
    l.setCursor(0,1); l.print("Humidity: "); l.print(d.getHumidity()); l.print("%");
  }

  else{
    l.setCursor(0,0); l.print("DHT11: Erreur");
    l.setCursor(0,1); l.print("DHT11: Code");
    l.print((uint8_t)chk);
  }


}
