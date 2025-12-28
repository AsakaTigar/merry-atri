#!/bin/bash
# =============================================================================
# 🎹 ATRI 全链路双卡启动脚本
# GPU 0: TTS 调音台 (GPT-SoVITS v4)
# GPU 1: LLM 对话服务 (ATRI_Merged)
# =============================================================================

set -e

PROJECT_ROOT="/mnt/t2-6tb/Linpeikai/Voice/ATRI"
export PATH="/mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin:$PATH"

echo "🎹 ATRI 全链路启动中..."
echo ""

# === 清理残留进程 ===
echo "🧹 清理残留进程..."
pkill -f atri_tuning 2>/dev/null || true
pkill -f "llamafactory-cli api" 2>/dev/null || true
sleep 2

# === GPU 1: 启动 LLM API 服务 ===
echo "🧠 [GPU 1] 启动 ATRI LLM API 服务..."
cd "${PROJECT_ROOT}/frameworks/LLaMA-Factory"
CUDA_VISIBLE_DEVICES=1 nohup /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/llamafactory-cli api \
    --model_name_or_path "${PROJECT_ROOT}/weights/llm/ATRI_Merged" \
    --template qwen \
    --infer_backend huggingface \
    --port 8000 \
    > "${PROJECT_ROOT}/logs/llm_api.log" 2>&1 &
LLM_PID=$!
echo "   PID: ${LLM_PID}"
echo "   日志: logs/llm_api.log"
echo "   接口: http://localhost:8000"

# === 等待 LLM 加载 ===
echo "   等待模型加载 (约30秒)..."
sleep 30

# === GPU 0: 启动 TTS 调音台 ===
echo "🎤 [GPU 0] 启动 TTS 调音台..."
cd "${PROJECT_ROOT}"
CUDA_VISIBLE_DEVICES=0 nohup /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/python \
    atri_tuning_console.py \
    > "${PROJECT_ROOT}/logs/tts_console.log" 2>&1 &
TTS_PID=$!
echo "   PID: ${TTS_PID}"
echo "   日志: logs/tts_console.log"
echo "   接口: http://localhost:7880"

# === 显示状态 ===
echo ""
echo "============================================"
echo "✅ ATRI 全链路已启动！"
echo "============================================"
echo ""
echo "📡 服务端点:"
echo "   LLM API:  http://localhost:8000/v1/chat/completions"
echo "   TTS 调音台: http://localhost:7880"
echo ""
echo "📊 监控命令:"
echo "   nvidia-smi"
echo "   tail -f logs/llm_api.log"
echo "   tail -f logs/tts_console.log"
echo ""
echo "🔌 停止服务:"
echo "   pkill -f atri_tuning"
echo "   pkill -f 'llamafactory-cli api'"
echo ""
