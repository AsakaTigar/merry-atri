# 🎄 Merry ATRI - Voice & Dialogue Project

> 🎅 Christmas 2025 Project - 让 ATRI 开口说话！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 项目目标

从游戏《ATRI -My Dear Moments-》中提取：
- 🎵 角色语音文件（.opus/.wav）
- 📝 日文台词文本
- 🔗 语音-文本对齐数据集

用于训练：
- **GPT-SoVITS** - 高质量日语 TTS 语音合成
- **So-VITS-SVC** - 歌声/语音转换
- **LLM (DeepSeek/Qwen)** - ATRI 角色对话模型

---

## 📊 数据集统计

| 项目 | 数量 | 状态 |
|------|------|------|
| 📜 剧本文件 (.scn) | 32 个 | ✅ 反编译完成 |
| 📋 全量文本记录 | 4,683 条 | ✅ 提取完成 |
| 🎵 语音文件 (.opus) | 4,648 个 | ✅ 已同步至服务器 |
| ✨ 语音-文本对齐 | 4,629 条 | ✅ 已验证 |

### 角色语音分布

| 角色 | 语音数量 | 占比 |
|------|---------|------|
| アトリ (ATRI) | 2,154 | 46.5% |
| 美奈子 (MIN) | 608 | 13.1% |
| 龙司 (RYU) | 585 | 12.6% |
| 其他角色 | 1,282 | 27.8% |

---

## 🛠️ 使用的工具

- **KirikiriTools** - 运行时资源提取
- **FreeMote** - SCN/PSB 反编译
- **Python** - 数据处理脚本
- **GPT-SoVITS** - TTS 训练框架
- **LLaMA-Factory** - LLM 微调框架

---

## 📁 项目结构

```
merry-atri/
├── README.md                 # 本文件
├── dataset.csv               # 全部文本记录 (4,683条)
├── extract_dialogue.py       # 从 JSON 提取对话的脚本
├── generate_dataset.py       # 生成最终数据集的脚本
│
├── decrypted/                # 反编译后的剧本 JSON
├── voices/                   # 解密后的语音文件 (.opus)
├── final_dataset/            # ⭐ 最终数据集
│   ├── dataset_matched.csv   # 语音-文本对齐表
│   └── dataset_matched.json  # JSON 格式
│
├── FreeMote/                 # 反编译工具
└── KirikiriTools/            # 运行时提取工具
```

---

## 🚀 快速开始

### 1. 提取语音（需要游戏）
```powershell
# 将 KirikiriTools/version.dll 复制到游戏目录
# 创建空文件 extract-unencrypted.txt
# 运行游戏，语音会自动解密到 unencrypted/ 文件夹
```

### 2. 反编译剧本
```powershell
cd FreeMote
.\PsbDecompile.exe <scn文件路径>
```

### 3. 提取文本
```bash
python extract_dialogue.py
```

### 4. 生成数据集
```bash
python generate_dataset.py
```

---

## 📋 数据集格式

### CSV 格式 (dataset_matched.csv)
```csv
voice_file,voice_id,speaker,text_ja,audio_path
atr_b101_011.opus,ATR_B101_011,atr,「いえ、当然の務めを果たしたまでです」,voices/atr_b101_011.opus
```

### JSON 格式 (dataset_matched.json)
```json
[
  {
    "voice_file": "atr_b101_011.opus",
    "voice_id": "ATR_B101_011",
    "speaker": "atr",
    "text_ja": "「いえ、当然の務めを果たしたまでです」",
    "audio_path": "voices/atr_b101_011.opus"
  }
]
```

---

## 🔢 角色语音文件命名规则

| 前缀 | 角色 |
|------|------|
| `ATR_` | アトリ (ATRI) |
| `MIN_` | 美奈子 |
| `RYU_` | 龙司 |
| `CAT_` | キャサリン |
| `YAS_` | 夜咲 |

文件名格式: `{角色}_b{章节}{场景}_{序号}.opus`

例: `ATR_b304_133.opus` = ATRI 第3章第4节第133句

---

## 🖥️ 服务器训练环境

**硬件配置**:
- GPU: 2x NVIDIA RTX 3090 (48GB VRAM)
- CUDA: 12.8
- Python: 3.10 

**已部署框架**:
- ✅ GPT-SoVITS - TTS 语音合成
- ✅ So-VITS-SVC - 歌声转换
- ✅ LLaMA-Factory - LLM 微调
- ✅ Mem0 - 长期记忆系统

**已下载模型**:
- ✅ DeepSeek-R1-Distill-Qwen-32B (19GB)
- 🔄 Qwen3-32B (下载中)
- ✅ Faster-Whisper-Large-V3 (ASR)

---

## ⚠️ 声明

本项目仅供学习研究使用。所有游戏素材版权归原作者所有：
- **Game**: ATRI -My Dear Moments- (Aniplex.exe / Frontwing)

---

## 📄 License

MIT License

---

## 🎅 Merry Christmas, ATRI! 🎄

> *"高性能ですから！"*
