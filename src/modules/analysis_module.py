# NOTE:
# ca: chiffre d'affaire
# nq: nouvell quantite
# cm: costing module

from costing_module import CostingModule

class AnalysisModule:
    def __init__(self, costing_module):
        self.costing_module = costing_module
        
    def seuil_rentabilite(self):
        return self.costing_module.cf / (self.costing_module.pv - self.costing_module.cv)
        
    def point_mort_ca(self):
        return self.seuil_rentabilite() * self.costing_module.pv
        
    def est_rentable(self):
        if self.costing_module.q >= self.seuil_rentabilite():
            return True
        else:
            return False
            
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
        if self.marge_securite() < 0:
            return "Non rentable, c'est du perte"
        elif self.marge_securite() < self.seuil_rentabilite() * 0.2: # on a un marge de 20% min
            return "Vous ête rentable mais proche du seuil"
        else:
            return "Vous ête rentable avec bonne marge"
            
    def to_dict(self):
        resultats = {
            "seuil rentabilite": self.seuil_rentabilite(),
            "point mort de chiffre d'affaire": self.point_mort_ca(),
            "est rentable": self.est_rentable(),
            "marge de securite": self.marge_securite(),
            "conseil": self.conseil_automatique()
        }
        return resultats