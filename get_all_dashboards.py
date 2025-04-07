"""
Author: Aleksandro Matejic, 2025
Description:
This script fetches all dashboards from a specified Grafana instance and extracts any PromQL queries found within them.
It saves the raw dashboards as JSON files and writes all PromQL queries to a separate text file. You can optionally filter queries by a specific metric name.

Requirements:

The following environment variables must be set:
        •	GRAFANA_URL: The URL of your Grafana instance (e.g., http://localhost:3000)
        •	GRAFANA_SESSION_COOKIE: The Grafana session cookie used for authentication

Why use this?

You might wonder why you’d want to extract all queries from Grafana. In my case, I needed to compare the PromQL queries used in dashboards with the results from the Prometheus promtool CLI.
The goal was to remove high-cardinality metrics and labels to reduce memory usage — but without breaking anything used in dashboards.

usage: python get_all_dashboards.py
"""

import json
import os

import requests

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_SESSION_COOKIE = os.getenv("GRAFANA_SESSION_COOKIE")

DASHBOARDS_FILE = "dashboards.json"
SPECIFIC_METRIC = "specific_metric.json"
OUTPUT_DIR = "grafana_dashboards"
QUERY_FILE = "grafana_promql_queries.txt"

headers = {"Cookie": f"grafana_session={GRAFANA_SESSION_COOKIE}"}


def load_dashboard_metadata():
    with open(DASHBOARDS_FILE, "r") as f:
        return json.load(f)


def fetch_dashboard(uid):
    url = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/uid/{uid}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def extract_queries(dashboard_json):
    queries = []
    panels = dashboard_json.get("dashboard", {}).get("panels", [])
    for panel in panels:
        targets = panel.get("targets", [])
        for target in targets:
            expr = target.get("expr")
            if expr:
                # include the dashboard title
                title = dashboard_json["dashboard"]["title"]
                queries.append(f"{title}: {expr}")
    return queries


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_queries = []
    dashboards = load_dashboard_metadata()

    for dash in dashboards:
        uid = dash["uid"]
        title = dash["title"]
        print(f"Fetching dashboard: {title} (UID: {uid})")

        try:
            dashboard_json = fetch_dashboard(uid)
            with open(f"{OUTPUT_DIR}/{uid}.json", "w") as f:
                json.dump(dashboard_json, f, indent=2)

            queries = extract_queries(dashboard_json)
            all_queries.extend(queries)

        except requests.RequestException as e:
            print(f"❌ Failed to fetch {title}: {e}")

    with open(QUERY_FILE, "w") as f:
        f.write("\n".join(all_queries))

    print(f"\n✅ Extracted {len(all_queries)} PromQL queries.")
    print(f"💾 Saved to {QUERY_FILE}")

    # ask if you want to get a specific metric from the queries
    specific_metric = input(
        "Do you want to get a specific metric from the queries? (y/n): "
    )
    if specific_metric.lower() == "y":
        metric_name = input("Enter the metric name: ")
        # all that contains the metric name
        filtered_queries = [query for query in all_queries if metric_name in query]
        if filtered_queries:
            print(f"Found {len(filtered_queries)} queries with metric '{metric_name}':")
            # save the filtered queries to a file SPECIFIC_METRIC
            with open(SPECIFIC_METRIC, "w") as f:
                f.write("\n".join(filtered_queries))
            print(f"💾 Saved to {SPECIFIC_METRIC}")

        else:
            print(f"No queries found with metric '{metric_name}'.")


if __name__ == "__main__":
    if not GRAFANA_URL or not GRAFANA_SESSION_COOKIE:
        raise EnvironmentError("GRAFANA_URL and GRAFANA_SESSION_COOKIE must be set")
    main()
