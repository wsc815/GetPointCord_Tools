#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组织数据集文件并生成列表文件
1. 将同名图片和txt文件移动到以文件名命名的文件夹中
2. 生成train.list和test.list文件
"""

import sys
import shutil
from pathlib import Path


def organize_files(dataset_dir):
    """
    组织数据集文件结构并生成列表文件

    Args:
        dataset_dir: 数据集根目录，包含train和test子目录
    """
    root_path = Path(dataset_dir)

    if not root_path.exists() or not root_path.is_dir():
        print(f"错误: 目录 '{dataset_dir}' 不存在")
        sys.exit(1)

    # 处理train和test目录
    for subset in ['train', 'test']:
        subset_path = root_path / subset

        if not subset_path.exists():
            print(f"警告: 未找到 {subset} 目录，跳过")
            continue

        print(f"\n处理 {subset} 目录...")
        print("=" * 60)

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

        # 收集所有需要组织的文件对
        files_to_organize = []

        # 1. 查找目录中直接存在的图片和txt文件（需要组织）
        for item in subset_path.iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                txt_file = item.with_suffix('.txt')
                if txt_file.exists():
                    files_to_organize.append((item, txt_file))
                else:
                    print(f"  ⚠ 警告: {item.name} 没有对应的txt文件")

        # 2. 组织需要移动的文件
        organized_count = 0
        for image_file, txt_file in files_to_organize:
            folder_name = image_file.stem
            target_folder = subset_path / folder_name
            target_folder.mkdir(exist_ok=True)

            new_image_path = target_folder / image_file.name
            new_txt_path = target_folder / txt_file.name

            # 移动文件到新文件夹
            shutil.move(str(image_file), str(new_image_path))
            shutil.move(str(txt_file), str(new_txt_path))
            organized_count += 1
            print(f"  ✓ 组织: {folder_name}/")

        # 3. 扫描所有已经组织好的文件夹，收集配对
        pairs = []
        for folder in sorted(subset_path.iterdir()):
            if folder.is_dir():
                # 查找文件夹中的图片文件
                image_files = [f for f in folder.iterdir()
                               if f.is_file() and f.suffix.lower() in image_extensions]

                for image_file in image_files:
                    txt_file = image_file.with_suffix('.txt')

                    if txt_file.exists():
                        # 记录路径对（相对于根目录）
                        rel_image = image_file.relative_to(root_path)
                        rel_txt = txt_file.relative_to(root_path)

                        # 使用正斜杠
                        image_str = str(rel_image).replace('\\', '/')
                        txt_str = str(rel_txt).replace('\\', '/')

                        pairs.append((image_str, txt_str))

        # 按路径排序
        pairs.sort()

        print(f"\n{subset} 目录处理完成:")
        print(f"  组织了 {organized_count} 对文件")
        print(f"  共有 {len(pairs)} 对文件")

        # 生成列表文件
        if pairs:
            list_file = root_path / f"{subset}.list"
            with open(list_file, 'w', encoding='utf-8') as f:
                for img_path, txt_path in pairs:
                    f.write(f"{img_path} {txt_path}\n")
            print(f"  生成列表文件: {list_file.name}")

    print("\n" + "=" * 60)
    print("全部完成！")


def main():
    if len(sys.argv) != 2:
        print("使用方法: python Getlist.py <数据集根目录>")
        print("\n示例: python Getlist.py ./dataset")
        print("\n目录结构要求:")
        print("  dataset/")
        print("  ├── train/")
        print("  │   ├── img01.jpg")
        print("  │   ├── img01.txt")
        print("  │   ├── img02.jpg")
        print("  │   └── img02.txt")
        print("  └── test/")
        print("      ├── img03.jpg")
        print("      ├── img03.txt")
        print("      └── ...")
        print("\n执行后:")
        print("  dataset/")
        print("  ├── train/")
        print("  │   ├── img01/")
        print("  │   │   ├── img01.jpg")
        print("  │   │   └── img01.txt")
        print("  │   └── img02/")
        print("  │       ├── img02.jpg")
        print("  │       └── img02.txt")
        print("  ├── test/")
        print("  │   └── img03/")
        print("  │       ├── img03.jpg")
        print("  │       └── img03.txt")
        print("  ├── train.list")
        print("  └── test.list")
        sys.exit(1)

    organize_files(sys.argv[1])


if __name__ == "__main__":
    main()