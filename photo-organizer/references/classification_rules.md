# 照片分类规则

本文档定义了照片整理大师的分类规则和算法说明。

## 分类维度

### 1. 按时间分类

**目录结构**：
```
照片库/
├── 2024/
│   ├── 01-January/
│   ├── 02-February/
│   └── ...
├── 2025/
│   ├── 01-January/
│   ├── 02-February/
│   └── ...
└── 未分类/
    └── 无EXIF照片/
```

**数据来源优先级**：
1. EXIF DateTimeOriginal（拍摄时间）
2. EXIF DateTime（文件创建时间）
3. 文件修改时间（mtime）
4. 文件名中的日期（如 IMG_20260209_143052.jpg）

### 2. 按内容分类

**分类标准**：
- **风景**：自然景观、城市风光、建筑、天空、海洋
- **人物**：肖像、合影、自拍、人脸特写
- **美食**：餐厅菜品、家常菜、甜点、饮料
- **文档**：证件、票据、文字截图、扫描件
- **截图**：手机/电脑截图、应用界面
- **其他**：无法分类的照片

**识别特征**：
| 类别 | 特征 |
|------|------|
| 风景 | 无人脸、色彩丰富、水平线、天空占比大 |
| 人物 | 人脸检测、肤色占比、人物轮廓 |
| 美食 | 圆形/方形盘子、暖色调、近距离拍摄 |
| 文档 | 高对比度、文字密集、矩形边界 |
| 截图 | 固定分辨率、UI元素、状态栏 |

### 3. 按事件分类

**事件识别规则**：
- **旅行**：连续3天以上、GPS位置变化大、风景照为主
- **聚会**：同一天、多人合影、室内场景
- **工作**：工作日、文档/截图为主、办公环境
- **日常**：零散照片、无明显主题

## EXIF 元数据

### 常用 EXIF 标签

| 标签 | 说明 | 示例 |
|------|------|------|
| DateTimeOriginal | 拍摄时间 | 2026:02:09 14:30:52 |
| Make | 相机制造商 | Apple |
| Model | 相机型号 | iPhone 15 Pro |
| GPSLatitude | GPS纬度 | 39.9042° N |
| GPSLongitude | GPS经度 | 116.4074° E |
| FNumber | 光圈值 | f/1.8 |
| ExposureTime | 快门速度 | 1/120 |
| ISOSpeedRatings | ISO感光度 | 100 |
| FocalLength | 焦距 | 26mm |

### EXIF 提取方法

**方法1：使用 PIL（Python）**
```python
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('photo.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")
```

**方法2：使用 exiftool（命令行）**
```bash
exiftool photo.jpg
exiftool -DateTimeOriginal -Make -Model photo.jpg
```

## 重复检测算法

### 1. 完全重复（MD5）

**原理**：计算文件的 MD5 哈希值，相同哈希值表示文件完全相同。

**优点**：
- 100% 准确
- 速度快
- 适合大量照片

**缺点**：
- 无法检测相似照片
- 编辑后的照片无法识别

**实现**：
```python
import hashlib

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
```

### 2. 相似照片（感知哈希）

**原理**：计算图像的感知哈希值（pHash），通过汉明距离判断相似度。

**优点**：
- 可检测相似照片
- 对缩放、压缩不敏感
- 可调节相似度阈值

**缺点**：
- 速度较慢
- 需要图像处理库

**实现**：
```python
import imagehash
from PIL import Image

def calculate_phash(file_path):
    img = Image.open(file_path)
    return imagehash.phash(img)

def is_similar(hash1, hash2, threshold=5):
    return hash1 - hash2 < threshold
```

**阈值建议**：
- 0-5：非常相似（连拍、轻微编辑）
- 6-10：相似（不同角度、不同光线）
- 11-15：有些相似（同一场景）
- 16+：不相似

### 3. 连拍照片

**识别规则**：
- 时间戳相差 < 2秒
- 文件名连续（如 IMG_1234.jpg, IMG_1235.jpg）
- 相同设备拍摄

