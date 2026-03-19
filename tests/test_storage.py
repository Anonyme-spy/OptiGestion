# tests/test_storage.py
# Tests unitaires pour StorageModule — OptiGestion v1.0
# Structure : src/db/storage_module.py
# Lancer avec : uv run pytest tests/test_storage.py -v

import pytest
import os
import csv
from src.modules.costing_module import CostingModule
from src.db.storage_module import StorageModule

# ── FIXTURES ─────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    """Crée une base SQLite temporaire propre pour chaque test."""
    return StorageModule(db_path=str(tmp_path / "test_optigestion.db"))

@pytest.fixture
def costing_base():
    """CostingModule standard : CF=1000, CV=12, PV=25, Q=150."""
    return CostingModule(cf=1000, cv=12, pv=25, q=150)

@pytest.fixture
def costing_optimise():
    """CostingModule optimisé : CF=1000, CV=10, PV=28, Q=200."""
    return CostingModule(cf=1000, cv=10, pv=28, q=200)

@pytest.fixture
def costing_perte():
    """CostingModule en perte : Q trop faible pour couvrir CF."""
    return CostingModule(cf=5000, cv=12, pv=25, q=50)

# ── INIT db ───────────────────────────────────────────────────────────────────

class TestInitDB:
    def test_db_file_cree(self, tmp_path):
        """La base SQLite doit être créée sur le disque."""
        path = str(tmp_path / "optigestion.db")
        StorageModule(db_path=path)
        assert os.path.exists(path)

    def test_table_scenarios_existe(self, db):
        """La table scenarios doit exister après init."""
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'"
            ).fetchone()
        assert table is not None

# ── SAUVEGARDE ────────────────────────────────────────────────────────────────

class TestSauvegarder:
    def test_retourne_id_entier(self, db, costing_base):
        """sauvegarder() doit retourner un entier positif."""
        id_ = db.sauvegarder("Test", costing_base)
        assert isinstance(id_, int) and id_ > 0

    def test_ids_incrementes(self, db, costing_base, costing_optimise):
        """Deux sauvegardes successives doivent avoir des ids distincts."""
        id1 = db.sauvegarder("S1", costing_base)
        id2 = db.sauvegarder("S2", costing_optimise)
        assert id2 > id1

    def test_donnees_costing_stockees(self, db, costing_base):
        """Les données du CostingModule doivent être correctement stockées."""
        id_ = db.sauvegarder("Vérif costing", costing_base)
        row = db.charger(id_)
        assert row["cf"] == costing_base.cf
        assert row["cv"] == costing_base.cv
        assert row["pv"] == costing_base.pv
        assert row["q"]  == costing_base.q

    def test_calculs_costing_stockes(self, db, costing_base):
        """Les résultats calculés par CostingModule doivent être stockés."""
        id_ = db.sauvegarder("Calculs", costing_base)
        row = db.charger(id_)
        assert row["cout_total"]              == pytest.approx(costing_base.cout_total())
        assert row["chiffre_affaire"]         == pytest.approx(costing_base.chiffre_affaire())
        assert row["benefice"]                == pytest.approx(costing_base.benefice())
        assert row["marge_sur_cout_variable"] == pytest.approx(costing_base.marge_sur_cout_variable())
        assert row["taux_de_marge"]           == pytest.approx(costing_base.taux_de_marge())
        assert row["cout_de_revient"]         == pytest.approx(costing_base.cout_de_revient_unitaire())

    def test_calculs_analyse_stockes(self, db, costing_base):
        """Les résultats de l'AnalysisModule doivent être stockés."""
        from src.modules.analysis_module import AnalysisModule
        analyse = AnalysisModule(costing_base)
        id_ = db.sauvegarder("Analyse", costing_base)
        row = db.charger(id_)
        assert row["seuil_rentabilite"] == pytest.approx(analyse.seuil_rentabilite())
        assert row["point_mort_ca"]     == pytest.approx(analyse.point_mort_ca())
        assert row["est_rentable"]      == analyse.est_rentable()
        assert row["marge_securite"]    == pytest.approx(analyse.marge_securite())
        assert row["conseil"]           == analyse.conseil_automatique()

    def test_sauvegarde_avec_notes(self, db, costing_base):
        """Les notes doivent être correctement sauvegardées."""
        note = "Scénario pour le mois de mars"
        id_ = db.sauvegarder("Avec notes", costing_base, notes=note)
        assert db.charger(id_)["notes"] == note

    def test_notes_vides_par_defaut(self, db, costing_base):
        """Sans notes, le champ doit être une chaîne vide."""
        id_ = db.sauvegarder("Sans notes", costing_base)
        assert db.charger(id_)["notes"] == ""

    def test_scenario_perte(self, db, costing_perte):
        """Un scénario en perte doit être sauvegardé correctement."""
        id_ = db.sauvegarder("Perte", costing_perte)
        row = db.charger(id_)
        assert row["benefice"] < 0
        assert row["est_rentable"] == False
        assert "perte" in row["conseil"].lower()

