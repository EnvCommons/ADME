# Data Upload Requirements for AdmePred

## Overview
This environment requires ADME property prediction data uploaded to OpenReward cloud storage.

## Directory Structure
```
/orwd_data/
└── data/
    ├── train.json (1000 tasks, ~500 KB)
    └── test.json (100 tasks, ~50 KB)
```

## Files Required
- **train.json**: 1000 ADME property prediction tasks pooled from 8 TDC datasets (Lipophilicity, Solubility, Caco-2, PPBR, Clearance Hepatocyte, Clearance Microsome, VDss, Half-Life)
- **test.json**: 100 ADME property prediction tasks (same distribution)

## Data Generation
Run locally: `python prepare_data.py` (requires `pip install PyTDC pandas`)

## Upload Instructions
Upload the `data/` directory to your OpenReward namespace at https://openreward.ai.
