"""
程序员面试助手RAG系统配置文件
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass
class RAGConfig:
    """程序员面试助手RAG系统配置类"""

    # 路径配置
    data_path: str = "../knowledge_base/docs"  # 技术文档路径
    index_save_path: str = "./vector_index"    # 向量索引保存路径
    
    # 模型配置
    embedding_model: str = "BAAI/bge-small-zh-v1.5"  # 中文嵌入模型
    llm_model: str = "kimi-k2-0711-preview"          # Kimi大语言模型
    
    # 检索配置
    top_k: int = 5                    # 检索返回的文档数量
    chunk_size: int = 1000            # 文档分块大小
    chunk_overlap: int = 200          # 分块重叠大小
    
    # 生成配置
    temperature: float = 0.1          # 生成温度，控制随机性
    max_tokens: int = 2048            # 最大生成token数
    
    # 系统配置
    log_level: str = "INFO"           # 日志级别
    enable_query_rewrite: bool = True # 是否启用查询重写

    def __post_init__(self):
        """初始化后的处理"""
        # 验证数据路径
        if not Path(self.data_path).exists():
            raise FileNotFoundError(f"知识库路径不存在: {self.data_path}")
        
        # 验证API密钥
        if not os.getenv("MOONSHOT_API_KEY"):
            raise ValueError("请设置 MOONSHOT_API_KEY 环境变量")
        
        # 创建索引保存目录
        Path(self.index_save_path).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RAGConfig':
        """从字典创建配置对象"""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'data_path': self.data_path,
            'index_save_path': self.index_save_path,
            'embedding_model': self.embedding_model,
            'llm_model': self.llm_model,
            'top_k': self.top_k,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'log_level': self.log_level,
            'enable_query_rewrite': self.enable_query_rewrite
        }

# 默认配置实例
DEFAULT_CONFIG = RAGConfig()
