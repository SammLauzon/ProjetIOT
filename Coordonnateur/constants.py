#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
'''Des constantes pour le fonctionnement du coordonnateur.

Ce module fait partie du programme ex_i2c_coord_v[X].py

GPA788 Conception et intégration des objets connectés
Tony Wong
Juillet 2020
'''

# Temps d'échantillonnage du coordonnateur. Il doit être
# supérieur au temps d'échantillonage du noeud.
SAMPLING_TIME = 1      # Ts du coordonnateur
NEW_TS = 6              # nouvelle Ts pour le noeud
NEW_Vrms = 32           # nouvelle valeur Vrms pour le MAX4466
New_Li = 10             # nouvelle valeur Li pour le MAX4466
THINGSPK_URL = 'https://api.thingspeak.com/update' #URL pour la platforme thingspeak
THINGSPK_API_KEY = 'FKFMV3PVL12YV209' #API_KEY d'écriture pour le serveur infonuagique
DELAY = 20              # interval de transmission

# Adresses IC2 du noeud - tuple
I2C_ADDRESS = (0x44, 0x45)

# Adresse min et max du I2C à 7 bits
I2C_MAX_ADR = 127
I2C_MIN_ADR = 0

# Commandes possible entre le coordonnateur et le noeud
I2C_CMD_SET_TS = 0xA0   # Changer le temps d'échantillonnage
I2C_CMD_SET_STOP = 0xA1 # Arrêter l'échantillonnage
I2C_CMD_SET_GO = 0xA2   # Démarrer l'échantillonnage
I2C_CMD_SET_NB_VRMS = 0xA3   # Changer le nombre de Vrms
I2C_CMD_SET_NB_LI = 0xA4   # Changer le nombre d'échantillon Li pour calculer Leq
I2C_CMD_SET_PAUSE = 0xA5  # Met les noeuds sur pause (n'envoie plus les données)
I2C_CMD_SET_RESTART = 0xA6 # Redémarrage de l'envoie des données des noeuds 

# Adresse des registres sur le noeud. Elle correspond
# à la carte des registres du noeud.
I2C_NODE_TS = 0         # Temps d'échantillonnage (1 octet)
I2C_NODE_NS_LSB = 1     # Nombre d'échantillons depuis la mise en
I2C_NODE_NS_MSB = 2     # marche du noeud (int sur 2 octets)
I2C_NODE_TEMP_LSB0 = 3  # Temperature DHT11 et intensité MAX4466
I2C_NODE_TEMP_LSB1 = 4  # (float sur 4 octets)
I2C_NODE_TEMP_MSB0 = 5  
I2C_NODE_TEMP_MSB1 = 6
I2C_NODE_HUM_LSB0 = 7   # Humidité DHT11
I2C_NODE_HUM_LSB1 = 8   # (float sur 4 octets)
I2C_NODE_HUM_MSB0 = 9
I2C_NODE_HUM_MSB1 = 10

