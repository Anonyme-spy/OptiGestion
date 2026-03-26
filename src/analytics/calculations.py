# src/analytics/calculations.py
"""
Analytical calculations for profitability, break-even, scenario analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

from .data_manager import DataManager

class AnalyticsEngine:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    # -------------------------------------------------------------------------
    # Product profitability
    # -------------------------------------------------------------------------
    def product_profitability(self) -> pd.DataFrame:
        """
        Return a DataFrame with per-product profitability:
        revenue, cost, profit, margin %
        """
        products = self.dm.get_table_as_df('products')
        costs = self.dm.get_table_as_df('costs')
        # Merge on product_id (products.product_id)
        merged = pd.merge(products, costs, on='product_id', how='left')
        # Fill missing costs with 0
        merged.fillna(0, inplace=True)
        # Calculate revenue (selling_price * quantity sold) – but we need volumes
        # For simplicity, we'll use the latest period volumes. Let's get volumes.
        volumes = self.dm.get_table_as_df('volumes')
        # Aggregate volumes by product: we can use the latest period or sum? Here we'll use sum for simplicity.
        vol_sum = volumes.groupby('product_id').agg({'sold': 'sum'}).reset_index()
        merged = pd.merge(merged, vol_sum, on='product_id', how='left')
        merged.fillna(0, inplace=True)
        # Revenue
        merged['revenue'] = merged['selling_price'] * merged['sold']
        # Total cost = fixed_costs + variable_costs * quantity (plus labor, raw materials)
        # But we have separate cost components. For now, assume total cost = fixed + variable * quantity.
        # We'll use variable_costs as unit variable cost.
        merged['total_cost'] = merged['fixed_costs'] + merged['variable_costs'] * merged['sold']
        # Profit
        merged['profit'] = merged['revenue'] - merged['total_cost']
        # Margin %
        merged['margin_percent'] = (merged['profit'] / merged['revenue']) * 100
        # Select relevant columns
        result = merged[['product_id', 'name', 'category', 'sold', 'revenue', 'total_cost', 'profit', 'margin_percent']]
        return result

    # -------------------------------------------------------------------------
    # Break-even analysis
    # -------------------------------------------------------------------------
    def break_even_analysis(self) -> Dict[str, Any]:
        """
        Compute global break-even point.
        Returns dict with break-even units, revenue, and margin per unit.
        """
        products = self.dm.get_table_as_df('products')
        costs = self.dm.get_table_as_df('costs')
        # Get total fixed costs
        total_fixed = costs['fixed_costs'].sum()
        # Average selling price and variable cost (weighted by volume?)
        # For simplicity, use average across products
        avg_price = products['selling_price'].mean()
        avg_variable = costs['variable_costs'].mean()
        margin_per_unit = avg_price - avg_variable
        if margin_per_unit <= 0:
            return {'error': 'Margin per unit is zero or negative'}
        be_units = total_fixed / margin_per_unit
        be_revenue = be_units * avg_price
        return {
            'break_even_units': be_units,
            'break_even_revenue': be_revenue,
            'margin_per_unit': margin_per_unit,
            'total_fixed_costs': total_fixed
        }

    # -------------------------------------------------------------------------
    # Company summary
    # -------------------------------------------------------------------------
    def company_summary(self) -> Dict[str, Any]:
        """
        Overall company metrics: total revenue, total cost, net profit, average margin.
        """
        prod_profit = self.product_profitability()
        total_revenue = prod_profit['revenue'].sum()
        total_cost = prod_profit['total_cost'].sum()
        net_profit = total_revenue - total_cost
        avg_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'average_margin_percent': avg_margin
        }

    # -------------------------------------------------------------------------
    # Scenario analysis
    # -------------------------------------------------------------------------
    def apply_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """
        Apply a scenario template to current data and return new metrics.
        """
        scenarios = self.dm.get_table_as_df('scenario_templates')
        scenario = scenarios[scenarios['id'] == scenario_id]
        if scenario.empty:
            raise ValueError(f"Scenario {scenario_id} not found")
        sales_change = scenario.iloc[0]['sales_change'] / 100
        cost_change = scenario.iloc[0]['cost_change'] / 100

        # Adjust product selling prices and costs
        products = self.dm.get_table_as_df('products').copy()
        costs = self.dm.get_table_as_df('costs').copy()
        # New selling price
        products['new_selling_price'] = products['selling_price'] * (1 + sales_change)
        # New variable costs
        costs['new_variable_costs'] = costs['variable_costs'] * (1 + cost_change)

        # Recalculate profitability
        volumes = self.dm.get_table_as_df('volumes')
        vol_sum = volumes.groupby('product_id')['sold'].sum().reset_index()
        merged = pd.merge(products, costs, on='product_id', how='left')
        merged = pd.merge(merged, vol_sum, on='product_id', how='left')
        merged.fillna(0, inplace=True)
        merged['revenue'] = merged['new_selling_price'] * merged['sold']
        merged['total_cost'] = merged['fixed_costs'] + merged['new_variable_costs'] * merged['sold']
        merged['profit'] = merged['revenue'] - merged['total_cost']

        total_revenue = merged['revenue'].sum()
        total_cost = merged['total_cost'].sum()
        net_profit = total_revenue - total_cost
        return {
            'scenario_name': scenario.iloc[0]['name'],
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'profit_change_percent': ((net_profit - self.company_summary()['net_profit']) / self.company_summary()['net_profit']) * 100 if self.company_summary()['net_profit'] != 0 else 0
        }

    # -------------------------------------------------------------------------
    # Time series for volumes
    # -------------------------------------------------------------------------
    def volume_trends(self, product_id: Optional[str] = None) -> pd.DataFrame:
        """
        Return volume trends (produced and sold) over time.
        If product_id is None, return aggregated by period.
        """
        volumes = self.dm.get_table_as_df('volumes')
        if product_id:
            volumes = volumes[volumes['product_id'] == product_id]
        # Aggregate by period (sum over products if product_id is None)
        if product_id is None:
            trend = volumes.groupby('period').agg({'produced': 'sum', 'sold': 'sum'}).reset_index()
        else:
            trend = volumes[['period', 'produced', 'sold']].copy()
        return trend