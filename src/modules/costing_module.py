# NOTE:
# cf: cout fixe
# cv: cout variable
# pv: prix de vente 
# q: quantite

import warnings

class CostingModule:
    def __init__(self, cf, cv, pv, q):
        self.cf = cf
        self.cv = cv
        self.pv = pv
        self.q = q
        
        self.est_valide()
        
    def est_valide(self):
        if self.cf < 0:
            raise ValueError("Le cout fixe ne doit pas negatif!")
        elif self.pv <= 0:
           raise ValueError("Le prix de vente ne doit etre positif!")
        elif self.q == 0:
            raise ValueError("La quantite ne doit pas etre 0.")
        elif self.pv < self.cv:
            warnings.warn("Le prix de vente ne doit pas etre inferieur au cout vaiable")
        
    def cout_total(self):
        return self.cf + (self.cv * self.q)
        
    def chiffre_affaire(self):
        return self.pv * self.q
        
    def benefice(self):
        return self.chiffre_affaire() - self.cout_total()
        
    def marge_sur_cout_variable(self):
        return self.pv - self.cv
        
    def taux_de_marge(self):
        return (self.marge_sur_cout_variable() / self.pv) * 100
        
    def cout_de_revient_unitaire(self):
        return self.cout_total() / self.q
        
    def to_dict(self):
        resultats = {
            "cout fixe": self.cf,
            "cout variable": self.cv,
            "prix de vente": self.pv,
            "quantite": self.q,
            
            "cout total": self.cout_total(),
            "chiffre affaire": self.chiffre_affaire(),
            "benefice": self.benefice(),
            "marge sur cout variable": self.marge_sur_cout_variable(),
            "taux de marge": self.taux_de_marge(),
            "cout de revient": self.cout_de_revient_unitaire(),
        }
        
        return resultats