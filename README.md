# Grafana PromQL Query Extractor

## Overview

This tool extracts PromQL queries from all dashboards in a specified Grafana instance. It is useful for auditing, optimizing, or validating Prometheus queries embedded in Grafana dashboards. Queries can optionally be filtered by a specific metric name.

## Author
**Aleksandro Matejic, 2025**

## Purpose

When managing a large-scale Prometheus setup, it's essential to minimize high-cardinality metrics and unnecessary label usage. This script facilitates:

- Extracting all PromQL queries from dashboards for review.
- Enabling comparisons of these queries against `promtool` results or custom logic.
- Identifying and potentially refactoring costly metrics.

## Features
- Fetch all dashboards using Grafana's HTTP API.
- Save each dashboard as a JSON file for inspection or version control.
- Extract and save all PromQL queries to a text file.
- Interactive prompt to filter and extract queries containing a specific metric.

## Environment Requirements
The following environment variables must be set before execution:

- `GRAFANA_URL`: The base URL of the Grafana instance (e.g., `http://localhost:3000`).
- `GRAFANA_SESSION_COOKIE`: Session cookie string for authenticating with Grafana.

## File Outputs
- `dashboards.json`: JSON file containing metadata (UIDs, titles) for all dashboards.
- `grafana_dashboards/`: Directory containing raw JSON exports of all dashboards.
- `grafana_promql_queries.txt`: All extracted PromQL queries, each prepended with the dashboard title.
- `specific_metric.json`: (Optional) File containing only queries referencing a user-specified metric.

## Functional Components

### 1. Load Dashboard Metadata
Parses `dashboards.json` to retrieve a list of dashboards with UID and title.

### 2. Fetch Dashboard
Uses the Grafana API to retrieve full JSON for each dashboard by UID. Raises an exception if the fetch fails.

### 3. Extract Queries
Navigates to `panels[*].targets[*].expr` in each dashboard's JSON, extracting all PromQL queries. Each query is tagged with the dashboard title.

### 4. Filter Queries by Metric
After extraction, users are prompted to optionally filter queries by metric name. Matching queries are saved separately.

## Error Handling
- Fails fast if required environment variables are not set.
- Gracefully handles HTTP errors when fetching dashboards, logging the issue per dashboard.

## Example Usage
```bash
export GRAFANA_URL="http://localhost:3000"
export GRAFANA_SESSION_COOKIE="your_session_cookie"
python get_all_dashboards.py
```

## Notes
- This tool assumes `dashboards.json` is already populated. Fetching dashboard metadata is out of scope.
- Ensure that the Grafana session cookie is valid and has permission to access all dashboards.

## Future Enhancements
- Add support for API Token authentication.
- Include more panel types or data sources.
- Integrate directly with `promtool` for automated query linting.

---

## Security Considerations
- Avoid hardcoding credentials. Use environment variables.
- Treat output files as sensitive — they may contain internal metric names.

## License
MIT or as defined by the author.

