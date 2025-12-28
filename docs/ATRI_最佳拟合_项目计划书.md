# ATRI - 极致语音拟合项目计划书

> 🎄 **最后更新**: 2025-12-28 16:25
> 📊 **状态**: ✅ 全链路已完成！

---

## 🎯 项目目标

构建 **ATRI (亚托莉)** 的超高质量语音生成系统，实现：
1. **GPT-SoVITS v4**: 主力 TTS 引擎
2. **LLM 情感分析**: 自动匹配参考音频
3. **长期记忆**: 智能对话系统

---

## ✅ 已完成

| 阶段 | 任务 | 状态 |
|------|------|------|
| **数据工程** | 4648 语音提取 → 2154 条 ATRI 训练集 | ✅ |
| **v2 训练** | SoVITS e50 + GPT e15 | ✅ |
| v4 预训练 | s2Gv4.pth (769MB) + vocoder (57MB) | ✅ |
| **v4 训练 (双卡)** | SoVITS (e10) + GPT (e20, Acc 90%) | ✅ |
| **HQ 合成** | 调音台 WebUI `atri_tuning_console.py` | ✅ |
| **参考库** | 9 种情感 × 2154 样本 | ✅ |
| **评测工具** | `evaluate_checkpoints.py` | ✅ |
| **对话数据** | 1566 组 ShareGPT 格式 | ✅ |
| **LLM 微调** | QLoRA 4-bit, Loss 2.6→0.37 | ✅ |
| **模型合并** | ATRI_Merged (28GB, 16 shards) | ✅ |
| **全链路脚本** | `start_atri_full_pipeline.sh` | ✅ |

---

## 🚀 快速启动

### 全链路一键启动 (推荐)
```bash
cd /mnt/t2-6tb/Linpeikai/Voice/ATRI
./start_atri_full_pipeline.sh
```

### 单独启动组件
```bash
# GPU 0: TTS 调音台
CUDA_VISIBLE_DEVICES=0 python atri_tuning_console.py

# GPU 1: LLM API 服务
CUDA_VISIBLE_DEVICES=1 llamafactory-cli api \
    --model_name_or_path ./weights/llm/ATRI_Merged \
    --template qwen --port 8000
```

---

## 📂 关键目录

```
/mnt/t2-6tb/Linpeikai/Voice/ATRI/
├── dataset/
│   ├── gpt_sovits_train/        # 2154 条 WAV
│   ├── reference_library.json   # 情感参考库
│   └── llm_finetune/            # 对话数据集 (1566组)
├── weights/
│   ├── gpt-sovits/ATRI/         # v4 TTS 模型
│   └── llm/
│       ├── ATRI_LLM_Checkpoints/  # LoRA adapter
│       └── ATRI_Merged/           # 合并后完整模型 (28GB)
├── tools/                        # 核心脚本
│   ├── atri_tuning_console.py    # TTS 调音台
│   ├── atri_llm_tts_bridge.py    # 情感-TTS 桥接
│   └── atri_personality_check.py # 性格自检
├── logs/                         # 训练/推理日志
└── frameworks/
    ├── GPT-SoVITS/               # TTS 框架
    └── LLaMA-Factory/            # LLM 框架
```

---

## 🎹 服务端点

| 服务 | 地址 | GPU |
|------|------|-----|
| TTS 调音台 | http://localhost:7880 | 0 |
| LLM API | http://localhost:8000 | 1 |

---

> *"高性能ですから！"* 🎄