**处理建议**：
- 保留最清晰的一张
- 或保留所有，标记为连拍组

## 质量评估

### 1. 模糊检测

**算法**：拉普拉斯方差（Laplacian Variance）

**原理**：计算图像的拉普拉斯算子方差，方差越小越模糊。

**实现**：
```python
import cv2

def is_blurry(image_path, threshold=100):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    return laplacian_var < threshold
```

**阈值建议**：
- < 50：严重模糊
- 50-100：轻微模糊
- 100-500：清晰
- > 500：非常清晰

### 2. 曝光检测

**算法**：直方图分析

**原理**：分析像素亮度分布，判断过曝/欠曝。

**实现**：
```python
import cv2
import numpy as np

def check_exposure(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    
    # 过曝：高亮区域占比 > 30%
    overexposed = np.sum(hist[240:]) / np.sum(hist) > 0.3
    
    # 欠曝：暗部区域占比 > 30%
    underexposed = np.sum(hist[:16]) / np.sum(hist) > 0.3
    
    if overexposed:
        return "过曝"
    elif underexposed:
        return "欠曝"
    else:
        return "正常"
```

### 3. 人脸检测

**算法**：Haar Cascade 或 深度学习模型

**用途**：
- 识别人物照片
- 统计人脸数量
- 评估人脸清晰度

**实现**：
```python
import cv2

def detect_faces(image_path):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return len(faces)
```

## 批量操作

### 1. 重命名规则

**格式选项**：
- `YYYYMMDD_HHMMSS_序号.jpg`（推荐）
- `YYYY-MM-DD_HHMMSS_序号.jpg`
- `原文件名_YYYYMMDD.jpg`
- 自定义格式

**示例**：
```
IMG_1234.jpg → 20260209_143052_001.jpg
IMG_1235.jpg → 20260209_143053_002.jpg
```

### 2. 文件名冲突处理

**策略**：
- 添加序号后缀（推荐）
- 添加时间戳后缀
- 跳过（保留原文件）
- 覆盖（不推荐）

### 3. 操作日志

**日志格式**（JSON）：
```json
{
  "timestamp": "2026-02-09 14:30:52",
  "operation": "organize_by_date",
  "source_dir": "~/Pictures/未整理/",
  "target_dir": "~/Pictures/已整理/",
  "operations": [
    {
      "source": "~/Pictures/未整理/IMG_1234.jpg",
      "target": "~/Pictures/已整理/2026/02-February/IMG_1234.jpg",
      "date": "2026-02-09 14:30:52"
    }
  ]
}
```

## 安全机制

### 1. 撤销操作

**实现**：
- 读取操作日志
- 反向执行操作（移动回原位置）
- 删除临时文件夹

**限制**：
- 仅支持移动操作的撤销
- 删除操作无法撤销（建议先移至"待删除"文件夹）

### 2. 备份建议

**整理前备份**：
```bash
# Time Machine（macOS）
tmutil startbackup

# 手动备份
cp -r ~/Pictures/未整理/ /Volumes/Backup/照片备份_20260209/
```

### 3. 预览模式

**功能**：
- 不实际移动文件
- 生成预览报告
- 用户确认后再执行

**使用**：
```bash
python organize_photos.py ~/Pictures/未整理/ --dry-run
```

## 性能优化

### 1. 批量处理

**策略**：
- 分批处理（每批1000张）
- 多线程并行（EXIF 提取）
- 进度显示

### 2. 缓存机制

**缓存内容**：
- EXIF 数据
- 感知哈希值
- 人脸检测结果

**缓存格式**（JSON）：
```json
{
  "photo.jpg": {
    "md5": "abc123...",
    "phash": "8f8f8f8f8f8f8f8f",
    "date": "2026-02-09 14:30:52",
    "faces": 2,
    "blur_score": 150.5
  }
}
```

### 3. 增量处理

**策略**：
- 仅处理新增照片
- 跳过已处理照片
- 基于修改时间判断

## 版本历史

- **v1.0.0** (2026-02-09)：初始版本，定义分类规则和算法
