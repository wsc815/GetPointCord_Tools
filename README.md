
# GetPointCord

**用于批量提取 JSON 标注文件中的 point 坐标，并自动组织为 P2PNet 格式数据集的实用工具集**

本仓库包含三个脚本，分别用于：

1. **GetPointCord.py**

   * 解析单个 JSON 标注文件
   * 提取 `shape_type="point"` 的标注
   * 输出为 `P2PNet` 所需的单独 `.txt` 文件

2. **Batch_GetPointCord.py**

   * 批量读取文件夹下所有 JSON
   * 自动批量生成所有 `.txt`（与 JSON 同名）
   * 支持按标签过滤（可选）

3. **GetList.py（或 BuildP2PNetDataset.py）**

   * 根据原始图像与批量生成的 `.txt`
   * 自动构建完整的 P2PNet 数据集结构
   * 自动划分 train/test
   * 自动生成 train.list / test.list

✔ 完整解决了从 JSON 标注 → P2PNet 数据格式的全部流程
✔ 避免手动整理文件，极大提高数据准备效率

---

# 📁 仓库结构

```
GetPointCord/
│── GetPointCord.py           # 单个 JSON → txt
│── Batch_GetPointCord.py     # 批量 JSON → txt
│── GetList.py                # 构建 P2PNet 数据集
│── README.md
│── example/（可选示例）
```

---

# 📌 1. GetPointCord.py

### 作用

从单个 JSON 文件中提取带有 `"shape_type": "point"` 的坐标，输出到 `.txt`。

### 用法

```bash
# 提取所有 point
python GetPointCord.py /path/to/annotation.json

# 只提取指定标签
python GetPointCord.py /path/to/annotation.json hzbokchoy broadleaf_weed

# 显式声明提取所有 point
python GetPointCord.py /path/to/annotation.json all
```

### 输出示例（txt）

```
120 300
248 410
...
```

---

# 📌 2. Batch_GetPointCord.py

### 作用

批量处理一整个文件夹的 JSON，生成对应 `.txt` 文件。

### 用法

#### （1）提取所有 point 类型

```bash
python Batch_GetPointCord.py ./json_dir ./output_txt
```

#### （2）只提取指定标签

```bash
python Batch_GetPointCord.py ./json_dir ./output_txt hzbokchoy broadleaf_weed
```

#### （3）等价于提取全部

```bash
python Batch_GetPointCord.py ./json_dir ./output_txt all
```

### 输出结构

```
output_txt/
    img001.txt
    img002.txt
    ...
```

---

# 📌 3. GetList.py（BuildP2PNetDataset.py）

### 作用

根据图片与 txt 文件自动生成标准 **P2PNet** 数据集结构。

包括：

✔ train/test 自动划分
✔ train/xxx/xxx.jpg & xxx.txt
✔ test/xxx/xxx.jpg & xxx.txt
✔ train.list
✔ test.list

---

## 使用方法

```bash
python GetList.py <images_dir> <txt_dir> <output_dataset_root> <train_ratio>
```

示例：

```bash
python GetList.py ./images ./points_txt ./P2PNet_dataset 0.8
```

---

# 输出示例（最终数据集结构）

```
P2PNet_dataset/
│── train/
│     ├── img_0001/
│     │      ├── img_0001.jpg
│     │      └── img_0001.txt
│     ├── img_0002/
│     └── ...
│
│── test/
│     ├── img_0101/
│     │      ├── img_0101.jpg
│     │      └── img_0101.txt
│
│── train.list
│── test.list
```

### train.list 示例

```
train/img_0001/img_0001.jpg train/img_0001/img_0001.txt
train/img_0002/img_0002.jpg train/img_0002/img_0002.txt
...
```

---

# 📝 P2PNet 所需的 txt 格式说明

每行一个点，**像素坐标从 0 开始**：

```
x1 y1
x2 y2
x3 y3
...
```

注意：

✔ 这是 **密集点标注（crowd counting）** 格式
✔ 与 YOLO、COCO 等 bbox 格式不同
✔ JSON 中的坐标会自动转为 int

---

# ⚠ 注意事项

### 1. JSON 格式需为 LabelMe 风格

必须包含如下字段：

```json
{
  "shapes": [
    {
      "label": "hzbokchoy",
      "shape_type": "point",
      "points": [[120.3, 450.8]]
    }
  ]
}
```

### 2. 图片名与 txt 名必须一致

如：

```
img001.jpg ↔ img001.json ↔ img001.txt
```

### 3. 点标注必须是 point 类型

polygon、rectangle、circle 均不会被提取。

### 4. GetList.py 不会递归处理子目录

建议你将 **所有图片放在同一目录一级目录**。

---

# 完整流程

### 第一步：批量抽取 JSON → txt

```bash
python Batch_GetPointCord.py ./json ./points_txt
```

### 第二步：生成 P2PNet 数据集

```bash
python GetList.py ./images ./points_txt ./P2PNet_dataset 0.7 0.15 0.15
```

然后即可直接用于 P2PNet 训练：

```
--data_root ./P2PNet_dataset
--dataset_file P2P   # 自定义
--train_list train.list
--test_list  test.list
```

---

# 适用场景

* 🌱 杂草密集点标注（weed counting）
* 👨‍👩‍👧‍👦 人群计数（crowd counting）
* 🍇 果园密集果实点标注
* 🍃 任何需要 point-based counting 的数据集

---

# ❤️ 贡献与联系

欢迎提交 Issues 或 Pull Requests 来共同完善本工具！
如果在使用过程中遇到任何问题、或有改进建议，也非常欢迎联系我。

特别感谢 @TONYHUaNGggggg 在项目开发中的协作与支持！

📧 Email：wangshichen0815@outlook.com

🐙 GitHub Issues：在仓库页面提交即可

感谢你对项目的关注与支持！

---

