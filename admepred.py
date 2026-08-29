"""
AdmePred - ADME Property Prediction Environment

Single-turn environment where agents predict ADME (Absorption, Distribution,
Metabolism, Excretion) property values for molecules given their SMILES notation.

Covers multiple ADME endpoints: Caco-2 permeability, lipophilicity (LogP),
aqueous solubility, plasma protein binding, clearance, volume of distribution,
and half-life.

Continuous reward based on relative prediction error using 1/cosh scaling.
"""

import json
import math
import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from openreward.environments import (
    Environment,
    JSONObject,
    Split,
    TextBlock,
    ToolOutput,
    tool,
)

# Reward for a submission made after the task has already been graded. Negative
# so repeat submissions are actively discouraged, not merely left unscored.
REPEAT_SUBMISSION_PENALTY = -0.1

# Path handling (production vs local development)
if os.path.exists("/orwd_data"):
    ENV_PATH = Path("/orwd_data")
else:
    ENV_PATH = Path(__file__).parent


def load_all_tasks() -> dict[str, list[dict]]:
    """Load tasks from JSON at module import time."""
    data_dir = ENV_PATH / "data"
    all_tasks = {}
    for split in ["train", "test"]:
        json_file = data_dir / f"{split}.json"
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                all_tasks[split] = json.load(f)
        else:
            print(f"Warning: {json_file} not found")
            all_tasks[split] = []
    return all_tasks


ALL_TASKS = load_all_tasks()

ANSWERS = {
    task["task_id"]: {"value": task["answer"]}
    for split_tasks in ALL_TASKS.values()
    for task in split_tasks
}

print(f"Loaded {len(ANSWERS)} AdmePred tasks")


class AdmePredTaskSpec(BaseModel):
    task_id: str
    smiles: str
    property_name: str
    property_units: str
    question: str


class SubmitPredictionInput(BaseModel):
    prediction: float = Field(
        ..., description="Your predicted numerical value for the ADME property"
    )


class AdmePred(Environment):
    """
    ADME property prediction environment.

    Agents predict numerical ADME property values for molecules.
    Reward is continuous in [0, 1] based on relative prediction accuracy.
    """

    def __init__(self, task_spec: JSONObject, secrets: dict[str, str] = {}) -> None:
        super().__init__(task_spec)
        self.validated = AdmePredTaskSpec.model_validate(task_spec)

        if self.validated.task_id not in ANSWERS:
            raise ValueError(f"Task {self.validated.task_id} not found in ANSWERS")

        self.answer = ANSWERS[self.validated.task_id]

        # Graded submissions this session. Only the first is rewarded: the
        # reward is a smooth function of |predicted - actual| reported back to
        # 4dp, so repeated probing recovers the target value.
        self.submitted = 0

    @classmethod
    def list_splits(cls) -> list[Split]:
        return [
            Split(name="train", type="train"),
            Split(name="test", type="test"),
        ]

    @classmethod
    def list_tasks(cls, split: str) -> list[JSONObject]:
        if split not in ALL_TASKS:
            return []
        return [
            {k: v for k, v in task.items() if k != "answer"}
            for task in ALL_TASKS[split]
        ]

    async def get_prompt(self) -> List[TextBlock]:
        return [TextBlock(text=self.validated.question)]

    @tool
    async def submit_prediction(self, params: SubmitPredictionInput) -> ToolOutput:
        """Submit your predicted ADME property value for the molecule."""
        if self.submitted > 0:
            return ToolOutput(
                blocks=[TextBlock(text="A prediction has already been submitted for this task. "
                                       "This episode is over: it is not re-graded, and repeat "
                                       "submissions are penalised (reward -0.1).")],
                metadata={"already_submitted": True, "submission_count": self.submitted},
                reward=REPEAT_SUBMISSION_PENALTY,
                finished=True,
            )

        predicted = params.prediction
        actual = self.answer["value"]
        reward = self._compute_reward(predicted, actual)

        feedback = (
            f"Prediction: {predicted:.4f}\n"
            f"Reward: {reward:.4f}\n\n"
            f"Property: {self.validated.property_name} ({self.validated.property_units})"
        )

        self.submitted += 1

        return ToolOutput(
            blocks=[TextBlock(text=feedback)],
            metadata={
                "task_id": self.validated.task_id,
                "smiles": self.validated.smiles,
                "property_name": self.validated.property_name,
                "predicted": predicted,
                "actual": actual,
                "reward": reward,
            },
            reward=reward,
            finished=True,
        )

    def _compute_reward(self, predicted: float, actual: float) -> float:
        """Continuous reward in [0, 1] based on relative closeness.

        Uses 1/cosh(relative_error * scale) for smooth decay:
        - ~10% error -> reward ~0.95
        - ~50% error -> reward ~0.64
        - 100% error -> reward ~0.27
        - 200% error -> reward ~0.07
        """
        if actual == 0:
            abs_err = abs(predicted - actual)
            return max(0.0, 1.0 / math.cosh(abs_err * 3.0))

        rel_error = abs(predicted - actual) / abs(actual)
        scale = 3.0
        reward = 1.0 / math.cosh(rel_error * scale)
        return round(reward, 4)
