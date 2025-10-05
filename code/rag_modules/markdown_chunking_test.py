"""
数据准备模块完整测试程序
测试Markdown文档加载和分块功能
"""
import os
import sys
import logging
from pathlib import Path

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_preparation import DataPreparationModule

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_preparation():
    """测试数据准备模块的完整功能"""
    
    print("=" * 60)
    print("📚 数据准备模块测试程序")
    print("=" * 60)
    
    # 构建知识库路径
    current_dir = Path(__file__).parent
    knowledge_base_path = current_dir.parent / "knowledge_base" / "docs" / "java"
    
    print(f"📁 测试数据路径: {knowledge_base_path}")
    
    # 检查路径是否存在
    if not knowledge_base_path.exists():
        print(f"❌ 错误: 知识库路径不存在: {knowledge_base_path}")
        print("请确保路径正确，或创建测试数据")
        create_test_data(knowledge_base_path)
        return
    
    try:
        # 1. 初始化数据准备模块
        print("\n🔧 初始化数据准备模块...")
        module = DataPreparationModule()
        module(str(knowledge_base_path))  # 调用__call__方法
        
        # 2. 加载文档
        print("\n📖 加载Markdown文档...")
        documents = module.load_documents()
        
        if not documents:
            print("❌ 没有找到任何Markdown文档")
            return
        
        print(f"✅ 成功加载 {len(documents)} 个文档")
        
        # 3. 显示文档信息
        print("\n📋 文档信息概览:")
        for i, doc in enumerate(documents, 1):
            title = doc.metadata.get('title', '未知')
            category = doc.metadata.get('category', '未知分类')
            content_length = len(doc.page_content)
            source = doc.metadata.get('source', '')
            
            print(f"  {i}. 📄 {title}")
            print(f"     分类: {category}")
            print(f"     大小: {content_length} 字符")
            print(f"     路径: {Path(source).name}")
            
            # 显示内容预览
            preview = doc.page_content[:150].replace('\n', ' ').strip()
            if len(doc.page_content) > 150:
                preview += "..."
            print(f"     预览: {preview}")
            print()
        
        # 4. 执行分块处理
        print("🔪 执行Markdown结构化分块...")
        chunks = module.chunk_documents()
        
        print(f"✅ 成功分块为 {len(chunks)} 个chunk")
        
        # 5. 分析分块结果
        print("\n📊 分块结果分析:")
        
        # 按父文档分组显示
        parent_chunks = {}
        for chunk in chunks:
            parent_id = chunk.metadata.get('parent_id', 'unknown')
            parent_title = chunk.metadata.get('title', '未知文档')
            
            if parent_id not in parent_chunks:
                parent_chunks[parent_id] = {
                    'title': parent_title,
                    'chunks': []
                }
            parent_chunks[parent_id]['chunks'].append(chunk)
        
        # 显示每个文档的分块情况
        for parent_id, info in parent_chunks.items():
            print(f"\n📄 {info['title']} ({len(info['chunks'])} 个chunk):")
            
            for i, chunk in enumerate(info['chunks'], 1):
                chunk_size = len(chunk.page_content)
                
                # 提取标题信息
                headers = []
                for key, value in chunk.metadata.items():
                    if key in ['主标题', '二级标题', '三级标题'] and value:
                        headers.append(f"{key}: {value}")
                
                header_info = " | ".join(headers) if headers else "无标题结构"
                
                print(f"  {i}. Chunk-{chunk.metadata.get('chunk_index', i)} ({chunk_size} 字符)")
                print(f"     标题: {header_info}")
                
                # 显示内容预览
                preview = chunk.page_content[:100].replace('\n', ' ').strip()
                if len(chunk.page_content) > 100:
                    preview += "..."
                print(f"     内容: {preview}")
                print()
        
        # 6. 显示统计信息
        print("📈 统计信息:")
        stats = module.get_statistics()
        
        print(f"  • 总文档数: {stats.get('total_documents', 0)}")
        print(f"  • 总chunk数: {stats.get('total_chunks', 0)}")
        print(f"  • 平均chunk大小: {stats.get('avg_chunk_size', 0):.1f} 字符")
        
        # 分类统计
        categories = stats.get('categories', {})
        if categories:
            print("  • 分类分布:")
            for category, count in categories.items():
                print(f"    - {category}: {count} 个文档")
        
        # 7. 测试分类过滤功能
        print("\n🔍 测试分类过滤功能:")
        for category in module.get_supported_categories():
            filtered_docs = module.filter_documents_by_category(category)
            if filtered_docs:
                print(f"  • {category}: {len(filtered_docs)} 个文档")
        
        # 8. 测试父子文档映射
        print("\n🔗 测试父子文档映射:")
        if chunks:
            # 选择前3个chunk测试父文档获取
            test_chunks = chunks[:3]
            parent_docs = module.get_parent_documents(test_chunks)
            
            print(f"  从 {len(test_chunks)} 个chunk中获取到 {len(parent_docs)} 个父文档:")
            for doc in parent_docs:
                print(f"  • {doc.metadata.get('title', '未知')}")
        
        # 9. 导出元数据
        metadata_file = current_dir / "test_metadata.json"
        print(f"\n💾 导出元数据到: {metadata_file}")
        module.export_metadata(str(metadata_file))
        
        print("\n✅ 测试完成！所有功能正常工作。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def create_test_data(knowledge_base_path: Path):
    """创建测试数据"""
    print(f"\n🔧 创建测试数据到: {knowledge_base_path}")
    
    # 创建目录结构
    basis_dir = knowledge_base_path / "basis"
    collection_dir = knowledge_base_path / "collection"
    
    basis_dir.mkdir(parents=True, exist_ok=True)
    collection_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建Java基础测试文件
    basis_content = """# Java基础教程

本文档介绍Java编程语言的基础知识。

## 数据类型

Java有丰富的数据类型系统。

### 基本数据类型

Java提供了8种基本数据类型：

- byte: 8位有符号整数
- short: 16位有符号整数  
- int: 32位有符号整数
- long: 64位有符号整数
- float: 32位浮点数
- double: 64位浮点数
- char: 16位Unicode字符
- boolean: 布尔值

### 引用数据类型

引用数据类型包括：
- 类(Class)
- 接口(Interface) 
- 数组(Array)

## 控制结构

Java提供了多种控制结构来控制程序流程。

### 条件语句

#### if-else语句
```java
if (condition) {
    // 代码块
} else {
    // 代码块
}
```

#### switch语句
```java
switch (variable) {
    case value1:
        // 代码
        break;
    default:
        // 默认代码
}
```

### 循环语句

#### for循环
```java
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}
```

#### while循环
```java
while (condition) {
    // 循环体
}
```
"""
    
    # 创建集合框架测试文件
    collection_content = """# Java集合框架

Java集合框架是Java中用于存储和操作对象集合的统一架构。

## 集合层次结构

Java集合框架的核心接口包括：

### Collection接口

Collection是所有集合类的根接口。

#### List接口
List是有序集合，允许重复元素：
- ArrayList: 动态数组实现
- LinkedList: 双向链表实现
- Vector: 同步的动态数组

#### Set接口  
Set是不允许重复元素的集合：
- HashSet: 哈希表实现
- TreeSet: 红黑树实现
- LinkedHashSet: 哈希表+链表实现

### Map接口

Map存储键值对映射关系：

#### HashMap
基于哈希表的Map实现：
```java
Map<String, Integer> map = new HashMap<>();
map.put("key", 123);
```

#### TreeMap
基于红黑树的有序Map：
```java
Map<String, Integer> treeMap = new TreeMap<>();
```

## 集合操作

### 遍历集合
```java
// 使用增强for循环
for (String item : list) {
    System.out.println(item);
}

// 使用迭代器
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}
```

### 集合排序
```java
Collections.sort(list);
Collections.sort(list, comparator);
```
"""
    
    # 写入测试文件
    (basis_dir / "java_basics.md").write_text(basis_content, encoding='utf-8')
    (collection_dir / "java_collections.md").write_text(collection_content, encoding='utf-8')
    
    print("✅ 测试数据创建完成！")
    print(f"  - {basis_dir / 'java_basics.md'}")
    print(f"  - {collection_dir / 'java_collections.md'}")

if __name__ == "__main__":
    test_data_preparation()