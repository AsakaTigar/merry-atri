#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRI 剧本解析脚本
从 FreeMote 反编译的 JSON 文件中提取 语音文件名 <-> 日文台词 的对应关系
"""

import json
import re
import csv
import os
from pathlib import Path

def extract_voice_text_pairs(json_file):
    """从单个 JSON 文件中提取语音-文本对"""
    pairs = []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 voice 字段
    voice_pattern = r'"voice":\s*"([^"]+)"'
    
    # 查找对话模式：[角色名, 显示名, [[语言1, 文本1], [语言2, 文本2], ...]]
    # 日文通常是第一个
    dialogue_pattern = r'\["([^"]*)",\s*"([^"]*)",\s*\[\[([^\]]*)\]\]'
    
    # 更简单的方法：直接搜索包含日文的文本
    japanese_text_pattern = r'"([^"]*[ぁ-んァ-ンー一-龥][^"]*)"'
    
    # 尝试解析 JSON
    try:
        data = json.loads(content)
        
        def recursive_search(obj, current_voice=None, current_speaker=None):
            """递归搜索 JSON 结构"""
            results = []
            
            if isinstance(obj, dict):
                # 检查是否有 voice 字段
                voice = obj.get('voice')
                speaker = obj.get('name') or current_speaker
                
                # 检查对话内容
                if voice and isinstance(voice, str) and voice.strip():
                    # 在同一个对象或附近查找文本
                    text = find_text_in_context(obj)
                    if text:
                        results.append({
                            'voice': voice,
                            'speaker': speaker or '',
                            'text_ja': text
                        })
                
                # 递归搜索子对象
                for key, value in obj.items():
                    results.extend(recursive_search(value, voice or current_voice, speaker or current_speaker))
            
            elif isinstance(obj, list):
                # 检查是否是对话格式 [speaker, display_name, [[lang, text], ...]]
                if len(obj) >= 3 and isinstance(obj[0], str) and isinstance(obj[2], list):
                    speaker = obj[0]
                    texts = obj[2]
                    if isinstance(texts, list) and len(texts) > 0:
                        for item in texts:
                            if isinstance(item, list) and len(item) >= 2:
                                lang, text = item[0], item[1]
                                if contains_japanese(text):
                                    # 这可能是日文文本
                                    pass
                
                for item in obj:
                    results.extend(recursive_search(item, current_voice, current_speaker))
            
            return results
        
        pairs = recursive_search(data)
        
    except json.JSONDecodeError:
        # JSON 解析失败，使用正则表达式
        print(f"JSON 解析失败，使用正则表达式: {json_file}")
        
        # 查找所有语音引用
        voices = re.findall(voice_pattern, content)
        print(f"找到 {len(voices)} 个语音引用")
    
    return pairs


def contains_japanese(text):
    """检查文本是否包含日文"""
    if not isinstance(text, str):
        return False
    # 平假名、片假名、汉字
    return bool(re.search(r'[ぁ-んァ-ンー一-龥]', text))


def find_text_in_context(obj):
    """在对象上下文中查找日文文本"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and contains_japanese(value):
                return value
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and contains_japanese(item):
                        return item
    return None


def extract_with_regex(json_file):
    """使用正则表达式提取语音-文本对"""
    pairs = []
    
    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找模式：语音文件名附近的日文文本
    # 格式类似："voice": "ATR_b101_001" 附近有 "「日文台词」"
    
    # 首先找到所有语音引用
    voice_matches = list(re.finditer(r'"voice":\s*"([A-Z]{3}_b\d+_\d+[a-z]?)"', content))
    
    for match in voice_matches:
        voice_id = match.group(1)
        start_pos = max(0, match.start() - 2000)
        end_pos = min(len(content), match.end() + 500)
        context = content[start_pos:end_pos]
        
        # 在上下文中查找日文对话（带引号的日文文本）
        # 日文对话通常是 「...」 格式
        ja_matches = re.findall(r'「([^」]+)」', context)
        if ja_matches:
            # 取最后一个（最接近 voice 的）
            text_ja = '「' + ja_matches[-1] + '」'
        else:
            # 尝试其他格式
            ja_matches = re.findall(r'"([^"]*[ぁ-んァ-ン][^"]*)"', context)
            text_ja = ja_matches[-1] if ja_matches else ''
        
        # 查找角色名
        speaker_matches = re.findall(r'\["([^"]+)",\s*"([^"]+)"', context)
        speaker = speaker_matches[-1][0] if speaker_matches else ''
        
        if text_ja:
            pairs.append({
                'voice': voice_id,
                'speaker': speaker,
                'text_ja': text_ja
            })
    
    return pairs


def process_all_json_files(input_dir, output_csv):
    """处理所有 JSON 文件并输出 CSV"""
    all_pairs = []
    
    json_files = sorted(Path(input_dir).glob('*.json'))
    json_files = [f for f in json_files if not f.name.endswith('.resx.json')]
    
    print(f"找到 {len(json_files)} 个 JSON 文件")
    
    for json_file in json_files:
        print(f"处理: {json_file.name}")
        pairs = extract_with_regex(str(json_file))
        print(f"  提取到 {len(pairs)} 条记录")
        all_pairs.extend(pairs)
    
    # 去重
    seen = set()
    unique_pairs = []
    for pair in all_pairs:
        key = pair['voice']
        if key not in seen:
            seen.add(key)
            unique_pairs.append(pair)
    
    # 按语音文件名排序
    unique_pairs.sort(key=lambda x: x['voice'])
    
    # 输出 CSV
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['voice', 'speaker', 'text_ja'])
        writer.writeheader()
        writer.writerows(unique_pairs)
    
    print(f"\n总计提取 {len(unique_pairs)} 条语音-文本对")
    print(f"已保存到: {output_csv}")
    
    return unique_pairs


if __name__ == '__main__':
    import sys
    
    input_dir = sys.argv[1] if len(sys.argv) > 1 else 'H:/GDUT2025_12/Voice_atri_mika/decrypted'
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'H:/GDUT2025_12/Voice_atri_mika/dataset.csv'
    
    process_all_json_files(input_dir, output_csv)
