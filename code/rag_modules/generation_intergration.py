"""
生成集成模块
"""

import os
import logging
from typing import List

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class GenerationIntegrationModule:
    """生成集成模块 - 负责LLM集成和回答生成"""

    def __init__(self, model_name: str = "kimi-k2-0711-preview", temperature: float = 0.1, max_tokens: int = 2048):
        """
        初始化生成集成模块
        
        Args:
            model_name: 模型名称
            temperature: 生成温度
            max_tokens: 最大token数
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = None
        self.setup_llm()

    def setup_llm(self):
        logger.info(f"正在初始化LLM:{self.model_name}")

        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError("请设置 MOONSHOT_API_KEY 环境变量")
        
        self.llm = MoonshotChat(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            moonshot_api_key=api_key
        )
        logger.info("LLM初始化完成")

    def generate_basic_answer(self, query: str, context_docs: List[Document]) -> str:
        """
        生成基础回答

        Args:
            query: 用户查询
            context_docs: 上下文文档列表

        Returns:
            生成的回答
        """
        context = self._build_context(context_docs)

        prompt = ChatPromptTemplate.from_template("""
你是一位经验丰富的Java后端开发工程师。请根据以下技术文档信息回答用户的问题。

用户问题: {question}

相关技术文档信息:
{context}

请提供详细、实用的回答。如果信息不足，请诚实说明。

回答:""")

        # 使用LCEL构建链
        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke(query)
        return response
    
    def query_rewrite(self,query: str) -> str:
        """
        智能查询重写 - 让大模型判断是否需要重写查询

        Args:
            query: 原始查询

        Returns:
            重写后的查询或原查询
        """
        prompt = PromptTemplate(
            template="""
你是一个智能查询分析助手。请分析用户的查询，判断是否需要重写以提高技术文档搜索效果。

原始查询: {query}

分析规则：
1. **具体明确的查询**（直接返回原查询）：
   - 包含具体技术概念：如"Spring Boot 启动原理"、"MySQL 索引优化"
   - 明确的技术问题：如"HashMap 和 ConcurrentHashMap 区别"、"Redis 持久化机制"
   - 具体的面试问题：如"Java 垃圾回收算法有哪些"、"TCP 三次握手过程"

2. **模糊不清的查询**（需要重写）：
   - 过于宽泛：如"Java"、"数据库"、"算法"
   - 缺乏具体信息：如"面试题"、"基础知识"、"框架"
   - 口语化表达：如"怎么学习"、"有什么推荐"、"什么是好的"

重写原则：
- 保持原意不变
- 增加相关技术术语
- 转化为常见面试问题格式
- 保持技术专业性

示例：
- "Java" → "Java 核心面试知识点"
- "数据库" → "数据库基础面试题"
- "算法" → "常见算法面试题"
- "框架" → "Java 主流框架面试要点"
- "Spring Boot 启动原理" → "Spring Boot 启动原理"（保持原查询）
- "MySQL 索引优化" → "MySQL 索引优化"（保持原查询）

请输出最终查询（如果不需要重写就返回原查询）:""",
            input_variables=["query"]
        )

        chain = (
            {"query": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        response = chain.invoke(query).strip()

        # 记录重写结果
        if response != query:
            logger.info(f"查询已重写: '{query}' → '{response}'")
        else:
            logger.info(f"查询无需重写: '{query}'")

        return response
    
    def generate_basic_answer_stream(self, query: str, context_docs: List[Document]):
        """
        生成基础回答 - 流式输出

        Args:
            query: 用户查询
            context_docs: 上下文文档列表

        Yields:
            生成的回答片段
        """
        context = self._build_context(context_docs)

        prompt = ChatPromptTemplate.from_template("""
你是一位专业的Java后端工程师。请根据以下技术文档信息回答用户的问题。

用户问题: {question}
                                                  
相关技术文档信息:
{context}

请提供详细、实用的回答。如果信息不足，请诚实说明。

回答:""")

        chain = (
            {"question": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        for chunk in chain.stream(query):
            yield chunk

    def _build_context(self, docs: List[Document], max_length: int = 4000) -> str:
        """
        构建上下文字符串
        
        Args:
            docs: 文档列表
            max_length: 最大长度
            
        Returns:
            格式化的上下文字符串
        """
        if not docs:
            return "暂无相关技术文档信息。"
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(docs, 1):
            # 添加元数据信息
            metadata_info = f"【技术文档 {i}】"
            if 'title' in doc.metadata:
                metadata_info += f" {doc.metadata['title']}"
            if 'category' in doc.metadata:
                metadata_info += f" | 分类: {doc.metadata['category']}"
            if 'source' in doc.metadata:
                # 提取文件名作为来源
                source_file = doc.metadata['source'].split('\\')[-1] if '\\' in doc.metadata['source'] else doc.metadata['source'].split('/')[-1]
                metadata_info += f" | 来源: {source_file}"
            
            # 构建文档文本
            doc_text = f"{metadata_info}\n{doc.page_content}\n"
            
            # 检查长度限制
            if current_length + len(doc_text) > max_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n" + "="*80 + "\n".join(context_parts)