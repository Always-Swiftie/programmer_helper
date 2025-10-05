"""
RAG系统测试脚本
"""

import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from main import ProgrammerHelperRAGSystem
from config import RAGConfig

def test_rag_system():
    """测试RAG系统的基本功能"""
    
    print("🧪 开始测试程序员面试助手RAG系统")
    print("=" * 50)
    
    try:
        # 创建配置
        config = RAGConfig(
            data_path="../knowledge_base/docs",
            top_k=3,
            temperature=0.1
        )
        
        # 创建系统实例
        system = ProgrammerHelperRAGSystem(config)
        
        # 初始化系统
        print("\n🚀 初始化系统...")
        system.initialize_system(force_rebuild=False)
        
        # 获取系统统计信息
        print("\n📊 系统统计信息:")
        stats = system.get_system_stats()
        print(f"   文档总数: {stats.get('total_documents', 0)}")
        print(f"   文档块总数: {stats.get('total_chunks', 0)}")
        if 'categories' in stats:
            print(f"   分类统计: {stats['categories']}")
        
        # 测试查询
        test_questions = [
            "Java中HashMap和ConcurrentHashMap的区别是什么？",
            "什么是Spring Boot？",
            "MySQL索引的原理是什么？",
            "什么是JVM垃圾回收？"
        ]
        
        print("\n🤔 开始测试查询功能...")
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- 测试问题 {i} ---")
            print(f"问题: {question}")
            try:
                answer = system.query(question)
                print(f"回答: {answer[:200]}...")  # 只显示前200个字符
                print("✅ 查询成功")
            except Exception as e:
                print(f"❌ 查询失败: {e}")
        
        print("\n🎉 RAG系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("MOONSHOT_API_KEY"):
        print("❌ 请先设置 MOONSHOT_API_KEY 环境变量")
        print("   例如: export MOONSHOT_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    test_rag_system()