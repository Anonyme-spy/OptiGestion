# OptiGestion

**OptiGestion** est une application de gestion et d'optimisation financière permettant de calculer des coûts de revient, analyser des marges, simuler des scénarios et visualiser des résultats.

---

## 📁 Structure du projet

```
OptiGestion/
│
├── pyproject.toml              # Configuration uv (dépendances, métadonnées)
├── README.md                   # Documentation générale du projet
├── .gitignore                  # Fichiers ignorés par Git
├── uv.lock                     # Fichier de verrouillage des dépendances
│
├── src/                # Package Python principal
│   ├── __init__.py             # Rend le dossier importable comme package
│   ├── main.py                 # Point d'entrée principal de l'application
│   │
│   ├── data/                   # Données d'exemple (CSV / JSON)
│   │   ├── produits.csv        # Liste des produits
│   │   ├── couts.csv           # Données de coûts
│   │   ├── volumes.csv         # Volumes de production/ventes
│   │   └── scenarios.json      # Scénarios de simulation
│   │
│   ├── modules/                # Modules fonctionnels
│   │   ├── input_module.py     # Gestion des entrées et import/export (CSV, JSON)
│   │   ├── costing_module.py   # Calcul du coût de revient et marges brutes
│   │   ├── analysis_module.py  # Seuil de rentabilité, marges, simulations
│   │   ├── visualization_module.py  # Génération de graphiques
│   │   └── storage_module.py   # Lecture/écriture des données persistantes
│   │
│   └── utils/                  # Fonctions utilitaires
│       └── helpers.py          # Helpers partagés entre les modules
│
├── tests/                      # Tests unitaires et d'intégration
│   ├── conftest.py             # Configuration et fixtures pytest
│   ├── test_costing.py         # Tests du module de costing
│   ├── test_analysis.py        # Tests du module d'analyse
│   └── test_storage.py         # Tests du module de stockage
│
└── docs/                       # Documentation technique
    ├── specification.md        # Spécifications fonctionnelles
    ├── modele_donnees.md       # Modèle de données
    └── manuel_utilisateur.md   # Manuel utilisateur
```

---

## ⚙️ Prérequis

- Python **≥ 3.13**
- [uv](https://github.com/astral-sh/uv) (gestionnaire de paquets)

---

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/OptiGestion.git
cd OptiGestion

# Installer les dépendances avec uv
uv sync
```

---

## ▶️ Lancement

```bash
uv run python -m optigestion.main
```

---

## 🧪 Tests

```bash
uv run pytest tests/
```

---

## 🔍 Linting

```bash
uv run ruff check
```

---

## 📦 Dépendances principales

| Paquet    | Version   | Rôle                              |
|-----------|-----------|-----------------------------------|
| `pandas`  | ≥ 3.0.0   | Manipulation et analyse de données |
| `pyqt6`   | ≥ 6.10.2  | Interface graphique (GUI)          |
| `ruff`    | ≥ 0.15.1  | Linter et formateur de code        |

---

## 📌 Modules

### `input_module`
Gère l'importation et l'exportation de données aux formats **CSV** et **JSON**.

### `costing_module`
Calcule le **coût de revient** et la **marge brute** par produit.

### `analysis_module`
Analyse le **seuil de rentabilité**, simule des scénarios et effectue des analyses de sensibilité.

### `visualization_module`
Génère des **graphiques** (séparés et combinés) à partir des données analysées.

### `storage_module`
Assure la **persistance des données** : lecture et écriture sur le système de fichiers.

---

## 📄 Licence

Ce projet est sous licence MIT.

