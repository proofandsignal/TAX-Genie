"""Reproducible invoice extraction benchmark: separate synthetic and consented-real."""
from collections import defaultdict
from .invoice_evidence import extract_invoice_evidence, FIELDS

def evaluate(rows: list[dict], *, require_50: bool = False) -> dict:
    if require_50 and len(rows) != 50:
        raise ValueError("PAPER 50 requires exactly 50 rows")
    if len({r.get("id") for r in rows}) != len(rows):
        raise ValueError("Duplicate benchmark IDs")
    tallies = defaultdict(lambda: {"tp":0, "fp":0, "fn":0, "tn":0})
    datasets = defaultdict(lambda: {"count":0,"perfect":0})
    for row in rows:
        if row.get("dataset") not in {"synthetic", "consented_real"}:
            raise ValueError("Dataset must be synthetic or consented_real")
        truth = row.get("truth")
        if not isinstance(truth, dict) or set(truth)-set(FIELDS):
            raise ValueError("Invalid ground truth")
        if any(not isinstance(v,str) for v in truth.values()):
            raise ValueError("Ground truth values must be strings")
        if not isinstance(row.get("text"),str):
            raise ValueError("Text missing")
        result=extract_invoice_evidence(row["text"])
        pred={k:v["value"] for k,v in result["fields"].items()}
        group=row["dataset"]; datasets[group]["count"]+=1
        if pred==truth: datasets[group]["perfect"]+=1
        for field in FIELDS:
            target=truth.get(field); actual=pred.get(field)
            t=tallies[(group,field)]
            if target is None and actual is None: t["tn"]+=1
            elif target is not None and actual==target: t["tp"]+=1
            else:
                if actual is not None: t["fp"]+=1
                if target is not None: t["fn"]+=1
    metrics={}
    for (group,field), t in sorted(tallies.items()):
        metrics.setdefault(group,{})[field]={
            **t,
            "precision":None if t["tp"]+t["fp"]==0 else round(t["tp"]/(t["tp"]+t["fp"]),4),
            "recall":None if t["tp"]+t["fn"]==0 else round(t["tp"]/(t["tp"]+t["fn"]),4),
        }
    return {"total":len(rows), "datasets":dict(datasets), "per_field":metrics,
            "interpretation":"Exact-match extraction only; not tax eligibility or refund performance."}
