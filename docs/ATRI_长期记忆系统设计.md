# ATRI - 长期记忆系统设计

> 🎄 **最后更新**: 2025-12-27 16:30
> 📊 **状态**: 基础架构就绪，待与 LLM-TTS 集成

---

## 🎯 核心目标

使 ATRI 能够"记住"与用户的对话历史、偏好和重要约定。

---

## ✅ 已完成

| 组件 | 状态 |
|------|------|
| Qdrant 向量库 | ✅ 测试通过 |
| Sentence-Transformers | ✅ |
| Mem0 引擎 | ✅ 已安装 |
| RAG 核心逻辑 | ✅ |

---

## 🧠 记忆层级

| 层级 | 功能 | 实现 |
|------|------|------|
| L1 瞬时 | 最近 10-20 轮 | LLM Context |
| L2 短期 | 当日摘要 | Mem0 |
| L3 长期 | 重要事件/偏好 | Qdrant |
| L4 身份 | 固定设定 | System Prompt |

---

## 🔗 与 TTS 集成规划

### Phase 1: 情感标签 (已实现)
```
用户输入 → LLM → [Emotion] → reference_library.json → TTS
```

### Phase 2: 动态参数控制 (封神级)
```
用户输入 → LLM → [Emotion=Sad, Speed=0.85, Pitch=-2]
                          ↓
            hq_tts_synthesis.py 解析标签
                          ↓
            GPT-SoVITS 动态调参合成
```

**参数映射表**:
| 场景 | Speed | Pitch | 效果 |
|------|-------|-------|------|
| 能量不足 | 0.85 | -1 | 低沉、疲惫 |
| 兴奋骄傲 | 1.1 | +1 | 活泼、上扬 |
| 害羞小声 | 0.9 | 0 | 轻柔、犹豫 |

---

## 📁 相关文件

| 文件 | 用途 |
|------|------|
| `test_memory_logic.py` | 记忆测试 |
| `reference_library.json` | 情感参考库 |
| `hq_tts_synthesis.py` | HQ 合成脚本 |

---

> *"我会记住关于你的一切……高性能ですから！"* 🎄
