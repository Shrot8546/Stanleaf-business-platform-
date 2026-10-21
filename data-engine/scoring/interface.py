"""
Stanleaf Data Engine — Scoring Interface (Reserved for Step 5)
=============================================================
Defines the abstract interface for the future explainable Business Health Score
evaluation engine.

NOTE: Per architecture specifications, no score formula or synthetic score
is implemented in Step 4. This interface will be realized in Step 5.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseScoringEngine(ABC):
    """
    Abstract contract for explainable scoring implementations.
    Strictly reserved for Step 5: Business Health Score Formula.
    """

    @abstractmethod
    def evaluate(self, pipeline_output: Any) -> Dict[str, Any]:
        """
        Calculates domain-explainable health scores from validated pipeline features.
        Must be implemented in Step 5.
        """
        raise NotImplementedError(
            "Scoring engine evaluation is reserved for Step 5. "
            "No score formula or fabricated scores are permitted in Step 4."
        )
