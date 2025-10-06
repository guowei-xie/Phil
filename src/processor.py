from src.lark.aliy import Aliy
import pandas as pd
from typing import List, Dict, Any, Set

aliy = Aliy()

def process_single_case(record):
    """
    处理单个样本数据
    """
    body = {
        "message_detail": record['fields']['message_detail']
    }
    response = aliy.trigger_custom_task(body)

    result = {
        "sample_id": record['fields']['sample_id'],
        "message_detail": record['fields']['message_detail'],
        "ground_truth": record['fields']['ground_truth'],
        "object": response['object'],
        "content": response['content']
    }
    return result


def _to_label_set(labels: Any) -> Set[str]:
    """
    将输入的标签字段规整为集合形式，便于集合级别对比。

    参数:
        labels: 可能为 list/tuple/set/str/None 的标签字段

    返回:
        set[str]: 规整后的标签集合（统一为字符串）
    """
    if labels is None:
        return set()
    if isinstance(labels, (list, tuple, set)):
        return {str(x).strip() for x in labels if str(x).strip()}
    # 兜底：单个标量
    value = str(labels).strip()
    return {value} if value else set()


def analyze_results_by_sample(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    基于样本维度分析，计算每条样本预测结果与真实标签集合是否完全匹配。

    参数:
        results: process_single_case 的结果列表，每项包含 sample_id/ground_truth/object 等字段

    返回:
        pd.DataFrame: 按样本的分析明细，新增列 is_match（1 完全匹配，0 不匹配）
    """
    rows: List[Dict[str, Any]] = []
    for item in results:
        gt_set = _to_label_set(item.get('ground_truth'))
        pred_set = _to_label_set(item.get('object'))
        is_match = 1 if gt_set == pred_set else 0
        rows.append({
            'sample_id': item.get('sample_id'),
            'message_detail': item.get('message_detail'),
            'ground_truth': list(gt_set),
            'object': list(pred_set),
            'content': item.get('content'),
            'is_match': is_match,
        })
    return pd.DataFrame(rows)


def analyze_results_by_label(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    基于标签维度分析，计算每个唯一标签的召回率与准确率（精确率）。

    定义:
        - support: 该标签在真实数据中出现的样本数（Ground Truth 正例数）
        - predicted: 该标签被预测为正的样本数
        - tp: 该标签的真正例数（真实包含且预测包含）
        - recall = tp / support （support=0 时记为 NaN）
        - precision = tp / predicted （predicted=0 时记为 NaN）

    参数:
        results: process_single_case 的结果列表

    返回:
        pd.DataFrame: 每个标签的 support/predicted/tp/recall/precision 指标
    """
    # 统计容器
    support: Dict[str, int] = {}
    predicted: Dict[str, int] = {}
    tp: Dict[str, int] = {}

    for item in results:
        gt_set = _to_label_set(item.get('ground_truth'))
        pred_set = _to_label_set(item.get('object'))

        for l in gt_set:
            support[l] = support.get(l, 0) + 1
        for l in pred_set:
            predicted[l] = predicted.get(l, 0) + 1
        for l in gt_set.intersection(pred_set):
            tp[l] = tp.get(l, 0) + 1

    # 统一标签全集：仅取自 ground_truth（support 的键）
    all_labels = set(support.keys())

    rows: List[Dict[str, Any]] = []
    for label in sorted(all_labels):
        s = support.get(label, 0)
        p = predicted.get(label, 0)
        t = tp.get(label, 0)
        recall = (t / s) if s > 0 else float('nan')
        precision = (t / p) if p > 0 else float('nan')
        rows.append({
            'label': label,
            'support': s,
            'predicted': p,
            'tp': t,
            'recall': recall,
            'precision': precision,
        })

    df = pd.DataFrame(rows)
    # 便于浏览，按 support 降序、再按 label 升序
    if not df.empty:
        df = df.sort_values(by=['support', 'label'], ascending=[False, True], ignore_index=True)
    return df
