# ADME

[![OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/GeneralReasoning/ADME)

## Description

**ADME** is an environment for evaluating agents on ADME (Absorption, Distribution, Metabolism, Excretion) property prediction. Given a molecule's SMILES string and an ADME endpoint name, agents predict the numerical property value. The dataset pools 8 ADME regression datasets from [Therapeutics Data Commons (TDC)](https://tdcommons.ai/), covering Caco-2 permeability, lipophilicity, aqueous solubility, plasma protein binding, clearance, volume of distribution, and half-life.

## Capabilities

- Predicting diverse ADME molecular properties from SMILES notation
- Quantitative molecular property prediction across multiple endpoints
- Understanding structure-property relationships in pharmacokinetics

## Compute Requirements

ADME does not require a sandbox. It has minimal compute requirements.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (following the TDC dataset licenses).

## Tasks

There are two splits: train (1,000 tasks) and test (100 tasks), totaling 1,100 tasks. Tasks are sampled proportionally from 8 TDC ADME regression datasets:

| Dataset | Property | Units | Molecules | Source |
|---------|----------|-------|-----------|--------|
| Lipophilicity_AstraZeneca | Lipophilicity | LogP | 4,200 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#lipophilicity-astrazeneca) |
| Solubility_AqSolDB | Aqueous Solubility | log(mol/L) | 9,982 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#solubility-aqsoldb) |
| PPBR_AZ | Plasma Protein Binding Rate | % | 2,828 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#ppbr-az) |
| Caco2_Wang | Caco-2 Permeability | log cm/s | 910 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#caco-2-wang) |
| Clearance_Hepatocyte_AZ | Hepatocyte Clearance | uL/min/10^6 cells | 1,213 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#clearance-hepatocyte-az) |
| Clearance_Microsome_AZ | Microsome Clearance | uL/min/mg | 1,102 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#clearance-microsome-az) |
| VDss_Lombardo | Volume of Distribution | L/kg | 1,130 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#vdss-lombardo) |
| Half_Life_Obach | Half-Life | hr | 667 | [TDC](https://tdcommons.ai/single_pred_tasks/adme/#half-life-obach) |

Each task provides a molecule's SMILES string, the property name, and the expected units.

## Reward Structure

This is a sparse, verifiable reward environment with continuous scoring. The agent calls `submit_prediction` once with a predicted value. The reward is based on relative error using inverse hyperbolic cosine scaling:

$$\text{Reward} = \frac{1}{\cosh(\text{relative\_error} \times 3.0)}$$

where $\text{relative\_error} = \frac{|\hat{y} - y|}{|y|}$.

| Relative Error | Reward |
|---------------|--------|
| 0% (exact) | 1.000 |
| 10% | 0.957 |
| 50% | 0.425 |
| 100% | 0.099 |

For actual values of 0, the reward falls back to absolute error scaling.

We do not use LLM graders for this task.

## Data

Task data is pooled from 8 [TDC ADME](https://tdcommons.ai/single_pred_tasks/adme/) regression datasets (~22,000 molecules total). 1,100 molecules are sampled proportionally across datasets. Data files are stored on the OpenReward platform.

## Tools

Agents are given a single tool:

- `submit_prediction`: Submit a predicted numerical value for the ADME property. Returns the reward based on prediction accuracy. This tool can only be called once per task.

## Time Horizon

ADME is a single-turn environment. The agent receives a molecule and property endpoint, then submits one prediction. Each task requires exactly one tool call.

## Environment Difficulty

[Fill in: baseline model performance, human expert comparison, variance across property types]

## Other Environment Requirements

There are no further environment requirements; ADME works out of the box with the OpenReward endpoint.

## Safety

Agents in ADME are asked to predict pharmacokinetic properties for molecules. The environment does not present direct safety risks, as agents only provide numerical predictions with no access to external systems or real pharmacological processes.

However, this is a dual-use domain and models trained for capabilities in this environment could be used for malicious uses in other agentic workflows.

## Citations

```bibtex
@dataset{GRADME,
  author    = {General Reasoning Inc. Team},
  title     = {ADME},
  year      = {2026},
  publisher = {OpenReward},
  url       = {https://openreward.ai/GeneralReasoning/ADME}
}

@article{huang2021therapeutics,
  title={Therapeutics Data Commons: Machine learning datasets and tasks for drug discovery and development},
  author={Huang, Kexin and Fu, Tianfan and Gao, Wenhao and Zhao, Yue and Roohani, Yusuf and Leskovec, Jure and Coley, Connor W and Xiao, Cao and Sun, Jimeng and Zitnik, Marinka},
  journal={Proceedings of NeurIPS Datasets and Benchmarks},
  year={2021}
}
```
