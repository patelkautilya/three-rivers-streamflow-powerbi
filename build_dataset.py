"""Build a reproducible three-gauge USGS daily mean streamflow panel."""

from __future__ import annotations

import csv
import json
import math
import statistics
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).parent
START, END = date(2024, 1, 1), date(2025, 12, 31)
SITES = {
    "01646500": "Potomac River near Washington, DC",
    "05331000": "Mississippi River at St. Paul, MN",
    "09402500": "Colorado River near Grand Canyon, AZ",
}
PARAMETER = "00060"  # Discharge, cubic feet per second.
STATISTIC = "00003"  # Daily mean.
FIELDS = [
    "site_id", "site", "date", "year", "month", "discharge_cfs",
    "quality_qualifiers", "site_p90_cfs", "above_site_p90",
]


def fetch() -> tuple[dict, str]:
    params = {
        "format": "json",
        "sites": ",".join(SITES),
        "startDT": START.isoformat(),
        "endDT": END.isoformat(),
        "parameterCd": PARAMETER,
        "statCd": STATISTIC,
    }
    url = "https://waterservices.usgs.gov/nwis/dv/?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "KautilyaPatelAnalystPortfolio/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response), url


def date_range():
    current = START
    while current <= END:
        yield current
        current += timedelta(days=1)


def nearest_rank(values: list[float], fraction: float) -> float:
    assert values
    ordered = sorted(values)
    return ordered[math.ceil(fraction * len(ordered)) - 1]


def build() -> None:
    payload, url = fetch()
    series = payload["value"]["timeSeries"]
    assert len(series) == len(SITES), f"Expected 3 site series, got {len(series)}"
    observed: dict[str, dict[str, tuple[float, str]]] = {}
    source_names = {}
    for item in series:
        site_id = item["sourceInfo"]["siteCode"][0]["value"]
        assert site_id in SITES and site_id not in observed
        assert item["variable"]["variableCode"][0]["value"] == PARAMETER
        assert item["variable"]["unit"]["unitCode"] == "ft3/s"
        source_names[site_id] = item["sourceInfo"]["siteName"]
        data = {}
        for block in item["values"]:
            for point in block["value"]:
                day = point["dateTime"][:10]
                assert day not in data, f"Duplicate {site_id}/{day}"
                value = float(point["value"])
                assert value >= 0, f"Negative discharge {site_id}/{day}"
                data[day] = (value, ";".join(point.get("qualifiers", [])))
        observed[site_id] = data

    days = [day.isoformat() for day in date_range()]
    thresholds = {
        site_id: nearest_rank([v for day, (v, _) in points.items() if day in days], 0.90)
        for site_id, points in observed.items()
    }
    rows = []
    for site_id, label in SITES.items():
        for day in days:
            point = observed[site_id].get(day)
            value, qualifier = point if point else (None, "")
            rows.append({
                "site_id": site_id,
                "site": label,
                "date": day,
                "year": int(day[:4]),
                "month": day[:7],
                "discharge_cfs": "" if value is None else f"{value:g}",
                "quality_qualifiers": qualifier,
                "site_p90_cfs": f"{thresholds[site_id]:g}",
                "above_site_p90": "" if value is None else str(value > thresholds[site_id]).lower(),
            })
    assert len(rows) == len(days) * len(SITES) == 2193
    assert len({(r["site_id"], r["date"]) for r in rows}) == len(rows)

    with (ROOT / "usgs_daily_streamflow_2024_2025.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    by_site = defaultdict(list)
    for row in rows:
        if row["discharge_cfs"]:
            by_site[row["site_id"]].append(float(row["discharge_cfs"]))
    summary = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_url": url,
        "source_site_names": source_names,
        "period": {"start": START.isoformat(), "end": END.isoformat()},
        "grain": "one site per calendar day",
        "rows": len(rows),
        "expected_days_per_site": len(days),
        "missing_rows": sum(not r["discharge_cfs"] for r in rows),
        "qualifiers": dict(Counter(r["quality_qualifiers"] for r in rows if r["discharge_cfs"])),
        "site_checks": {
            site_id: {
                "available_days": len(values),
                "median_daily_cfs": statistics.median(values),
                "p90_daily_cfs_nearest_rank": thresholds[site_id],
                "days_above_site_p90": sum(v > thresholds[site_id] for v in values),
                "maximum_daily_cfs": max(values),
            }
            for site_id, values in by_site.items()
        },
    }
    (ROOT / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build()
