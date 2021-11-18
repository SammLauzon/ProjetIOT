#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Ce programme lit trois (3) données du champ 2 d'un canal sur ThingSpeak.

Requête REST à réaliser:
GET GET https://api.thingspeak.com/channels/numero_canal/fields/2.json?api_key=cle_lecture&results=3

Note: on veut la réponse sous forme de la représentation JSON

Le programme utilise le module "requests" pour réaliser la communication HTTP.
C'est la façon moderne et simple d'accéder au services WEB sous Python. Ainsi,
l'accès à une plateforme IoT via leur API REST est devenu très simple.

(voir les notes de cours "Style REST (I)")

Convention PEP 8 (Python Enhencement Proposal 8):
  Variables -> snake_case
  Class -> PascalCase
  Constante -> SNAKE_CASE

GPA788 Conception et intégration des objets connectés
T. Wong
Juin 2018
Juillet 2020
Novembre 2021
'''
# -------------------------------------------------------------------
# Les modules utiles
# -------------------------------------------------------------------
import requests, sys
import numpy as np
import pandas as pd

# -------------------------------------------------------------------
# ThingSpeak
# -------------------------------------------------------------------
# Méthode: GET
# -------------------------------------------------------------------
# URL pour lire des donnée:
# https://api.thingspeak.com/channels/numero_canal/fields/numero_champ.<format>
#--------------------------------------------------------------------
# Référence API REST de ThingSpeak:
# https://www.mathworks.com/help/thingspeak/rest-api.html
# -------------------------------------------------------------------
THINGSPK_CHANNEL_ID = '1569816'
THINGSPK_FIELD_NO = '1'
THINGSPK_URL = ('https://api.thingspeak.com/channels/' + THINGSPK_CHANNEL_ID
                + '/fields/' + THINGSPK_FIELD_NO + 'json')
THINGSPK_READ_API_KEY = 'MVPPF123IDHFK1BQ'
NB_POINTS = 3123
NB_CHANNELS = 3
data = np.empty((NB_POINTS,NB_CHANNELS))
# -------------------------------------------------------------------
# Fonction principale
# -------------------------------------------------------------------
def main():
  # Note: f-string disponible depuis Python 3.6
  for c in range(1,NB_CHANNELS+1):
    THINGSPK_FIELD_NO = str(c)
    THINGSPK_URL = ('https://api.thingspeak.com/channels/' + THINGSPK_CHANNEL_ID
                + '/fields/' + THINGSPK_FIELD_NO + 'json')
    print(F'Lire {NB_POINTS} données du champ {THINGSPK_FIELD_NO} les plus récentes du canal {THINGSPK_CHANNEL_ID}')
    try:
      resp = requests.get(THINGSPK_URL,
                          # 10 secondes pour connection et read timeout
                          timeout = (10, 10),
                          # Paramètres de cette requête
                          params = { "api_key" : THINGSPK_READ_API_KEY, "results"  : NB_POINTS}
                          )
      print('La requête est:', resp.url)
      print("ThingSpeak GET response: ", resp.status_code)
      if resp.status_code != 200:
          print("Erreur de communication détectée!")
          sys.exit(1)     # # Par exemple, notre convention est 1 = Erreur requête 
      # Décoder la réponse de JSON à Python
      # Voir le document "Représentation JSON" pour un survol
      print('Décodage de la réponse de JSON à Python...')
      try:
          # Voir le document "Représentation JSON" pour connaître
          # le format de la représentation JSON utilisé par ThingSpeak
          r = resp.json()
          idx = 0
          for d in r['feeds']:
              print(f"Point # {d['entry_id']},", end = ' ')
              print(f"valeur du champ {str(c)}: {d['field' + str(c)]}")
              data[idx, c-1] = d['field' + str(c)]
              idx += 1

      except ValueError:
          print('Exception ValueError reçue (décodage JSON)')
          sys.exit(2)     # Par exemple, notre convention est 2 = Erreur JSON 

    except requests.ConnectionError:
      print('Erreur de connexion')
      sys.exit(3)         # 3 = Erreur de connexion
    except requests.Timeout:
      print("Exception de timeout reçue (connexion ou écriture)")
      sys.exit(4)         # 4 = Erreur de timeout
    except requests.HTTPError:
      print('Erreur au niveau du protocole HTTP')
      sys.exit(5)         # 5 = Erreur HTTP
  # print(data)
  # index = np.where(data[:,0])
  df = pd.DataFrame(data=data, columns=["Température(°C)","Humidité relative (%)","Leq (dB)"])
  matrice_bool = (df > 0).all(1)
  df = df[matrice_bool==True]
  df.to_excel('test.xlsx')

# ------------------------------------------------------
# Programme principal
# ------------------------------------------------------
if __name__ == '__main__':
  main()

