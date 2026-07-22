# Solution 1 Provider Comparison - Mapbox vs Geoapify vs Overpass

Scope: compare committed Solution 1 outputs after remote update 863ea21.

Input files:

- outputs/solution1_mapbox_results.json
- outputs/solution1_geoapify_results.json
- outputs/solution1_overpass_results.json

## Summary

| Metric | Value |
|---|---:|
| Compared cases | 10 |
| Mapbox coverage | 10/10 (V1_001-V1_010) |
| Geoapify coverage | 10/10 (V1_001-V1_010) |
| Overpass coverage | 10/10 (V1_001-V1_010) |
| Same Top 1 across all 3 providers | 2/10 |
| Same Top 1: Mapbox vs Geoapify | 4/10 |
| Same Top 1: Mapbox vs Overpass | 2/10 |
| Same Top 1: Geoapify vs Overpass | 4/10 |
| Avg Top5 overlap: Mapbox vs Geoapify | 2.3/5 |
| Avg Top5 overlap: Mapbox vs Overpass | 2/5 |
| Avg Top5 overlap: Geoapify vs Overpass | 3.2/5 |
| Avg latency Mapbox | 481044.9 ms |
| Avg latency Geoapify | 317397.1 ms |
| Avg latency Overpass | 529236.6 ms |

## Per-case Comparison

| Case | Mapbox Top 1 | Geoapify Top 1 | Overpass Top 1 | All same Top 1 | M-G overlap | M-O overlap | G-O overlap |
|---|---|---|---|---|---:|---:|---:|
| V1_001 | GV_010 | GV_017 | GV_017 | No | 4/5 | 4/5 | 5/5 |
| V1_002 | GV_002 | GV_002 | GV_002 | Yes | 2/5 | 2/5 | 5/5 |
| V1_003 | GV_037 | TB_008 | TB_008 | No | 3/5 | 3/5 | 5/5 |
| V1_004 | GV_010 | TB_015 | GV_003 | No | 0/5 | 1/5 | 3/5 |
| V1_005 | GV_002 | GV_002 | GV_002 | Yes | 2/5 | 2/5 | 5/5 |
| V1_006 | GV_008 | GV_008 | GV_018 | No | 3/5 | 0/5 | 0/5 |
| V1_007 | GV_003 | GV_009 | GV_002 | No | 3/5 | 0/5 | 1/5 |
| V1_008 | GV_037 | TB_035 | TB_008 | No | 3/5 | 4/5 | 3/5 |
| V1_009 | GV_010 | TB_005 | TB_006 | No | 1/5 | 2/5 | 2/5 |
| V1_010 | GV_002 | GV_002 | GV_001 | No | 2/5 | 2/5 | 3/5 |

## Findings

- Provider choice changes ranking materially: only 2/10 cases have the same Top 1 across all 3 providers.
- Mapbox differs most from Overpass: same Top 1 is 2/10 and average Top5 overlap is 2/5.
- Geoapify and Overpass are closer to each other than to Mapbox in this run: same Top 1 is 4/10 and average overlap is 3.2/5.
- Mapbox is now available as committed validation output, but still only for V1_001-V1_010.
- Expanded validation cases V1_011-V1_013 still need Solution 1 rerun for each final provider scope.

## Cause-effect Notes

1. SOLUTION1_ENRICHMENT_PROVIDER selects both DB-loaded enriched dataset and dynamic map tool.
2. Different providers return different POI distance/count values.
3. Different POI values change LLM reasoning, scoring, and Top 5.
4. Therefore provider-specific validation must be reported separately.

## Next Validation Step

Run Solution 1 on V1_011-V1_013, preferably with Mapbox first because docs mark Mapbox as final provider.
