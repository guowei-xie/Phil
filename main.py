from unittest import result
from urllib3 import response
from src.lark.bitable import LarkBitable
from src.processor import process_single_case
from tqdm import tqdm

# 获取验证集
bitable = LarkBitable()

records = bitable.get_dataset()

# 处理样本数据
results = []

for record in tqdm(records, desc="处理样本数据", total=len(records)):
    result = process_single_case(record)
    results.append(result)

# 比对分析
