#!/usr/bin/env python3
"""
从学习笔记生成 Anki 闪卡

用法:
    python generate_flashcards.py notes.md -o flashcards.txt
"""

import argparse
import re
from pathlib import Path

def extract_qa_pairs(markdown_content):
    """从 Markdown 提取问答对"""
    qa_pairs = []
    
    # 匹配 "- [ ] Q: ... A: ..." 格式
    pattern = r'- \[ \] Q: (.+?)\n\s+- A: (.+?)(?=\n|$)'
    matches = re.findall(pattern, markdown_content, re.MULTILINE | re.DOTALL)
    
    for question, answer in matches:
        qa_pairs.append((question.strip(), answer.strip()))
    
    return qa_pairs

def generate_anki_format(qa_pairs, tags=''):
    """生成 Anki 导入格式"""
    lines = []
    for q, a in qa_pairs:
        # Anki 格式：问题;答案;标签
        lines.append(f"{q};{a};{tags}")
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='生成 Anki 闪卡')
    parser.add_argument('input', help='输入笔记文件')
    parser.add_argument('-o', '--output', default='flashcards.txt', help='输出文件')
    parser.add_argument('--tags', default='', help='标签（逗号分隔）')
    
    args = parser.parse_args()
    
    # 读取笔记
    content = Path(args.input).read_text(encoding='utf-8')
    
    # 提取问答对
    qa_pairs = extract_qa_pairs(content)
    
    if not qa_pairs:
        print("未找到问答对。请确保笔记中包含以下格式：")
        print("- [ ] Q: 问题")
        print("  - A: 答案")
        return
    
    # 生成 Anki 格式
    anki_content = generate_anki_format(qa_pairs, args.tags)
    
    # 写入文件
    Path(args.output).write_text(anki_content, encoding='utf-8')
    
    print(f"✅ 生成 {len(qa_pairs)} 张闪卡")
    print(f"输出文件: {args.output}")
    print("\n导入 Anki 步骤：")
    print("1. 打开 Anki")
    print("2. 文件 -> 导入")
    print(f"3. 选择 {args.output}")
    print("4. 字段分隔符选择：分号")

if __name__ == '__main__':
    main()
