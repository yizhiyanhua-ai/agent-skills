#!/usr/bin/env python3
"""
会议录音转录脚本
使用 Whisper 将音频文件转换为文本

用法:
    python transcribe_audio.py <音频文件路径> [-o 输出文件] [--language zh]

示例:
    python transcribe_audio.py meeting.mp3
    python transcribe_audio.py meeting.mp3 -o transcript.txt
    python transcribe_audio.py meeting.mp3 --language zh --model medium
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='使用 Whisper 转录音频文件')
    parser.add_argument('audio_file', help='音频文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认：<音频文件名>_transcript.txt）')
    parser.add_argument('--language', default='zh', help='语言代码（默认：zh）')
    parser.add_argument('--model', default='medium', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                        help='Whisper 模型大小（默认：medium）')
    parser.add_argument('--verbose', action='store_true', help='显示详细输出')
    
    args = parser.parse_args()
    
    # 检查音频文件是否存在
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"错误: 音频文件不存在: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # 确定输出文件路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = audio_path.parent / f"{audio_path.stem}_transcript.txt"
    
    print(f"正在转录音频文件: {audio_path}")
    print(f"使用模型: {args.model}")
    print(f"语言: {args.language}")
    print(f"输出文件: {output_path}")
    print()
    
    # 调用 Whisper CLI
    import subprocess
    
    cmd = [
        'whisper',
        str(audio_path),
        '--language', args.language,
        '--model', args.model,
        '--output_format', 'txt',
        '--output_dir', str(output_path.parent)
    ]
    
    if args.verbose:
        cmd.append('--verbose')
        print(f"执行命令: {' '.join(cmd)}")
        print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=not args.verbose)
        
        # Whisper 会自动生成文件名，需要重命名
        whisper_output = output_path.parent / f"{audio_path.stem}.txt"
        if whisper_output.exists() and whisper_output != output_path:
            whisper_output.rename(output_path)
        
        print(f"✅ 转录完成！")
        print(f"输出文件: {output_path}")
        
        # 显示文件大小和行数
        content = output_path.read_text(encoding='utf-8')
        lines = content.count('\n') + 1
        words = len(content)
        print(f"文件大小: {words} 字符, {lines} 行")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 转录失败: {e}", file=sys.stderr)
        print(f"\n请检查:", file=sys.stderr)
        print(f"1. Whisper 是否已安装: pip install openai-whisper", file=sys.stderr)
        print(f"2. ffmpeg 是否已安装: brew install ffmpeg (macOS)", file=sys.stderr)
        print(f"3. 音频文件格式是否支持", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
