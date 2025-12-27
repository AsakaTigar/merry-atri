# ATRI 对话模型 (LLM) 可行性与资源清单

> 🎄 **最后更新**: 2025-12-27 16:32
> 📊 **状态**: 模型库完备，待选型微调

---

## 1. 硬件资源

**配置**: 2x NVIDIA RTX 3090 (48GB VRAM)
**评估**: **极高可行性** ✅

---

## 2. 可用模型库 (总计 ~265GB)

| 模型 | 大小 | 特点 | 推荐用途 |
|------|------|------|----------|
| **Qwen2.5-14B-Roleplay-ZH** | 28G | 中文角色扮演专精 | ⭐ 首选 |
| **DeepSeek-R1-Distill-Qwen-14B** | 28G | 强推理能力 | 推理任务 |
| **Qwen3-14B-Base** | 28G | 通用底模 | 通用 |
| **Qwen2.5-14B-MegaFusion-RP** | 26G | 融合角色扮演 | RP 备选 |
| **Aris-Qwen1.5-14B-DPO** | 27G | DPO 优化 | 对齐优化 |
| **Ministral-3-14B-Instruct** | 30G | 指令遵循 | 指令任务 |
| **Yi-1.5-9B-Chat** | 17G | 轻量对话 | 快速推理 |
| **Qwen3-32B-final** | 62G | 大规模 | ⚠️ 需优化 |
| **DeepSeek-R1-Distill-Qwen-32B** | 19G | 不完整 | ❌ 弃用 |

**存储路径**: `/mnt/t2-6tb/Linpeikai/Voice/ATRI/weights/llm/`

---

## 3. 推荐方案

### 🎯 主力: Qwen2.5-14B-Roleplay-ZH
- **理由**: 专为中文角色扮演优化，情感理解能力强
- **显存**: ~16GB (QLoRA) / ~28GB (Full)
- **输出格式**: `[Emotion] 文本内容`

### 备选: DeepSeek-R1-Distill-Qwen-14B  
- **理由**: 强推理，适合复杂对话逻辑

---

## 4. 数据集

| 类型 | 数量 | 格式 |
|------|------|------|
| 对话数据 | 1566 组 | ShareGPT |
| 语音-文本对齐 | 4629 条 | CSV |
| 情感参考库 | 2154 条 | JSON |

---

## 5. 集成架构

```
用户输入 → LLM 分析 → [Emotion] 标签
                ↓
        reference_library.json
                ↓
        GPT-SoVITS v4 合成
```

---

## 6. 组件状态

| 组件 | 状态 |
|------|------|
| 14B 模型库 | ✅ 7 个可用 |
| LLaMA-Factory | ✅ 已部署 |
| GPT-SoVITS v4 | 🔥 训练中 |
| 长期记忆 (Mem0) | ✅ 测试通过 |

---

> *"高性能ですから！"* 🎄
