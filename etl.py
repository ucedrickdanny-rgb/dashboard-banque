
import pandas as pd
import os

MAPPING_COLONNES = {
    'date'             : 'date',
    'Date_Operation'   : 'date',
    'DATE'             : 'date',
    'Date'             : 'date',
    'date_mvt'         : 'date',
    'TXN_DATE'         : 'date',
    'date_transaction' : 'date',
    'depot'             : 'depot',
    'Montant_Versement' : 'depot',
    'EPARGNE'           : 'depot',
    'credit_compte'     : 'depot',
    'CR_AMOUNT'         : 'depot',
    'versement'         : 'depot',
    'Versement'         : 'depot',
    'montant_depot'     : 'depot',
    'Depot'             : 'depot',
    'DEPOT'             : 'depot',
    'retrait'           : 'retrait',
    'Montant_Retrait'   : 'retrait',
    'RETRAIT'           : 'retrait',
    'debit_compte'      : 'retrait',
    'DR_AMOUNT'         : 'retrait',
    'Retrait'           : 'retrait',
    'montant_retrait'   : 'retrait',
    'withdrawal'        : 'retrait',
    'agence'            : 'agence',
    'Succursale'        : 'agence',
    'COOPERATIVE'       : 'agence',
    'code_agence'       : 'agence',
    'BRANCH_CODE'       : 'agence',
    'Agence'            : 'agence',
    'AGENCE'            : 'agence',
    'branch'            : 'agence',
    'agence_code'       : 'agence',
    'clients'           : 'clients',
    'Nbre_Clients'      : 'clients',
    'MEMBRES'           : 'clients',
    'nb_clients_jour'   : 'clients',
    'Clients'           : 'clients',
    'CLIENTS'           : 'clients',
    'nombre_clients'    : 'clients',
    'nbre_clients'      : 'clients',
    'credits'           : 'credits',
    'Nbre_Credits'      : 'credits',
    'PRETS'             : 'credits',
    'nb_prets'          : 'credits',
    'Credits'           : 'credits',
    'CREDITS'           : 'credits',
    'nombre_credits'    : 'credits',
    'inguzanyo'         : 'credits',
}

def extract(path='data/transactions.csv'):
    if path.endswith('.xlsx') or path.endswith('.xls'):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    colonnes_iboneka = {k: v for k, v in MAPPING_COLONNES.items() if k in df.columns}
    df = df.rename(columns=colonnes_iboneka)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    print(f"✓ Extract: imirongo {len(df):,}")
    print(f"  Colonnes zabonetse: {list(df.columns)}")
    return df

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
    if 'date' in df.columns:
        df = df.dropna(subset=['date'])
    if 'depot'   in df.columns: df = df[df['depot']   > 0]
    if 'retrait' in df.columns: df = df[df['retrait'] > 0]
    df = df.drop_duplicates()
    if 'agence' in df.columns:
        df['agence'] = df['agence'].str.strip().str.title()
    if 'date' not in df.columns:
        df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
    if 'agence' not in df.columns:
        df['agence'] = 'Principale'
    if 'clients' not in df.columns:
        df['clients'] = 0
    if 'credits' not in df.columns:
        df['credits'] = 0
    df['mois']           = df['date'].dt.to_period('M')
    df['trimestre']      = df['date'].dt.quarter
    df['annee']          = df['date'].dt.year
    df['solde_net']      = df['depot'] - df['retrait']
    df['ratio_retrait']  = (df['retrait'] / df['depot']).round(3)
    df['solde_cumulatif'] = df['solde_net'].cumsum()
    df['kigega_agence']  = df.groupby('agence')['solde_net'].cumsum()
    n_nyuma = len(df)
    print(f"✓ Transform: zinjiye {n_mbere:,} → zikoresha {n_nyuma:,}")
    return df

def load(df):
    kpis = {
        'depot_moyen'   : round(df['depot'].mean()),
        'retrait_moyen' : round(df['retrait'].mean()),
        'solde_total'   : df['solde_net'].sum(),
        'clients_moyen' : round(df['clients'].mean()),
        'kigega_ubu'    : df['solde_cumulatif'].iloc[-1],
    }
    mensuel = df.groupby('mois').agg(
        depot_total     = ('depot',           'sum'),
        retrait_total   = ('retrait',         'sum'),
        clients_moy     = ('clients',         'mean'),
        solde_net       = ('solde_net',       'sum'),
        kigega_fin_mois = ('solde_cumulatif', 'last'),
    ).reset_index()
    par_agence = df.groupby('agence').agg(
        depot_total   = ('depot',   'sum'),
        retrait_total = ('retrait', 'sum'),
        clients_total = ('clients', 'sum'),
        credits_total = ('credits', 'sum'),
    ).reset_index()
    print("✓ Load: KPIs zateguwe")
    return kpis, mensuel, par_agence

def run_pipeline(path='data/transactions.csv'):
    df = extract(path)
    df = transform(df)
    kpis, mensuel, par_agence = load(df)
    return df, kpis, mensuel, par_agence