# 🎄 Merry ATRI - 高性能ですから！

> 基于《ATRI -My Dear Moments-》的全栈 AI 项目

[![GitHub stars](https://img.shields.io/github/stars/AsakaTigar/merry-atri?style=social)](https://github.com/AsakaTigar/merry-atri)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<p align="center">
  <i>"我可是高性能的！"</i>
</p>

---

## 📖 项目简介

本项目旨在通过现代 AI 技术重现《ATRI -My Dear Moments-》中的角色交互体验，实现：

- **语音合成** - 高质量的 VITS/GPT-SoVITS 语音克隆
- **对话系统** - 基于 LLM 的个性化角色扮演
- **长期记忆** - 实现对话历史的持久化与检索

---

## ✨ 特色工具

### 1. 模型下载监控面板

一个直观的 Web 界面，实时监控多个大模型的下载进度。

```bash
# 启动
python model_download_dashboard.py

# 访问: http://localhost:9877
```

**功能特点**：
- 实时进度条 (每10秒刷新)
- 渐变动画 + 响应式设计
- 一键添加新模型下载
- 支持 HF-Mirror (国内直连) 和 ModelScope

### 2. 后台模型下载脚本

支持断点续传的批量模型下载脚本，已预置 7 个二次元 RP 优化模型。

```bash
# 后台运行
nohup bash download_models_bg.sh > logs/download_models.log 2>&1 &

# 查看进度
bash monitor_progress.sh
```

**预置模型**：
| 模型 | 大小 | 特点 |
|------|------|------|
| Qwen3-14B-Base | ~28GB | 通用基座 |
| DeepSeek-R1-Distill-Qwen-14B | ~28GB | 推理增强 |
| Ministral-3-14B-Instruct | ~28GB | Mistral 最新 |
| Qwen2.5-14B-Roleplay-ZH | ~28GB | 🎌 二次元 RP |
| Yi-1.5-9B-Chat | ~18GB | 文学创作 |
| Qwen2.5-14B-MegaFusion-RP | ~28GB | 多数据融合 |
| Aris-Qwen1.5-14B-DPO | ~28GB | 社区口碑 |

### 3. Clash TUN 代理绕过配置

为服务器上的全局 TUN 代理配置国内镜像直连，避免下载模型时消耗代理流量。

**已配置直连的域名**：
- ModelScope、HF-Mirror、Mistral.ai
- 清华 TUNA、阿里镜像、华为云
- 百度、腾讯、B站等国内站点

详见 `/opt/clash/runtime.yaml` 中的 `fake-ip-filter` 配置。

### 4. GPT-SoVITS 语音训练

基于 GPT-SoVITS 的亚托莉语音克隆。

```bash
# 一键训练
bash train_gpt_sovits_master.sh

# TensorBoard 监控
tensorboard --logdir=frameworks/GPT-SoVITS/logs/ATRI
```

### 5. LLM 对话模型微调

使用 LLaMA-Factory 对 14B 模型进行 LoRA 微调。

```bash
# 一键启动 (数据处理 + 训练)
bash train_llm_master.sh
```

**训练数据**：游戏完整剧本对话，共 5030 条，29 个 Session，平均 66 轮/会话。

---

## 📂 项目结构

```
merry-atri/
├── 📄 README.md                    # 本文件
├── 📄 每次必读文件.md               # 开发者必读
├── 📄 工作日志情况.md               # 开发日志
│
├── tools/                          # 工具脚本
│   ├── atri_tuning_console.py      # 调音台 WebUI
│   ├── hq_tts_synthesis.py         # 高质量合成 CLI
│   ├── model_download_dashboard.py # Web 监控面板
│   └── ...
│
├── weights/
│   ├── llm/                        # LLM 模型权重
│   └── gpt_sovits/                 # 语音模型权重
│
├── dataset/                        # 训练数据
│   └── phase2_import/              # 游戏剧本 JSON
│
├── frameworks/
│   ├── GPT-SoVITS/                 # 语音合成框架
│   └── LLaMA-Factory/              # LLM 微调框架
│
└── logs/                           # 训练日志
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- CUDA 12.x
- 2x RTX 3090 或同等算力 (48GB+ VRAM)
- 200GB+ 磁盘空间

### 1. 克隆仓库
```bash
git clone https://github.com/AsakaTigar/merry-atri.git
cd merry-atri
```

### 2. 安装依赖
```bash
conda activate Aoduo  # 或你的环境
pip install flask modelscope transformers datasets
```

### 3. 下载模型
```bash
# 启动下载
nohup bash download_models_bg.sh > logs/download_models.log 2>&1 &

# 监控进度
python model_download_dashboard.py  # 打开 http://localhost:9877
```

### 4. 开始微调
```bash
bash train_llm_master.sh
```

---

## 📝 TODO

- [x] GPT-SoVITS 语音训练
- [x] LLM 对话数据提取
- [x] 模型下载监控面板
- [x] 调音台 WebUI
- [ ] LLM 微调完成
- [ ] 整合语音 + 对话 Pipeline
- [ ] 长期记忆系统 (Mem0)

---

## 🙏 致谢

- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) - 语音合成
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) - LLM 微调
- [ATRI -My Dear Moments-](https://atri-mdm.com/) - 原作游戏
- Qwen、DeepSeek、Mistral、Yi 等开源模型

---

## 📜 License

MIT License - 仅供学习交流，请勿用于商业用途。

---

<p align="center">
  <b>高性能ですから！</b> 🎄
</p>
