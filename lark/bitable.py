"""
飞书多维表格API模块
"""
from lark_oapi.api.bitable.v1 import *
from lark.base import LarkBase
import configparser
import json

class LarkBitable(LarkBase):
    """飞书多维表格操作类"""
    
    def __init__(self, log_level=None):
        """
        初始化飞书多维表格客户端
        
        参数:
            log_level: 日志级别，默认继承LarkBase的默认值
        """
        super().__init__(logger_name='lark_bitable')
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.app_token = config['DATASET']['appToken']
        self.table_id = config['DATASET']['tableId']
        self.sample_size = int(config['DATASET']['sampleSize'])
        self.wiki = config['DATASET']['wiki'] == 'True'
        if self.wiki:
            self.wiki_node_space = self.get_wiki_node_space(self.app_token, 'wiki')
            self.app_token = self.wiki_node_space.data.node.obj_token

    def get_all_records(self, app_token=None, table_id=None, view_id=None, page_size=100):
        """
        获取多维表格中的所有记录
        
        参数:
            app_token: 多维表格的应用令牌，默认使用配置中的app_token
            table_id: 表格ID，默认为None
            view_id: 视图ID，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            包含所有记录的列表
        """
        app_token = app_token or self.app_token
        if not app_token:
            raise ValueError("必须提供app_token参数或在配置文件中设置bitableToken")
        if not table_id:
            raise ValueError("必须提供table_id参数")
            
        self.logger.debug(f"开始获取多维表格记录，表格ID: {table_id}")
        
        all_records = []
        page_token = None
        
        while True:
            # 获取一页记录
            records_page = self._get_records_page(app_token, table_id, view_id, page_token, page_size)
            
            # 添加当前页的记录到结果列表
            if records_page.data and records_page.data.items:
                all_records.extend(records_page.data.items)
                
            # 检查是否有更多页
            if not records_page.data or not records_page.data.has_more or not records_page.data.page_token:
                break
                
            # 更新页标记以获取下一页
            page_token = records_page.data.page_token
            self.logger.debug(f"获取下一页记录，页标记: {page_token}")
        
        self.logger.info(f"成功获取所有记录，共 {len(all_records)} 条")
        return all_records

    def get_all_records_json(self, app_token=None, table_id=None, view_id=None, page_size=100):
        """
        将获取到的全部记录转换为json格式
        
        参数:
            app_token: 多维表格的应用令牌，默认使用配置中的app_token
            table_id: 表格ID，默认为None
            view_id: 视图ID，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            JSON格式的记录数据
        """
        table_records = self.get_all_records(app_token, table_id, view_id, page_size)
        
        # 将 AppTableRecord 对象转换为可序列化的字典
        serializable_records = []
        for record in table_records:
            record_dict = {
                "record_id": record.record_id,
                "fields": record.fields
            }
            serializable_records.append(record_dict)
            
        return serializable_records
    
    def _get_records_page(self, app_token, table_id, view_id=None, page_token=None, page_size=100):
        """
        获取多维表格中的一页记录
        
        参数:
            app_token: 多维表格的应用令牌
            table_id: 表格ID
            view_id: 视图ID，默认为None
            page_token: 分页标记，默认为None
            page_size: 每页记录数，默认为100
            
        返回:
            包含一页记录的响应对象
        """
        # 构造请求对象
        request_builder = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .page_size(page_size)
            
        # 添加可选参数
        if view_id:
            request_builder.view_id(view_id)
        if page_token:
            request_builder.page_token(page_token)
            
        request = request_builder.build()
        
        # 发起请求
        response = self.client.bitable.v1.app_table_record.list(request)
        
        # 处理响应
        return self.handle_response(response, "获取多维表格记录")

    def get_dataset(self):
        """
        获取验证集样本数据
        """
        records = self.get_all_records_json(self.app_token, self.table_id)
        records = [record for record in records if record['fields']['origin_content'] is not None]
        # 当sample_size小于等于0时，返回所有记录
        if self.sample_size > 0:
            records = records[:self.sample_size]
        
        self.logger.info(f"获取有效的样本数据量: {len(records)}")
        return records