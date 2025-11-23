#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取JSON标注文件中target_point的坐标并输出到txt文件
"""

import json
import sys
import os
from pathlib import Path


def extract_target_points(json_path):
    """
    从JSON文件中提取所有target_point的坐标

    Args:
        json_path: JSON文件路径

    Returns:
        list: 包含所有target_point坐标的列表 [(x1, y1), (x2, y2), ...]
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{json_path}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: '{json_path}' 不是有效的JSON文件")
        sys.exit(1)

    target_points = []

    # 遍历所有shapes
    if 'shapes' in data:
        for shape in data['shapes']:
            # 检查label是否为target_point
            if shape.get('label') == 'target_point':
                # 获取points坐标
                points = shape.get('points', [])
                if points and len(points) > 0:
                    # target_point通常只有一个坐标点
                    x, y = points[0]
                    target_points.append((x, y))

    return target_points


def save_to_txt(coordinates, output_path):
    """
    将坐标保存到txt文件

    Args:
        coordinates: 坐标列表 [(x1, y1), (x2, y2), ...]
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for x, y in coordinates:
                # 将坐标转换为整数（像素值从0开始）
                f.write(f"{int(x)} {int(y)}\n")
        print(f"成功提取 {len(coordinates)} 个target_point坐标")
        print(f"输出文件: {output_path}")
    except Exception as e:
        print(f"错误: 无法写入文件 '{output_path}' - {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python script.py <json文件路径>")
        print("示例: python script.py /path/to/annotation.json")
        sys.exit(1)

    json_path = sys.argv[1]

    # 验证文件是否存在
    if not os.path.exists(json_path):
        print(f"错误: 文件 '{json_path}' 不存在")
        sys.exit(1)

    # 生成输出文件路径（与输入文件同目录，扩展名改为.txt）
    input_path = Path(json_path)
    output_path = input_path.parent / f"{input_path.stem}.txt"

    print(f"正在处理: {json_path}")

    # 提取坐标
    coordinates = extract_target_points(json_path)

    if not coordinates:
        print("警告: 未找到任何target_point标注")
        sys.exit(0)

    # 保存到txt文件
    save_to_txt(coordinates, output_path)


if __name__ == "__main__":
    main()