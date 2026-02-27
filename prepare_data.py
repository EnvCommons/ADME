"""
Download and prepare ADME datasets from TDC.

Pools 8 ADME endpoints into 1000 train + 100 test tasks.
Run once locally: python prepare_data.py
"""

import json
import os
from pathlib import Path

import pandas as pd
from tdc.single_pred import ADME

DATASETS = [
    {"name": "Lipophilicity_AstraZeneca", "property": "Lipophilicity", "units": "LogP"},
    {"name": "Solubility_AqSolDB", "property": "Aqueous Solubility", "units": "log(mol/L)"},
    {"name": "PPBR_AZ", "property": "Plasma Protein Binding Rate", "units": "%"},
    {"name": "Caco2_Wang", "property": "Caco-2 Permeability", "units": "log cm/s"},
    {"name": "Clearance_Hepatocyte_AZ", "property": "Hepatocyte Clearance", "units": "uL/min/10^6 cells"},
    {"name": "Clearance_Microsome_AZ", "property": "Microsome Clearance", "units": "uL/min/mg"},
    {"name": "VDss_Lombardo", "property": "Volume of Distribution", "units": "L/kg"},
    {"name": "Half_Life_Obach", "property": "Half-Life", "units": "hr"},
]

TRAIN_SIZE = 1000
TEST_SIZE = 100
TOTAL = TRAIN_SIZE + TEST_SIZE


def make_question(smiles: str, prop_name: str, units: str) -> str:
    return (
        f"You are a molecular property prediction expert.\n\n"
        f"Given the molecule with SMILES notation: {smiles}\n\n"
        f"Predict the {prop_name} value for this molecule (in {units}).\n\n"
        f"Submit your prediction as a single floating-point number using the submit_prediction tool."
    )


def main():
    all_rows = []

    for ds_info in DATASETS:
        print(f"Downloading {ds_info['name']}...")
        data = ADME(name=ds_info["name"])
        df = data.get_data()
        df = df.dropna(subset=["Drug", "Y"])
        df = df.drop_duplicates(subset=["Drug"])

        df["property_name"] = ds_info["property"]
        df["property_units"] = ds_info["units"]
        df["dataset"] = ds_info["name"]

        all_rows.append(df)
        print(f"  -> {len(df)} molecules")

    combined = pd.concat(all_rows, ignore_index=True)
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"\nTotal pooled molecules: {len(combined)}")

    if len(combined) < TOTAL:
        print(f"Warning: only {len(combined)} molecules, need {TOTAL}")

    selected = combined.head(TOTAL)

    tasks = []
    for idx, row in selected.iterrows():
        split = "test" if idx < TEST_SIZE else "train"
        task = {
            "task_id": f"adme_{split}_{idx}",
            "smiles": row["Drug"],
            "property_name": row["property_name"],
            "property_units": row["property_units"],
            "answer": float(row["Y"]),
            "question": make_question(row["Drug"], row["property_name"], row["property_units"]),
        }
        tasks.append(task)

    test_tasks = [t for t in tasks if "test" in t["task_id"]]
    train_tasks = [t for t in tasks if "train" in t["task_id"]]

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    with open(data_dir / "test.json", "w") as f:
        json.dump(test_tasks, f, indent=2)
    with open(data_dir / "train.json", "w") as f:
        json.dump(train_tasks, f, indent=2)

    print(f"\nSaved {len(train_tasks)} train tasks and {len(test_tasks)} test tasks")


if __name__ == "__main__":
    main()
