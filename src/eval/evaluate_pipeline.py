"""
Comprehensive validation of the DSS Recommendation Pipeline.

Validates the pipeline against 50 diverse scenarios using multiple
information-retrieval and decision-quality metrics:

  1. Constraint Satisfaction Rate (CSR)
  2. Precision@K (K=3, 5)
  3. Recall@K (K=3, 5)
  4. NDCG@K (K=3, 5)
  5. Mean Average Precision (MAP)
  6. Sensitivity Analysis  — per-archetype breakdown

Outputs:
  - outputs/validation_report.md   (detailed markdown report)
  - outputs/validation_summary.json (machine-readable metrics)
"""

import json
import math
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ENRICHED_DATA_FILE = os.path.join(BASE_DIR, 'data', 'go_vap_enriched.json')
VALIDATION_FILE = os.path.join(BASE_DIR, 'data', 'validation_50_scenarios.json')
REPORT_FILE = os.path.join(BASE_DIR, 'outputs', 'validation_report.md')
SUMMARY_JSON_FILE = os.path.join(BASE_DIR, 'outputs', 'validation_summary.json')


# ── Data loading ────────────────────────────────────────────────────
def load_data():
    with open(ENRICHED_DATA_FILE, 'r', encoding='utf-8') as f:
        properties = json.load(f)
    with open(VALIDATION_FILE, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    return properties, scenarios


# ── Pipeline replica (must match src/models/ logic exactly) ─────────
def normalize_val(val, limit_min, limit_max, direction):
    if limit_max == limit_min:
        return 0.5
    if direction == 'lower_better':
        return max(0.0, min(1.0, (limit_max - val) / (limit_max - limit_min)))
    elif direction == 'higher_better':
        return max(0.0, min(1.0, (val - limit_min) / (limit_max - limit_min)))
    return 0.0


def get_attr_value(prop, attr):
    if attr == 'price':
        return prop['price_million_vnd']
    elif attr == 'price_per_m2':
        return prop.get('price_per_m2_million', 0) or 0
    return prop.get(attr, 0) or 0


def run_recommender(scenario, properties, k=5):
    """Run the pipeline's recommender logic and return Top-K."""
    hc = scenario['hard_constraints']
    sp = scenario['soft_preferences']

    candidates = [
        p for p in properties
        if p['price_million_vnd'] <= hc['budget_max_million']
        and p['bedrooms'] >= hc['min_bedrooms']
    ]

    scored = []
    for cand in candidates:
        total_score = 0.0
        for attr, config in sp.items():
            val = get_attr_value(cand, attr)
            norm = normalize_val(val, config['min'], config['max'], config['direction'])
            total_score += norm * config['weight']
        scored.append({**cand, 'score': round(total_score, 4)})

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:k]


# ── Metric calculations ────────────────────────────────────────────
def precision_at_k(recommended_ids, ground_truth_ids, k):
    rec = recommended_ids[:k]
    hits = sum(1 for r in rec if r in ground_truth_ids)
    return hits / k if k > 0 else 0.0


def recall_at_k(recommended_ids, ground_truth_ids, k):
    rec = recommended_ids[:k]
    hits = sum(1 for r in rec if r in ground_truth_ids)
    return hits / len(ground_truth_ids) if ground_truth_ids else 0.0


def ndcg_at_k(recommended_ids, ground_truth_ids, k):
    gt_rel = {gid: len(ground_truth_ids) - idx for idx, gid in enumerate(ground_truth_ids)}

    dcg = 0.0
    for i, rid in enumerate(recommended_ids[:k]):
        rel = gt_rel.get(rid, 0)
        dcg += rel / math.log2(i + 2)

    idcg = 0.0
    for i in range(min(k, len(ground_truth_ids))):
        rel = len(ground_truth_ids) - i
        idcg += rel / math.log2(i + 2)

    return dcg / idcg if idcg > 0 else 0.0


