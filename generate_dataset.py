#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRI 语音数据集生成器
将语音文件和文本对齐，生成最终的训练数据集
"""

import csv
import json
import os
from pathlib import Path
import subprocess
import shutil

def check_ffmpeg():
    """检查 ffmpeg 是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def convert_opus_to_wav(input_path, output_path):
    """将 opus 转换为 wav"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-y', '-i', str(input_path), '-ar', '22050', '-ac', '1', str(output_path)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"转换失败: {e}")
        return False

def generate_dataset(voices_dir, csv_path, output_dir, convert_audio=False):
    """生成最终数据集"""
    
    voices_dir = Path(voices_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取 CSV
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        text_data = {row['voice'].upper(): row for row in reader}
    
    print(f"CSV 中共有 {len(text_data)} 条文本记录")
    
    # 获取所有语音文件
    voice_files = list(voices_dir.glob('*.opus'))
    print(f"找到 {len(voice_files)} 个语音文件")
    
    # 匹配并生成数据集
    matched = []
    unmatched_voices = []
    
    for voice_file in voice_files:
        voice_id = voice_file.stem.upper()
        
        if voice_id in text_data:
            record = text_data[voice_id]
            matched.append({
                'voice_file': voice_file.name,
                'voice_id': voice_id,
                'speaker': record['speaker'],
                'text_ja': record['text_ja'],
                'audio_path': str(voice_file)
            })
        else:
            unmatched_voices.append(voice_file.name)
    
    print(f"\n匹配成功: {len(matched)} 条")
    print(f"未匹配 (语音有但文本无): {len(unmatched_voices)} 条")
    
    # 保存匹配结果
    output_csv = output_dir / 'dataset_matched.csv'
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['voice_file', 'voice_id', 'speaker', 'text_ja', 'audio_path']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matched)
    
    print(f"\n匹配数据集已保存到: {output_csv}")
    
    # 保存为 JSON 格式（更方便后续处理）
    output_json = output_dir / 'dataset_matched.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)
    
    print(f"JSON 格式已保存到: {output_json}")
    
    # 如果需要转换音频
    if convert_audio and check_ffmpeg():
        wav_dir = output_dir / 'wavs'
        wav_dir.mkdir(exist_ok=True)
        
        print(f"\n开始转换音频到 WAV 格式...")
        converted = 0
        for item in matched:
            input_path = Path(item['audio_path'])
            output_path = wav_dir / (input_path.stem + '.wav')
            
            if convert_opus_to_wav(input_path, output_path):
                converted += 1
                if converted % 100 == 0:
                    print(f"  已转换 {converted} 个...")
        
        print(f"音频转换完成: {converted} 个")
    
    # 统计信息
    print("\n" + "="*50)
    print("📊 数据集统计")
    print("="*50)
    print(f"总文本记录: {len(text_data)}")
    print(f"总语音文件: {len(voice_files)}")
    print(f"成功匹配: {len(matched)}")
    print(f"匹配率: {len(matched)/len(text_data)*100:.1f}%")
    
    # 按角色统计
    speakers = {}
    for item in matched:
        speaker = item['speaker']
        speakers[speaker] = speakers.get(speaker, 0) + 1
    
    print(f"\n按角色统计 (前10):")
    for speaker, count in sorted(speakers.items(), key=lambda x: -x[1])[:10]:
        print(f"  {speaker}: {count} 条")
    
    return matched


if __name__ == '__main__':
    import sys
    
    voices_dir = sys.argv[1] if len(sys.argv) > 1 else 'H:/GDUT2025_12/Voice_atri_mika/voices'
    csv_path = sys.argv[2] if len(sys.argv) > 2 else 'H:/GDUT2025_12/Voice_atri_mika/dataset.csv'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'H:/GDUT2025_12/Voice_atri_mika/final_dataset'
    
    # 是否转换音频（默认不转换，因为 ffmpeg 可能不可用）
    convert_audio = '--convert' in sys.argv
    
    generate_dataset(voices_dir, csv_path, output_dir, convert_audio)
