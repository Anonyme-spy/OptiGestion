# NOTE:
# ca: chiffre d'affaire
# nq: nouvell quantite
# cm: costing module
# sr: seuil de rentabilite

from costing_module import CostingModule

class AnalysisModule:
    def __init__(self, costing_module):
        self.costing_module = costing_module
        
    def seuil_rentabilite(self):
        if self.costing_module.pv <= self.costing_module.cv:
            raise ValueError("Marge non positive: pv <= cv, seuil de rentabilite indefini.")
        return self.costing_module.cf / (self.costing_module.pv - self.costing_module.cv)
        
    def point_mort_ca(self):
        return self.seuil_rentabilite() * self.costing_module.pv
        
    def est_rentable(self):
        return self.costing_module.q >= self.seuil_rentabilite()
            
    def marge_securite(self):
        return self.costing_module.q - self.seuil_rentabilite()
        
    def simulation(self, nouvelle_quantite):
        nq = CostingModule(self.costing_module.cf, self.costing_module.cv, self.costing_module.pv, nouvelle_quantite)
        return nq.to_dict()
        
    def analyse_sensibilite(self, parametre, variations):
        resultats = []
        for valeur in variations:
            if parametre == "cf":
                cm = CostingModule(valeur, self.costing_module.cv, self.costing_module.pv, self.costing_module.q)
            elif parametre == "cv":
                cm = CostingModule(self.costing_module.cf, valeur, self.costing_module.pv, self.costing_module.q)
            elif parametre == "pv":
                cm = CostingModule(self.costing_module.cf, self.costing_module.cv, valeur, self.costing_module.q)
            elif parametre == "q":
                cm = CostingModule(self.costing_module.cf, self.costing_module.cv, self.costing_module.pv, valeur)
            else:
                raise ValueError("Valeur invalide!")
            resultats.append(cm.to_dict())
        return resultats
        
    def conseil_automatique(self):
        benefice = self.costing_module.benefice()
        sr = self.seuil_rentabilite()
        perte = sr - self.costing_module.q
        
        if self.marge_securite() < 0:
            return (f"Non rentable: vous perdez {abs(benefice):.2f} ar \n"
                f"Il manque {perte:.0f} unite ou bien augmentez vos prix.")
        elif self.marge_securite() < self.seuil_rentabilite() * 0.2: # on a un marge de 20% min
            return ("Rentable: trop proche du seuil \n"
                f"({self.costing_module.q - sr:.0f} unite de marge).")
        else:
            return (f"Bonne marge: benefice de {benefice:.2f} ar \n"
                f"sur {self.costing_module.q} unites.")
            
    def to_dict(self):
        resultats = {
            "seuil rentabilite": self.seuil_rentabilite(),
            "point mort de chiffre d'affaire": self.point_mort_ca(),
            "est rentable": self.est_rentable(),
            "marge de securite": self.marge_securite(),
            "conseil": self.conseil_automatique()
        }
        return resultats