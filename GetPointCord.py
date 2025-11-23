#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取 JSON 标注文件中 point 类型标注的坐标并输出到 txt 文件

支持两种使用方式：
1）不指定标签：提取所有 shape_type == "point" 的点
2）指定标签列表：只提取给定标签名的 point 点

命令行示例：
    # 提取所有 point 点
    python GetPointCord.py /path/to/annotation.json

    # 只提取 hzbokchoy 和 broadleaf_weed 两种标签
    python GetPointCord.py /path/to/annotation.json hzbokchoy broadleaf_weed

    # 显式提取全部 point 点（等价于不写后面的标签）
    python GetPointCord.py /path/to/annotation.json all
"""

import json
import sys
import os
from pathlib import Path


def extract_target_points(json_path, target_labels=None):
    """
    从 JSON 文件中提取 point 类型标注的坐标

    Args:
        json_path: JSON 文件路径
        target_labels: 需要保留的标签列表（list[str] 或 None）
                       - None: 不按标签过滤，提取所有 shape_type == "point" 的点
                       - list: 只保留 label 在该列表中的点

    Returns:
        list[tuple[int, int]]: 所有符合条件的点坐标 [(x1, y1), (x2, y2), ...]
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{json_path}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: '{json_path}' 不是有效的 JSON 文件")
        sys.exit(1)

    points_list = []

    shapes = data.get('shapes', [])
    for shape in shapes:
        label = shape.get('label', '')
        shape_type = shape.get('shape_type', '')

        # 只处理 point 类型标注
        if shape_type != 'point':
            continue

        # 如果指定了标签列表，则进行过滤
        if target_labels is not None and label not in target_labels:
            continue

        # 获取坐标
        points = shape.get('points', [])
        if not points:
            continue

        # point 类型通常只有一个坐标点，取第一个
        x, y = points[0]
        points_list.append((x, y))

    return points_list


def save_to_txt(coordinates, output_path):
    """
    将坐标保存到 txt 文件

    Args:
        coordinates: 坐标列表 [(x1, y1), (x2, y2), ...]
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for x, y in coordinates:
                # 将坐标转换为整数（像素索引从 0 开始）
                f.write(f"{int(x)} {int(y)}\n")

        print(f"成功提取 {len(coordinates)} 个点坐标")
        print(f"输出文件: {output_path}")
    except Exception as e:
        print(f"错误: 无法写入文件 '{output_path}' - {e}")
        sys.exit(1)


def parse_args(argv):
    """
    解析命令行参数：
        argv[1] = json 文件路径
        argv[2:] = 可选标签列表，或 'all'

    Returns:
        json_path: str
        target_labels: list[str] or None
    """
    if len(argv) < 2:
        print("使用方法: python GetPointCord.py <json文件路径> [标签1 标签2 ... | all]")
        print("示例1: python GetPointCord.py /path/to/annotation.json")
        print("       （提取所有 shape_type == 'point' 的点）")
        print("示例2: python GetPointCord.py /path/to/annotation.json hzbokchoy broadleaf_weed")
        print("       （只提取指定标签的 point 点）")
        print("示例3: python GetPointCord.py /path/to/annotation.json all")
        print("       （显式指定提取所有 point 点）")
        sys.exit(1)

    json_path = argv[1]

    if len(argv) == 2:
        # 未指定标签，默认提取所有 point 类型
        target_labels = None
    else:
        # 指定了标签
        labels = argv[2:]
        # 如果包含 all，则视为不按标签过滤
        if len(labels) == 1 and labels[0].lower() == 'all':
            target_labels = None
        else:
            target_labels = labels

    return json_path, target_labels


def main():
    """主函数"""
    json_path, target_labels = parse_args(sys.argv)

    # 验证文件是否存在
    if not os.path.exists(json_path):
        print(f"错误: 文件 '{json_path}' 不存在")
        sys.exit(1)

    # 生成输出文件路径（与输入文件同目录，扩展名改为 .txt）
    input_path = Path(json_path)
    output_path = input_path.parent / f"{input_path.stem}.txt"

    print(f"正在处理: {json_path}")
    if target_labels is None:
        print("标签过滤: 关闭（提取所有 shape_type == 'point' 的点）")
    else:
        print(f"标签过滤: 仅保留 {target_labels}")

    # 提取坐标
    coordinates = extract_target_points(json_path, target_labels=target_labels)

    if not coordinates:
        print("警告: 未找到任何符合条件的 point 标注")
        sys.exit(0)

    # 保存到 txt 文件
    save_to_txt(coordinates, output_path)


if __name__ == "__main__":
    main()
