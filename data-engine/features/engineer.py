"""
Stanleaf Data Engine — Feature Engineering
==========================================
Derives deterministic domain-specific financial, operational, and unit economic
features for Restaurant and E-commerce businesses from validated cleaned metrics.
"""

from typing import Dict, Any, Optional, List
from cleaning.models import CleanedMetric, MetricStatus
from cleaning.validator import normalize_industry_key
from analytics.calculations import safe_divide, calculate_percentage
from .models import DerivedFeature


class FeatureEngineer:
    """
    Computes domain-specific analytical features from cleaned metrics.
    Ensures that missing inputs and zero divisions are handled safely
    without fabricating data.
    """

    @classmethod
    def _get_val(cls, metrics: Dict[str, CleanedMetric], key: str) -> Optional[float]:
        """Safely retrieves a numeric value if the metric is valid."""
        metric = metrics.get(key)
        if metric and metric.status == MetricStatus.VALID and metric.value is not None:
            try:
                return float(metric.value)
            except (ValueError, TypeError):
                return None
        return None

    @classmethod
    def engineer_features(
        cls,
        cleaned_metrics: Dict[str, CleanedMetric],
        industry: str,
    ) -> Dict[str, DerivedFeature]:
        industry_norm = normalize_industry_key(industry)
        features: Dict[str, DerivedFeature] = {}

        # -------------------------------------------------------------
        # 1. Universal Financial Features (Supported across industries)
        # -------------------------------------------------------------
        rev = cls._get_val(cleaned_metrics, "monthly_revenue")
        exp = cls._get_val(cleaned_metrics, "monthly_expenses")

        # Feature: operating_profit
        if rev is not None and exp is not None:
            profit = rev - exp
            features["operating_profit"] = DerivedFeature(
                name="operating_profit",
                value=round(profit, 2),
                unit="₹ / $",
                source_inputs=["monthly_revenue", "monthly_expenses"],
                derivation_rule="monthly_revenue - monthly_expenses",
                status="computed",
                notes="Net monthly operating cash generated before taxes.",
            )
        else:
            features["operating_profit"] = DerivedFeature(
                name="operating_profit",
                value=None,
                unit="₹ / $",
                source_inputs=["monthly_revenue", "monthly_expenses"],
                derivation_rule="monthly_revenue - monthly_expenses",
                status="skipped_missing_input",
                notes="Requires both valid monthly_revenue and monthly_expenses.",
            )

        # Feature: operating_margin
        op_profit_feat = features["operating_profit"]
        if op_profit_feat.value is not None and rev is not None and rev > 0:
            margin = (op_profit_feat.value / rev) * 100.0
            features["operating_margin"] = DerivedFeature(
                name="operating_margin",
                value=round(margin, 2),
                unit="%",
                source_inputs=["operating_profit", "monthly_revenue"],
                derivation_rule="(operating_profit / monthly_revenue) * 100",
                status="computed",
                notes="Operating profitability percentage relative to gross monthly revenue.",
            )
        elif rev is not None and rev <= 0:
            features["operating_margin"] = DerivedFeature(
                name="operating_margin",
                value=None,
                unit="%",
                source_inputs=["operating_profit", "monthly_revenue"],
                derivation_rule="(operating_profit / monthly_revenue) * 100",
                status="skipped_zero_division",
                notes="Cannot divide by zero or non-positive revenue.",
            )
        else:
            features["operating_margin"] = DerivedFeature(
                name="operating_margin",
                value=None,
                unit="%",
                source_inputs=["operating_profit", "monthly_revenue"],
                derivation_rule="(operating_profit / monthly_revenue) * 100",
                status="skipped_missing_input",
                notes="Requires valid operating profit and revenue.",
            )

        # Feature: marketing_spend_ratio
        mktg = cls._get_val(cleaned_metrics, "monthly_marketing_spend")
        if mktg is not None and rev is not None:
            if rev > 0:
                mktg_ratio = (mktg / rev) * 100.0
                features["marketing_spend_ratio"] = DerivedFeature(
                    name="marketing_spend_ratio",
                    value=round(mktg_ratio, 2),
                    unit="%",
                    source_inputs=["monthly_marketing_spend", "monthly_revenue"],
                    derivation_rule="(monthly_marketing_spend / monthly_revenue) * 100",
                    status="computed",
                    notes="Marketing budget intensity relative to total revenue.",
                )
            else:
                features["marketing_spend_ratio"] = DerivedFeature(
                    name="marketing_spend_ratio",
                    value=None,
                    unit="%",
                    source_inputs=["monthly_marketing_spend", "monthly_revenue"],
                    derivation_rule="(monthly_marketing_spend / monthly_revenue) * 100",
                    status="skipped_zero_division",
                    notes="Cannot calculate marketing ratio with zero revenue.",
                )
        else:
            features["marketing_spend_ratio"] = DerivedFeature(
                name="marketing_spend_ratio",
                value=None,
                unit="%",
                source_inputs=["monthly_marketing_spend", "monthly_revenue"],
                derivation_rule="(monthly_marketing_spend / monthly_revenue) * 100",
                status="skipped_missing_input",
                notes="Requires valid marketing spend and revenue.",
            )

        # Feature: calculated_average_order_value (calculated vs reported AOV)
        orders = cls._get_val(cleaned_metrics, "monthly_orders")
        if rev is not None and orders is not None:
            if orders > 0:
                calc_aov = rev / orders
                features["calculated_average_order_value"] = DerivedFeature(
                    name="calculated_average_order_value",
                    value=round(calc_aov, 2),
                    unit="₹ / $ / order",
                    source_inputs=["monthly_revenue", "monthly_orders"],
                    derivation_rule="monthly_revenue / monthly_orders",
                    status="computed",
                    notes="Empirically calculated ticket size per order transaction.",
                )
            else:
                features["calculated_average_order_value"] = DerivedFeature(
                    name="calculated_average_order_value",
                    value=None,
                    unit="₹ / $ / order",
                    source_inputs=["monthly_revenue", "monthly_orders"],
                    derivation_rule="monthly_revenue / monthly_orders",
                    status="skipped_zero_division",
                    notes="Monthly order volume is zero.",
                )
        else:
            features["calculated_average_order_value"] = DerivedFeature(
                name="calculated_average_order_value",
                value=None,
                unit="₹ / $ / order",
                source_inputs=["monthly_revenue", "monthly_orders"],
                derivation_rule="monthly_revenue / monthly_orders",
                status="skipped_missing_input",
                notes="Requires monthly revenue and monthly orders.",
            )

        # -------------------------------------------------------------
        # 2. Industry-Specific Feature Derivation
        # -------------------------------------------------------------
        if industry_norm == "restaurant":
            # Feature: revenue_per_employee
            emp = cls._get_val(cleaned_metrics, "employee_count")
            if rev is not None and emp is not None:
                if emp > 0:
                    features["revenue_per_employee"] = DerivedFeature(
                        name="revenue_per_employee",
                        value=round(rev / emp, 2),
                        unit="₹ / $ / employee",
                        source_inputs=["monthly_revenue", "employee_count"],
                        derivation_rule="monthly_revenue / employee_count",
                        status="computed",
                        notes="Labor productivity metric.",
                    )
                else:
                    features["revenue_per_employee"] = DerivedFeature(
                        name="revenue_per_employee",
                        value=None,
                        unit="₹ / $ / employee",
                        source_inputs=["monthly_revenue", "employee_count"],
                        derivation_rule="monthly_revenue / employee_count",
                        status="skipped_zero_division",
                        notes="Employee count is zero.",
                    )
            else:
                features["revenue_per_employee"] = DerivedFeature(
                    name="revenue_per_employee",
                    value=None,
                    unit="₹ / $ / employee",
                    source_inputs=["monthly_revenue", "employee_count"],
                    derivation_rule="monthly_revenue / employee_count",
                    status="skipped_missing_input",
                )

            # Feature: revenue_per_customer
            cust = cls._get_val(cleaned_metrics, "monthly_customers")
            if rev is not None and cust is not None:
                if cust > 0:
                    features["revenue_per_customer"] = DerivedFeature(
                        name="revenue_per_customer",
                        value=round(rev / cust, 2),
                        unit="₹ / $ / customer",
                        source_inputs=["monthly_revenue", "monthly_customers"],
                        derivation_rule="monthly_revenue / monthly_customers",
                        status="computed",
                        notes="Average spend per dining customer/cover.",
                    )
                else:
                    features["revenue_per_customer"] = DerivedFeature(
                        name="revenue_per_customer",
                        value=None,
                        unit="₹ / $ / customer",
                        source_inputs=["monthly_revenue", "monthly_customers"],
                        derivation_rule="monthly_revenue / monthly_customers",
                        status="skipped_zero_division",
                    )
            else:
                features["revenue_per_customer"] = DerivedFeature(
                    name="revenue_per_customer",
                    value=None,
                    unit="₹ / $ / customer",
                    source_inputs=["monthly_revenue", "monthly_customers"],
                    derivation_rule="monthly_revenue / monthly_customers",
                    status="skipped_missing_input",
                )

            # Feature: orders_per_customer
            if orders is not None and cust is not None:
                if cust > 0:
                    features["orders_per_customer"] = DerivedFeature(
                        name="orders_per_customer",
                        value=round(orders / cust, 3),
                        unit="orders / customer",
                        source_inputs=["monthly_orders", "monthly_customers"],
                        derivation_rule="monthly_orders / monthly_customers",
                        status="computed",
                        notes="Order frequency ratio per customer cover.",
                    )
                else:
                    features["orders_per_customer"] = DerivedFeature(
                        name="orders_per_customer",
                        value=None,
                        unit="orders / customer",
                        source_inputs=["monthly_orders", "monthly_customers"],
                        derivation_rule="monthly_orders / monthly_customers",
                        status="skipped_zero_division",
                    )
            else:
                features["orders_per_customer"] = DerivedFeature(
                    name="orders_per_customer",
                    value=None,
                    unit="orders / customer",
                    source_inputs=["monthly_orders", "monthly_customers"],
                    derivation_rule="monthly_orders / monthly_customers",
                    status="skipped_missing_input",
                )

            # Feature: revenue_per_table (Optional metric table_count)
            tables = cls._get_val(cleaned_metrics, "table_count")
            if rev is not None and tables is not None:
                if tables > 0:
                    features["revenue_per_table"] = DerivedFeature(
                        name="revenue_per_table",
                        value=round(rev / tables, 2),
                        unit="₹ / $ / table",
                        source_inputs=["monthly_revenue", "table_count"],
                        derivation_rule="monthly_revenue / table_count",
                        status="computed",
                        notes="Table yield / physical seating efficiency.",
                    )
                else:
                    features["revenue_per_table"] = DerivedFeature(
                        name="revenue_per_table",
                        value=None,
                        unit="₹ / $ / table",
                        source_inputs=["monthly_revenue", "table_count"],
                        derivation_rule="monthly_revenue / table_count",
                        status="skipped_zero_division",
                    )
            else:
                features["revenue_per_table"] = DerivedFeature(
                    name="revenue_per_table",
                    value=None,
                    unit="₹ / $ / table",
                    source_inputs=["monthly_revenue", "table_count"],
                    derivation_rule="monthly_revenue / table_count",
                    status="skipped_missing_input",
                    notes="Optional table_count was not provided.",
                )

            # Feature: labor_intensity
            if cust is not None and emp is not None:
                if emp > 0:
                    features["labor_intensity"] = DerivedFeature(
                        name="labor_intensity",
                        value=round(cust / emp, 1),
                        unit="customers / employee",
                        source_inputs=["monthly_customers", "employee_count"],
                        derivation_rule="monthly_customers / employee_count",
                        status="computed",
                        notes="Staff customer servicing capacity ratio.",
                    )
                else:
                    features["labor_intensity"] = DerivedFeature(
                        name="labor_intensity",
                        value=None,
                        unit="customers / employee",
                        source_inputs=["monthly_customers", "employee_count"],
                        derivation_rule="monthly_customers / employee_count",
                        status="skipped_zero_division",
                    )
            else:
                features["labor_intensity"] = DerivedFeature(
                    name="labor_intensity",
                    value=None,
                    unit="customers / employee",
                    source_inputs=["monthly_customers", "employee_count"],
                    derivation_rule="monthly_customers / employee_count",
                    status="skipped_missing_input",
                )

        elif industry_norm == "ecommerce":
            # Feature: revenue_per_visitor
            traffic = cls._get_val(cleaned_metrics, "monthly_website_traffic")
            if rev is not None and traffic is not None:
                if traffic > 0:
                    features["revenue_per_visitor"] = DerivedFeature(
                        name="revenue_per_visitor",
                        value=round(rev / traffic, 2),
                        unit="₹ / $ / visitor",
                        source_inputs=["monthly_revenue", "monthly_website_traffic"],
                        derivation_rule="monthly_revenue / monthly_website_traffic",
                        status="computed",
                        notes="Average revenue generated per storefront visitor session.",
                    )
                else:
                    features["revenue_per_visitor"] = DerivedFeature(
                        name="revenue_per_visitor",
                        value=None,
                        unit="₹ / $ / visitor",
                        source_inputs=["monthly_revenue", "monthly_website_traffic"],
                        derivation_rule="monthly_revenue / monthly_website_traffic",
                        status="skipped_zero_division",
                    )
            else:
                features["revenue_per_visitor"] = DerivedFeature(
                    name="revenue_per_visitor",
                    value=None,
                    unit="₹ / $ / visitor",
                    source_inputs=["monthly_revenue", "monthly_website_traffic"],
                    derivation_rule="monthly_revenue / monthly_website_traffic",
                    status="skipped_missing_input",
                )

            # Feature: orders_per_visitor (Empirical conversion check)
            if orders is not None and traffic is not None:
                if traffic > 0:
                    features["orders_per_visitor"] = DerivedFeature(
                        name="orders_per_visitor",
                        value=round(orders / traffic, 4),
                        unit="orders / visitor",
                        source_inputs=["monthly_orders", "monthly_website_traffic"],
                        derivation_rule="monthly_orders / monthly_website_traffic",
                        status="computed",
                        notes="Empirical order completion rate per storefront visitor.",
                    )
                else:
                    features["orders_per_visitor"] = DerivedFeature(
                        name="orders_per_visitor",
                        value=None,
                        unit="orders / visitor",
                        source_inputs=["monthly_orders", "monthly_website_traffic"],
                        derivation_rule="monthly_orders / monthly_website_traffic",
                        status="skipped_zero_division",
                    )
            else:
                features["orders_per_visitor"] = DerivedFeature(
                    name="orders_per_visitor",
                    value=None,
                    unit="orders / visitor",
                    source_inputs=["monthly_orders", "monthly_website_traffic"],
                    derivation_rule="monthly_orders / monthly_website_traffic",
                    status="skipped_missing_input",
                )

            # Feature: cac_to_aov_ratio (Optional CAC)
            cac = cls._get_val(cleaned_metrics, "customer_acquisition_cost")
            reported_aov = cls._get_val(cleaned_metrics, "reported_average_order_value")
            # fallback to calculated AOV if reported AOV is not available
            target_aov = reported_aov if reported_aov is not None else (
                features["calculated_average_order_value"].value
                if "calculated_average_order_value" in features
                else None
            )

            if cac is not None and target_aov is not None:
                if target_aov > 0:
                    features["cac_to_aov_ratio"] = DerivedFeature(
                        name="cac_to_aov_ratio",
                        value=round(cac / target_aov, 3),
                        unit="ratio",
                        source_inputs=["customer_acquisition_cost", "reported_average_order_value"],
                        derivation_rule="customer_acquisition_cost / average_order_value",
                        status="computed",
                        notes="CAC to ticket size ratio. Ratios < 1.0 indicate immediate first-order unit payback.",
                    )
                else:
                    features["cac_to_aov_ratio"] = DerivedFeature(
                        name="cac_to_aov_ratio",
                        value=None,
                        unit="ratio",
                        source_inputs=["customer_acquisition_cost", "reported_average_order_value"],
                        derivation_rule="customer_acquisition_cost / average_order_value",
                        status="skipped_zero_division",
                    )
            else:
                features["cac_to_aov_ratio"] = DerivedFeature(
                    name="cac_to_aov_ratio",
                    value=None,
                    unit="ratio",
                    source_inputs=["customer_acquisition_cost", "reported_average_order_value"],
                    derivation_rule="customer_acquisition_cost / average_order_value",
                    status="skipped_missing_input",
                    notes="Optional customer_acquisition_cost was not provided.",
                )

            # Feature: effective_return_impact
            ret_rate = cls._get_val(cleaned_metrics, "return_rate_percentage")
            if rev is not None and ret_rate is not None:
                ret_impact = rev * (ret_rate / 100.0)
                features["effective_return_impact"] = DerivedFeature(
                    name="effective_return_impact",
                    value=round(ret_impact, 2),
                    unit="₹ / $",
                    source_inputs=["monthly_revenue", "return_rate_percentage"],
                    derivation_rule="monthly_revenue * (return_rate_percentage / 100.0)",
                    status="computed",
                    notes="Estimated gross merchandise value lost to product refunds/returns.",
                )
            else:
                features["effective_return_impact"] = DerivedFeature(
                    name="effective_return_impact",
                    value=None,
                    unit="₹ / $",
                    source_inputs=["monthly_revenue", "return_rate_percentage"],
                    derivation_rule="monthly_revenue * (return_rate_percentage / 100.0)",
                    status="skipped_missing_input",
                )

        return features
