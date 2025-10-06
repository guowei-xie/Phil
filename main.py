from src.lark.bitable import LarkBitable
from src.processor import process_single_case, analyze_results_by_sample, analyze_results_by_label
from tqdm import tqdm
import pandas as pd
import os
from datetime import datetime

# 获取验证集
bitable = LarkBitable()

records = bitable.get_dataset()

# 请求工作流
results = []

for record in tqdm(records, desc="处理样本数据", total=len(records)):
    result = process_single_case(record)
    results.append(result)

# 分析结果
df_samples = analyze_results_by_sample(results)
df_labels = analyze_results_by_label(results)

total = len(df_samples)
match_rate = df_samples['is_match'].mean() if total > 0 else float('nan')
print("\n==== 样本级概览 ====")
print(f"样本总数: {total}")
print(f"完全匹配率: {match_rate:.2%}" if total > 0 else "完全匹配率: N/A")

print("\n==== 标签级概览 ====")
print(df_labels.to_string(index=False))

# 保存结果
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_dir = os.path.join(os.getcwd(), 'results')
os.makedirs(results_dir, exist_ok=True)
excel_path = os.path.join(results_dir, f'analysis_{timestamp}.xlsx')
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_samples.to_excel(writer, sheet_name='sheet1_samples', index=False)
    df_labels.to_excel(writer, sheet_name='sheet2_labels', index=False)
print(f"\n结果保存至: {excel_path}")
