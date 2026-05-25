import json
from collections import Counter
from pathlib import Path


def count_alert_labels(records):
    counter = Counter()
    for record in records:
        alerts_text = record.get("alerts_json") or "[]"
        try:
            alerts = json.loads(alerts_text)
        except json.JSONDecodeError:
            alerts = []
        for label in alerts:
            counter[label] += 1
    return counter


def export_alert_chart(records, output_path):
    """Export a simple bar chart for alert statistics."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for chart export.") from exc

    counts = count_alert_labels(records)
    labels = ["phone", "sleep", "eat"]
    values = [counts.get(label, 0) for label in labels]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["#2ca02c", "#1f77b4", "#ff7f0e"])
    plt.title("Study Behavior Alert Statistics")
    plt.xlabel("Behavior")
    plt.ylabel("Alert Count")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()
    return output
