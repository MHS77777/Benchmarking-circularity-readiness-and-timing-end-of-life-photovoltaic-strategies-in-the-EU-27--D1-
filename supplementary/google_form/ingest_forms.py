"""Convert the Google Forms response sheet (exported as CSV) into the files the
Layer-C pipeline expects.

Usage:
    python3 ingest_forms.py responses.csv [--out ../data]

Outputs (in --out, default ../data):
    expert_ratings.csv      expert_id, horizon, archetype, alternative, criterion, rating   (read by layer_c.py)
    expert_weights.csv      expert_id, criterion, importance (1-9) and the normalised panel-mean weights
    expert_profile.csv      anonymous panel profile (role, sector, years, countries, familiarity)
    expert_comments.csv     free-text answers, keyed by expert_id

Mapping of Section 4 ("context") ratings to archetypes
------------------------------------------------------
Section 3 gives a rating r(h, a, c) for a typical member state. Section 4 gives an overall feasibility
rating k(g, a) for g in {L, CONV} at horizon H2. The archetype-specific rating used by the model is the
linguistic level nearest to  0.5 * level(r) + 0.5 * level(k)  for g = L, and the same with k(CONV, a) for
g in {CE, CL} (the early/late distinction enters through wave timing in Layer B, not through expert
judgement). Set --no-context to use Section 3 ratings unchanged for all archetypes.
"""
import argparse
import re
from pathlib import Path

import pandas as pd

LEVELS = ["VL", "L", "M", "H", "VH"]
RX_RATE = re.compile(r"^(H[123])\|(C[1-4]).*\[(A[1-7])")
RX_CTX = re.compile(r"^CONTEXT\|(L|CONV).*\[(A[1-7])")
RX_W = re.compile(r"^WEIGHTS.*\[(C[1-9])")
RX_PROF = re.compile(r"^PROFILE\|(\w+)")
RX_COMM = re.compile(r"^(COMMENT|OPEN)\|(\w+)")


def level(s):
    return LEVELS.index(str(s).split(" ")[0].strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--out", default="../data"); ap.add_argument("--no-context", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(exist_ok=True)
    df = pd.read_csv(a.csv)
    df = df[df.iloc[:, 0].notna()].reset_index(drop=True)
    df["expert_id"] = [f"E{i+1:02d}" for i in range(len(df))]

    ratings, ctx, weights, prof, comm = [], [], [], [], []
    for _, row in df.iterrows():
        e = row.expert_id
        for col, val in row.items():
            if pd.isna(val) or col == "expert_id":
                continue
            m = RX_RATE.match(col)
            if m:
                ratings.append({"expert_id": e, "horizon": m.group(1), "criterion": m.group(2), "alternative": m.group(3), "lvl": level(val)}); continue
            m = RX_CTX.match(col)
            if m:
                ctx.append({"expert_id": e, "group": m.group(1), "alternative": m.group(2), "lvl": level(val)}); continue
            m = RX_W.match(col)
            if m:
                weights.append({"expert_id": e, "criterion": m.group(1), "importance": int(str(val).strip())}); continue
            m = RX_PROF.match(col)
            if m:
                prof.append({"expert_id": e, "field": m.group(1), "value": val}); continue
            m = RX_COMM.match(col)
            if m:
                comm.append({"expert_id": e, "item": m.group(2), "text": val})
    R = pd.DataFrame(ratings); C = pd.DataFrame(ctx)
    rows = []
    for _, r in R.iterrows():
        for g, grp in [("L", "L"), ("CE", "CONV"), ("CL", "CONV")]:
            lv = r.lvl
            if not a.no_context and len(C):
                k = C[(C.expert_id == r.expert_id) & (C.group == grp) & (C.alternative == r.alternative)]
                if len(k):
                    lv = round(0.5 * r.lvl + 0.5 * k.lvl.iloc[0])
            rows.append({"expert_id": r.expert_id, "horizon": r.horizon, "archetype": g, "alternative": r.alternative,
                         "criterion": r.criterion, "rating": LEVELS[int(lv)]})
    ER = pd.DataFrame(rows).sort_values(["expert_id", "horizon", "archetype", "alternative", "criterion"])
    ER.to_csv(out / "expert_ratings.csv", index=False)

    W = pd.DataFrame(weights)
    if len(W):
        mean = W.groupby("criterion").importance.mean()
        W.to_csv(out / "expert_weights.csv", index=False)
        (mean / mean.sum()).rename("weight").to_csv(out / "expert_weights_normalised.csv")
        groups = {"inst": ["C1", "C2", "C3", "C4"], "econ": ["C5"], "env": ["C6", "C7", "C8"], "soc": ["C9"]}
        gw = {k: float(mean.reindex(v).sum() / mean.sum()) for k, v in groups.items()}
        print("Panel group weights for GROUP_W in layer_c.py:", {k: round(v, 3) for k, v in gw.items()})
    pd.DataFrame(prof).to_csv(out / "expert_profile.csv", index=False)
    pd.DataFrame(comm).to_csv(out / "expert_comments.csv", index=False)
    print(f"{len(df)} responses -> {len(ER)} rating rows written to {out/'expert_ratings.csv'}")
    print("Next: python3 layer_c.py && python3 figures_c.py && python3 synthesis.py && python3 make_tables.py")


if __name__ == "__main__":
    main()
