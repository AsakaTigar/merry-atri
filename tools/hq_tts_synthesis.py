#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRI 超高质量语音合成脚本
基于 GPT-SoVITS，使用优化参数实现最佳音质
"""

import os
import sys
import argparse
import time
import numpy as np
import soundfile as sf
import torch

# === Configuration ===
GPT_SOVITS_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS"
DATASET_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/dataset/gpt_sovits_train/wavs"
OUTPUT_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/tts_outputs/hq_synthesis"

# Model Weights (Best checkpoint)
# 纯血 v4 模型
GPT_MODEL_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS/GPT_weights_v2/ATRI-e20.ckpt"
SOVITS_MODEL_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/GPT-SoVITS/SoVITS_weights_v4/ATRI_e10_s910_l32.pth"

# High-Quality Reference Audio Presets (All clips 3-10 seconds)
REF_PRESETS = {
    "default": {  # 7.5s
        "path": f"{DATASET_PATH}/atr_b102_025.wav",
        "text": "はい、間違いありません。今朝、そちらにいる夏生さんに海から引き揚げてもらいました",
        "lang": "日文"
    },
    "proud": {  # 5.2s - determined/confident tone
        "path": f"{DATASET_PATH}/atr_b112_073.wav",
        "text": "まかされました。大船に乗った気分でどうぞ",
        "lang": "日文"
    },
    "happy": {  # 3.6s - cheerful
        "path": f"{DATASET_PATH}/atr_b121_025.wav",
        "text": "カニは美味しいです。美味しいは嬉しいです！",
        "lang": "日文"
    },
    "shy": {  # 6s - gentle caring
        "path": f"{DATASET_PATH}/atr_b103_008.wav",
        "text": "あの……夏生さん。汗を拭いてあげたいのですけど",
        "lang": "日文"
    },
    "love": {  # 5.1s - romantic
        "path": f"{DATASET_PATH}/atr_b205_025.wav",
        "text": "好きって言い合った者同士でおでかけするのはデートです",
        "lang": "日文"
    },
    "normal": {  # 7.5s - neutral explanatory
        "path": f"{DATASET_PATH}/atr_b102_025.wav",
        "text": "はい、間違いありません。今朝、そちらにいる夏生さんに海から引き揚げてもらいました",
        "lang": "日文"
    }
}

# === Setup paths ===
sys.path.insert(0, GPT_SOVITS_PATH)
sys.path.insert(0, os.path.join(GPT_SOVITS_PATH, "GPT_SoVITS"))
os.chdir(GPT_SOVITS_PATH)

# === Import GPT-SoVITS ===
try:
    from tools.i18n.i18n import I18nAuto
    from GPT_SoVITS.inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav
    i18n = I18nAuto()
    print("✓ GPT-SoVITS modules loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import GPT-SoVITS: {e}")
    sys.exit(1)


class HQSynthesizer:
    """High-Quality TTS Synthesizer"""
    
    # Optimized parameters for best quality
    DEFAULT_PARAMS = {
        "top_k": 5,           # Lower = more deterministic
        "top_p": 0.8,         # Nucleus sampling threshold
        "temperature": 0.5,   # Lower = more consistent
        "sample_steps": 32,   # CFM steps (v3/v4 only)
        "if_sr": False,       # Super-resolution (v3 only)
        "speed": 0.95,        # Slightly slower for clarity
        "pause_second": 0.2,  # Inter-sentence pause
    }
    
    def __init__(self):
        self.initialized = False
        
    def init_models(self):
        """Load TTS models"""
        if self.initialized:
            return
            
        print(f"Loading GPT model: {os.path.basename(GPT_MODEL_PATH)}")
        change_gpt_weights(gpt_path=GPT_MODEL_PATH)
        
        print(f"Loading SoVITS model: {os.path.basename(SOVITS_MODEL_PATH)}")
        # Pass prompt_language and text_language to get the generator working
        try:
            gen = change_sovits_weights(
                sovits_path=SOVITS_MODEL_PATH,
                prompt_language="日文",
                text_language="日文"
            )
            for _ in gen:
                pass
        except Exception as e:
            print(f"Warning during SoVITS init: {e}")
            
        self.initialized = True
        print("✓ Models initialized")
        
    def synthesize(
        self,
        text: str,
        ref_preset: str = "default",
        output_path: str = None,
        **kwargs
    ) -> str:
        """
        Synthesize speech with high-quality settings.
        
        Args:
            text: Text to synthesize (Chinese/Japanese/English)
            ref_preset: Reference audio preset name
            output_path: Optional output file path
            **kwargs: Override default parameters
        
        Returns:
            Path to generated audio file
        """
        self.init_models()
        
        # Get reference audio
        ref = REF_PRESETS.get(ref_preset, REF_PRESETS["default"])
        
        # Merge parameters
        params = {**self.DEFAULT_PARAMS, **kwargs}
        
        print(f"\n{'='*50}")
        print(f"Text: {text}")
        print(f"Reference: {ref_preset} - {ref['text'][:30]}...")
        print(f"Parameters: top_k={params['top_k']}, temp={params['temperature']}, steps={params['sample_steps']}")
        print(f"{'='*50}")
        
        # Detect language
        text_lang = self._detect_language(text)
        
        # Synthesize
        start_time = time.time()
        
        synthesis_result = get_tts_wav(
            ref_wav_path=ref["path"],
            prompt_text=ref["text"],
            prompt_language=i18n(ref["lang"]),
            text=text,
            text_language=i18n(text_lang),
            how_to_cut=i18n("凑四句一切"),
            top_k=params["top_k"],
            top_p=params["top_p"],
            temperature=params["temperature"],
            sample_steps=params["sample_steps"],
            if_sr=params["if_sr"],
            speed=params["speed"],
            pause_second=params["pause_second"],
        )
        
        # Collect results
        result_list = list(synthesis_result)
        if not result_list:
            raise RuntimeError("No audio generated")
            
        sampling_rate = result_list[0][0]
        audio_data = np.concatenate([item[1] for item in result_list])
        
        # Normalize audio
        max_val = np.abs(audio_data).max()
        if max_val > 0.99:
            audio_data = audio_data / max_val * 0.95
        
        # Save output
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(OUTPUT_DIR, f"hq_{ref_preset}_{timestamp}.wav")
        
        sf.write(output_path, audio_data, sampling_rate)
        
        elapsed = time.time() - start_time
        duration = len(audio_data) / sampling_rate
        rtf = elapsed / duration
        
        print(f"\n✓ Generated: {output_path}")
        print(f"  Duration: {duration:.2f}s | Time: {elapsed:.2f}s | RTF: {rtf:.2f}x")
        
        return output_path
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        import re
        
        # Check for Japanese characters (hiragana/katakana)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return "日文"
        # Check for Chinese characters
        elif re.search(r'[\u4e00-\u9fff]', text):
            return "中文"
        else:
            return "英文"


def main():
    parser = argparse.ArgumentParser(description="ATRI High-Quality TTS Synthesizer")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--preset", type=str, default="default", 
                        choices=list(REF_PRESETS.keys()), help="Reference audio preset")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--top_k", type=int, default=5, help="Top-K sampling")
    parser.add_argument("--top_p", type=float, default=0.8, help="Top-P sampling")
    parser.add_argument("--temperature", type=float, default=0.5, help="Temperature")
    parser.add_argument("--sample_steps", type=int, default=32, help="CFM sample steps (v3/v4)")
    parser.add_argument("--speed", type=float, default=0.95, help="Speech speed")
    parser.add_argument("--sr", action="store_true", help="Enable super-resolution (v3)")
    
    args = parser.parse_args()
    
    synth = HQSynthesizer()
    synth.synthesize(
        text=args.text,
        ref_preset=args.preset,
        output_path=args.output,
        top_k=args.top_k,
        top_p=args.top_p,
        temperature=args.temperature,
        sample_steps=args.sample_steps,
        speed=args.speed,
        if_sr=args.sr,
    )


if __name__ == "__main__":
    main()
