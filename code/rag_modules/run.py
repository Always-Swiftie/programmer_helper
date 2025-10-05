"""
程序员面试助手RAG系统启动脚本
"""

import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查API密钥
    if not os.getenv("MOONSHOT_API_KEY"):
        print("❌ 未找到 MOONSHOT_API_KEY 环境变量")
        print("   请设置您的Moonshot API密钥:")
        print("   Windows: set MOONSHOT_API_KEY=your_api_key_here")
        print("   Linux/Mac: export MOONSHOT_API_KEY='your_api_key_here'")
        return False
    
    # 检查知识库路径
    knowledge_base_path = Path("../knowledge_base/docs")
    if not knowledge_base_path.exists():
        print(f"❌ 知识库路径不存在: {knowledge_base_path.absolute()}")
        return False
    
    print("✅ 环境检查通过")
    return True

def main():
    """主函数"""
    print("🚀 程序员面试助手RAG系统")
    print("="*60)
    
    # 检查环境
    if not check_environment():
        return
    
    try:
        # 导入主模块
        from main import create_interactive_cli
        
        # 启动交互式命令行界面
        create_interactive_cli()
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖都已正确安装")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()