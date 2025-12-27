# ATRI - 极致语音拟合项目计划书

> 🎄 **最后更新**: 2025-12-27 16:30
> 📊 **状态**: v4 双卡训练中 🔥

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

---

## 🔥 当前进度: v4 训练

### 双卡并行策略 (2x RTX 3090)

| GPU | 模型 | 配置 | 显存 |
|-----|------|------|------|
| 0 | SoVITS v4 | Batch 24, 10 epochs | 20GB |
| 1 | GPT v4 (DPO) | Batch 8, 20 epochs | 12GB |

### 日志位置
```
logs/train_sovits_v4.log
logs/train_gpt_v4.log
```

---

## 📂 关键目录

```
/mnt/t2-6tb/Linpeikai/Voice/ATRI/
├── dataset/
│   ├── gpt_sovits_train/     # 2154 条 WAV
│   ├── reference_library.json # 情感参考库
│   └── llm_finetune/         # 对话数据集
├── weights/gpt-sovits/ATRI/  # 训练产物
├── tts_outputs/              # 合成输出
└── frameworks/GPT-SoVITS/    # 主框架
```

---

## 🎯 下一步

1. **训练完成** → 运行 `python evaluate_checkpoints.py`
2. **效果对比** → v2 vs v4 A/B 测试
3. **LLM 联动** → [Emotion] 标签自动选参考音频

---

> *"高性能ですから！"* 🎄
