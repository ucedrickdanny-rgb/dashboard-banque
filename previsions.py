
from prophet import Prophet
import pandas as pd
from etl import run_pipeline

def preparer_prophet(df, colonne='depot'):
    data = df[['date', colonne]].copy()
    data = data.rename(columns={'date': 'ds', colonne: 'y'})
    return data

def faire_previsions(df, colonne='depot', horizon=90):
    data = preparer_prophet(df, colonne)
    model = Prophet(
        yearly_seasonality = True,
        weekly_seasonality = True,
        daily_seasonality  = False,
    )
    model.fit(data)
    futur = model.make_future_dataframe(periods=horizon)
    previsions = model.predict(futur)
    return previsions[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

if __name__ == '__main__':
    df, kpis, mensuel, par_agence = run_pipeline()
    print("\n⏳ Prophet ikora prévisions — rindira amasegonda 10...")
    prev = faire_previsions(df, colonne='depot', horizon=90)
    print("\n━━━ PREVISIONS Z'AMEZI 3 (iminsi 5 ya nyuma) ━━━")
    print(prev.tail(5).to_string(index=False))
    prev_gusa = prev.tail(90)
    print(f"\n━━━ INCAMAKE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Depot moyen uzotegerezwa: BIF {prev_gusa['yhat'].mean():>12,.0f}")
    print(f"  Nto  (yhat_lower)       : BIF {prev_gusa['yhat_lower'].mean():>12,.0f}")
    print(f"  Nkuru (yhat_upper)      : BIF {prev_gusa['yhat_upper'].mean():>12,.0f}")
    print("\n✓ Prévisions zarangiye neza!")