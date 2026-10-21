"""
Stanleaf Data Engine — Analytics Subpackage
==========================================
Provides reusable descriptive calculations and aggregation helpers.
"""

from .calculations import (
    safe_divide,
    calculate_percentage,
    calculate_variance,
    is_within_bounds,
    check_period_compatibility,
)

__all__ = [
    "safe_divide",
    "calculate_percentage",
    "calculate_variance",
    "is_within_bounds",
    "check_period_compatibility",
]
