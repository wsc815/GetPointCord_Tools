#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取指定文件夹下所有JSON标注文件中target_point的坐标并输出到txt文件
调用 GetPointCord 模块来处理单个文件
"""

import sys
import os
from pathlib import Path

# 导入原有的单文件处理模块
try:
    from GetPointCord import extract_target_points, save_to_txt
except ImportError:
    print("错误: 找不到 GetPointCord.py 模块")
    print("请确保 GetPointCord.py 文件在同一目录下")
    sys.exit(1)


def process_directory(directory_path):
    """
    处理指定目录下的所有JSON文件

    Args:
        directory_path: 目录路径
    """
    directory = Path(directory_path)

    # 检查目录是否存在
    if not directory.exists():
        print(f"错误: 目录 '{directory_path}' 不存在")
        sys.exit(1)

    if not directory.is_dir():
        print(f"错误: '{directory_path}' 不是一个目录")
        sys.exit(1)

    # 查找所有JSON文件
    json_files = list(directory.glob('*.json'))

    if not json_files:
        print(f"警告: 在目录 '{directory_path}' 中未找到任何JSON文件")
        sys.exit(0)

    print(f"找到 {len(json_files)} 个JSON文件\n")
    print("=" * 60)

    # 统计信息
    success_count = 0
    skip_count = 0
    error_count = 0

    # 处理每个JSON文件
    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] 处理: {json_file.name}")

        try:
            # 调用原有模块的函数提取坐标
            coordinates = extract_target_points(json_file)

            if not coordinates:
                print(f"  ⚠ 未找到target_point标注，跳过")
                skip_count += 1
                continue

            # 生成输出文件路径
            output_path = json_file.parent / f"{json_file.stem}.txt"

            # 调用原有模块的函数保存到txt文件
            save_to_txt(coordinates, output_path)
            print(f"  ✓ 成功: 提取 {len(coordinates)} 个坐标点 → {output_path.name}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            error_count += 1

    # 显示统计信息
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"  成功: {success_count} 个文件")
    print(f"  跳过: {skip_count} 个文件（无target_point）")
    print(f"  错误: {error_count} 个文件")
    print("=" * 60)


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python script.py <目录路径>")
        print("示例: python script.py /path/to/annotations/")
        print("      python script.py ./annotations/")
        sys.exit(1)

    directory_path = sys.argv[1]

    print(f"目标目录: {directory_path}")
    print("正在扫描JSON文件...\n")

    # 处理目录
    process_directory(directory_path)


if __name__ == "__main__":
    main()