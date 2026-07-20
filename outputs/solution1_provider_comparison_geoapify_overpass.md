# Solution 1 Provider Comparison - Geoapify vs Overpass

Scope: compare committed Solution 1 outputs after merge `79e92d6`.

Input files:

- `outputs/solution1_geoapify_results.json`
- `outputs/solution1_overpass_results.json`

## Summary

| Metric | Value |
|---|---:|
| Compared cases | 10 |
| Geoapify case coverage | 10/10 (`V1_001`-`V1_010`) |
| Overpass case coverage | 10/10 (`V1_001`-`V1_010`) |
| Same Top 1 | 4/10 |
| Average Top 5 overlap | 3.20/5 |
| Avg latency Geoapify | 317,397.1 ms |
| Avg latency Overpass | 529,236.6 ms |

## Per-case Comparison

| Case | Geoapify Top 1 | Overpass Top 1 | Same Top 1 | Top 5 overlap | Geoapify latency | Overpass latency |
|---|---|---|---|---:|---:|---:|
| V1_001 | GV_017 | GV_017 | Yes | 5/5 | 288.7s | 225.5s |
| V1_002 | GV_002 | GV_002 | Yes | 5/5 | 189.1s | 227.1s |
| V1_003 | TB_008 | TB_008 | Yes | 5/5 | 321.3s | 197.4s |
| V1_004 | TB_015 | GV_003 | No | 3/5 | 445.3s | 422.7s |
| V1_005 | GV_002 | GV_002 | Yes | 5/5 | 311.3s | 415.0s |
| V1_006 | GV_008 | GV_018 | No | 0/5 | 224.7s | 754.7s |
| V1_007 | GV_009 | GV_002 | No | 1/5 | 560.7s | 813.7s |
| V1_008 | TB_035 | TB_008 | No | 3/5 | 297.0s | 1074.8s |
| V1_009 | TB_005 | TB_006 | No | 2/5 | 277.4s | 330.0s |
| V1_010 | GV_002 | GV_001 | No | 3/5 | 258.4s | 831.6s |

## Findings

- Provider choice changes ranking materially: only 4/10 cases have the same Top 1.
- Top 5 still overlaps partly: average overlap is 3.20/5, so providers are not random, but not interchangeable.
- Largest ranking drift appears in `V1_006` and `V1_007`. `V1_006` has 0/5 overlap; `V1_007` has 1/5 overlap.
- Overpass is slower in this run: average latency is 529,236.6 ms vs Geoapify 317,397.1 ms.
- These outputs cover only `V1_001`-`V1_010`. The expanded validation cases `V1_011`-`V1_013` still need rerun.
- No committed Solution 1 Mapbox validation output was found yet, even though Mapbox is the documented final provider.

## Cause-effect Notes

1. `SOLUTION1_ENRICHMENT_PROVIDER` now controls both DB-loaded enriched dataset and dynamic map tool.
2. Changing provider changes POI distances/counts.
3. Changed POI values affect LLM reasoning and score/tradeoff explanation.
4. Therefore provider-specific validation must be reported separately instead of merging Geoapify and Overpass into one generic Solution 1 result.

## Next Validation Step

Run the same `V1_001`-`V1_013` set for:

- Solution 1 + Mapbox
- Solution 1 + Geoapify
- Solution 1 + Overpass
- Solution 2 on the same final provider scope

Then update the final Solution 1 vs Solution 2 comparison.
