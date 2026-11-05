# Findings and metric definitions

The 2024–2025 snapshot contains 731 daily mean discharge values at each of three selected USGS gauges. Values are in cubic feet per second (ft³/s). The dashboard must retain the site and quality qualifiers and avoid presenting the three sites as a representative sample of U.S. rivers.

## Checked results

| Gauge | Median daily discharge, 2024–2025 | Nearest-rank site p90 | Days strictly above p90 | Highest daily mean |
| --- | ---: | ---: | ---: | ---: |
| Potomac near Washington, DC (`01646500`) | 5,150 | 21,200 | 73 | 136,000 |
| Mississippi at St. Paul, MN (`05331000`) | 11,900 | 42,900 | 73 | 114,000 |
| Colorado near Grand Canyon, AZ (`09402500`) | 10,900 | 12,700 | 56 | 15,000 |

For the Mississippi gauge, **65 of its 73** above-p90 days occur in 2024 and **8 in 2025**. This is an observation relative to the 2024–2025 site threshold, not a flood count or evidence of a long-term trend. For the Potomac gauge, the corresponding split is 45 and 28; the Colorado gauge has 28 in each year. Ties at the threshold explain why the Colorado count is below the nominal 10% of days.

Annual median daily discharge at the Mississippi gauge is **10,550 ft³/s in 2024** and **13,200 ft³/s in 2025**. This illustrates why an annual median and a count of high-flow days can tell different stories: the high-flow count is sensitive to the upper tail and its two-year reference threshold.

## Quality and interpretation

- `A` denotes approved values, `P` provisional values, and `A;e` approved values with an estimated-value qualifier in the USGS response. This snapshot has 45 provisional values, all at the Mississippi gauge. The source may later revise them.
- Daily mean discharge is a volume rate averaged over a day. It is not a peak instantaneous flow or a direct flood warning. The site-specific 90th percentile is computed from this two-year sample, not from a long historical record or USGS flood-stage definition.
- River basin size, operations, withdrawals, and gauge location affect discharge. Do not compare raw ft³/s as if the rivers had identical catchments or risk. The three selected gauges are examples, not a random sample.
- The dates are calendar dates from the USGS daily-value service. The dashboard should describe patterns without attributing them to weather, reservoir operations, or climate unless independent evidence supports that explanation.
