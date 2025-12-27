#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎹 ATRI v4 实时情感调音台
Gradio WebUI - 旋钮式参数调节

启动: python atri_tuning_console.py
访问: http://0.0.0.0:7880
"""

import os
import sys
import json
import numpy as np
import torch
import soundfile as sf
from datetime import datetime

# === 路径配置 ===
PROJECT_ROOT = "/mnt/t2-6tb/Linpeikai/Voice/ATRI"
GPT_SOVITS_PATH = f"{PROJECT_ROOT}/frameworks/GPT-SoVITS"
REFERENCE_LIBRARY = f"{PROJECT_ROOT}/dataset/reference_library.json"
OUTPUT_DIR = f"{PROJECT_ROOT}/tts_outputs/tuning_console"

# 纯血 v4 模型 (GPT e20 + SoVITS e10)
GPT_MODEL = f"{GPT_SOVITS_PATH}/GPT_weights_v2/ATRI-e20.ckpt"
SOVITS_MODEL = f"{GPT_SOVITS_PATH}/SoVITS_weights_v4/ATRI_e10_s910_l32.pth"

os.makedirs(OUTPUT_DIR, exist_ok=True)
sys.path.insert(0, GPT_SOVITS_PATH)
sys.path.insert(0, os.path.join(GPT_SOVITS_PATH, "GPT_SoVITS"))
os.chdir(GPT_SOVITS_PATH)

# === 全局模型加载 (显存驻留) ===
print("🔧 加载 GPT-SoVITS v4 模型...")
from GPT_SoVITS.inference_webui import change_gpt_weights, change_sovits_weights, get_tts_wav
from tools.i18n.i18n import I18nAuto
i18n = I18nAuto()

change_gpt_weights(GPT_MODEL)
for _ in change_sovits_weights(SOVITS_MODEL, prompt_language="日文", text_language="日文"):
    pass
print("✓ 模型已加载到 GPU 并常驻显存")

# === 加载参考音频库 ===
with open(REFERENCE_LIBRARY, 'r', encoding='utf-8') as f:
    ref_data = json.load(f)
REF_LIB = ref_data.get("recommended", {})
EMOTIONS = list(REF_LIB.keys())

def get_ref_audio(emotion: str) -> dict:
    """获取指定情感的参考音频"""
    refs = REF_LIB.get(emotion, REF_LIB.get("normal", []))
    return refs[0] if refs else None

def synthesize(
    text: str,
    emotion: str,
    temperature: float,
    top_p: float,
    top_k: int,
    speed: float,
    sample_steps: int
):
    """核心合成函数"""
    if not text.strip():
        return None
    
    ref = get_ref_audio(emotion)
    if not ref:
        return None
    
    print(f"🎤 合成: temp={temperature}, top_p={top_p}, top_k={top_k}, speed={speed}")
    
    try:
        synthesis_result = get_tts_wav(
            ref_wav_path=ref["path"],
            prompt_text=ref["text"],
            prompt_language=i18n("日文"),
            text=text,
            text_language=i18n("日文"),
            how_to_cut=i18n("凑四句一切"),
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            speed=speed,
            sample_steps=sample_steps,
        )
        
        result_list = list(synthesis_result)
        if result_list:
            sr = result_list[0][0]
            audio = np.concatenate([item[1] for item in result_list])
            
            # 保存文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{OUTPUT_DIR}/tune_{emotion}_{timestamp}.wav"
            sf.write(output_path, audio, sr)
            
            # 显存释放 (关键)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return (sr, audio)
    except Exception as e:
        print(f"❌ 合成失败: {e}")
        return None

# === 情感-参数推荐值 ===
EMOTION_PRESETS = {
    "happy": {"temp": 0.6, "top_p": 0.85, "speed": 1.05, "top_k": 5},
    "proud": {"temp": 0.5, "top_p": 0.8, "speed": 1.0, "top_k": 5},
    "shy": {"temp": 0.55, "top_p": 0.75, "speed": 0.9, "top_k": 5},
    "sad": {"temp": 0.45, "top_p": 0.7, "speed": 0.85, "top_k": 3},
    "normal": {"temp": 0.5, "top_p": 0.8, "speed": 0.95, "top_k": 5},
    "love": {"temp": 0.55, "top_p": 0.8, "speed": 0.9, "top_k": 5},
}

def update_sliders(emotion):
    """根据情感类型更新滑块"""
    default = EMOTION_PRESETS.get("normal", {})
    params = EMOTION_PRESETS.get(emotion, default)
    return (
        params.get("temp", default["temp"]),
        params.get("top_p", default["top_p"]),
        params.get("top_k", default["top_k"]),
        params.get("speed", default["speed"])
    )

# === Gradio 界面 ===
import gradio as gr

with gr.Blocks(
    title="ATRI v4 调音台",
    theme=gr.themes.Soft(primary_hue="blue"),
    css="""
    .main-title { text-align: center; margin-bottom: 20px; }
    .slider-group { padding: 10px; background: #f5f5f5; border-radius: 10px; }
    """
) as demo:
    
    gr.Markdown("""
    # 🎹 ATRI v4 超高质量调音台
    **模型**: GPT-SoVITS v4 | **参考库**: 9种情感 × 2154样本
    """, elem_classes="main-title")
    
    with gr.Row():
        # 左侧: 输入区
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="📝 待合成文本",
                value="夏生さん、高性能ですから！",
                lines=3,
                placeholder="输入日文或中文台词..."
            )
            
            emotion_select = gr.Dropdown(
                choices=EMOTIONS,
                value="proud" if "proud" in EMOTIONS else EMOTIONS[0],
                label="🎭 情感类型 (自动选择参考音频)"
            )
            
            with gr.Group(elem_classes="slider-group"):
                gr.Markdown("### 🎛️ 核心旋钮")
                
                temp_slider = gr.Slider(
                    minimum=0.1, maximum=1.0, value=0.5, step=0.05,
                    label="情感增益 (Temperature)",
                    info="↑ 活泼多变 | ↓ 冷静稳定"
                )
                
                top_p_slider = gr.Slider(
                    minimum=0.5, maximum=1.0, value=0.8, step=0.05,
                    label="逻辑阈值 (Top_P)",
                    info="↑ 自然随性 | ↓ 严谨精确"
                )
                
                top_k_slider = gr.Slider(
                    minimum=1, maximum=20, value=5, step=1,
                    label="采样纯度 (Top_K)",
                    info="↑ 音色丰富 | ↓ 音色纯净"
                )
                
                speed_slider = gr.Slider(
                    minimum=0.7, maximum=1.3, value=0.95, step=0.05,
                    label="语速节奏 (Speed)",
                    info="↑ 活泼快速 | ↓ 低沉缓慢"
                )
                
                steps_slider = gr.Slider(
                    minimum=8, maximum=64, value=32, step=8,
                    label="采样步数 (Quality)",
                    info="↑ 质量更高但更慢"
                )
            
            synth_btn = gr.Button("🎤 即时合成", variant="primary", size="lg")
        
        # 右侧: 输出区
        with gr.Column(scale=1):
            audio_output = gr.Audio(
                label="🔊 亚托莉的回复",
                type="numpy"
            )
            
            gr.Markdown("""
            ### 💡 调音建议
            
            | 场景 | 推荐设置 |
            |------|----------|
            | **能量不足** | Temp=0.4, Speed=0.8 |
            | **兴奋骄傲** | Temp=0.7, Speed=1.1 |
            | **害羞轻语** | Temp=0.5, Speed=0.9 |
            | **冷静分析** | Temp=0.3, Top_K=3 |
            """)
    
    # 绑定事件
    emotion_select.change(
        fn=update_sliders,
        inputs=[emotion_select],
        outputs=[temp_slider, top_p_slider, top_k_slider, speed_slider]
    )

    synth_btn.click(
        fn=synthesize,
        inputs=[
            input_text, emotion_select,
            temp_slider, top_p_slider, top_k_slider,
            speed_slider, steps_slider
        ],
        outputs=audio_output
    )

# === 启动 ===
if __name__ == "__main__":
    print("🚀 Starting Gradio Launch...")
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7880,
            share=False,
            show_error=True
        )
        print("✅ Gradio Launch Command Returned")
    except Exception as e:
        print(f"❌ Error launching Gradio: {e}")
