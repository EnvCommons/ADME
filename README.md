# AdmePred

Single-turn OpenReward environment for predicting ADME (Absorption, Distribution, Metabolism, Excretion) molecular properties from SMILES notation.

## Task

Given a molecule's SMILES string and an ADME endpoint name, the agent predicts the numerical property value. One tool call per task — predict and receive a reward.

## Data Source

All data comes from [Therapeutics Data Commons (TDC)](https://tdcommons.ai/single_pred_tasks/adme/), pooling 8 ADME regression datasets:

| Dataset | Property | Units | Molecules | Source Paper |
|---------|----------|-------|-----------|-------------|
| Lipophilicity_AstraZeneca | Lipophilicity | LogP | 4,200 | AstraZeneca |
| Solubility_AqSolDB | Aqueous Solubility | log(mol/L) | 9,982 | AqSolDB |
| PPBR_AZ | Plasma Protein Binding Rate | % | 1,614 | AstraZeneca |
| Caco2_Wang | Caco-2 Permeability | cm/s (log) | 906 | Wang et al. |
| Clearance_Hepatocyte_AZ | Hepatocyte Clearance | uL/min/10^6 cells | 1,020 | AstraZeneca |
| Clearance_Microsome_AZ | Microsome Clearance | uL/min/mg | 1,102 | AstraZeneca |
| VDss_Lombardo | Volume of Distribution | L/kg (log) | 1,111 | Lombardo et al. |
| Half_Life_Obach | Half-Life | hours (log) | 665 | Obach et al. |

Total pool: ~20,600 molecules. 1,100 sampled (1,000 train + 100 test), shuffled with `random_state=42`.

### Property Distribution in Splits

**Train (1,000 tasks):** Aqueous Solubility (463), Lipophilicity (198), Plasma Protein Binding (89), Volume of Distribution (58), Microsome Clearance (57), Caco-2 Permeability (54), Hepatocyte Clearance (47), Half-Life (34).

**Test (100 tasks):** Aqueous Solubility (51), Lipophilicity (13), Plasma Protein Binding (10), Volume of Distribution (6), Microsome Clearance (6), Hepatocyte Clearance (5), Half-Life (5), Caco-2 Permeability (4).

The distribution is proportional to dataset size — solubility dominates because AqSolDB is the largest source.

## Reward Function

Continuous reward in [0, 1] using inverse hyperbolic cosine of the relative error:

```
reward = 1 / cosh(relative_error * 3.0)
```

Where `relative_error = |predicted - actual| / |actual|`.

| Relative Error | Reward |
|---------------|--------|
| 0% (exact) | 1.000 |
| 5% | 0.989 |
| 10% | 0.957 |
| 25% | 0.772 |
| 50% | 0.425 |
| 100% | 0.099 |
| 200% | 0.005 |

For actual values of 0, falls back to absolute error scaling.

## Environment API

- **Splits:** `train` (1,000 tasks), `test` (100 tasks)
- **Tool:** `submit_prediction(prediction: float)` — submit a numerical value
- **Prompt:** Provides SMILES string, property name, and units
- **Finished:** Always `True` after one tool call (single-turn)

## Files

```
admepred/
├── admepred.py        # Environment class (AdmePred)
├── server.py          # Server wrapper
├── test_agent.py      # OpenAI Responses API test harness
├── prepare_data.py    # TDC download + JSON generation script
├── requirements.txt   # openreward, pydantic
├── Dockerfile
├── DATA_UPLOAD.md     # Cloud storage upload instructions
└── data/
    ├── train.json     # 1,000 training tasks
    └── test.json      # 100 test tasks
```

## Local Development

```bash
# Generate data (requires PyTDC)
pip install PyTDC pandas
python prepare_data.py

# Run server
pip install -r requirements.txt
python server.py

# Test with agent
export OPENAI_API_KEY=...
python test_agent.py
```

## Docker

```bash
docker build -t admepred:test .
docker run -p 8080:8080 admepred:test
```
