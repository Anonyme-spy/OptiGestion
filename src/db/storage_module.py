# src/db/storage_module.py
# Gestion de la persistance SQLite pour OptiGestion v1.0
# Sauvegarde et chargement des scénarios issus de CostingModule + AnalysisModule

import sqlite3
import os
from src.modules.costing_module import CostingModule
from src.modules.analysis_module import AnalysisModule

DB_PATH = os.path.join(os.path.dirname(__file__), "optigestion.db")


class StorageModule:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ── CONNEXION ────────────────────────────────────────────────────────────
    def _connect(self):
        """Retourne une connexion SQLite avec Row factory pour accès par nom de colonne."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── INITIALISATION ───────────────────────────────────────────────────────
    def _init_db(self):
        """Crée la table scenarios si elle n'existe pas encore."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom         TEXT    NOT NULL,
                    -- Données saisies (CostingModule)
                    cf          REAL    NOT NULL,
                    cv          REAL    NOT NULL,
                    pv          REAL    NOT NULL,
                    q           REAL    NOT NULL,
                    -- Résultats calculés (CostingModule)
                    cout_total              REAL,
                    chiffre_affaire         REAL,
                    benefice                REAL,
                    marge_sur_cout_variable REAL,
                    taux_de_marge           REAL,
                    cout_de_revient         REAL,
                    -- Résultats analyse (AnalysisModule)
                    seuil_rentabilite       REAL,
                    point_mort_ca           REAL,
                    est_rentable            INTEGER,
                    marge_securite          REAL,
                    conseil                 TEXT,
                    -- Métadonnées
                    notes       TEXT    DEFAULT '',
                    created_at  TEXT    DEFAULT (datetime('now', 'localtime'))
                )
            """)
            conn.commit()

    # ── SAUVEGARDE ───────────────────────────────────────────────────────────
    def sauvegarder(self, nom: str, costing: CostingModule, notes: str = "") -> int:
        """
        Sauvegarde un scénario complet (CostingModule + AnalysisModule calculés).
        Retourne l'id du scénario créé.
        """
        analyse = AnalysisModule(costing)
        c = costing.to_dict()
        a = analyse.to_dict()

        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO scenarios (
                    nom, cf, cv, pv, q,
                    cout_total, chiffre_affaire, benefice,
                    marge_sur_cout_variable, taux_de_marge, cout_de_revient,
                    seuil_rentabilite, point_mort_ca, est_rentable,
                    marge_securite, conseil, notes
                ) VALUES (
                    :nom, :cf, :cv, :pv, :q,
                    :cout_total, :chiffre_affaire, :benefice,
                    :marge_sur_cout_variable, :taux_de_marge, :cout_de_revient,
                    :seuil_rentabilite, :point_mort_ca, :est_rentable,
                    :marge_securite, :conseil, :notes
                )
            """, {
                "nom":                     nom,
                "cf":                      c["cout fixe"],
                "cv":                      c["cout variable"],
                "pv":                      c["prix de vente"],
                "q":                       c["quantite"],
                "cout_total":              c["cout total"],
                "chiffre_affaire":         c["chiffre affaire"],
                "benefice":                c["benefice"],
                "marge_sur_cout_variable": c["marge sur cout variable"],
                "taux_de_marge":           c["taux de marge"],
                "cout_de_revient":         c["cout de revient"],
                "seuil_rentabilite":       a["seuil rentabilite"],
                "point_mort_ca":           a["point mort de chiffre d'affaire"],
                "est_rentable":            int(a["est rentable"]),
                "marge_securite":          a["marge de securite"],
                "conseil":                 a["conseil"],
                "notes":                   notes,
            })
            conn.commit()
            return cursor.lastrowid

    # ── CHARGEMENT ───────────────────────────────────────────────────────────
    def charger(self, scenario_id: int) -> dict:
        """
        Charge un scénario par son id.
        Retourne un dict avec les données + un CostingModule reconstruit.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM scenarios WHERE id = ?", (scenario_id,)
            ).fetchone()

        if row is None:
            raise ValueError(f"Scénario id={scenario_id} introuvable.")

        data = dict(row)
        data["est_rentable"] = bool(data["est_rentable"])
        data["costing_module"] = CostingModule(
            data["cf"], data["cv"], data["pv"], data["q"]
        )
        return data

    # ── LISTE ────────────────────────────────────────────────────────────────
    def lister(self) -> list[dict]:
        """Retourne la liste de tous les scénarios (sans recalcul)."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, nom, cf, cv, pv, q, benefice, conseil, created_at "
                "FROM scenarios ORDER BY created_at DESC, id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    # ── SUPPRESSION ──────────────────────────────────────────────────────────
    def supprimer(self, scenario_id: int) -> bool:
        """Supprime un scénario par son id. Retourne True si supprimé."""
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM scenarios WHERE id = ?", (scenario_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ── MISE À JOUR DES NOTES ────────────────────────────────────────────────
    def maj_notes(self, scenario_id: int, notes: str) -> bool:
        """Met à jour les notes d'un scénario existant."""
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE scenarios SET notes = ? WHERE id = ?",
                (notes, scenario_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ── COMPARAISON ──────────────────────────────────────────────────────────
    def comparer(self, id1: int, id2: int) -> dict:
        """
        Compare deux scénarios côte à côte.
        Retourne un dict avec les deux scénarios et les écarts clés.
        """
        s1 = self.charger(id1)
        s2 = self.charger(id2)
        return {
            "scenario_1": s1,
            "scenario_2": s2,
            "ecarts": {
                "benefice":          s2["benefice"]          - s1["benefice"],
                "seuil_rentabilite": s2["seuil_rentabilite"] - s1["seuil_rentabilite"],
                "cout_total":        s2["cout_total"]        - s1["cout_total"],
                "chiffre_affaire":   s2["chiffre_affaire"]   - s1["chiffre_affaire"],
                "taux_de_marge":     s2["taux_de_marge"]     - s1["taux_de_marge"],
            }
        }

    # ── EXPORT CSV ───────────────────────────────────────────────────────────
    def exporter_csv(self, chemin: str) -> None:
        """Exporte tous les scénarios dans un fichier CSV."""
        import csv
        scenarios = self.lister()
        if not scenarios:
            raise ValueError("Aucun scénario à exporter.")

        with open(chemin, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=scenarios[0].keys())
            writer.writeheader()
            writer.writerows(scenarios)