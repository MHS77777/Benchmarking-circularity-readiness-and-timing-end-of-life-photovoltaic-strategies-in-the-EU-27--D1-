"""Minimal Eurostat JSON-stat 2.0 client.

Fetches a dataset from the Eurostat dissemination API and flattens it into a
long pandas DataFrame with one row per (dimension combination), including the
observation status flag (e.g. 'e' estimated, 'p' provisional, 'b' break in
series, 'u' low reliability, 'd' definition differs).
"""
import itertools
import json
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
CACHE = Path(__file__).resolve().parent.parent / "data" / "raw"
CACHE.mkdir(parents=True, exist_ok=True)

EU27 = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE"]


def fetch_json(code: str, params: dict | None = None, force: bool = False) -> dict:
    params = dict(params or {})
    params.setdefault("format", "JSON")
    params.setdefault("lang", "EN")
    key = code + "_" + "_".join(f"{k}-{v}" for k, v in sorted(params.items()) if k not in ("format", "lang"))
    fp = CACHE / f"{key}.json"
    if fp.exists() and not force:
        return json.loads(fp.read_text())
    for attempt in range(4):
        r = requests.get(BASE + code, params=params, timeout=120)
        if r.status_code == 200:
            js = r.json()
            fp.write_text(json.dumps(js))
            return js
        time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"{code}: HTTP {r.status_code} {r.text[:200]}")


def jsonstat_to_df(js: dict) -> pd.DataFrame:
    dims = js["id"]
    sizes = js["size"]
    cats = []
    for d in dims:
        idx = js["dimension"][d]["category"]["index"]
        # index may be dict {code: pos} or list
        if isinstance(idx, dict):
            codes = sorted(idx, key=lambda c: idx[c])
        else:
            codes = list(idx)
        cats.append(codes)
    values = js.get("value", {})
    status = js.get("status", {})
    rows = []
    # linear index -> multi-index (row-major, last dimension fastest)
    for lin_str, val in values.items():
        lin = int(lin_str)
        coords = []
        rem = lin
        for s in reversed(sizes):
            coords.append(rem % s)
            rem //= s
        coords = coords[::-1]
        row = {d: cats[i][c] for i, (d, c) in enumerate(zip(dims, coords))}
        row["value"] = val
        row["flag"] = status.get(lin_str, "")
        rows.append(row)
    df = pd.DataFrame(rows)
    if "time" in df.columns:
        df["time"] = df["time"].astype(int)
    return df


def get(code: str, params: dict | None = None) -> pd.DataFrame:
    js = fetch_json(code, params)
    df = jsonstat_to_df(js)
    df["dataset"] = code
    df.attrs["label"] = js.get("label", "")
    df.attrs["dims"] = {d: js["dimension"][d]["category"].get("label", {}) for d in js["id"]}
    return df


if __name__ == "__main__":
    import sys
    code = sys.argv[1]
    df = get(code)
    print(df.attrs["label"])
    for d, lab in df.attrs["dims"].items():
        if d in ("geo", "time"):
            continue
        print(f"  {d}: {lab}")
    print(df.head())
    print(len(df), "rows; years", df.time.min(), "-", df.time.max())
