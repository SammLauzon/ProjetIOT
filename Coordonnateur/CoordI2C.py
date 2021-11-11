#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Ce programme réalise le côté coordonnateur d'une communication I2C.

Version du programme ex_i2c_coord gérant deux (2) noeuds. La gestion
des exceptions/erreurs repose sur le style orienté-objet de Python.

Contexte
-=-=-==-
Dans cet exemple, les noeuds (Arduino) effectuent:
  1) la lecture de la température du CPU;
  2) incrémenter le numéro d'échantillon.
selon la période d'échantillonnage NEW_TS programmé par le coordonnateur (Pi).
À toutes les SAMPLING_TIME, le coordonnateur lit ces deux valeurs des noeuds
et les affiche à la sortie standard (terminal Python). On a NEW_TS != SAMPLE_TIME
pour montrer l'asynchronisme entre les noeuds et le coordonnateur.

(voir les notes de cours "I2C: Pi et Arduino")

GPA788 Conception et intégration des objets connectés
T. Wong
Juin 2018
Juillet 2020
'''

# -------------------------------------------------------------------
# Les modules utiles
# -------------------------------------------------------------------
import smbus            # pour la communication I2C
import time             # pour sleep()
import struct           # pour la conversion octet -> float
from datetime import datetime    # pour l'horodatage des échantillons
import constants as cst # constants du programme
import datetime

# -------------------------------------------------------------------
# Structures pour la conversion des données reçues
# -------------------------------------------------------------------
''' bytearray
    Liste d'octets qui servira à la conversion octets -> int (numéro d'échantillon)
    et octets -> float (températire interne de l'ATmega328P)

    dictionnaire de dictionnaires
    Structure servant à entreposer les valeurs (no. d'échantillon et tempéraure)
    de chaque des noeuds. Les dictionnaires permettent l'indexage numérique et
    alphanumérique des champs. Ainsi, on utilisera l'adresse I2C des noeuds
    comme l'index principal. Cela facilitera la programmation des accès aux données.
'''
# -------------------------------------------------------------------
# Classe d'exception
# -------------------------------------------------------------------
class CoordException(Exception):
  '''Cette classe représente les exceptions en lien avec l'utilisation
     des fonctions de ce programme.

  Un objet de cette classe d'exception est envoyée au programme principal
  par les fonctions. Elle représente les problèmes détectés l'utilisation
  du bus I2C et les bornes fonctions MAIS pas les erreurs de communication I2C.
  '''
  def __init__(self, *args):
    if args:
      self.message = args[0]
    else:
      self.message = None
      super().__init__(self.message)

  def __str__(self):
    if self.message:
      return self.message
    else:
      return F"Exception CoordException a été lancée."



# -------------------------------------------------------------------
# Classe de communication
# -------------------------------------------------------------------
class CoordCommunication():

  def __init__(self, address = -1, bus = None):

    self.address = address
    self.bus = bus

  # ------------------------------------------------------
  # Fonctions utilisateurs
  # ------------------------------------------------------
  def send_stop(self):
    '''Envoyer la commande Arrêt sur le bus i2c au noeud à l'adresse adr.

    Paramètres:
    bus -- objet SMBUS déjà initialisé
    adr (int) -- adresse du noeud destinataire

    Retour: n/a
    Exceptions possibles: CoordException, IOError
    '''
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      self.bus.write_byte(self.address, cst.I2C_CMD_SET_STOP)
    else:
      raise CoordException(F"<send_stop> Bus non initié ou adresse I2C invalide.")

  def send_go(self):
    '''Envoyer la commande démarrage sur le bus i2c au noeud à l'adresse adr.

    Arguments:
    bus -- objet SMBUS déjà initialisé
    adr (int) -- adresse du noeud destinataire

    Retour: n/a
    Exceptions possibles: CoordException, IOError
    '''
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      self.bus.write_byte(self.address, cst.I2C_CMD_SET_GO)
    else:
      raise CoordException(F"<send_go> Bus non initié ou adresse I2C invalide.")

  def send_Ts(self, ts = -1):
    '''Envoyer la commande pour le changement de période d'échantillonnage
    et sa nouvelle valeur.

    Arguments:
    bus -- objet SMBUS déjà initialisé
    adr (int) -- adresse du noeud destinataire
    ts (int) -- nouvelle période d'échantillonnage

    Retour: n/a
    Exceptions possibles: CoordException, IOError
    '''
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Note: la fonction write_i2c_block_data transmet une commande
      #       et des données en bloc. Les données doivent être dans
      #       une liste même si elle n'a qu'une seule données d'où
      #       [ts] avec des crochets.
      self.bus.write_i2c_block_data(self.address, cst.I2C_CMD_SET_TS, [ts])
    else:
      raise CoordException(F"<send_Ts> Bus non initié ou adresse I2C invalide.")
  
  def send_Nb_Vrms(self, nb_Vrms =-1):

    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Note: la fonction write_i2c_block_data transmet une commande
      #       et des données en bloc. Les données doivent être dans
      #       une liste même si elle n'a qu'une seule données d'où
      #       [ts] avec des crochets.
      self.bus.write_i2c_block_data(self.address, cst.I2C_CMD_SET_NB_VRMS, [nb_Vrms])
    else:
      raise CoordException(F"<send_Nb_Vrms> Bus non initié ou adresse I2C invalide.")
  
  def send_Nb_Li(self, nb_Li =-1):

    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Note: la fonction write_i2c_block_data transmet une commande
      #       et des données en bloc. Les données doivent être dans
      #       une liste même si elle n'a qu'une seule données d'où
      #       [ts] avec des crochets.
      self.bus.write_i2c_block_data(self.address, cst.I2C_CMD_SET_NB_LI, [nb_Li])
    else:
      raise CoordException(F"<send_Nb_Li> Bus non initié ou adresse I2C invalide.")

  def send_Restart(self):

    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Note: la fonction write_i2c_block_data transmet une commande
      #       et des données en bloc. Les données doivent être dans
      #       une liste même si elle n'a qu'une seule données d'où
      #       [ts] avec des crochets.
      self.bus.write_byte(self.address, cst.I2C_CMD_SET_RESTART)
    else:
      raise CoordException(F"<send_Restart> Bus non initié ou adresse I2C invalide.")

  def send_Pause(self):
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Note: la fonction write_i2c_block_data transmet une commande
      #       et des données en bloc. Les données doivent être dans
      #       une liste même si elle n'a qu'une seule données d'où
      #       [ts] avec des crochets.

      self.bus.write_byte(self.address, cst.I2C_CMD_SET_PAUSE)
    
    else:
      raise CoordException(F"<send_Pause> Bus non initié ou adresse I2C invalide.")


  def read_Value(self, startByte = 0):
    '''Lire la température du noeud à l'adresse adr.

    Arguments:
    bus -- objet SMBUS déjà initialisé
    adr (int) -- adresse du noeud destinataire

    Retour (float): Valeur de la température
    Exceptions possibles: CoordException, IOError, struct.error
    '''
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # On fait la lecture de la température octet par octet.
      # MSB -> adresse haute, LSB -> adresse basse
      # (c'est l'ordre little Endian)
      T = bytearray([0x00, 0x00, 0x00, 0x00])
      #if startByte == 3:
      self.bus.write_byte(self.address, startByte + 3)
      T[3] = self.bus.read_byte(self.address)
      self.bus.write_byte(self.address, startByte + 2)
      T[2] = self.bus.read_byte(self.address)
      self.bus.write_byte(self.address, startByte + 1 )
      T[1] = self.bus.read_byte(self.address)
      self.bus.write_byte(self.address, startByte)
      T[0] = self.bus.read_byte(self.address)

      # Convertir les 4 octets représentant la température de format binary32 
      # en nombre virgule flottante
      value = struct.unpack('f', T)
      # Note: la conversion par struct produit des listes d'objets dans nb_echan 
      #       et temperature. C'est pourquoi on prend uniquement le premier élément
      #       avec la syntaxe [0].
      return value[0]
    else:
      raise CoordException(F"<read_Temp> Bus non initié ou adresse I2C invalide.")

  def read_SNumber(self):
    '''Lire le numéro de l'échantillon de la température du noeud à l'adresse adr.

    Arguments:
    bus -- objet SMBUS déjà initialisé
    adr (int) -- adresse du noeud destinataire

    Retour (int): Numéro de l'échantillon
    Exceptions possibles: CoordException, IOError, struct.error
    '''
    if self.bus != None and (self.address >= cst.I2C_MIN_ADR and self.address <= cst.I2C_MAX_ADR):
      # Lire le numéro d'échantillon acquis par le noeud depuis son démarrage.
      # On fait cette lecture octet par octet (ordre little Endian)
      N = bytearray([0x00, 0x00])
      self.bus.write_byte(self.address, cst.I2C_NODE_NS_MSB)
      N[1] = self.bus.read_byte(self.address)
      self.bus.write_byte(self.address, cst.I2C_NODE_NS_LSB)
      N[0] = self.bus.read_byte(self.address)
      # Convertir les 2 octets du numéro d'échantillon en valeur entière
      nb_echan = struct.unpack('H', N)
      # Note: la conversion par struct produit des listes d'objets dans nb_echan 
      #       et temperature. C'est pourquoi on prend uniquement le premier élément
      #       avec la syntaxe [0].
      return nb_echan[0]
    else:
      raise CoordException(F"<read_SNumber> Bus non initié ou adresse I2C invalide.")
  
  
