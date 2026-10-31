"""Fetch the Layer-B inputs from Eurostat: PV net capacity, population, PV-panel WEEE collected
(old scope 2015-2018 and open scope 2019-2024) and PV modules put on the market."""
from pathlib import Path

import pandas as pd

from eurostat import EU27, get

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

pv = get("nrg_inf_epcrw", {"siec": "RA420", "plant_tec": "CAP_NET_ELC", "unit": "MW"})
pv = pv[pv.geo.isin(EU27)].pivot(index="time", columns="geo", values="value")
pv.to_csv(DATA / "pv_capacity_mw.csv")

pop = get("tps00001")
pop[pop.geo.isin(EU27)].pivot(index="time", columns="geo", values="value").to_csv(DATA / "population.csv")

old = get("env_waselee")
old = old[(old.waste == "EE_CPV_PVP") & (old.geo.isin(EU27)) & (old.unit == "T")]
old.to_csv(DATA / "weee_pv_raw.csv", index=False)
o = old[old.wst_oper == "COL"][["geo", "time", "value"]].copy(); o["scope"] = "old"

new = get("env_waseleeos")
n = new[(new.waste == "EE_LE_PVP") & (new.unit == "T") & (new.geo.isin(EU27))]
nc = n[n.wst_oper == "COL"][["geo", "time", "value", "flag"]].copy(); nc["scope"] = "open"
pd.concat([o, nc]).to_csv(DATA / "weee_pv_all.csv", index=False)
n[n.wst_oper == "MKT"][["geo", "time", "value"]].to_csv(DATA / "weee_pv_mkt.csv", index=False)
print("capacity years", pv.index.min(), pv.index.max(), "| PV WEEE rows", len(o) + len(nc), "| MKT rows", int((n.wst_oper == "MKT").sum()))
