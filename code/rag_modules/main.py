"""
程序员面试助手RAG系统主程序
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from config import DEFAULT_CONFIG, RAGConfig
from data_preparation import DataPreparationModule
from index_construction import IndexConstructionModule
from retrieval_optimization import RetrievalOptimizationModule
from generation_intergration import GenerationIntegrationModule

# 加载环境变量
load_dotenv()

class ProgrammerHelperRAGSystem:
    """程序员面试助手RAG系统主类"""

    def __init__(self, config: Optional[RAGConfig] = None):
        """
        初始化程序员面试助手RAG系统

        Args:
            config: RAG系统配置，默认使用DEFAULT_CONFIG
        """
        self.config = config or DEFAULT_CONFIG
        
        # 设置日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个模块
        self.data_module = None
        self.index_module = None
        self.retrieval_module = None
        self.generation_module = None
        
        # 系统状态
        self.is_initialized = False
        self.documents = []
        self.chunks = []
        
        self.logger.info("程序员面试助手RAG系统创建完成")

    def _setup_logging(self):
        """设置日志配置"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 获取日志级别
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # 配置日志
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(),  # 控制台输出
                logging.FileHandler('rag_system.log', encoding='utf-8')  # 文件输出
            ]
        )
    
    def initialize_system(self, force_rebuild: bool = False):
        """
        初始化所有模块
        
        Args:
            force_rebuild: 是否强制重建索引
        """
        try:
            print("🚀 正在初始化程序员面试助手RAG系统...")
            self.logger.info("开始初始化RAG系统")

            # 1. 初始化数据准备模块
            print("📚 初始化数据准备模块...")
            self.data_module = DataPreparationModule()
            self.data_module(self.config.data_path)
            
            # 2. 初始化索引构建模块
            print("🔍 初始化索引构建模块...")
            self.index_module = IndexConstructionModule(
                model_name=self.config.embedding_model,
                index_save_path=self.config.index_save_path
            )

            # 3. 初始化生成集成模块
            print("🤖 初始化生成集成模块...")
            self.generation_module = GenerationIntegrationModule(
                model_name=self.config.llm_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            # 4. 加载或构建索引
            print("📖 加载文档和构建索引...")
            self._load_documents_and_build_index(force_rebuild)

            self.is_initialized = True
            print("✅ 系统初始化完成！")
            self.logger.info("RAG系统初始化成功")
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            print(f"❌ 系统初始化失败: {e}")
            raise

    def _load_documents_and_build_index(self, force_rebuild: bool = False):
        """加载文档并构建索引"""
        # 无论是否有现有索引，都需要加载文档数据到内存
        print("📄 开始加载技术文档...")
        
        # 加载文档
        self.documents = self.data_module.load_documents()
        print(f"📚 成功加载 {len(self.documents)} 个技术文档")
        
        # 分块处理
        print("✂️ 开始文档分块...")
        self.chunks = self.data_module.chunk_documents()
        print(f"📦 成功分割为 {len(self.chunks)} 个文档块")
        
        # 尝试加载现有索引
        if not force_rebuild and self.index_module.load_index():
            print("✅ 成功加载现有向量索引")
        else:
            # 构建向量索引
            print("🔗 开始构建向量索引...")
            self.index_module.build_vector_index(self.chunks)
            
            # 保存索引
            print("💾 保存向量索引...")
            self.index_module.save_index()
        
        # 初始化检索优化模块
        print("⚡ 初始化检索优化模块...")
        self.retrieval_module = RetrievalOptimizationModule(
            vectorstore=self.index_module.vectorstore,
            chunks=self.chunks
        )

    def query(self, question: str, use_rewrite: bool = None) -> str:
        """
        查询问答
        
        Args:
            question: 用户问题
            use_rewrite: 是否使用查询重写，默认使用配置值
            
        Returns:
            回答结果
        """
        if not self.is_initialized:
            raise RuntimeError("系统尚未初始化，请先调用 initialize_system()")
        
        start_time = time.time()
        
        # 是否使用查询重写
        if use_rewrite is None:
            use_rewrite = self.config.enable_query_rewrite
            
        try:
            # 查询重写（可选）
            if use_rewrite:
                print("🔄 正在分析并优化查询...")
                rewritten_query = self.generation_module.query_rewrite(question)
                query_to_use = rewritten_query
            else:
                query_to_use = question
            
            # 检索相关文档
            print("🔍 正在检索相关技术文档...")
            if self.retrieval_module:
                # 使用混合检索
                relevant_docs = self.retrieval_module.hybrid_search(
                    query_to_use, 
                    top_k=self.config.top_k
                )
            else:
                # 使用基础相似度检索
                relevant_docs = self.index_module.similarity_search(
                    query_to_use,
                    k=self.config.top_k
                )
            
            print(f"📋 找到 {len(relevant_docs)} 个相关文档")
            
            # 生成回答
            print("💭 正在生成回答...")
            answer = self.generation_module.generate_basic_answer(
                query=question,  # 使用原始问题生成回答
                context_docs=relevant_docs
            )
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ 查询完成，耗时 {elapsed_time:.2f} 秒")
            
            self.logger.info(f"查询成功: {question[:50]}... -> 返回答案长度: {len(answer)}")
            
            return answer
            
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            return f"抱歉，查询过程中出现错误: {str(e)}"

    def query_stream(self, question: str, use_rewrite: bool = None):
        """
        流式查询问答
        
        Args:
            question: 用户问题
            use_rewrite: 是否使用查询重写
            
        Yields:
            回答片段
        """
        if not self.is_initialized:
            raise RuntimeError("系统尚未初始化，请先调用 initialize_system()")
        
        # 是否使用查询重写
        if use_rewrite is None:
            use_rewrite = self.config.enable_query_rewrite
            
        try:
            # 查询重写（可选）
            if use_rewrite:
                rewritten_query = self.generation_module.query_rewrite(question)
                query_to_use = rewritten_query
            else:
                query_to_use = question
            
            # 检索相关文档
            if self.retrieval_module:
                relevant_docs = self.retrieval_module.hybrid_search(
                    query_to_use, 
                    top_k=self.config.top_k
                )
            else:
                relevant_docs = self.index_module.similarity_search(
                    query_to_use,
                    k=self.config.top_k
                )
            
            # 流式生成回答
            for chunk in self.generation_module.generate_basic_answer_stream(
                query=question,
                context_docs=relevant_docs
            ):
                yield chunk
                
        except Exception as e:
            yield f"抱歉，查询过程中出现错误: {str(e)}"

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        if not self.data_module:
            return {"error": "系统尚未初始化"}
            
        stats = {
            "initialized": self.is_initialized,
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "config": self.config.to_dict()
        }
        
        # 添加数据统计信息
        if self.data_module:
            data_stats = self.data_module.get_statistics()
            stats.update(data_stats)
            
        return stats

    def search_by_category(self, query: str, category: str, top_k: int = None) -> str:
        """
        按分类检索
        
        Args:
            query: 查询问题
            category: 技术分类
            top_k: 返回文档数量
            
        Returns:
            回答结果
        """
        if not self.is_initialized:
            raise RuntimeError("系统尚未初始化")
            
        if not self.retrieval_module:
            raise RuntimeError("检索模块未初始化")
            
        top_k = top_k or self.config.top_k
        
        # 使用元数据过滤检索
        relevant_docs = self.retrieval_module.metadata_filtered_search(
            query=query,
            filters={"category": category},
            top_k=top_k
        )
        
        if not relevant_docs:
            return f"抱歉，在 '{category}' 分类中没有找到相关内容。"
        
        # 生成回答
        answer = self.generation_module.generate_basic_answer(
            query=query,
            context_docs=relevant_docs
        )
        
        return answer


def create_interactive_cli():
    """创建交互式命令行界面"""
    def print_banner():
        print("="*60)
        print("🚀 程序员面试助手 RAG 系统")
        print("   Java后端开发面试知识库问答系统")
        print("="*60)
        print()

    def print_help():
        print("\n📋 可用命令:")
        print("  help     - 显示帮助信息")
        print("  stats    - 显示系统统计信息")
        print("  category - 按分类搜索 (格式: category <分类名> <问题>)")
        print("  quit/exit - 退出系统")
        print("  直接输入问题进行查询")
        print()

    # 创建系统实例
    system = ProgrammerHelperRAGSystem()
    
    print_banner()
    
    try:
        # 初始化系统
        system.initialize_system()
        print()
        print_help()
        
        while True:
            try:
                user_input = input("\n💭 请输入您的问题 (输入 'help' 查看帮助): ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n👋 感谢使用程序员面试助手，祝您面试顺利！")
                    break
                    
                elif user_input.lower() == 'help':
                    print_help()
                    
                elif user_input.lower() == 'stats':
                    stats = system.get_system_stats()
                    print(f"\n📊 系统统计信息:")
                    print(f"   文档总数: {stats.get('total_documents', 0)}")
                    print(f"   文档块总数: {stats.get('total_chunks', 0)}")
                    if 'categories' in stats:
                        print(f"   分类统计: {stats['categories']}")
                    
                elif user_input.lower().startswith('category '):
                    parts = user_input[9:].split(' ', 1)  # 去掉 'category '
                    if len(parts) >= 2:
                        category, question = parts[0], parts[1]
                        print(f"\n🔍 在 '{category}' 分类中搜索: {question}")
                        answer = system.search_by_category(question, category)
                        print(f"\n💡 回答:\n{answer}")
                    else:
                        print("❌ 格式错误，请使用: category <分类名> <问题>")
                        
                else:
                    # 普通查询
                    print(f"\n🤔 正在思考您的问题: {user_input}")
                    answer = system.query(user_input)
                    print(f"\n💡 回答:\n{answer}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 检测到 Ctrl+C，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 处理请求时出错: {e}")
                
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        return


if __name__ == "__main__":
    # 运行交互式命令行界面
    create_interactive_cli()