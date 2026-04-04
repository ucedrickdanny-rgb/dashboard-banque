
import pandas as pd
import numpy as np
import os

os.makedirs('tests', exist_ok=True)
np.random.seed(42)
dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
n = len(dates)

# TEST 1 — Données nziza
df1 = pd.DataFrame({
    'date'    : dates,
    'depot'   : np.random.normal(5_000_000, 500_000, n).clip(1_000_000).round(0).astype(int),
    'retrait' : np.random.normal(3_000_000, 400_000, n).clip(500_000).round(0).astype(int),
    'clients' : np.random.randint(100, 300, n),
    'agence'  : np.random.choice(['Bujumbura','Gitega','Ngozi','Rumonge'], n),
    'credits' : np.random.randint(2, 15, n),
})
df1.to_excel('tests/test1_nziza.xlsx', index=False)
print("✓ Test 1 yateguwe: tests/test1_nziza.xlsx")

# TEST 2 — Données mbi
df2 = df1.copy()
idx_depot   = np.random.choice(df2.index, size=int(n*0.20), replace=False)
df2.loc[idx_depot, 'depot'] = np.nan
idx_clients = np.random.choice(df2.index, size=int(n*0.15), replace=False)
df2.loc[idx_clients, 'clients'] = np.nan
df2.loc[5,  'agence'] = 'BUJUMBURA'
df2.loc[10, 'agence'] = ' Gitega '
df2.loc[15, 'depot']  = 'cinq millions'
df2.to_excel('tests/test2_mbi.xlsx', index=False)
print("✓ Test 2 yateguwe: tests/test2_mbi.xlsx")

# TEST 3 — Amazina atandukanye (BRB)
df3 = pd.DataFrame({
    'Date_Operation'    : dates,
    'Montant_Versement' : df1['depot'],
    'Montant_Retrait'   : df1['retrait'],
    'Nbre_Clients'      : df1['clients'],
    'Succursale'        : df1['agence'],
    'Nbre_Credits'      : df1['credits'],
})
df3.to_excel('tests/test3_mapping.xlsx', index=False)
print("✓ Test 3 yateguwe: tests/test3_mapping.xlsx")

# TEST 4 — Solde negative
df4 = pd.DataFrame({
    'date'    : dates,
    'depot'   : np.random.normal(2_000_000, 300_000, n).clip(500_000).round(0).astype(int),
    'retrait' : np.random.normal(4_500_000, 400_000, n).clip(1_000_000).round(0).astype(int),
    'clients' : np.random.randint(80, 200, n),
    'agence'  : np.random.choice(['Bujumbura','Gitega','Ngozi','Rumonge'], n),
    'credits' : np.random.randint(1, 8, n),
})
df4.to_excel('tests/test4_akaga.xlsx', index=False)
print("✓ Test 4 yateguwe: tests/test4_akaga.xlsx")

print("\n━━━ Tests zose ziri muri dossier tests/ ━━━")
print("  test1_nziza.xlsx   — données nziza")
print("  test2_mbi.xlsx     — données mbi + amakosa")
print("  test3_mapping.xlsx — amazina ya BRB")
print("  test4_akaga.xlsx   — solde negative")