"""
Stanleaf Data Engine
====================
Core Data Science & Big Data Analytics engine for Stanleaf.

Pipeline Architecture:
1. Ingestion: Ingests raw public business data and owner-uploaded records.
2. Cleaning: Cleans, deduplicates, and sanitizes input data.
3. Features: Computes financial, operational, and benchmark feature representations.
4. Analytics: Aggregates industry cohorts, calculates percentiles, and generates benchmark distributions.
5. Scoring: Evaluates health score metrics across financial, operational, and market risk dimensions.
"""

__version__ = "0.1.0"