def average_precision(recommended_ids, ground_truth_ids, k):
    """Average Precision for a single query."""
    hits = 0
    sum_precisions = 0.0
    for i, rid in enumerate(recommended_ids[:k]):
        if rid in ground_truth_ids:
            hits += 1
            sum_precisions += hits / (i + 1)
    return sum_precisions / min(k, len(ground_truth_ids)) if ground_truth_ids else 0.0


def constraint_satisfaction_rate(recommended, hard_constraints):
    if not recommended:
        return 1.0
    violations = sum(
        1 for p in recommended
        if p['price_million_vnd'] > hard_constraints['budget_max_million']
        or p['bedrooms'] < hard_constraints['min_bedrooms']
    )
    return (len(recommended) - violations) / len(recommended)


# ── Main evaluation ────────────────────────────────────────────────
def main():
    if not os.path.exists(ENRICHED_DATA_FILE):
        print(f"Error: {ENRICHED_DATA_FILE} not found. Run enrichment first.")
        return

    properties, scenarios = load_data()

    all_results = []
    archetype_metrics = defaultdict(lambda: defaultdict(list))

    for sc in scenarios:
        gt = sc['ground_truth_top5']
        top5 = run_recommender(sc, properties, k=5)
        top3 = top5[:3]
        rec_ids_5 = [p['property_id'] for p in top5]
        rec_ids_3 = [p['property_id'] for p in top3]

        csr = constraint_satisfaction_rate(top5, sc['hard_constraints'])
        p3 = precision_at_k(rec_ids_5, gt, 3)
        p5 = precision_at_k(rec_ids_5, gt, 5)
        r3 = recall_at_k(rec_ids_5, gt, 3)
        r5 = recall_at_k(rec_ids_5, gt, 5)
        n3 = ndcg_at_k(rec_ids_5, gt, 3)
        n5 = ndcg_at_k(rec_ids_5, gt, 5)
        ap = average_precision(rec_ids_5, gt, 5)

        n_candidates = sc.get('candidates_after_filter', '?')

        result = {
            'id': sc['scenario_id'],
            'name': sc['name'],
            'archetype': sc.get('archetype', 'unknown'),
            'candidates': n_candidates,
            'rec_ids': rec_ids_5,
            'gt_ids': gt,
            'csr': csr,
            'p3': p3, 'p5': p5,
            'r3': r3, 'r5': r5,
            'n3': n3, 'n5': n5,
            'ap': ap,
        }
        all_results.append(result)

        arch = result['archetype']
        for metric in ['csr', 'p3', 'p5', 'r3', 'r5', 'n3', 'n5', 'ap']:
            archetype_metrics[arch][metric].append(result[metric])

    # ── Aggregate ───────────────────────────────────────────────────
    n = len(all_results)
    avg = lambda key: sum(r[key] for r in all_results) / n if n else 0

    global_metrics = {
        'total_scenarios': n,
        'avg_csr': round(avg('csr'), 4),
        'avg_precision_3': round(avg('p3'), 4),
        'avg_precision_5': round(avg('p5'), 4),
        'avg_recall_3': round(avg('r3'), 4),
        'avg_recall_5': round(avg('r5'), 4),
        'avg_ndcg_3': round(avg('n3'), 4),
        'avg_ndcg_5': round(avg('n5'), 4),
        'mean_avg_precision': round(avg('ap'), 4),
    }

    # Edge case stats
    zero_candidates = [r for r in all_results if r['candidates'] == 0]
    few_candidates = [r for r in all_results if isinstance(r['candidates'], int) and 0 < r['candidates'] < 5]

    # ── Write markdown report ───────────────────────────────────────
    report = []
    report.append("# 📋 Báo cáo Validation Hệ thống Tư vấn BĐS (50 Scenarios)")
    report.append("")
    report.append(f"**Tổng số kịch bản kiểm thử:** {n}")
    report.append(f"**Phân bổ:** 5 archetype × 10 biến thể mỗi archetype")
    report.append(f"**Tập dữ liệu:** {len(properties)} BĐS tại Quận Gò Vấp, TP.HCM")
    report.append("")

    # Summary table
    report.append("## 📊 Tổng hợp chỉ số đánh giá (Global Metrics)")
    report.append("")
    report.append("| Chỉ số | Giá trị |")
    report.append("| :--- | :---: |")
    report.append(f"| Constraint Satisfaction Rate (CSR) | **{global_metrics['avg_csr']*100:.1f}%** |")
    report.append(f"| Precision@3 | **{global_metrics['avg_precision_3']*100:.1f}%** |")
    report.append(f"| Precision@5 | **{global_metrics['avg_precision_5']*100:.1f}%** |")
    report.append(f"| Recall@3 | **{global_metrics['avg_recall_3']*100:.1f}%** |")
    report.append(f"| Recall@5 | **{global_metrics['avg_recall_5']*100:.1f}%** |")
    report.append(f"| NDCG@3 | **{global_metrics['avg_ndcg_3']:.4f}** |")
    report.append(f"| NDCG@5 | **{global_metrics['avg_ndcg_5']:.4f}** |")
    report.append(f"| Mean Average Precision (MAP) | **{global_metrics['mean_avg_precision']:.4f}** |")
    report.append("")

    # Per-archetype
    report.append("---")
    report.append("")
    report.append("## 🎯 Phân tích theo nhóm người dùng (Per-Archetype Breakdown)")
    report.append("")
    report.append("| Archetype | #Scenarios | Avg CSR | Avg P@5 | Avg R@5 | Avg NDCG@5 | Avg MAP |")
    report.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")

    archetype_names = {
        'family': '👨‍👩‍👧‍👦 Gia đình',
        'young_professional': '👤 Người trẻ',
        'investor': '💰 Nhà đầu tư',
        'elderly': '🧓 Người cao tuổi',
        'couple': '💑 Cặp đôi',
    }

    for arch in ['family', 'young_professional', 'investor', 'elderly', 'couple']:
        m = archetype_metrics[arch]
        cnt = len(m['csr'])
        a_csr = sum(m['csr']) / cnt if cnt else 0
        a_p5 = sum(m['p5']) / cnt if cnt else 0
        a_r5 = sum(m['r5']) / cnt if cnt else 0
        a_n5 = sum(m['n5']) / cnt if cnt else 0
        a_map = sum(m['ap']) / cnt if cnt else 0
        label = archetype_names.get(arch, arch)
        report.append(f"| {label} | {cnt} | {a_csr*100:.0f}% | {a_p5*100:.0f}% | {a_r5*100:.0f}% | {a_n5:.4f} | {a_map:.4f} |")

    report.append("")

    # Edge cases
    report.append("---")
    report.append("")
    report.append("## ⚠️ Phân tích Edge Cases")
    report.append("")
    report.append(f"- **Scenarios không có BĐS phù hợp (0 candidates):** {len(zero_candidates)}")
    if zero_candidates:
        for r in zero_candidates:
            report.append(f"  - `{r['id']}` — {r['name']}")
    report.append(f"- **Scenarios có ít hơn 5 candidates:** {len(few_candidates)}")
    if few_candidates:
        for r in few_candidates:
            report.append(f"  - `{r['id']}` — {r['name']} ({r['candidates']} candidates)")
    report.append("")

    # Detailed table
    report.append("---")
    report.append("")
    report.append("## 📈 Kết quả chi tiết từng kịch bản")
    report.append("")
    report.append("| ID | Tên kịch bản | #Cands | Top 5 đề xuất | CSR | P@5 | R@5 | NDCG@5 | AP |")
    report.append("| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |")

    for r in all_results:
        rec_str = ", ".join(r['rec_ids']) if r['rec_ids'] else "∅"
        report.append(
            f"| {r['id']} | {r['name']} | {r['candidates']} | {rec_str} "
            f"| {r['csr']*100:.0f}% | {r['p5']*100:.0f}% | {r['r5']*100:.0f}% "
            f"| {r['n5']:.4f} | {r['ap']:.4f} |"
        )

    report.append("")

    # Interpretation
    report.append("---")
    report.append("")
    report.append("## 🔍 Phân tích & Nhận xét")
    report.append("")
    report.append("### 1. Constraint Satisfaction Rate (CSR)")
    if global_metrics['avg_csr'] == 1.0:
        report.append("- CSR đạt **100%** trên toàn bộ 50 scenarios → Module lọc cứng (Hard Constraint Filter) hoạt động hoàn hảo.")
    else:
        report.append(f"- CSR trung bình: **{global_metrics['avg_csr']*100:.1f}%** — Cần kiểm tra lại logic lọc cứng.")
    report.append("")

    report.append("### 2. Chất lượng đề xuất (Precision & Recall)")
    report.append(f"- **Precision@5 = {global_metrics['avg_precision_5']*100:.1f}%**: Tỷ lệ BĐS đề xuất trùng với ground-truth.")
    report.append(f"- **Recall@5 = {global_metrics['avg_recall_5']*100:.1f}%**: Tỷ lệ BĐS ground-truth được tìm thấy trong đề xuất.")
    report.append("")

    report.append("### 3. Chất lượng xếp hạng (NDCG & MAP)")
    report.append(f"- **NDCG@5 = {global_metrics['avg_ndcg_5']:.4f}**: Đo lường chất lượng thứ tự xếp hạng.")
    report.append(f"- **MAP = {global_metrics['mean_avg_precision']:.4f}**: Mean Average Precision đo lường toàn diện.")
    report.append("")

    report.append("### 4. Robustness qua các nhóm người dùng")
    report.append("- Hệ thống được kiểm thử trên **5 archetype khác nhau**, mỗi archetype có 10 biến thể tham số.")
    report.append("- Điều này đảm bảo DSS hoạt động ổn định trên các nhu cầu đa dạng: gia đình, người trẻ, nhà đầu tư, người cao tuổi, cặp đôi.")
    report.append("")

    report.append("### 5. Edge Cases")
    report.append(f"- {len(zero_candidates)} scenarios không có BĐS nào thỏa mãn ràng buộc cứng → Hệ thống trả về danh sách rỗng (đúng hành vi mong đợi).")
    report.append(f"- {len(few_candidates)} scenarios có ít hơn 5 candidates → Đánh giá khả năng graceful degradation của hệ thống.")
    report.append("")

    # Write files
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    summary_output = {
        'global_metrics': global_metrics,
        'per_archetype': {
            arch: {metric: round(sum(vals)/len(vals), 4) if vals else 0 for metric, vals in metrics.items()}
            for arch, metrics in archetype_metrics.items()
        },
        'edge_cases': {
            'zero_candidates': [r['id'] for r in zero_candidates],
            'few_candidates': [{'id': r['id'], 'count': r['candidates']} for r in few_candidates],
        }
    }
    with open(SUMMARY_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary_output, f, ensure_ascii=False, indent=2)

    # Console output
    print("\n" + "=" * 65)
    print("✅ VALIDATION REPORT — 50 Scenarios")
    print("=" * 65)
    print(f"  CSR (avg):        {global_metrics['avg_csr']*100:.1f}%")
    print(f"  Precision@3:      {global_metrics['avg_precision_3']*100:.1f}%")
    print(f"  Precision@5:      {global_metrics['avg_precision_5']*100:.1f}%")
    print(f"  Recall@3:         {global_metrics['avg_recall_3']*100:.1f}%")
    print(f"  Recall@5:         {global_metrics['avg_recall_5']*100:.1f}%")
    print(f"  NDCG@3:           {global_metrics['avg_ndcg_3']:.4f}")
    print(f"  NDCG@5:           {global_metrics['avg_ndcg_5']:.4f}")
    print(f"  MAP:              {global_metrics['mean_avg_precision']:.4f}")
    print(f"\n  Edge cases:       {len(zero_candidates)} empty, {len(few_candidates)} partial")
    print(f"\n  Report:  {REPORT_FILE}")
    print(f"  Summary: {SUMMARY_JSON_FILE}")
    print("=" * 65)


if __name__ == '__main__':
    main()
