# Solution Comparison - Solution 1 Mapbox vs Solution 2

Scope: compare committed outputs after remote update 863ea21.

Input files:

- outputs/solution1_mapbox_results.json
- outputs/solution2_results.json

## Summary

| Metric | Value |
|---|---:|
| Compared common cases | 10 |
| Solution 1 Mapbox coverage | 10/10 (V1_001-V1_010) |
| Solution 2 coverage | 13/13 (V1_001-V1_013) |
| Same Top 1 on common cases | 4/10 |
| Average Top5 overlap | 2.50/5 |
| Avg latency Solution 1 Mapbox | 481,044.9 ms |
| Avg latency Solution 2 | 2.2 ms |

## Per-case Comparison

| Case | Solution 1 Mapbox Top 1 | Solution 2 Top 1 | Same Top 1 | Top 5 overlap | S1 latency | S2 latency |
|---|---|---|---|---:|---:|---:|
| V1_001 | GV_010 | GV_010 | Yes | 2/5 | 564.8s | 1ms |
| V1_002 | GV_002 | GV_002 | Yes | 3/5 | 316.8s | 0.3ms |
| V1_003 | GV_037 | GV_010 | No | 1/5 | 748.1s | 0.6ms |
| V1_004 | GV_010 | GV_009 | No | 3/5 | 404.4s | 0.4ms |
| V1_005 | GV_002 | GV_002 | Yes | 2/5 | 377.5s | 0.3ms |
| V1_006 | GV_008 | GV_008 | Yes | 2/5 | 615.2s | 4.9ms |
| V1_007 | GV_003 | GV_002 | No | 4/5 | 163.1s | 6.9ms |
| V1_008 | GV_037 | TB_035 | No | 3/5 | 509.3s | 3.2ms |
| V1_009 | GV_010 | GV_009 | No | 3/5 | 649.8s | 0.5ms |
| V1_010 | GV_002 | GV_010 | No | 2/5 | 461.4s | 3.8ms |

## Findings

- On 10 common cases, Solution 1 Mapbox and Solution 2 have same Top 1 in 4/10 cases.
- Average Top5 overlap is 2.50/5, so outputs are related but not equivalent.
- Solution 2 now has output for V1_011-V1_013; Solution 1 still needs rerun for those cases.
- Final winner should not be concluded until Solution 1 also covers all 13 cases.

## Cause-effect Notes

1. Solution 2 has broader case coverage after the new push.
2. Solution 1 now has Mapbox output, matching the documented final provider direction.
3. Common-case comparison is possible for V1_001-V1_010.
4. Final 13-case comparison is still blocked by missing Solution 1 output for V1_011-V1_013.
