import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
n = len(dates)

df = pd.DataFrame({
    'date': dates,

    # Dépôts ziyongera buri mwaka
    'depot': (
        np.random.normal(5_000_000, 700_000, n)
        + np.linspace(0, 1_000_000, n)
    ).clip(1_000_000).round(0).astype(int),

    # Retraits — ntoyi kuruta dépôts
    'retrait': (
        np.random.normal(3_200_000, 500_000, n)
        + np.linspace(0, 500_000, n)
    ).clip(500_000).round(0).astype(int),

    # Clients baza muri agence buri munsi
    'clients': np.random.randint(80, 280, n),

    # Agence 4 za Burundi — na Rumonge!
    'agence': np.random.choice(
        ['Bujumbura', 'Gitega', 'Ngozi', 'Rumonge'],
        n,
        p=[0.50, 0.25, 0.15, 0.10]
    ),

    # Inguzanyo zapfunzwe uyu munsi
    'credits': np.random.randint(2, 15, n),
})

# Solde net = depot - retrait
df['solde_net'] = df['depot'] - df['retrait']

# Shira muri CSV
df.to_csv('data/transactions.csv', index=False)

# Reba ivyasohotse
print("✓ Données zateguwe!")
print(f"  Imirongo : {len(df):,}")
print(f"  Iminsi   : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  Agences  : {list(df['agence'].unique())}")
print("\nAgences na données zazo:")
print(df['agence'].value_counts())