#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取指定文件夹下所有 JSON 标注文件中 point 类型标注的坐标并输出到 txt 文件

依赖 GetPointCord.py 中的：
    - extract_target_points(json_path, target_labels=None)
    - save_to_txt(coordinates, output_path)

命令行用法示例：

    # 1）提取所有 point 类型的点（不按 label 过滤），txt 集中输出到 output_dir
    python Batch_GetPointCord.py /path/to/json_folder /path/to/output_folder

    # 2）只提取指定标签的 point 点
    python Batch_GetPointCord.py /path/to/json_folder /path/to/output_folder hzbokchoy broadleaf_weed

    # 3）显式声明提取所有 point 点（等价于示例1）
    python Batch_GetPointCord.py /path/to/json_folder /path/to/output_folder all

说明：
    - 所有生成的 txt 文件将放在 output_folder 中
    - txt 文件名与 json 文件名相同，仅扩展名不同（xxx.json -> xxx.txt）
"""

import sys
from pathlib import Path

# 导入单文件处理模块
try:
    from GetPointCord import extract_target_points, save_to_txt
except ImportError:
    print("错误: 找不到 GetPointCord.py 模块")
    print("请确保 GetPointCord.py 文件在同一目录下")
    sys.exit(1)


def process_directory(json_dir: Path, output_dir: Path, target_labels=None):
    """
    处理指定目录下的所有 JSON 文件

    Args:
        json_dir: JSON 文件所在目录
        output_dir: 输出 txt 文件所在目录
        target_labels: 需要保留的标签列表（list[str] 或 None）
                       - None: 不按标签过滤，提取所有 shape_type == "point" 的点
                       - list: 只保留 label 在该列表中的点
    """
    # 检查目录是否存在
    if not json_dir.exists():
        print(f"错误: 目录 '{json_dir}' 不存在")
        sys.exit(1)

    if not json_dir.is_dir():
        print(f"错误: '{json_dir}' 不是一个目录")
        sys.exit(1)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 查找所有 JSON 文件（仅当前目录，不递归）
    json_files = list(json_dir.glob('*.json'))

    if not json_files:
        print(f"警告: 在目录 '{json_dir}' 中未找到任何 JSON 文件")
        sys.exit(0)

    print(f"JSON 目录: {json_dir}")
    print(f"输出目录: {output_dir}")
    if target_labels is None:
        print("标签过滤: 关闭（提取所有 shape_type == 'point' 的点）")
    else:
        print(f"标签过滤: 仅保留标签 {target_labels}")
    print()
    print(f"找到 {len(json_files)} 个 JSON 文件")
    print("=" * 60)

    # 统计信息
    success_count = 0
    skip_count = 0
    error_count = 0

    # 处理每个 JSON 文件
    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] 处理: {json_file.name}")

        try:
            # 提取坐标
            coordinates = extract_target_points(json_file, target_labels=target_labels)

            if not coordinates:
                print("  ⚠ 未找到符合条件的 point 标注，跳过")
                skip_count += 1
                continue

            # 生成输出文件路径（全部集中到 output_dir）
            output_path = output_dir / f"{json_file.stem}.txt"

            # 保存到 txt 文件
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
    print(f"  跳过: {skip_count} 个文件（无符合条件的 point 标注）")
    print(f"  错误: {error_count} 个文件")
    print("=" * 60)


def parse_args(argv):
    """
    解析命令行参数：
        argv[1] = JSON 目录路径
        argv[2] = 输出 txt 目录路径
        argv[3:] = 可选标签列表，或 'all'

    Returns:
        json_dir: Path
        output_dir: Path
        target_labels: list[str] or None
    """
    prog = Path(argv[0]).name

    if len(argv) < 3:
        print(f"使用方法: python {prog} <json目录> <输出目录> [标签1 标签2 ... | all]")
        print("\n示例1: python {prog} ./json ./points_txt")
        print("       （提取所有 shape_type == 'point' 的点）")
        print("\n示例2: python {prog} ./json ./points_txt hzbokchoy broadleaf_weed")
        print("       （只提取指定标签的 point 点）")
        print("\n示例3: python {prog} ./json ./points_txt all")
        print("       （显式指定提取所有 point 点）")
        sys.exit(1)

    json_dir = Path(argv[1])
    output_dir = Path(argv[2])

    if len(argv) == 3:
        target_labels = None
    else:
        labels = argv[3:]
        if len(labels) == 1 and labels[0].lower() == 'all':
            target_labels = None
        else:
            target_labels = labels

    return json_dir, output_dir, target_labels


def main():
    """主函数"""
    json_dir, output_dir, target_labels = parse_args(sys.argv)

    print("正在扫描 JSON 文件...\n")

    process_directory(json_dir, output_dir, target_labels=target_labels)


if __name__ == "__main__":
    main()
