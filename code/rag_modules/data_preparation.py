"""
数据准备模块
"""
import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class DataPreparationModule:
    """数据准备模块 - 负责数据加载、清洗和预处理"""
    # 统一维护的分类与难度配置，供外部复用，避免关键词重复定义
    CATEGORY_MAPPING = {
        # /java
        'basis':'Java基础',
        'collection':'Java集合框架',
        'concurrent':'Java并发编程',
        'io':'Java IO',
        'jvm':'JVM',
        'new-features':'Java新特性',
        # /tools
        'docker':'docker',
        'git':'git',
        'gradle':'gradle',
        'maven':'maven',
        # /database
        'sql':'SQL',
        'redis':'Redis',
        'mysql':'MySQL',
        'mongodb':'mongodb',
        'elasticsearch':'elasticsearch',
        # /cs-basics
        'algorithms':'算法',
        'data-structure':'数据结构',
        'network':'计算机网络',
        'operating-system':'操作系统',
        # /zhuanlan
        'zhuanlan':'专栏',
        # /system-design
        'system-design':'系统设计',
        'basis':'系统设计基础',
        'framework':'系统设计框架',
        'security':'系统设计安全',
        # /open-source-project
        'open-source-project':'开源项目',
        # /interview-preparation
        'interview-preparation':'面试准备',
        # /high-quality-technical-articles
        'high-quality-technical-articles':'高质量技术文章',
        'advanced-programmer':'高级程序员',
        'interview':'面经',
        'personal-experience':'个人经验',
        # /high-performance
        'high-performance':'高性能',
        'message-queue':'消息队列',
        # /high-availability
        'high-availability':'高可用',
        # /distributed-system
        'distributed-system':'分布式系统',
        # /unisound
        'unisound':'云知声'

    }
    CATEGORY_LABELS = list(set(CATEGORY_MAPPING.values()))

    def __call__(self,data_path: str):
        """
        初始化数据准备模块
        
        Args:
            data_path: 数据文件夹路径
        """
        self.data_path = data_path
        self.documents: List[Document] = [] # 父文档(完整技术博客)
        self.chunks: List[Document] = [] # 子文档(按照标题分割后的文本块)
        self.parent_child_map: Dict[str, str] = {} # 父子文档映射关系
    
    def load_documents(self) -> List[Document]:
        """
        加载文档数据
        
        Returns:
            加载的文档列表
        """
        logger.info(f'正在从 {self.data_path} 加载文档...')

        # 直接读取指定目录下的所有Markdown文件
        documents = []
        data_path_obj = Path(self.data_path)
        for md_file in data_path_obj.rglob('*.md'):
            try:
                # 直接读取文件内容
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 需要为每个父文档分配确定性的唯一ID
                    try:
                        data_root = Path(self.data_path).resolve()
                        relative_path = Path(md_file).resolve().relative_to(data_root).as_posix()
                    except Exception:
                        relative_path = Path(md_file).as_posix()
                    parent_id = hashlib.md5(relative_path.encode("utf-8")).hexdigest()

                    # 为每个父文档创建Document对象
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(md_file),
                            'parent_id': parent_id,
                            'doc_type': 'parent' # 标记为父文档
                        }
                    )
                    documents.append(doc)
            except Exception as e:
                logger.error(f'加载文件 {md_file} 时出错: {e}')

        # 增强文档的元数据
        for doc in documents:
            self._enhance_metadata(doc)

        self.documents = documents
        logger.info(f'成功加载 {len(documents)} 个文档.')
        return documents
    
    def _enhance_metadata(self, doc: Document):
        """
        增强文档元数据
        
        Args:
            doc: 需要增强元数据的文档
        """
        file_path = Path(doc.metadata.get('source', ''))
        path_parts = file_path.parts

        # 根据目录提取博客分类
        doc.metadata['category'] = '未知分类'
        for key,value in self.CATEGORY_MAPPING.items():
            if key in path_parts:
                doc.metadata['category'] = value
                break
        
        # 提取主题
        doc.metadata['title'] = file_path.stem

    @classmethod
    def get_supported_categories(cls) -> List[str]:
        """
        获取支持的分类列表
        
        Returns:
            支持的分类列表
        """
        return cls.CATEGORY_LABELS
        
    def chunk_documents(self) -> List[Document]:
        """
        Markdown结构感知分块
        Returns:
            分块后的文档列表(chunks)
        """
        logger.info("正在进行Markdown结构感知分块...")

        if not self.documents:
            raise ValueError("文档为空,请先加载文档")
        
        # 使用langchain提供的Markdown标题分割器
        chunks = self._markdown_header_split()

        # 为每个chunk单独提供元数据
        for i,chunk in enumerate(chunks):
            if 'chunk_id' not in chunk.metadata:
                chunk.metadata['chunk_id'] = str(uuid.uuid4())
            chunk.metadata['batch_index'] = i
            chunk.metadata['chunk_size'] = len(chunk.page_content)

        self.chunks = chunks
        logger.info(f'成功分块为 {len(chunks)} 个chunk.')
        return chunks
    
    def _markdown_header_split(self) -> List[Document]:
        """
        使用Markdown标题分割器进行结构化分割

        Returns:
            按标题结构分割的文档列表
        """
        # 定义最小分割单元为三级标题,再小的不单独作为一个chunk,为语义完整性考虑
        # TODO:后续修改标题分割策略,比较一下效果
        header_to_split_on = [
            ("#","主标题"),
            ("##","二级标题"),
            ("###","三级标题")
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=header_to_split_on,
            strip_headers=False # 保留标题信息
        )

        all_chunks = []

        for doc in self.documents:
            try:
                # 检查文档内容是否包含Markdown标题
                content_preview = doc.page_content[:200]
                has_headers = any(line.strip().startswith('#') for line in content_preview.split('\n'))

                if not has_headers:
                    logger.warning(f"文档 {doc.metadata.get('dish_name', '未知')} 内容中没有发现Markdown标题")
                    logger.debug(f"内容预览: {content_preview}")
                
                md_chunks = markdown_splitter.split_text(doc.page_content)

                logger.debug(f'文档{doc.metadata.get("title", "未知")} 分割为{len(md_chunks)}个chunk')

                if len(md_chunks) <= 1:
                    logger.warning(f'文档{doc.metadata.get("title", "未知")}未能正常分块')

                # 为每个子chunks建立与父文档的映射关系(通过metadata)
                parent_id = doc.metadata['parent_id']
                for i,chunk in enumerate(md_chunks):
                    child_id = str(uuid.uuid4())

                    chunk.metadata.update(doc.metadata)
                    chunk.metadata.update({
                        "chunk_id": child_id,
                        "parent_id": parent_id,
                        "doc_type": "child",  # 标记为子文档
                        "chunk_index": i      # 在父文档中的位置
                    })

                    self.parent_child_map[child_id] = parent_id

                all_chunks.extend(md_chunks)

            except Exception as e:
                logger.warning(f"文档 {doc.metadata.get('source', '未知')} Markdown分割失败: {e}")
                # 如果Markdown分割失败，将整个文档作为一个chunk
                child_id = str(uuid.uuid4())
                doc.metadata.update({
                    "chunk_id": child_id,
                    "doc_type": "child",
                    "chunk_index": 0
                })
                self.parent_child_map[child_id] = doc.metadata['parent_id']
                all_chunks.append(doc)
        
        logger.info(f"Markdown结构分割完成，生成 {len(all_chunks)} 个结构化块")
        return all_chunks
    
    def filter_documents_by_category(self, category: str) -> List[Document]:
        """
        按分类过滤文档
        
        Args:
            category: 菜品分类
            
        Returns:
            过滤后的文档列表
        """
        return [doc for doc in self.documents if doc.metadata.get('category') == category]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据统计信息

        Returns:
            统计信息字典
        """
        if not self.documents:
            return {}

        categories = {}

        for doc in self.documents:
            # 统计分类
            category = doc.metadata.get('category', '未知')
            categories[category] = categories.get(category, 0) + 1

        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.chunks),
            'categories': categories,
            'avg_chunk_size': sum(chunk.metadata.get('chunk_size', 0) for chunk in self.chunks) / len(self.chunks) if self.chunks else 0
        }
    
    def export_metadata(self, output_path: str):
        """
        导出元数据到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        import json
        
        metadata_list = []
        for doc in self.documents:
            metadata_list.append({
                'source': doc.metadata.get('source'),
                'title': doc.metadata.get('tile'),
                'category': doc.metadata.get('category'),
                'content_length': len(doc.page_content)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"元数据已导出到: {output_path}")

    def get_parent_documents(self, child_chunks: List[Document]) -> List[Document]:
        """
        根据子块获取对应的父文档（智能去重）

        Args:
            child_chunks: 检索到的子块列表

        Returns:
            对应的父文档列表（去重，按相关性排序）
        """
        # 统计每个父文档被匹配的次数（相关性指标）
        parent_relevance = {}
        parent_docs_map = {}

        # 收集所有相关的父文档ID和相关性分数
        for chunk in child_chunks:
            parent_id = chunk.metadata.get("parent_id")
            if parent_id:
                # 增加相关性计数
                parent_relevance[parent_id] = parent_relevance.get(parent_id, 0) + 1

                # 缓存父文档（避免重复查找）
                if parent_id not in parent_docs_map:
                    for doc in self.documents:
                        if doc.metadata.get("parent_id") == parent_id:
                            parent_docs_map[parent_id] = doc
                            break

        # 按相关性排序（匹配次数多的排在前面）
        sorted_parent_ids = sorted(parent_relevance.keys(),
                                 key=lambda x: parent_relevance[x],
                                 reverse=True)

        # 构建去重后的父文档列表
        parent_docs = []
        for parent_id in sorted_parent_ids:
            if parent_id in parent_docs_map:
                parent_docs.append(parent_docs_map[parent_id])

        # 收集父文档名称和相关性信息用于日志
        parent_info = []
        for doc in parent_docs:
            dish_name = doc.metadata.get('dish_name', '未知菜品')
            parent_id = doc.metadata.get('parent_id')
            relevance_count = parent_relevance.get(parent_id, 0)
            parent_info.append(f"{dish_name}({relevance_count}块)")

        logger.info(f"从 {len(child_chunks)} 个子块中找到 {len(parent_docs)} 个去重父文档: {', '.join(parent_info)}")
        return parent_docs