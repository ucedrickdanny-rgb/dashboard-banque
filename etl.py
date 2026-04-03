
import pandas as pd
import os

# ═══════════════════════════════════════════════════
# MAPPING — hindura hano gusa iyo ugiye kuri banque nshasha
# Ibumoso  = izina rya colonne muri Excel ya banque
# Iburyo   = izina dashboard ikoresha
# ═══════════════════════════════════════════════════

MAPPING_COLONNES = {
    # ── Banque yacu ya mfano ──
    'date'    : 'date',
    'depot'   : 'depot',
    'retrait' : 'retrait',
    'agence'  : 'agence',
    'clients' : 'clients',
    'credits' : 'credits',
}

# ── Iyo ukiye kuri BRB: ──────────────────────────
# MAPPING_COLONNES = {
#     'Date_Operation'     : 'date',
#     'Montant_Versement'  : 'depot',
#     'Montant_Retrait'    : 'retrait',
#     'Succursale'         : 'agence',
#     'Nbre_Clients'       : 'clients',
#     'Nbre_Credits'       : 'credits',
# }

# ── Iyo ukiye kuri IBB: ──────────────────────────
# MAPPING_COLONNES = {
#     'date_mvt'           : 'date',
#     'credit_compte'      : 'depot',
#     'debit_compte'       : 'retrait',
#     'code_agence'        : 'agence',
#     'nb_clients_jour'    : 'clients',
#     'nb_prets'           : 'credits',
# }

# ── Iyo ukiye kuri FENACOBU: ─────────────────────
# MAPPING_COLONNES = {
#     'DATE'               : 'date',
#     'EPARGNE'            : 'depot',
#     'RETRAIT'            : 'retrait',
#     'COOPERATIVE'        : 'agence',
#     'MEMBRES'            : 'clients',
#     'PRETS'              : 'credits',
# }

# ═══════════════════════════════════════════════════
# E — EXTRACT
# ═══════════════════════════════════════════════════
def extract(path='data/transactions.csv'):
    if path.endswith('.xlsx') or path.endswith('.xls'):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    colonnes_iboneka = [c for c in MAPPING_COLONNES if c in df.columns]
    df = df[colonnes_iboneka].rename(columns=MAPPING_COLONNES)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    print(f"✓ Extract: imirongo {len(df):,} yafashwe")
    print(f"  Colonnes: {list(df.columns)}")
    return df


# ═══════════════════════════════════════════════════
# T — TRANSFORM + CLEANING
# ═══════════════════════════════════════════════════
def transform(df):
    n_mbere = len(df)

    for col in ['depot', 'retrait', 'clients', 'credits']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'depot'   in df.columns: df['depot'].fillna(df['depot'].median(),   inplace=True)
    if 'retrait' in df.columns: df['retrait'].fillna(df['retrait'].median(), inplace=True)
    if 'clients' in df.columns: df['clients'].fillna(df['clients'].median(), inplace=True)
    if 'credits' in df.columns: df['credits'].fillna(0,                    inplace=True)
    if 'agence'  in df.columns: df['agence'].fillna('Inconnue',           inplace=True)

    df = df.dropna(subset=['date'])

    if 'depot'   in df.columns: df = df[df['depot']   > 0]
    if 'retrait' in df.columns: df = df[df['retrait'] > 0]

    df = df.drop_duplicates()

    if 'agence' in df.columns:
        df['agence'] = df['agence'].str.strip().str.title()

    df['mois']           = df['date'].dt.to_period('M')
    df['trimestre']      = df['date'].dt.quarter
    df['annee']          = df['date'].dt.year
    df['solde_net']      = df['depot'] - df['retrait']
    df['ratio_retrait']  = (df['retrait'] / df['depot']).round(3)
    df['solde_cumulatif'] = df['solde_net'].cumsum()
    df['kigega_agence']  = df.groupby('agence')['solde_net'].cumsum()

    n_nyuma = len(df)
    print(f"✓ Transform yarangiye:")
    print(f"  Zinjiye   : {n_mbere:,}")
    print(f"  Zisibwe   : {n_mbere - n_nyuma:,}")
    print(f"  Zikoresha : {n_nyuma:,}")
    return df


# ═══════════════════════════════════════════════════
# L — LOAD
# ═══════════════════════════════════════════════════
def load(df):
    kpis = {
        'depot_moyen'   : round(df['depot'].mean()),
        'retrait_moyen' : round(df['retrait'].mean()),
        'solde_total'   : df['solde_net'].sum(),
        'clients_moyen' : round(df['clients'].mean()) if 'clients' in df.columns else 0,
        'kigega_ubu'    : df['solde_cumulatif'].iloc[-1],
        'n_zinjiye'     : len(df),
    }
    mensuel = df.groupby('mois').agg(
        depot_total     = ('depot',           'sum'),
        retrait_total   = ('retrait',         'sum'),
        clients_moy     = ('clients',         'mean') if 'clients' in df.columns else ('depot', 'count'),
        solde_net       = ('solde_net',       'sum'),
        kigega_fin_mois = ('solde_cumulatif', 'last'),
    ).reset_index()
    par_agence = df.groupby('agence').agg(
        depot_total   = ('depot',   'sum'),
        retrait_total = ('retrait', 'sum'),
        clients_total = ('clients', 'sum') if 'clients' in df.columns else ('depot', 'count'),
        credits_total = ('credits', 'sum') if 'credits' in df.columns else ('depot', 'count'),
    ).reset_index()
    print("✓ Load: KPIs zateguwe")
    return kpis, mensuel, par_agence


def run_pipeline(path='data/transactions.csv'):
    df = extract(path)
    df = transform(df)
    kpis, mensuel, par_agence = load(df)
    return df, kpis, mensuel, par_agence