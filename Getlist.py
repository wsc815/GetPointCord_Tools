#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据原始图像路径和批量 txt 路径，自动构建 P2PNet 数据集，并按比例划分 train / val / test。

命令行用法：
    python GetList.py <images_dir> <txt_dir> <output_dataset_root> <train_ratio> <val_ratio> <test_ratio>

参数说明：
    images_dir           : 原始图像所在目录（只包含图片文件，当前版本不递归子目录）
    txt_dir              : 上一个 batch 脚本生成的 txt 文件所在目录（文件名需和图片同名）
    output_dataset_root  : 输出的数据集根目录
    train_ratio          : 训练集比例（0~1 的小数）
    val_ratio            : 验证集比例（0~1 的小数）
    test_ratio           : 测试集比例（0~1 的小数）

要求：
    train_ratio + val_ratio + test_ratio ≈ 1.0（允许轻微误差，比如 0.7 0.15 0.15）

输出结构示例：
    output_dataset_root/
      ├── train/
      ├── val/
      ├── test/
      ├── train.list
      ├── val.list
      └── test.list
"""

import sys
import shutil
import random
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}


def is_image_file(path: Path) -> bool:
    """判断是否为支持的图片文件"""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def collect_pairs(images_dir: Path, txt_dir: Path):
    """
    从图像目录和 txt 目录中收集所有有效的 (image, txt) 配对。

    按文件名（不含后缀）匹配，例如：
        images_dir/img001.jpg   ↔   txt_dir/img001.txt

    返回：
        pairs: [(img_path, txt_path), ...]
    """
    if not images_dir.exists() or not images_dir.is_dir():
        print(f"错误: 图片目录 '{images_dir}' 不存在或不是目录")
        sys.exit(1)

    if not txt_dir.exists() or not txt_dir.is_dir():
        print(f"错误: txt 目录 '{txt_dir}' 不存在或不是目录")
        sys.exit(1)

    pairs = []
    missing_txt = 0

    # 为了方便后面检查“多余 txt”，先收集所有 txt stem
    txt_stems = {p.stem for p in txt_dir.iterdir() if p.is_file() and p.suffix.lower() == '.txt'}

    for img_file in sorted(images_dir.iterdir()):
        if not is_image_file(img_file):
            continue

        stem = img_file.stem
        txt_file = txt_dir / f"{stem}.txt"

        if not txt_file.exists():
            print(f"  ⚠ 警告: 图片 {img_file.name} 没有对应的 {stem}.txt，忽略该图片")
            missing_txt += 1
            continue

        pairs.append((img_file, txt_file))

    # 可选：提示有没有多余的 txt（没有对应图片）
    extra_txt = []
    image_stems = {p.stem for p, _ in pairs}
    for stem in txt_stems:
        if stem not in image_stems:
            extra_txt.append(stem)

    print("\n数据配对情况：")
    print(f"  有效图像+txt 配对数: {len(pairs)}")
    print(f"  没有 txt 的图片数  : {missing_txt}")
    if extra_txt:
        print(f"  ⚠ 有 {len(extra_txt)} 个 txt 没有对应图片（示例前几个）： {extra_txt[:5]}")

    if not pairs:
        print("错误: 没有找到任何有效的图片+txt 配对，无法构建数据集")
        sys.exit(1)

    return pairs


def split_train_val_test(pairs, train_ratio: float, val_ratio: float, test_ratio: float, seed: int = 42):
    """
    将 pairs 按 train/val/test 比例随机划分。

    返回：
        train_pairs, val_pairs, test_pairs
    """
    # 基本合法性检查
    for name, r in zip(["train_ratio", "val_ratio", "test_ratio"], [train_ratio, val_ratio, test_ratio]):
        if not (0.0 < r < 1.0):
            print(f"错误: {name} 必须在 (0, 1) 之间，而不是 {r}")
            sys.exit(1)

    ratio_sum = train_ratio + val_ratio + test_ratio
    if abs(ratio_sum - 1.0) > 1e-3:
        print(f"错误: train_ratio + val_ratio + test_ratio 之和必须约等于 1.0，当前为 {ratio_sum:.4f}")
        sys.exit(1)

    random.seed(seed)
    pairs_shuffled = pairs[:]
    random.shuffle(pairs_shuffled)

    total = len(pairs_shuffled)

    # 初步按比例计算数量
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)

    # 先保证至少为 1
    train_count = max(1, train_count)
    val_count = max(1, val_count)

    # 预留给 test 的数量
    remaining = total - train_count - val_count
    if remaining <= 0:
        # 如果 test 分不到样本，就从 train/val 中“借”一点
        remaining = 1
        # 简单调整：尽量保持 train 比较大
        if train_count > 1:
            train_count -= 1
        elif val_count > 1:
            val_count -= 1
        else:
            # 极端情况：总样本过少，直接报错更合理
            print("错误: 样本总数太少，无法同时划分出 train/val/test 三个非空子集。")
            sys.exit(1)

    test_count = remaining

    # 做一下边界保护，防止越界
    if train_count + val_count + test_count != total:
        # 强制修正最后一个集合的数量
        test_count = total - train_count - val_count

    # 真正切分
    train_pairs = pairs_shuffled[:train_count]
    val_pairs = pairs_shuffled[train_count:train_count + val_count]
    test_pairs = pairs_shuffled[train_count + val_count:]

    print("\n数据划分：")
    print(f"  总样本数 : {total}")
    print(f"  训练集数 : {len(train_pairs)}")
    print(f"  验证集数 : {len(val_pairs)}")
    print(f"  测试集数 : {len(test_pairs)}")
    print(f"  实际训练比例: {len(train_pairs) / total:.3f}")
    print(f"  实际验证比例: {len(val_pairs) / total:.3f}")
    print(f"  实际测试比例: {len(test_pairs) / total:.3f}")

    return train_pairs, val_pairs, test_pairs


def build_subset(pairs, out_root: Path, subset_name: str):
    """
    根据给定的 (img_path, txt_path) 对，构建一个子集（train/val/test）结构，
    并返回 list 用的相对路径对。

    输出结构：
        out_root/subset_name/stem/stem.jpg
        out_root/subset_name/stem/stem.txt
    """
    out_subset_dir = out_root / subset_name
    out_subset_dir.mkdir(parents=True, exist_ok=True)

    list_pairs = []

    print(f"\n构建子集: {subset_name}")
    print(f"  输出目录: {out_subset_dir}")
    print("=" * 60)

    for img_path, txt_path in pairs:
        stem = img_path.stem
        target_folder = out_subset_dir / stem
        target_folder.mkdir(exist_ok=True)

        dst_img = target_folder / img_path.name
        dst_txt = target_folder / txt_path.name

        # 复制（保留原始数据）
        shutil.copy2(str(img_path), str(dst_img))
        shutil.copy2(str(txt_path), str(dst_txt))

        rel_img = dst_img.relative_to(out_root)
        rel_txt = dst_txt.relative_to(out_root)

        img_str = str(rel_img).replace('\\', '/')
        txt_str = str(rel_txt).replace('\\', '/')

        list_pairs.append((img_str, txt_str))
        print(f"  ✓ 组织样本: {subset_name}/{stem}/")

    # 写 .list 文件
    if list_pairs:
        list_file = out_root / f"{subset_name}.list"
        with open(list_file, 'w', encoding='utf-8') as f:
            for img_path_str, txt_path_str in list_pairs:
                f.write(f"{img_path_str} {txt_path_str}\n")
        print(f"\n  ✓ 生成列表文件: {list_file.name} （共 {len(list_pairs)} 行）")
    else:
        print(f"  ⚠ {subset_name} 没有样本，未生成 {subset_name}.list")

    return list_pairs


def print_usage(prog_name: str):
    print(f"使用方法:")
    print(f"  python {prog_name} <images_dir> <txt_dir> <output_dataset_root> <train_ratio> <val_ratio> <test_ratio>\n")
    print("参数说明：")
    print("  images_dir          : 原始图像目录（只包含图像文件）")
    print("  txt_dir             : 批量生成的 txt 目录（文件名需与图片同名，如 img001.jpg ↔ img001.txt）")
    print("  output_dataset_root : 输出的数据集根目录")
    print("  train_ratio         : 训练集比例（0~1 的小数）")
    print("  val_ratio           : 验证集比例（0~1 的小数）")
    print("  test_ratio          : 测试集比例（0~1 的小数）")
    print("\n要求：train_ratio + val_ratio + test_ratio ≈ 1.0\n")
    print("输出结构示例：")
    print("  output_dataset_root/")
    print("    ├── train/")
    print("    ├── val/")
    print("    ├── test/")
    print("    ├── train.list")
    print("    ├── val.list")
    print("    └── test.list")


def main():
    argv = sys.argv
    prog = Path(argv[0]).name

    if len(argv) != 7:
        print_usage(prog)
        sys.exit(1)

    images_dir = Path(argv[1])
    txt_dir = Path(argv[2])
    out_root = Path(argv[3])

    try:
        train_ratio = float(argv[4])
        val_ratio = float(argv[5])
        test_ratio = float(argv[6])
    except ValueError:
        print(f"错误: train_ratio, val_ratio, test_ratio 必须是 0~1 的小数，例如 0.7 0.15 0.15")
        sys.exit(1)

    out_root.mkdir(parents=True, exist_ok=True)
    print(f"输出数据集根目录: {out_root.resolve()}")

    # 1. 收集所有有效 (image, txt) 对
    pairs = collect_pairs(images_dir, txt_dir)

    # 2. 按比例划分 train / val / test
    train_pairs, val_pairs, test_pairs = split_train_val_test(
        pairs,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        seed=42
    )

    # 3. 构建 train 子集
    build_subset(train_pairs, out_root, subset_name="train")

    # 4. 构建 val 子集
    build_subset(val_pairs, out_root, subset_name="val")

    # 5. 构建 test 子集
    build_subset(test_pairs, out_root, subset_name="test")

    print("\n" + "=" * 60)
    print("全部完成！数据集已构建完成，可用于 P2PNet 训练 / 验证 / 测试。")


if __name__ == "__main__":
    main()
