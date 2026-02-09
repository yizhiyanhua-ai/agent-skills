#!/usr/bin/env python3
"""
照片整理主流程脚本
功能：扫描照片、提取EXIF、按时间分类、生成报告
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import json

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def extract_exif_date(image_path):
    """从照片提取拍摄时间"""
    if not PIL_AVAILABLE:
        # 使用文件修改时间作为备选
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)
    
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        
        # 无EXIF，使用文件修改时间
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)
    
    except Exception as e:
        # 出错时使用文件修改时间
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)


def scan_photos(source_dir):
    """扫描照片文件"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp', '.tiff', '.raw', '.cr2', '.nef', '.arw'}
    photos = []
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in image_extensions:
                photo_path = os.path.join(root, file)
                photos.append(photo_path)
    
    return photos


def organize_by_date(photos, target_dir, dry_run=False):
    """按日期整理照片"""
    stats = defaultdict(int)
    operations = []
    
    for photo_path in photos:
        try:
            # 提取拍摄日期
            photo_date = extract_exif_date(photo_path)
            
            # 创建目标路径
            year = photo_date.strftime('%Y')
            month = photo_date.strftime('%m-%B')  # 01-January
            
            target_folder = os.path.join(target_dir, year, month)
            
            # 记录统计
            stats[f"{year}/{month}"] += 1
            
            # 生成目标文件路径
            filename = os.path.basename(photo_path)
            target_path = os.path.join(target_folder, filename)
            
            # 处理文件名冲突
            counter = 1
            while os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                counter += 1
            
            operations.append({
                'source': photo_path,
                'target': target_path,
                'date': photo_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            if not dry_run:
                # 创建目标文件夹
                os.makedirs(target_folder, exist_ok=True)
                # 移动文件
                shutil.move(photo_path, target_path)
        
        except Exception as e:
            print(f"⚠️ 处理失败: {photo_path} - {e}")
            stats['errors'] += 1
    
    return stats, operations


def generate_report(stats, operations, output_file=None):
    """生成整理报告"""
    report = "# 照片整理报告\n\n"
    report += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # 统计信息
    report += "## 统计信息\n\n"
    total = sum(v for k, v in stats.items() if k != 'errors')
    report += f"- 总照片数：{total}张\n"
    
    if stats.get('errors', 0) > 0:
        report += f"- 处理失败：{stats['errors']}张\n"
    
    report += "\n## 分类详情\n\n"
    report += "| 年份/月份 | 照片数 |\n"
    report += "|----------|--------|\n"
    
    for folder, count in sorted(stats.items()):
        if folder != 'errors':
            report += f"| {folder} | {count}张 |\n"
    
    # 操作日志
    if operations:
        report += "\n## 操作日志\n\n"
        report += f"共移动 {len(operations)} 个文件\n\n"
        report += "详细日志已保存到 organize_operations.json\n"
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已生成：{output_file}")
    else:
        print(report)
    
    # 保存操作日志（用于撤销）
    if operations:
        log_file = 'organize_operations.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(operations, f, indent=2, ensure_ascii=False)
        print(f"✅ 操作日志已保存：{log_file}")


def main():
    parser = argparse.ArgumentParser(description='照片整理工具')
    parser.add_argument('source', help='源照片文件夹')
    parser.add_argument('--target', help='目标文件夹（默认为源文件夹/已整理）')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（不实际移动文件）')
    parser.add_argument('--report', help='报告输出文件（默认打印到终端）')
    
    args = parser.parse_args()
    
    source_dir = args.source
    target_dir = args.target or os.path.join(source_dir, '已整理')
    
    if not os.path.exists(source_dir):
        print(f"❌ 源文件夹不存在：{source_dir}")
        return
    
    print(f"📂 扫描照片：{source_dir}")
    photos = scan_photos(source_dir)
    print(f"✅ 找到 {len(photos)} 张照片")
    
    if len(photos) == 0:
        print("⚠️ 未找到照片文件")
        return
    
    if args.dry_run:
        print("\n🔍 预览模式（不会实际移动文件）")
    
    print(f"\n📁 目标文件夹：{target_dir}")
    print("🚀 开始整理...")
    
    stats, operations = organize_by_date(photos, target_dir, dry_run=args.dry_run)
    
    print("\n✅ 整理完成！\n")
    generate_report(stats, operations, args.report)


if __name__ == '__main__':
    main()
