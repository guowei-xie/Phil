from lark.bitable import LarkBitable


# 获取验证集
bitable = LarkBitable()

records = bitable.get_dataset()

# 遍历验证集,输出origin_content
for record in records:
    print(record['fields']['origin_content']) 
    print("-"*100)