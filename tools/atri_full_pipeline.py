#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRI 全链路测试脚本
LLM 情感分析 → 参考音频选择 → GPT-SoVITS v4 合成

用法: python atri_full_pipeline.py --text "你的文本"
"""

import os
import sys
import json
import re
import random
import argparse
import numpy as np
import soundfile as sf
from datetime import datetime

# === Paths ===
PROJECT_ROOT = "/mnt/t2-6tb/Linpeikai/Voice/ATRI"
GPT_SOVITS_PATH = f"{PROJECT_ROOT}/frameworks/GPT-SoVITS"
REFERENCE_LIBRARY = f"{PROJECT_ROOT}/dataset/reference_library.json"
OUTPUT_DIR = f"{PROJECT_ROOT}/tts_outputs/full_pipeline"

# 纯血 v4 模型 (GPT e20 + SoVITS e10)
GPT_MODEL = f"{GPT_SOVITS_PATH}/GPT_weights_v2/ATRI-e20.ckpt"
SOVITS_MODEL = f"{GPT_SOVITS_PATH}/SoVITS_weights_v4/ATRI_e10_s910_l32.pth"

# LLM 配置
LLM_MODEL_PATH = f"{PROJECT_ROOT}/weights/llm/Qwen2.5-14B-Roleplay-ZH"

sys.path.insert(0, GPT_SOVITS_PATH)
sys.path.insert(0, os.path.join(GPT_SOVITS_PATH, "GPT_SoVITS"))
os.chdir(GPT_SOVITS_PATH)

# === 情感-参数映射 ===
EMOTION_PARAMS = {
    "happy": {"speed": 1.05, "top_k": 5, "temperature": 0.6},
    "proud": {"speed": 1.0, "top_k": 5, "temperature": 0.5},
    "shy": {"speed": 0.92, "top_k": 5, "temperature": 0.55},
    "sad": {"speed": 0.85, "top_k": 3, "temperature": 0.45},
    "normal": {"speed": 0.95, "top_k": 5, "temperature": 0.5},
    "love": {"speed": 0.9, "top_k": 5, "temperature": 0.55},
}

def load_reference_library():
    """加载参考音频库"""
    with open(REFERENCE_LIBRARY, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("recommended", {})

def analyze_emotion_with_llm(text: str) -> dict:
    """使用 LLM 分析文本情感和合成参数"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        print("🧠 加载 LLM...")
        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_PATH, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="cuda:1",  # 使用空闲的 GPU 1
            trust_remote_code=True
        )
        
        prompt = f"""你是一个情感分析助手。分析以下亚托莉角色的台词，输出情感标签和语音合成参数。

台词: {text}

请用以下JSON格式回复:
{{"emotion": "happy/proud/shy/sad/normal/love", "speed": 0.8-1.1, "reason": "简短理由"}}

只输出JSON，不要其他内容:"""

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.3)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取 JSON
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            result = json.loads(json_match.group())
            return result
    except Exception as e:
        print(f"⚠️ LLM 分析失败: {e}")
    
    # 回退：基于关键词的简单分析
    return analyze_emotion_simple(text)

def analyze_emotion_simple(text: str) -> dict:
    """简单关键词情感分析（回退方案）"""
    keywords = {
        "happy": ["嬉しい", "楽しい", "やった", "大好き", "好き"],
        "proud": ["高性能", "当然", "任せて", "できます"],
        "shy": ["恥ずかし", "えっと", "その"],
        "sad": ["悲しい", "寂しい", "ごめん"],
        "love": ["愛して", "好きです", "デート"],
    }
    
    for emotion, words in keywords.items():
        if any(w in text for w in words):
            return {"emotion": emotion, "speed": EMOTION_PARAMS[emotion]["speed"]}
    
    return {"emotion": "normal", "speed": 0.95}

def synthesize_with_v4(text: str, ref_audio: dict, params: dict, output_path: str):
    """使用 v4 模型合成语音"""
    from GPT_SoVITS.inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav
    from tools.i18n.i18n import I18nAuto
    i18n = I18nAuto()
    
    print(f"🔧 加载 v4 模型...")
    change_gpt_weights(GPT_MODEL)
    for _ in change_sovits_weights(SOVITS_MODEL, prompt_language="日文", text_language="日文"):
        pass
    
    speed = params.get("speed", 0.95)
    top_k = params.get("top_k", 5)
    temperature = params.get("temperature", 0.5)
    
    print(f"🎤 合成中... (speed={speed}, top_k={top_k}, temp={temperature})")
    
    synthesis_result = get_tts_wav(
        ref_wav_path=ref_audio["path"],
        prompt_text=ref_audio["text"],
        prompt_language=i18n("日文"),
        text=text,
        text_language=i18n("日文"),
        how_to_cut=i18n("凑四句一切"),
        top_k=top_k,
        top_p=0.8,
        temperature=temperature,
        speed=speed,
    )
    
    result_list = list(synthesis_result)
    if result_list:
        sr = result_list[0][0]
        audio = np.concatenate([item[1] for item in result_list])
        sf.write(output_path, audio, sr)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="ATRI 全链路 TTS")
    parser.add_argument("--text", type=str, required=True, help="要合成的文本")
    parser.add_argument("--skip-llm", action="store_true", help="跳过 LLM 分析，使用简单关键词")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 ATRI 全链路语音合成")
    print("=" * 60)
    print(f"📝 输入: {args.text}")
    
    # Step 1: 情感分析
    print("\n🔍 Step 1: 情感分析")
    if args.skip_llm:
        emotion_result = analyze_emotion_simple(args.text)
    else:
        emotion_result = analyze_emotion_with_llm(args.text)
    
    emotion = emotion_result.get("emotion", "normal")
    print(f"   → 检测情感: [{emotion.upper()}]")
    
    # Step 2: 选择参考音频
    print("\n📂 Step 2: 选择参考音频")
    ref_lib = load_reference_library()
    refs = ref_lib.get(emotion, ref_lib.get("normal", []))
    
    if not refs:
        print("   ⚠️ 未找到参考音频，使用默认")
        refs = list(ref_lib.values())[0] if ref_lib else []
    
    ref_audio = random.choice(refs) if refs else None
    if ref_audio:
        print(f"   → 参考: {ref_audio['text'][:30]}...")
    
    # Step 3: 合成
    print("\n🎤 Step 3: v4 语音合成")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{OUTPUT_DIR}/atri_{emotion}_{timestamp}.wav"
    
    params = EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["normal"])
    
    if ref_audio and synthesize_with_v4(args.text, ref_audio, params, output_path):
        print(f"\n✅ 生成成功: {output_path}")
    else:
        print("\n❌ 合成失败")

if __name__ == "__main__":
    main()