# ── CHARGEMENT ────────────────────────────────────────────────────────────────

class TestCharger:
    def test_retourne_dict(self, db, costing_base):
        """charger() doit retourner un dict non vide pour un id valide."""
        id_ = db.sauvegarder("À charger", costing_base)
        row = db.charger(id_)
        assert isinstance(row, dict)
        assert row["nom"] == "À charger"

    def test_reconstruit_costing_module(self, db, costing_base):
        """charger() doit reconstruire un CostingModule fonctionnel."""
        id_ = db.sauvegarder("Reconstruction", costing_base)
        cm = db.charger(id_)["costing_module"]
        assert isinstance(cm, CostingModule)
        assert cm.cout_total() == pytest.approx(costing_base.cout_total())

    def test_id_inexistant_leve_erreur(self, db):
        """charger() doit lever ValueError pour un id inconnu."""
        with pytest.raises(ValueError, match="introuvable"):
            db.charger(9999)

    def test_est_rentable_est_booleen(self, db, costing_base):
        """est_rentable doit être un bool Python, pas un entier SQLite."""
        id_ = db.sauvegarder("Bool test", costing_base)
        assert isinstance(db.charger(id_)["est_rentable"], bool)

# ── LISTE ─────────────────────────────────────────────────────────────────────

class TestLister:
    def test_liste_vide_au_depart(self, db):
        """lister() doit retourner une liste vide si aucun scénario."""
        assert db.lister() == []

    def test_count_correct(self, db, costing_base, costing_optimise):
        """lister() doit retourner autant d'entrées que de sauvegardes."""
        db.sauvegarder("S1", costing_base)
        db.sauvegarder("S2", costing_optimise)
        assert len(db.lister()) == 2

    def test_ordre_anti_chronologique(self, db, costing_base):
        """Le scénario le plus récent doit apparaître en premier."""
        db.sauvegarder("Premier", costing_base)
        db.sauvegarder("Deuxième", costing_base)
        liste = db.lister()
        assert liste[0]["nom"] == "Deuxième"
        assert liste[1]["nom"] == "Premier"

    def test_champs_essentiels_presents(self, db, costing_base):
        """Chaque entrée doit contenir les champs clés."""
        db.sauvegarder("Champs", costing_base)
        row = db.lister()[0]
        for champ in ["id", "nom", "cf", "cv", "pv", "q", "benefice", "conseil", "created_at"]:
            assert champ in row, f"Champ manquant : {champ}"

# ── SUPPRESSION ───────────────────────────────────────────────────────────────

class TestSupprimer:
    def test_retourne_true_si_existant(self, db, costing_base):
        """supprimer() doit retourner True pour un id valide."""
        id_ = db.sauvegarder("À supprimer", costing_base)
        assert db.supprimer(id_) == True

    def test_absent_apres_suppression(self, db, costing_base):
        """Après suppression, le scénario ne doit plus apparaître."""
        id_ = db.sauvegarder("À supprimer", costing_base)
        db.supprimer(id_)
        assert id_ not in [r["id"] for r in db.lister()]

    def test_retourne_false_si_inexistant(self, db):
        """supprimer() doit retourner False pour un id inconnu."""
        assert db.supprimer(9999) == False

    def test_ne_touche_pas_les_autres(self, db, costing_base, costing_optimise):
        """La suppression d'un scénario ne doit pas affecter les autres."""
        id1 = db.sauvegarder("S1", costing_base)
        id2 = db.sauvegarder("S2", costing_optimise)
        db.supprimer(id1)
        ids = [r["id"] for r in db.lister()]
        assert id2 in ids
        assert id1 not in ids

