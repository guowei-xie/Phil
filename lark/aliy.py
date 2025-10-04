from ast import Pass
from lark.base import LarkBase
import configparser
import requests
import json

class Aliy(LarkBase):
    """Aliy API接口类"""

    def __init__(self, log_level=None):
        """
        初始化Aliy API接口类
        
        参数:
            log_level: 日志级别，默认继承LarkBase的默认值
        """
        super().__init__(logger_name='aliy')
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.webhook = config['Aliy']['webhook']
        self.api_key = config['Aliy']['apiKey']

    def trigger_custom_task(self, body):
        """
        触发自定义任务，发送请求
        
        参数:
            body: 携带请求参数，dict类型
            
        返回:
            response响应对象
        """
        header = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.post(
                url=self.webhook,
                headers=header,
                json=body,
                timeout=30
            )
        
        response_data = response.json()
        self.logger.debug(f"触发自定义任务返回内容: {response_data}")
        return response_data