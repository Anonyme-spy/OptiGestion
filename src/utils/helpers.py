print("taper list() pour connaître les fonctions dans helpers")

class helpers:

    def list():
       explications ="" \
       " role_module()\n " \
       "technologie()\n " \
       ""
       return explications
    
    def role_module(module:str):
        if module =="":
           return "paramétrer de la fonction role_module \n" \
           "-costing_module \n" \
           "-input_module \n" \
           "-analysis_module \n" \
           "-visualization_module \n" \
           "-storage_module \n"

        if module =="costing_module":
           return "Sert à calculer le coût de revient et les marges brutes"
        
        if module =="input_module":
           return "Sert à gérer les entrées et import/export CSV et JSON en utilisant Pandas"
        
        if module =="analysis_module":
           return "Sert à calculer le seuil de rentabilité, les marges et à faire des simulations"
        
        if module =="visualization_module":
           return "Sert à la génération de l'interface graphique en utilisant PyQt6"
        
        if module =="storage_module":
           return "Sert à la lecture/écriture persistante en utilisant SQLite"
        
    def technologie(tech:str):
        if tech =="":
           return "paramétrer de la fonction technologie \n" \
           "-PyQt6\n" \
           "-Pandas\n" \
           "-SQLite\n" \
           "-Matplotlib\n" \
           "-UV\n" \
           "-ReportLab\n"

        if tech =="PyQt6":
           return "Framework Python pour créer des interfaces graphiques professionnelles (fenêtres, boutons, tableaux)"
        
        if tech =="Pandas":
           return "Bibliothèque d'analyse et de manipulation de données (DataFrames, import/export CSV/JSON/Excel)"
        
        if tech =="SQLite":
           return "Base de données légère et sans serveur, stocke les données dans un simple fichier .db"
        
        if tech =="Matplotlib":
           return "Bibliothèque pour créer des graphiques et visualisations (courbes, barres, camemberts)"
        
        if tech =="UV":
           return "Gestionnaire de paquets Python ultra-rapide (alternative à pip) écrit en Rust"
        
        if tech =="ReportLab":
           return "Bibliothèque pour générer des documents PDF dynamiques avec texte, images et tableaux"