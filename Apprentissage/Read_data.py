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
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from math import sin, pi, exp

from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint
from conversion_signaux import signaux_apprentissage_supervise as ss
from tensorflow.python.keras.models import Model, Sequential
from tensorflow.python.keras.layers import LSTM
from tensorflow.python.keras.layers import Dense



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
def read_data():
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
  
  df = pd.DataFrame(data=data, columns=["Température(°C)","Humidité relative (%)","Leq (dB)"])
  matrice_bool = (df > 0).all(1)
  df = df[matrice_bool==True]

  return df[:800]

def learn(df):

  #Calcul statistique sur les valeurs
  vals = df.values
  std = np.std(vals, axis = 0)
  mean = np.mean(vals, axis = 0)

  distance_from_mean = np.abs(vals - mean)
  max_deviation = 2
  ep = 200

#Elimination des données abberantes
  not_outlier = distance_from_mean < max_deviation * std
  vals = vals[np.where(not_outlier.all(1) == True)]
  vals = vals.astype('float32')

#Parametre pour appliquer une fonction sin pour briser la corrélation des données.
  longueur = len(vals)
  periode = [450, 500, 550]
  amplitude = 0.5
  noise_factor = 0.1
  amortissement = 0
  
  signal = np.zeros((len(vals),len(periode)))

#Application du sinus sur les données
  for j in range (len(periode)):
    signal[:,j] = [amplitude - amplitude*sin(2*pi*i/periode[j])*exp(-amortissement*i) for i in range(longueur)]
  
  sin_vals = signal*vals

# Ajout de bruit pour enlever la corrélation restantes
  for i in range (len(vals[0])):
    rand = np.random.uniform(low = -noise_factor * np.max(sin_vals[:,i]), high = noise_factor * np.max(sin_vals[:,i]), size = len(sin_vals))
    sin_vals[:,i] += rand
  
  #Normalisation des données
  Scaler = MinMaxScaler(feature_range=(0,1))
  vals_normalisees = Scaler.fit_transform(sin_vals)

# Valeurs convertis sous forme décalée
  vals_convertis = ss(vals_normalisees,3,2)
  vals_convertis.drop(vals_convertis.columns[[9,10,12,13]], axis=1, inplace=True)
  nb_lignes, nb_cols = vals_convertis.shape

  train_val_split = 0.7

#Séparation des données en set d'apprentissage et de validation
  apprentissage = vals_convertis.values[:int(round(nb_lignes)*train_val_split),:]
  validation = vals_convertis.values[int(round(nb_lignes)*train_val_split):,:]
  apprentissage_X, apprentissage_Y = apprentissage[:,:-2], apprentissage[:,-2:]
  validation_X, validation_Y = validation[:,:-2], validation[:,-2:]

# Reshape les tenseurs de données pour avoir le format que Keras désire
  apprentissage_X = apprentissage_X.reshape((apprentissage_X.shape[0], 1, apprentissage_X.shape[1]))
  validation_X = validation_X.reshape((validation_X.shape[0], 1, validation_X.shape[1]))

  
#Construction du réseau
  reseau = Sequential()
  reseau.add(LSTM(20, input_shape=(apprentissage_X.shape[1], apprentissage_X.shape[2]),return_sequences=True)) # Première couche
  
  reseau.add(LSTM(20)) # deuxieme couche
  reseau.add(Dense(2))
  reseau.compile(loss='mae', optimizer='adam')
  
#Entrainement du réseau avec la fonction fit, earlyStopping et ModelCHeckpoint sont des fonctions pour optimiser le temps d'apprentissage.
  fonction_es = EarlyStopping(monitor='val_loss', min_delta = 0.001, mode = 'min', verbose = 1, patience = 50) 
  fonction_mc = ModelCheckpoint('reseau_lot200_2LSTM25.hdf5', monitor = 'val_loss', mode = 'min', 
                                verbose = 1, save_best_only = True) 
  history = reseau.fit(apprentissage_X, apprentissage_Y, epochs = ep, 
                       batch_size=32, validation_data=(validation_X,validation_Y), verbose = True, shuffle = True,
                       callbacks = [fonction_es, fonction_mc])

# Affichage graphique des courbes d'erreurs moyennes
  plt.plot(history.history['loss'])
  plt.plot(history.history['val_loss'])
  plt.xlabel('Epoch')
  plt.ylabel('loss')
  plt.legend(['train','validation'])
  plt.show()

def main():
  learn(read_data())
  

# ------------------------------------------------------
# Programme principal
# ------------------------------------------------------
if __name__ == '__main__':
  main()

