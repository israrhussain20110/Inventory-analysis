import os
import sys
import json
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import calculations

REPORTS_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_reports():
    """
    Generates all the reports and saves them to the reporting directory.
    """
    print("Generating reports...")

    # Generate inventory metrics report
    days_of_supply_data = calculations.calculate_days_of_supply()
    avg_days_of_supply = pd.DataFrame(days_of_supply_data)['days_of_supply'].mean()

    carrying_cost_data = calculations.calculate_carrying_cost()
    avg_carrying_cost = pd.DataFrame(carrying_cost_data)['carrying_cost'].mean()

    inventory_metrics = {
        "turnover": calculations.calculate_turnover(),
        "stockout_rate": calculations.calculate_stockout_rate(),
        "days_of_supply": {"days_of_supply": avg_days_of_supply},
        "carrying_cost": {"carrying_cost": avg_carrying_cost},
    }
    with open(os.path.join(REPORTS_DIR, "inventory_metrics.json"), "w") as f:
        json.dump(inventory_metrics, f, indent=4)

    # Generate slow movers report
    slow_movers = calculations.detect_slow_obsolete_items()
    with open(os.path.join(REPORTS_DIR, "slow_movers.json"), "w") as f:
        json.dump(slow_movers, f, indent=4)

    # Generate stockout heatmap report
    stockout_heatmap = calculations.calculate_stockout_heatmap_data()
    with open(os.path.join(REPORTS_DIR, "stockout_heatmap.json"), "w") as f:
        json.dump(stockout_heatmap, f, indent=4)

    print("Reports generated successfully.")

if __name__ == "__main__":
    generate_reports()
