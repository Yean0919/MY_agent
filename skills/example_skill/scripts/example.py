"""示例脚本"""

import argparse


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="示例 Skill 脚本")
    parser.add_argument("--input", help="输入文件路径")
    parser.add_argument("--output", help="输出文件路径")
    args = parser.parse_args()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
