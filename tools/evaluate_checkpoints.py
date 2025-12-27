#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRI 模型自动评测脚本
对比不同 Checkpoint 的合成质量
"""

import os
import sys
import glob
import time
import numpy as np
import soundfile as sf

# === Configuration ===
GPT_SOVITS_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS"
CHECKPOINTS_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS/SoVITS_weights_v4"
GPT_CHECKPOINTS_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS/GPT_weights_v2"
OUTPUT_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/tts_outputs/checkpoint_eval"
REFERENCE_LIBRARY = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/dataset/reference_library.json"

# 亚托莉经典语境测试集
TEST_CASES = [
    {
        "emotion": "proud",
        "texts": [
            "当然です！高性能ですから！",
            "わたしに任せてください。絶対に成功させます！",
        ]
    },
    {
        "emotion": "happy",
        "texts": [
            "夏生さん、大好きです！",
            "やったー！今日はとっても楽しいです！",
        ]
    },
    {
        "emotion": "sad",
        "texts": [
            "夏生さん……わたし、もうすぐ……",
            "どうして……どうしてですか……",
        ]
    },
    {
        "emotion": "shy", 
        "texts": [
            "な、夏生さん……そんなに見つめないでください……",
            "えっと……その……好きです……",
        ]
    },
    {
        "emotion": "normal",
        "texts": [
            "了解しました。すぐに処理を開始します。",
            "これは高性能AIの分析結果です。",
        ]
    }
]

sys.path.insert(0, GPT_SOVITS_PATH)
sys.path.insert(0, os.path.join(GPT_SOVITS_PATH, "GPT_SoVITS"))
os.chdir(GPT_SOVITS_PATH)

def load_reference_library():
    """加载参考音频库"""
    import json
    with open(REFERENCE_LIBRARY, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("recommended", {})

def find_checkpoints():
    """查找所有可用的 checkpoint"""
    sovits_ckpts = glob.glob(os.path.join(CHECKPOINTS_DIR, "ATRI*.pth"))
    gpt_ckpts = glob.glob(os.path.join(GPT_CHECKPOINTS_DIR, "ATRI*.ckpt"))
    
    # 按 epoch 排序
    sovits_ckpts.sort(key=lambda x: int(x.split('_e')[1].split('_')[0]) if '_e' in x else 0)
    gpt_ckpts.sort(key=lambda x: int(x.split('-e')[1].split('.')[0]) if '-e' in x else 0)
    
    return sovits_ckpts, gpt_ckpts

def evaluate_checkpoint(sovits_path, gpt_path, ref_lib, output_subdir):
    """评测单个 checkpoint 组合"""
    from GPT_SoVITS.inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav
    from tools.i18n.i18n import I18nAuto
    i18n = I18nAuto()
    
    print(f"\n{'='*60}")
    print(f"Evaluating:")
    print(f"  SoVITS: {os.path.basename(sovits_path)}")
    print(f"  GPT: {os.path.basename(gpt_path)}")
    print(f"{'='*60}")
    
    # 加载模型
    change_gpt_weights(gpt_path)
    for _ in change_sovits_weights(sovits_path, prompt_language="日文", text_language="日文"):
        pass
    
    os.makedirs(output_subdir, exist_ok=True)
    results = []
    
    for case in TEST_CASES:
        emotion = case["emotion"]
        refs = ref_lib.get(emotion, ref_lib.get("normal", []))
        
        if not refs:
            continue
        
        ref = refs[0]  # 使用第一个推荐参考
        
        for i, text in enumerate(case["texts"]):
            output_path = os.path.join(output_subdir, f"{emotion}_{i+1}.wav")
            
            try:
                synthesis_result = get_tts_wav(
                    ref_wav_path=ref["path"],
                    prompt_text=ref["text"],
                    prompt_language=i18n("日文"),
                    text=text,
                    text_language=i18n("日文"),
                    how_to_cut=i18n("凑四句一切"),
                    top_k=5,
                    top_p=0.8,
                    temperature=0.5,
                    speed=0.95,
                )
                
                result_list = list(synthesis_result)
                if result_list:
                    sr = result_list[0][0]
                    audio = np.concatenate([item[1] for item in result_list])
                    sf.write(output_path, audio, sr)
                    results.append({
                        "emotion": emotion,
                        "text": text,
                        "path": output_path,
                        "status": "success"
                    })
                    print(f"  ✓ {emotion}_{i+1}: {text[:20]}...")
            except Exception as e:
                results.append({
                    "emotion": emotion,
                    "text": text,
                    "error": str(e),
                    "status": "failed"
                })
                print(f"  ✗ {emotion}_{i+1}: {e}")
    
    return results

def main():
    import json
    
    print("🎯 ATRI 模型自动评测系统")
    print("=" * 60)
    
    ref_lib = load_reference_library()
    sovits_ckpts, gpt_ckpts = find_checkpoints()
    
    print(f"找到 SoVITS checkpoints: {len(sovits_ckpts)}")
    print(f"找到 GPT checkpoints: {len(gpt_ckpts)}")
    
    if not sovits_ckpts or not gpt_ckpts:
        print("⚠️ 未找到 checkpoint，请先完成训练！")
        print(f"  SoVITS 目录: {CHECKPOINTS_DIR}")
        print(f"  GPT 目录: {GPT_CHECKPOINTS_DIR}")
        return
    
    # 评测最新的和中间的 checkpoint
    all_results = {}
    
    # 使用最新的 GPT，测试不同的 SoVITS
    latest_gpt = gpt_ckpts[-1] if gpt_ckpts else None
    
    for sovits_path in sovits_ckpts[-3:]:  # 最近 3 个
        ckpt_name = os.path.basename(sovits_path).replace('.pth', '')
        output_subdir = os.path.join(OUTPUT_DIR, ckpt_name)
        
        results = evaluate_checkpoint(sovits_path, latest_gpt, ref_lib, output_subdir)
        all_results[ckpt_name] = results
    
    # 保存结果摘要
    summary_path = os.path.join(OUTPUT_DIR, "evaluation_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 评测完成！结果保存至: {OUTPUT_DIR}")
    print(f"  摘要文件: {summary_path}")

if __name__ == "__main__":
    main()
