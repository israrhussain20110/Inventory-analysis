import os
import json
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

REPORTS_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def dashboard():
    """
    Renders the reporting dashboard.
    """
    # Load the reports from the JSON files
    with open(os.path.join(REPORTS_DIR, "inventory_metrics.json"), "r") as f:
        inventory_metrics = json.load(f)

    with open(os.path.join(REPORTS_DIR, "slow_movers.json"), "r") as f:
        slow_movers = json.load(f)

    with open(os.path.join(REPORTS_DIR, "stockout_heatmap.json"), "r") as f:
        stockout_heatmap = json.load(f)

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html",
        inventory_metrics=inventory_metrics,
        slow_movers=slow_movers,
        stockout_heatmap=stockout_heatmap,
        last_updated=last_updated,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001)
