/*
 * Calculateur_Li
 * 
 * Une classe pour réaliser le calcul de la valeur Li en
 * utilisant la sensibilité et le gain du capteur Electret
 * MAX4466.
 * 
 * Voir les notes de cours "Conception des objets (IIB)" pour les
 * calculs à effectuer.
 * 
 * Note: Cette classe contient un objet de classe
 *       Calculateur_VRMS pour calculer la valeur dBV du signal
 *       échantillonné.
 * 
 * Convention:
 *  Variables -> camelCase
 *  Classes, fonctions -> PascalCase
 *  Constantes, types utilisateurs -> SNAKE_CASE
 * 
 * GPA788 - ETS
 * T. Wong
 * 09-2018
 * 08-2020
 */
#ifndef CALCULATEUR_LEQ_H
#define CALCULATEUR_LEQ_H

// Pour pouvoir utiliser un objet de type Calculateur_VRMS
#include "calculateur_li.h"

class Calculateur_Leq {
public:
  // Pour le microphone Electret une application de 94 dB SPL
  // produit -44 dBV/Pa à sa sortie. Le gain du MAX4466 est par
  // défaut réglé à 125 ou 42 dBV.
  Calculateur_Leq(double Ts, uint16_t VrmSamples, uint16_t LiSamples){
    mTs = Ts;
    mVrmSamples = VrmSamples;
    mLiSamples = LiSamples;
  }
    // Empêcher l'utilisation du constructeur de copie
  Calculateur_Leq(const Calculateur_Leq& other) = delete;
  // Empêcher l'utilisation de l'opérateur d'assignation
  Calculateur_Leq& operator=(const Calculateur_Leq& other) = delete;
  // Empêcher l'utilisation du constructeur par déplacement
  Calculateur_Leq(Calculateur_Leq&& other) = delete;
  // Empêcher l'utilisation de l'opérateur de déplacement
  Calculateur_Leq& operator=(Calculateur_Leq&& other) = delete;

  ~Calculateur_Leq() = default;  // Destructeur

  /* -------------------------------------------------------------
     Accesseurs des données membres de la classe
     -------------------------------------------------------------- */  
  inline double GetLeq() const { return m_Leq; }
  
  inline uint16_t GetNbSamples() const { return d.GetNbSamples(); }
  inline uint16_t GetTotalSamples() const { return d.GetTotalSamples(); }
  inline double GetVrms() const { return d.GetVrms(); }
  inline double GetdBV() const { return d.GetdBV(); }
  inline uint8_t GetAPin() const { return d.GetAPin(); }
  inline double GetVMax() const { return d.GetVMax(); }
  inline int16_t GetAdcMax() const { return d.GetAdcMax(); }
  inline double GetLi() const { return d.GetLi(); }
  inline double GetP() const { return d.GetP(); }
  inline double GetM() const { return d.GetM(); }
  inline double GetG() const { return d.GetG(); }
  inline uint32_t GetTs() const { return mTs; }
  inline uint16_t GetVrmSamples() const { return mVrmSamples; }
  inline uint16_t GetLiSamples() const { return mLiSamples; }
  inline uint32_t GetNbLi() const { return d.GetNbLi();}
  inline void SetNbLiSamples(uint32_t nbLiSamples) {mLiSamples = nbLiSamples; }
  inline void SetNbVrmsSamples(uint32_t nbVrmSample) {mVrmSamples = nbVrmSample; }
  inline void ResetNbLi(){d.ResetNbLi();}

  


  /* -------------------------------------------------------------
     Services publics offerts
     -------------------------------------------------------------- */
  // Utiliser Accumulate() de l'objet de classe Calculateur_VRMS
  // pour accumuler les valeurs du capteur sonore.
  // Note: La temporisation est la responsabilité de l'utilisateur.
  void Accumulate() {

    waitUntil(GetTs());
    
    d.Accumulate();
    

  }
  // Utiliser Compute() de l'objet de classe Calculateur_VRMS
  // pour calculer la valeur rms du signal sonore et ensuite
  // calculer Li du signal.
  // Note: La temporisation est la responsabilité de l'utilisateur.
  double Compute() {

    
    if(GetNbSamples() == mVrmSamples){

      d.Compute();
      mSumLeq += mTs * mVrmSamples * pow(10, 0.1 * GetLi());
    }
    

    if(GetNbLi() == mLiSamples && GetTotalSamples() != 0){
      m_Leq = 10*log10((1/(mTs * mVrmSamples * mLiSamples)*mSumLeq));
      mSumLeq = 0;
      ResetNbLi();

      return 1;
    }
    else{

      return 0;
    }
    return 0;
  }

  void waitUntil(uint32_t w) {
  uint32_t t{millis()};
  // Attendre w millisecondes
  while (millis() < t + w) {}
}
  
private:
  // Objet de classe Calculateur_VRMS pour réaliser les calculs
  // Vrms et dBV du signal échantillonné.
  // La relation entre la classe Calculateur_VRMS et la classe 
  // Calculateur_Li est une relation de "composition".
  Calculateur_Li d;
  // Pour le calcul de Li
  double m_Leq;                     // Niveau d'énergie sonore au temps ti
  double mSumLeq;                         
  double ti;
  double mTs;
  uint16_t compteur;
  uint16_t mVrmSamples;
  uint16_t mLiSamples;
};

#endif
