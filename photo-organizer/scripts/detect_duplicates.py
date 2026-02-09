#!/usr/bin/env python3
"""
重复照片检测脚本
功能：使用MD5和感知哈希检测重复和相似照片
"""

import os
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


def calculate_md5(file_path):
    """计算文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_phash(file_path):
    """计算感知哈希值"""
    if not IMAGEHASH_AVAILABLE:
        return None
    
    try:
        img = Image.open(file_path)
        return imagehash.phash(img)
    except Exception as e:
        print(f"⚠️ 无法计算感知哈希: {file_path} - {e}")
        return None


def find_exact_duplicates(photos):
    """查找完全重复的照片（MD5相同）"""
    md5_dict = defaultdict(list)
    
    print("🔍 计算MD5哈希值...")
    for i, photo in enumerate(photos, 1):
        if i % 100 == 0:
            print(f"  进度: {i}/{len(photos)}")
        
        md5 = calculate_md5(photo)
        md5_dict[md5].append(photo)
    
    # 找出重复项
    duplicates = {md5: files for md5, files in md5_dict.items() if len(files) > 1}
    
    return duplicates


def find_similar_photos(photos, threshold=5):
    """查找相似照片（感知哈希相近）"""
    if not IMAGEHASH_AVAILABLE:
        print("⚠️ 需要安装 imagehash: pip install imagehash")
        return {}
    
    print("🔍 计算感知哈希值...")
    phash_dict = {}
    
    for i, photo in enumerate(photos, 1):
        if i % 100 == 0:
            print(f"  进度: {i}/{len(photos)}")
        
        phash = calculate_phash(photo)
        if phash:
            phash_dict[photo] = phash
    
    # 查找相似照片
    print("🔍 比较相似度...")
    similar_groups = []
    processed = set()
    
    photos_list = list(phash_dict.keys())
    for i, photo1 in enumerate(photos_list):
        if photo1 in processed:
            continue
        
        group = [photo1]
        hash1 = phash_dict[photo1]
        
        for photo2 in photos_list[i+1:]:
            if photo2 in processed:
                continue
            
            hash2 = phash_dict[photo2]
            diff = hash1 - hash2
            
            if diff < threshold:
                group.append(photo2)
                processed.add(photo2)
        
        if len(group) > 1:
            similar_groups.append(group)
            processed.add(photo1)
    
    return similar_groups


def main():
    parser = argparse.ArgumentParser(description='重复照片检测工具')
    parser.add_argument('directory', help='照片文件夹')
    parser.add_argument('--mode', choices=['exact', 'similar', 'both'], default='both',
                        help='检测模式：exact(完全重复), similar(相似), both(两者)')
    parser.add_argument('--threshold', type=int, default=5,
                        help='相似度阈值（0-64，越小越严格，默认5）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ 文件夹不存在：{args.directory}")
        return
    
    # 扫描照片
    print(f"📂 扫描照片：{args.directory}")
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp'}
    photos = []
    
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in image_extensions:
                photos.append(os.path.join(root, file))
    
    print(f"✅ 找到 {len(photos)} 张照片\n")
    
    if len(photos) == 0:
        print("⚠️ 未找到照片文件")
        return
    
    # 检测完全重复
    if args.mode in ['exact', 'both']:
        print("=" * 50)
        print("检测完全重复的照片")
        print("=" * 50)
        
        duplicates = find_exact_duplicates(photos)
        
        if duplicates:
            print(f"\n✅ 找到 {len(duplicates)} 组完全重复的照片\n")
            
            total_duplicates = sum(len(files) - 1 for files in duplicates.values())
            print(f"可删除 {total_duplicates} 张重复照片\n")
            
            for i, (md5, files) in enumerate(duplicates.items(), 1):
                print(f"组 {i}（{len(files)}张）：")
                for file in files:
                    print(f"  - {file}")
                print()
        else:
            print("\n✅ 未找到完全重复的照片\n")
    
    # 检测相似照片
    if args.mode in ['similar', 'both']:
        print("=" * 50)
        print("检测相似照片")
        print("=" * 50)
        
        similar_groups = find_similar_photos(photos, args.threshold)
        
        if similar_groups:
            print(f"\n✅ 找到 {len(similar_groups)} 组相似照片\n")
            
            for i, group in enumerate(similar_groups, 1):
                print(f"组 {i}（{len(group)}张）：")
                for file in group:
                    print(f"  - {file}")
                print()
        else:
            print("\n✅ 未找到相似照片\n")


if __name__ == '__main__':
    main()
