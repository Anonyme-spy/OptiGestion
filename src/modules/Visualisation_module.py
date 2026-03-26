"""
Créé par : N°01 - RAKOTONANAHARY Anjarahoahy
Version : 3.1 - Intégration DataManager + auto-import initial
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from typing import Dict, Optional

# -------------------------------------------------------------------
# Import DataManager if available, otherwise fallback to file loading
# -------------------------------------------------------------------
try:
    from src.analytics.data_manager import DataManager
    USE_DATAMANAGER = True
except ImportError:
    USE_DATAMANAGER = False
    print("⚠️ DataManager non trouvé, utilisation du chargement direct des fichiers.")

# ============================================
# CONFIGURATION DU STYLE PROFESSIONNEL
# ============================================

COULEURS = {
    'primaire': '#2E86AB',
    'secondaire': '#A23B72',
    'accent': '#F18F01',
    'succes': '#73AB84',
    'danger': '#BF4E30',
    'gris_clair': '#F4F4F9',
    'gris_fonce': '#2D3142',
    'gris_moyen': '#4C5C68',
    'couts': '#E63946',
    'prix': '#2A9D8F',
    'marge': '#E9C46A'
}

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelweight': 'semibold',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
    'figure.titleweight': 'bold',
    'figure.facecolor': 'white',
    'axes.facecolor': COULEURS['gris_clair'],
    'axes.edgecolor': COULEURS['gris_moyen'],
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
})

# ============================================
# FONCTION DE CHARGEMENT DES DONNÉES (avec DataManager)
# ============================================

def charger_donnees() -> Dict[str, Optional[pd.DataFrame]]:
    """
    Charge les données en utilisant DataManager (si disponible) ou les fichiers CSV/JSON.
    Retourne un dictionnaire avec les DataFrames : 'produits', 'couts', 'volumes', 'scenarios'
    Les colonnes sont adaptées pour correspondre aux noms utilisés par les graphiques.
    """
    if USE_DATAMANAGER:
        print("📂 CHARGEMENT DES DONNÉES VIA DATAMANAGER...")
        dm = DataManager()
        try:
            # Vérifier si les tables sont vides et importer les données initiales si nécessaire
            conn = dm.storage._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()

            if count == 0:
                print("📦 Tables vides. Chargement initial depuis le dossier Data/ ...")
                dm.load_initial_data("Data")   # Cette méthode importe les fichiers CSV/JSON

            # Récupérer les tables depuis la base
            produits_db = dm.get_table_as_df('products')
            couts_db = dm.get_table_as_df('costs')
            volumes_db = dm.get_table_as_df('volumes')
            scenarios_db = dm.get_table_as_df('scenario_templates')

            # Adapter les colonnes pour correspondre aux noms attendus par les graphiques
            donnees = {}

            if produits_db is not None and not produits_db.empty:
                produits_db = produits_db.rename(columns={
                    'product_id': 'id_produit',
                    'name': 'nom',
                    'category': 'categorie',
                    'cost_price': 'cout_revient',
                    'selling_price': 'prix_vente'
                })
                donnees['produits'] = produits_db
                print(f"✅ produits : {len(produits_db)} lignes chargées")
            else:
                donnees['produits'] = None
                print("⚠️ Table 'products' vide ou inexistante")

            if couts_db is not None and not couts_db.empty:
                couts_db = couts_db.rename(columns={
                    'product_id': 'id_produit',
                    'fixed_costs': 'fixes',
                    'variable_costs': 'variables',
                    'labor_costs': 'main_oeuvre',
                    'raw_materials': 'matieres_premieres'
                })
                donnees['couts'] = couts_db
                print(f"✅ couts : {len(couts_db)} lignes chargées")
            else:
                donnees['couts'] = None
                print("⚠️ Table 'costs' vide ou inexistante")

            if volumes_db is not None and not volumes_db.empty:
                volumes_db = volumes_db.rename(columns={
                    'product_id': 'id_produit',
                    'period': 'periode',
                    'produced': 'volume_produit',
                    'sold': 'volume_vendu'
                })
                donnees['volumes'] = volumes_db
                print(f"✅ volumes : {len(volumes_db)} lignes chargées")
            else:
                donnees['volumes'] = None
                print("⚠️ Table 'volumes' vide ou inexistante")

            if scenarios_db is not None and not scenarios_db.empty:
                scenarios_db = scenarios_db.rename(columns={
                    'name': 'nom',
                    'sales_change': 'augmentation_ventes',
                    'cost_change': 'reduction_couts',
                    'description': 'description'
                })
                donnees['scenarios'] = scenarios_db
                print(f"✅ scénarios : {len(scenarios_db)} lignes chargées")
            else:
                donnees['scenarios'] = None
                print("⚠️ Table 'scenario_templates' vide ou inexistante")

            return donnees

        except Exception as e:
            print(f"❌ Erreur lors du chargement via DataManager : {e}")
            print("   Fallback vers les fichiers...")
            return _charger_depuis_fichiers()
    else:
        return _charger_depuis_fichiers()

def _charger_depuis_fichiers() -> Dict[str, Optional[pd.DataFrame]]:
    """Charge les données directement depuis les fichiers CSV/JSON (fallback)."""
    chemin_base = "Data/"
    fichiers = {
        'produits': 'produits.csv',
        'couts': 'couts.csv',
        'volumes': 'volumes.csv',
        'scenarios': 'scenarios.json'
    }
    donnees = {}
    print("📂 CHARGEMENT DES FICHIERS...")
    print("-" * 40)
    for nom, fichier in fichiers.items():
        chemin_complet = os.path.join(chemin_base, fichier)
        try:
            if fichier.endswith('.csv'):
                donnees[nom] = pd.read_csv(chemin_complet)
                print(f"✅ {fichier} : {len(donnees[nom])} lignes chargées")
            elif fichier.endswith('.json'):
                donnees[nom] = pd.read_json(chemin_complet)
                print(f"✅ {fichier} : {len(donnees[nom])} lignes chargées")
        except FileNotFoundError:
            print(f"❌ {fichier} : FICHIER NON TROUVÉ")
            donnees[nom] = None
    print("-" * 40)
    return donnees

# ============================================
# GRAPHIQUE 1 : Coûts et marges par produit
# ============================================

def graphique_couts_marges(donnees):
    """
    Diagramme en barres modernes avec dégradés et valeurs.
    """
    df_produits = donnees['produits']
    if df_produits is None or df_produits.empty:
        print("❌ Pas de données produits")
        return None

    # Calculer la marge
    df_produits['marge'] = df_produits['prix_vente'] - df_produits['cout_revient']
    df_produits['marge_percent'] = (df_produits['marge'] / df_produits['prix_vente']) * 100

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle('Analyse Financière des Produits', fontsize=16, fontweight='bold', y=1.02)

    # Barres groupées
    ax1 = plt.subplot(1, 2, 1)
    x = np.arange(len(df_produits))
    largeur = 0.25

    barres1 = ax1.bar(x - largeur, df_produits['cout_revient'], largeur,
                      label='Coût de revient', color=COULEURS['couts'],
                      edgecolor='white', linewidth=1.5, alpha=0.9)
    barres2 = ax1.bar(x, df_produits['prix_vente'], largeur,
                      label='Prix de vente', color=COULEURS['prix'],
                      edgecolor='white', linewidth=1.5, alpha=0.9)
    barres3 = ax1.bar(x + largeur, df_produits['marge'], largeur,
                      label='Marge brute', color=COULEURS['marge'],
                      edgecolor='white', linewidth=1.5, alpha=0.9)

    max_val = max(df_produits['prix_vente'].max(), df_produits['cout_revient'].max())
    for i, (cout, prix, marge) in enumerate(zip(df_produits['cout_revient'],
                                                df_produits['prix_vente'],
                                                df_produits['marge'])):
        ax1.text(i - largeur, cout + max_val*0.02, f'{cout:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax1.text(i, prix + max_val*0.02, f'{prix:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax1.text(i + largeur, marge + max_val*0.02, f'{marge:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_xlabel('Produits', fontsize=12, fontweight='semibold')
    ax1.set_ylabel('Montant (Ar)', fontsize=12, fontweight='semibold')
    ax1.set_title('Comparaison Coût / Prix / Marge', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_produits['nom'], rotation=45, ha='right')
    ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax1.set_ylim(0, max_val * 1.2)

    # Camembert des marges
    ax2 = plt.subplot(1, 2, 2)
    couleurs_camembert = [COULEURS['primaire'], COULEURS['secondaire'],
                          COULEURS['accent'], COULEURS['succes'], COULEURS['couts']]
    wedges, texts, autotexts = ax2.pie(df_produits['marge'],
                                        labels=df_produits['nom'],
                                        colors=couleurs_camembert[:len(df_produits)],
                                        autopct='%1.1f%%',
                                        startangle=90,
                                        explode=[0.05] * len(df_produits),
                                        shadow=True)
    for text in texts:
        text.set_fontsize(10)
        text.set_fontweight('semibold')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    ax2.set_title('Répartition des Marges par Produit', fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    return fig

# ============================================
# GRAPHIQUE 2 : Évolution des volumes
# ============================================

def graphique_evolution_volumes(donnees):
    df_volumes = donnees['volumes']
    if df_volumes is None or df_volumes.empty:
        print("❌ Pas de données volumes")
        return None

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('Suivi des Volumes de Production et Vente', fontsize=16, fontweight='bold', y=0.98)

    produits = df_volumes['id_produit'].unique()
    palette = [COULEURS['primaire'], COULEURS['secondaire'], COULEURS['accent'],
               COULEURS['succes'], COULEURS['couts']]

    for idx, produit in enumerate(produits):
        df_produit = df_volumes[df_volumes['id_produit'] == produit].sort_values('periode')
        couleur = palette[idx % len(palette)]

        axes[0].plot(df_produit['periode'], df_produit['volume_produit'],
                    marker='o', linewidth=2.5, color=couleur,
                    label=f'Produit {produit}', markersize=8, markeredgecolor='white',
                    markeredgewidth=2)
        axes[0].fill_between(df_produit['periode'], df_produit['volume_produit'],
                             alpha=0.15, color=couleur)

        axes[1].plot(df_produit['periode'], df_produit['volume_vendu'],
                    marker='s', linewidth=2.5, color=couleur,
                    label=f'Produit {produit}', markersize=8, markeredgecolor='white',
                    markeredgewidth=2)
        axes[1].fill_between(df_produit['periode'], df_produit['volume_vendu'],
                             alpha=0.15, color=couleur)

    axes[0].set_title('📈 Évolution de la Production', fontsize=13, fontweight='bold', pad=15)
    axes[0].set_ylabel('Volume produit (unités)', fontsize=11, fontweight='semibold')
    axes[0].legend(loc='upper left', frameon=True, fancybox=True, shadow=True, ncol=3)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title('📊 Évolution des Ventes', fontsize=13, fontweight='bold', pad=15)
    axes[1].set_xlabel('Période', fontsize=11, fontweight='semibold')
    axes[1].set_ylabel('Volume vendu (unités)', fontsize=11, fontweight='semibold')
    axes[1].legend(loc='upper left', frameon=True, fancybox=True, shadow=True, ncol=3)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

# ============================================
# GRAPHIQUE 3 : Comparaison des scénarios
# ============================================

def graphique_scenarios(donnees):
    df_scenarios = donnees['scenarios']
    df_produits = donnees['produits']
    if df_scenarios is None or df_produits is None:
        print("❌ Données manquantes pour les scénarios")
        return None

    marge_base = (df_produits['prix_vente'] - df_produits['cout_revient']).sum()

    noms_scenarios = []
    marges_scenarios = []
    variations = []

    for _, scenario in df_scenarios.iterrows():
        augmentation = 1 + scenario['augmentation_ventes'] / 100
        reduction_couts = 1 - scenario['reduction_couts'] / 100
        marge_scenario = marge_base * augmentation * reduction_couts
        variation = ((marge_scenario - marge_base) / marge_base) * 100

        noms_scenarios.append(scenario['nom'])
        marges_scenarios.append(marge_scenario)
        variations.append(variation)

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Analyse des Scénarios Stratégiques', fontsize=16, fontweight='bold', y=0.98)

    couleurs = []
    for nom in noms_scenarios:
        if 'optimiste' in nom.lower():
            couleurs.append('#73AB84')
        elif 'pessimiste' in nom.lower():
            couleurs.append('#E63946')
        else:
            couleurs.append('#2E86AB')

    barres = ax.bar(noms_scenarios, marges_scenarios, color=couleurs,
                    edgecolor='white', linewidth=2, alpha=0.85, width=0.6)

    for barre in barres:
        barre.set_zorder(3)

    ax.axhline(y=marge_base, color=COULEURS['gris_moyen'], linestyle='--',
               linewidth=2.5, alpha=0.7, zorder=1,
               label=f'Marge de base: {marge_base:,.0f} Ar')

    for barre, marge, variation in zip(barres, marges_scenarios, variations):
        hauteur = barre.get_height()
        ax.text(barre.get_x() + barre.get_width()/2., hauteur + marge_base*0.02,
                f'{marge:,.0f} Ar', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color=COULEURS['gris_fonce'])
        couleur_var = COULEURS['succes'] if variation > 0 else COULEURS['danger']
        symbole = '▲' if variation > 0 else '▼'
        ax.text(barre.get_x() + barre.get_width()/2., hauteur - marge_base*0.05,
                f'{symbole} {variation:+.1f}%', ha='center', va='top',
                fontsize=10, fontweight='bold', color=couleur_var,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    ax.set_xlabel('Scénarios', fontsize=12, fontweight='semibold')
    ax.set_ylabel('Marge totale (Ar)', fontsize=12, fontweight='semibold')
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax.set_facecolor(COULEURS['gris_clair'])
    ax.grid(True, alpha=0.2, axis='y')
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(marges_scenarios) * 1.15)

    plt.tight_layout()
    return fig

# ============================================
# GRAPHIQUE 4 : Seuil de rentabilité
# ============================================

def graphique_seuil_rentabilite(donnees):
    df_produits = donnees['produits']
    df_couts = donnees['couts']
    if df_produits is None or df_couts is None:
        print("❌ Données manquantes pour le seuil de rentabilité")
        return None

    prix_moyen = df_produits['prix_vente'].mean()
    cout_moyen = df_produits['cout_revient'].mean()
    marge_unitaire = prix_moyen - cout_moyen
    charges_fixes = df_couts['fixes'].sum()

    if marge_unitaire <= 0:
        print("⚠️ Marge unitaire non positive – seuil de rentabilité impossible")
        return None

    seuil_unites = charges_fixes / marge_unitaire
    seuil_ca = seuil_unites * prix_moyen

    volumes = np.linspace(0, seuil_unites * 2, 200)
    ca = volumes * prix_moyen
    couts_totaux = charges_fixes + volumes * cout_moyen

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle('Analyse du Seuil de Rentabilité', fontsize=16, fontweight='bold', y=0.98)

    ax.fill_between(volumes, ca, couts_totaux, where=(ca >= couts_totaux),
                    facecolor=COULEURS['succes'], alpha=0.25, label='Zone de profit')
    ax.fill_between(volumes, ca, couts_totaux, where=(ca < couts_totaux),
                    facecolor=COULEURS['danger'], alpha=0.25, label='Zone de perte')

    ax.plot(volumes, ca, color=COULEURS['prix'], linewidth=3,
            label='Chiffre d\'affaires', zorder=3)
    ax.plot(volumes, couts_totaux, color=COULEURS['couts'], linewidth=3,
            label='Coûts totaux', zorder=3)

    ax.scatter([seuil_unites], [seuil_ca], color=COULEURS['accent'], s=200,
               zorder=5, edgecolor='white', linewidth=2, label='Seuil de rentabilité')

    ax.axvline(x=seuil_unites, color=COULEURS['gris_moyen'], linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axhline(y=seuil_ca, color=COULEURS['gris_moyen'], linestyle='--', alpha=0.5, linewidth=1.5)

    ax.annotate(f'Point d\'équilibre\n{seuil_unites:,.0f} unités\n{seuil_ca:,.0f} Ar CA',
                xy=(seuil_unites, seuil_ca), xytext=(seuil_unites*1.15, seuil_ca*0.85),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         edgecolor=COULEURS['accent'], linewidth=2, alpha=0.9),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                              color=COULEURS['accent'], linewidth=2))

    ax.set_xlabel('Volume de vente (unités)', fontsize=12, fontweight='semibold')
    ax.set_ylabel('Montant (Ar)', fontsize=12, fontweight='semibold')
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.set_facecolor(COULEURS['gris_clair'])
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.set_axisbelow(True)

    ax.text(0.98, 0.02, f'Marge unitaire: {marge_unitaire:,.0f} Ar | Coûts fixes: {charges_fixes:,.0f} Ar',
            transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    plt.tight_layout()
    return fig

# ============================================
# SAUVEGARDE DES GRAPHIQUES
# ============================================

def sauvegarder_graphique(fig, nom_fichier, dossier="src/data/graphiques"):
    if not os.path.exists(dossier):
        os.makedirs(dossier)
    chemin = os.path.join(dossier, nom_fichier)
    fig.savefig(chemin, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Graphique sauvegardé : {chemin}")

# ============================================
# FONCTION PRINCIPALE (TEST)
# ============================================

if __name__ == "__main__":
    print("=" * 55)
    print("🎨 MODULE DE VISUALISATION - VERSION PROFESSIONNELLE")
    print("=" * 55)

    donnees = charger_donnees()

    if all(v is not None for v in donnees.values()):
        print("\n📊 GÉNÉRATION DES GRAPHIQUES ...")
        print("-" * 40)

        for name, func, filename in [
            ("Coûts et marges", graphique_couts_marges, "01_couts_marges.png"),
            ("Évolution des volumes", graphique_evolution_volumes, "02_evolution_volumes.png"),
            ("Comparaison scénarios", graphique_scenarios, "03_comparaison_scenarios.png"),
            ("Seuil de rentabilité", graphique_seuil_rentabilite, "04_seuil_rentabilite.png")
        ]:
            print(f"→ {name} ...")
            fig = func(donnees)
            if fig:
                sauvegarder_graphique(fig, filename)
            else:
                print(f"   ⚠️ Graphique {name} non généré")

        print("-" * 40)
        print("\n✨ TOUS LES GRAPHIQUES ONT ÉTÉ GÉNÉRÉS !")
        print("📁 Sauvegarde dans : src/data/graphiques/")
        print("\n🔍 Affichage des graphiques...")
        plt.show()
    else:
        print("\n❌ Données manquantes. Vérifiez les fichiers dans Data/ ou la base de données.")