# ── MISE À JOUR NOTES ─────────────────────────────────────────────────────────

class TestMajNotes:
    def test_mise_a_jour_reussie(self, db, costing_base):
        """maj_notes() doit mettre à jour les notes et retourner True."""
        id_ = db.sauvegarder("Notes test", costing_base)
        assert db.maj_notes(id_, "Note mise à jour") == True
        assert db.charger(id_)["notes"] == "Note mise à jour"

    def test_id_inexistant_retourne_false(self, db):
        """maj_notes() doit retourner False pour un id inconnu."""
        assert db.maj_notes(9999, "Test") == False

# ── COMPARAISON ───────────────────────────────────────────────────────────────

class TestComparer:
    def test_structure_retournee(self, db, costing_base, costing_optimise):
        """comparer() doit retourner scenario_1, scenario_2 et ecarts."""
        id1 = db.sauvegarder("S1", costing_base)
        id2 = db.sauvegarder("S2", costing_optimise)
        comp = db.comparer(id1, id2)
        assert "scenario_1" in comp
        assert "scenario_2" in comp
        assert "ecarts"     in comp

    def test_ecart_benefice_correct(self, db, costing_base, costing_optimise):
        """L'écart de bénéfice doit correspondre à la différence réelle."""
        id1 = db.sauvegarder("S1", costing_base)
        id2 = db.sauvegarder("S2", costing_optimise)
        ecart = db.comparer(id1, id2)["ecarts"]["benefice"]
        assert ecart == pytest.approx(costing_optimise.benefice() - costing_base.benefice())

    def test_tous_les_ecarts_presents(self, db, costing_base, costing_optimise):
        """Les écarts doivent couvrir tous les indicateurs clés."""
        id1 = db.sauvegarder("S1", costing_base)
        id2 = db.sauvegarder("S2", costing_optimise)
        ecarts = db.comparer(id1, id2)["ecarts"]
        for champ in ["benefice", "seuil_rentabilite", "cout_total", "chiffre_affaire", "taux_de_marge"]:
            assert champ in ecarts, f"Écart manquant : {champ}"

    def test_id_inexistant_leve_erreur(self, db, costing_base):
        """comparer() doit lever ValueError si un des ids est inconnu."""
        id1 = db.sauvegarder("S1", costing_base)
        with pytest.raises(ValueError):
            db.comparer(id1, 9999)

# ── EXPORT CSV ────────────────────────────────────────────────────────────────

class TestExporterCSV:
    def test_fichier_cree(self, db, costing_base, tmp_path):
        """exporter_csv() doit créer le fichier."""
        db.sauvegarder("S1", costing_base)
        chemin = str(tmp_path / "export.csv")
        db.exporter_csv(chemin)
        assert os.path.exists(chemin)

    def test_contient_toutes_les_lignes(self, db, costing_base, costing_optimise, tmp_path):
        """Le CSV doit contenir une ligne par scénario."""
        db.sauvegarder("S1", costing_base)
        db.sauvegarder("S2", costing_optimise)
        chemin = str(tmp_path / "export.csv")
        db.exporter_csv(chemin)
        with open(chemin, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2

    def test_colonnes_essentielles(self, db, costing_base, tmp_path):
        """Le CSV doit contenir les colonnes clés."""
        db.sauvegarder("S1", costing_base)
        chemin = str(tmp_path / "export.csv")
        db.exporter_csv(chemin)
        with open(chemin, encoding="utf-8") as f:
            header = f.readline()
        for col in ["nom", "cf", "cv", "pv", "q", "benefice", "conseil"]:
            assert col in header, f"Colonne manquante : {col}"

    def test_liste_vide_leve_erreur(self, db, tmp_path):
        """exporter_csv() doit lever ValueError si aucun scénario."""
        with pytest.raises(ValueError, match="Aucun scénario"):
            db.exporter_csv(str(tmp_path / "vide.csv"))