from src.lark.aliy import Aliy

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
