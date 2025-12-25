#!/bin/bash
# ATRI 后台模型下载脚本 - 支持断点续传
# 使用: nohup bash download_models_bg.sh > /mnt/t2-6tb/Linpeikai/Voice/ATRI/logs/download_models.log 2>&1 &

LOG_FILE="/mnt/t2-6tb/Linpeikai/Voice/ATRI/logs/download_models.log"
WEIGHTS_DIR="/mnt/t2-6tb/Linpeikai/Voice/ATRI/weights/llm"
PYTHON="/mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/python"

# 清除代理环境变量
unset https_proxy http_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

echo "============================================" 
echo "🚀 ATRI 后台模型下载启动"
echo "   时间: $(date)"
echo "============================================"

# 1. Qwen3-14B-Base (如果未完成)
QWEN_SIZE=$(du -sm "$WEIGHTS_DIR/Qwen3-14B-Base" 2>/dev/null | awk '{print $1}')
if [ "${QWEN_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [1/3] 下载 Qwen3-14B-Base..."
    $PYTHON -c "
from modelscope import snapshot_download
snapshot_download('Qwen/Qwen3-14B-Base', 
    cache_dir='$WEIGHTS_DIR', 
    local_dir='$WEIGHTS_DIR/Qwen3-14B-Base')
"
    echo "✅ Qwen3-14B-Base 下载完成"
else
    echo "✅ Qwen3-14B-Base 已存在 (${QWEN_SIZE}MB)"
fi

# 2. DeepSeek-R1-Distill-Qwen-14B (如果未完成)
DEEPSEEK_SIZE=$(du -sm "$WEIGHTS_DIR/DeepSeek-R1-Distill-Qwen-14B" 2>/dev/null | awk '{print $1}')
if [ "${DEEPSEEK_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [2/3] 下载 DeepSeek-R1-Distill-Qwen-14B..."
    $PYTHON -c "
from modelscope import snapshot_download
snapshot_download('deepseek-ai/DeepSeek-R1-Distill-Qwen-14B', 
    cache_dir='$WEIGHTS_DIR', 
    local_dir='$WEIGHTS_DIR/DeepSeek-R1-Distill-Qwen-14B')
"
    echo "✅ DeepSeek-R1-Distill-Qwen-14B 下载完成"
else
    echo "✅ DeepSeek-R1-Distill-Qwen-14B 已存在 (${DEEPSEEK_SIZE}MB)"
fi

# 3. Ministral-3-14B-Instruct-2512 (使用HF-Mirror) - 最新的14B!
MISTRAL_SIZE=$(du -sm "$WEIGHTS_DIR/Ministral-3-14B-Instruct" 2>/dev/null | awk '{print $1}')
if [ "${MISTRAL_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [3/6] 下载 Ministral-3-14B-Instruct-2512 (via HF-Mirror)..."
    export HF_ENDPOINT=https://hf-mirror.com
    /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download \
        mistralai/Ministral-3-14B-Instruct-2512 \
        --local-dir "$WEIGHTS_DIR/Ministral-3-14B-Instruct" \
        --exclude "*.gguf"
    echo "✅ Ministral-3-14B-Instruct 下载完成"
else
    echo "✅ Ministral-3-14B-Instruct 已存在 (${MISTRAL_SIZE}MB)"
fi

# ============================================
# 🎌 二次元/角色扮演优化模型
# ============================================

# 4. Qwen2.5-14B-Roleplay-ZH (二次元角色扮演优化)
RP_SIZE=$(du -sm "$WEIGHTS_DIR/Qwen2.5-14B-Roleplay-ZH" 2>/dev/null | awk '{print $1}')
if [ "${RP_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [4/6] 下载 Qwen2.5-14B-Roleplay-ZH (二次元RP优化)..."
    export HF_ENDPOINT=https://hf-mirror.com
    /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download \
        gctian/qwen2.5-14B-roleplay-zh \
        --local-dir "$WEIGHTS_DIR/Qwen2.5-14B-Roleplay-ZH" \
        --exclude "*.gguf"
    echo "✅ Qwen2.5-14B-Roleplay-ZH 下载完成"
else
    echo "✅ Qwen2.5-14B-Roleplay-ZH 已存在 (${RP_SIZE}MB)"
fi

# 5. Yi-1.5-9B-Chat (文学创作/细腻语感)
YI_SIZE=$(du -sm "$WEIGHTS_DIR/Yi-1.5-9B-Chat" 2>/dev/null | awk '{print $1}')
if [ "${YI_SIZE:-0}" -lt 17000 ]; then
    echo "📦 [5/6] 下载 Yi-1.5-9B-Chat (文学创作优化)..."
    export HF_ENDPOINT=https://hf-mirror.com
    /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download \
        01-ai/Yi-1.5-9B-Chat \
        --local-dir "$WEIGHTS_DIR/Yi-1.5-9B-Chat" \
        --exclude "*.gguf"
    echo "✅ Yi-1.5-9B-Chat 下载完成"
else
    echo "✅ Yi-1.5-9B-Chat 已存在 (${YI_SIZE}MB)"
fi

# 6. NQLSG-Qwen2.5-14B-MegaFusion-v5-Roleplay (多数据集融合RP模型)
MEGA_SIZE=$(du -sm "$WEIGHTS_DIR/Qwen2.5-14B-MegaFusion-RP" 2>/dev/null | awk '{print $1}')
if [ "${MEGA_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [6/6] 下载 NQLSG-Qwen2.5-14B-MegaFusion-v5-Roleplay..."
    export HF_ENDPOINT=https://hf-mirror.com
    /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download \
        Lunzima/NQLSG-Qwen2.5-14B-MegaFusion-v5-roleplay \
        --local-dir "$WEIGHTS_DIR/Qwen2.5-14B-MegaFusion-RP" \
        --exclude "*.gguf"
    echo "✅ Qwen2.5-14B-MegaFusion-RP 下载完成"
else
    echo "✅ Qwen2.5-14B-MegaFusion-RP 已存在 (${MEGA_SIZE}MB)"
fi

echo ""
echo "============================================"
echo "🎉 所有模型下载完成!"
echo "   时间: $(date)"
echo "============================================"

# 显示最终状态
echo ""
echo "📊 模型大小汇总:"
du -sh "$WEIGHTS_DIR/Qwen3-14B-Base" \
       "$WEIGHTS_DIR/DeepSeek-R1-Distill-Qwen-14B" \
       "$WEIGHTS_DIR/Ministral-3-14B-Instruct" \
       "$WEIGHTS_DIR/Qwen2.5-14B-Roleplay-ZH" \
       "$WEIGHTS_DIR/Yi-1.5-9B-Chat" \
       "$WEIGHTS_DIR/Qwen2.5-14B-MegaFusion-RP" 2>/dev/null


# 7. Aris-Qwen1.5-14B-Chat-Agent-DPO (社区口碑极好的RP模型)
ARIS_SIZE=$(du -sm "$WEIGHTS_DIR/Aris-Qwen1.5-14B-DPO" 2>/dev/null | awk '{print $1}')
if [ "${ARIS_SIZE:-0}" -lt 27000 ]; then
    echo "📦 [7/7] 下载 Aris-Qwen1.5-14B-Chat-Agent-DPO (社区RP神器)..."
    export HF_ENDPOINT=https://hf-mirror.com
    /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download \
        Aris-AI/Aris-Qwen1.5-14B-Chat-Agent-DPO-16K-20240531 \
        --local-dir "$WEIGHTS_DIR/Aris-Qwen1.5-14B-DPO" \
        --exclude "*.gguf"
    echo "✅ Aris-Qwen1.5-14B-DPO 下载完成"
else
    echo "✅ Aris-Qwen1.5-14B-DPO 已存在 (${ARIS_SIZE}MB)"
fi
