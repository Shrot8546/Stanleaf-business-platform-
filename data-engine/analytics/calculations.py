"""
Stanleaf Data Engine — Analytics Calculations
=============================================
Provides reusable, deterministic descriptive calculations, safe division,
and analytical helpers with robust edge-case handling (division by zero,
null values, and period compatibility).
"""

from typing import Optional, Union, Tuple
import math


def safe_divide(
    numerator: Optional[Union[int, float]],
    denominator: Optional[Union[int, float]],
    default: Optional[float] = None,
) -> Optional[float]:
    """
    Safely divides numerator by denominator.
    Returns `default` if either input is None, if denominator is zero,
    or if the result would be NaN or Infinite.
    """
    if numerator is None or denominator is None:
        return default

    try:
        num = float(numerator)
        den = float(denominator)
    except (ValueError, TypeError):
        return default

    if math.isnan(num) or math.isnan(den) or math.isinf(num) or math.isinf(den):
        return default

    if abs(den) < 1e-12:
        return default

    result = num / den
    if math.isnan(result) or math.isinf(result):
        return default

    return result


def calculate_percentage(
    part: Optional[Union[int, float]],
    whole: Optional[Union[int, float]],
    default: Optional[float] = None,
) -> Optional[float]:
    """
    Calculates percentage (part / whole * 100).
    Safely handles zero denominator and missing values.
    """
    ratio = safe_divide(part, whole, default=None)
    if ratio is None:
        return default
    return ratio * 100.0


def calculate_variance(
    actual: Optional[Union[int, float]],
    baseline: Optional[Union[int, float]],
    default: Optional[float] = None,
) -> Optional[float]:
    """
    Calculates percentage variance: ((actual - baseline) / baseline) * 100.
    """
    if actual is None or baseline is None:
        return default
    try:
        diff = float(actual) - float(baseline)
        return calculate_percentage(diff, baseline, default=default)
    except (ValueError, TypeError):
        return default


def is_within_bounds(
    value: Optional[Union[int, float]],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
) -> bool:
    """
    Checks if a numeric value falls within specified [min_value, max_value] bounds.
    """
    if value is None:
        return False
    try:
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return False
        if min_value is not None and val < float(min_value):
            return False
        if max_value is not None and val > float(max_value):
            return False
        return True
    except (ValueError, TypeError):
        return False


def check_period_compatibility(
    period_a: Optional[str],
    period_b: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """
    Validates whether two reporting periods are compatible for combined calculations.
    Returns (is_compatible, explanation).
    
    Standard supported periods: 'monthly', 'annual', 'quarterly', 'cumulative', 'instantaneous'.
    """
    if not period_a or not period_b:
        # If either period is unspecified, we assume default monthly compatibility with warning
        return True, None

    p_a = period_a.strip().lower()
    p_b = period_b.strip().lower()

    if p_a == p_b:
        return True, None

    # Instantaneous/cumulative metrics (e.g. employee_count, table_count) are compatible with periodic flows
    instantaneous_periods = {"instantaneous", "point_in_time", "cumulative", "snapshot"}
    if p_a in instantaneous_periods or p_b in instantaneous_periods:
        return True, None

    return False, f"Incompatible reporting periods: '{period_a}' and '{period_b}' cannot be directly combined."
