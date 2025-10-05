# 程序员面试助手 RAG系统

一个基于检索增强生成(RAG)技术的Java后端开发面试知识库问答系统。

## ✨ 功能特点

- 📚 **智能文档检索**: 基于向量相似度和BM25的混合检索
- 🤖 **智能问答**: 使用Moonshot AI大语言模型生成专业回答
- 🔄 **查询优化**: 自动分析和重写模糊查询
- 📂 **分类检索**: 支持按技术分类进行精确搜索
- 💭 **流式输出**: 支持实时流式回答生成
- 🎯 **面试导向**: 专门针对Java后端开发面试场景优化

## 🏗️ 系统架构

```
RAG系统
├── 数据准备模块 (data_preparation.py)
│   ├── Markdown文档加载
│   ├── 结构化分块处理
│   └── 元数据增强
├── 索引构建模块 (index_construction.py)
│   ├── BAAI/bge-small-zh-v1.5 嵌入
│   ├── FAISS向量索引
│   └── 索引持久化
├── 检索优化模块 (retrieval_optimization.py)
│   ├── 向量检索
│   ├── BM25关键词检索
│   └── RRF重排融合
├── 生成集成模块 (generation_integration.py)
│   ├── 查询重写优化
│   ├── 上下文构建
│   └── Moonshot AI回答生成
└── 主系统 (main.py)
    ├── 交互式CLI界面
    ├── 分类检索功能
    └── 系统统计信息
```

## 📋 环境要求

- Python 3.8+
- Moonshot API密钥
- 8GB+ 内存推荐

## 🚀 快速开始

### 1. 安装依赖

```bash
cd code
pip install -r requirements.txt
```

### 2. 设置API密钥

**Windows:**
```cmd
set MOONSHOT_API_KEY=your_moonshot_api_key_here
```

**Linux/Mac:**
```bash
export MOONSHOT_API_KEY='your_moonshot_api_key_here'
```

### 3. 启动系统

```bash
cd rag_modules
python run.py
```

## 🎮 使用方法

### 交互式问答

启动后直接输入问题即可：

```
💭 请输入您的问题: Java中HashMap和ConcurrentHashMap的区别是什么？

🤔 正在思考您的问题: Java中HashMap和ConcurrentHashMap的区别是什么？

💡 回答:
HashMap和ConcurrentHashMap的主要区别在于线程安全性...
```

### 可用命令

- `help` - 显示帮助信息
- `stats` - 显示系统统计信息  
- `category <分类> <问题>` - 按分类搜索
- `quit/exit` - 退出系统

### 分类检索示例

```
💭 请输入您的问题: category Java基础 什么是面向对象编程？

🔍 在 'Java基础' 分类中搜索: 什么是面向对象编程？

💡 回答:
面向对象编程(OOP)是一种编程范式...
```

## 📊 系统配置

在 `config.py` 中可以自定义以下配置：

```python
@dataclass
class RAGConfig:
    # 路径配置
    data_path: str = "../knowledge_base/docs"  
    index_save_path: str = "./vector_index"    
    
    # 模型配置
    embedding_model: str = "BAAI/bge-small-zh-v1.5"  
    llm_model: str = "kimi-k2-0711-preview"          
    
    # 检索配置
    top_k: int = 5                    
    chunk_size: int = 1000            
    chunk_overlap: int = 200          
    
    # 生成配置
    temperature: float = 0.1          
    max_tokens: int = 2048            
    
    # 系统配置
    log_level: str = "INFO"           
    enable_query_rewrite: bool = True 
```

## 📁 知识库结构

知识库位于 `knowledge_base/docs/` 目录，包含以下技术分类：

- `java/` - Java核心知识
- `database/` - 数据库相关
- `distributed-system/` - 分布式系统
- `high-performance/` - 高性能优化
- `tools/` - 开发工具
- ... 更多分类

## 🔧 测试系统

运行测试脚本验证系统功能：

```bash
python test_system.py
```

## 📝 API使用

也可以通过编程方式使用：

```python
from main import ProgrammerHelperRAGSystem
from config import RAGConfig

# 创建系统实例
system = ProgrammerHelperRAGSystem()

# 初始化
system.initialize_system()

# 查询
answer = system.query("什么是Spring Boot？")
print(answer)

# 流式查询
for chunk in system.query_stream("JVM垃圾回收机制"):
    print(chunk, end='')

# 分类查询
answer = system.search_by_category("MySQL索引原理", "数据库")
print(answer)
```

## 📊 性能优化

- **索引缓存**: 首次构建后会保存向量索引，后续启动直接加载
- **混合检索**: 结合语义检索和关键词检索提高准确性
- **查询重写**: 自动优化模糊查询提升检索效果
- **分块策略**: 基于Markdown结构的智能分块

## 🤝 贡献指南

欢迎提交Issue和Pull Request来完善这个项目！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，请提交Issue或发送邮件。

---

**祝您面试顺利！🎉**