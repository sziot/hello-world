# test_cli.py
import argparse

def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="一个简单的 CLI 工具示例")
    
    # 添加参数
    parser.add_argument('--name', type=str, help='你的名字', required=True)
    parser.add_argument('--greet', action='store_true', help='是否打印问候语')

    # 解析参数
    args = parser.parse_args()

    # 根据参数执行功能
    if args.greet:
        print(f"你好, {args.name}!")
    else:
        print(f"欢迎, {args.name}!")

if __name__ == "__main__":
    main()
