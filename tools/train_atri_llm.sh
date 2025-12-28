#!/bin/bash
# =============================================================================
# 🎯 ATRI LLM 微调训练脚本 (QLoRA 极致稳健版)
# 基于 Qwen2.5-14B-Roleplay-ZH，使用 4-bit QLoRA 进行 SFT
# 显存需求: ~10-12GB (可与 TTS 推理共存)
# =============================================================================

set -e

# === 环境配置 ===
export CUDA_VISIBLE_DEVICES=0
export WANDB_DISABLED=true
export PATH="/mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin:$PATH"

# === 路径配置 ===
PROJECT_ROOT="/mnt/t2-6tb/Linpeikai/Voice/ATRI"
LLAMA_FACTORY="${PROJECT_ROOT}/frameworks/LLaMA-Factory"
MODEL_PATH="${PROJECT_ROOT}/weights/llm/Qwen2.5-14B-Roleplay-ZH"
DATASET_DIR="${PROJECT_ROOT}/dataset/llm_finetune"
OUTPUT_DIR="${PROJECT_ROOT}/weights/llm/ATRI_LLM_Checkpoints"

# === 创建输出目录 ===
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${PROJECT_ROOT}/logs"

echo "🚀 Starting ATRI LLM Fine-tuning (QLoRA 4-bit)..."
echo "   Model: ${MODEL_PATH}"
echo "   Dataset: ${DATASET_DIR}/atri_roleplay.json"
echo "   Output: ${OUTPUT_DIR}"
echo "   Mode: QLoRA 4-bit + Double Quantization"
echo ""

# === 显存检查 ===
FREE_MEM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0 | head -1)
echo "   GPU 0 Free Memory: ${FREE_MEM} MiB"
if [ "$FREE_MEM" -lt 8000 ]; then
    echo "⚠️ Warning: Low GPU memory! Consider closing other processes."
fi
echo ""

# === 执行训练 (单卡 QLoRA) ===
cd "${LLAMA_FACTORY}"

/mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/llamafactory-cli train \
    --stage sft \
    --do_train true \
    --model_name_or_path "${MODEL_PATH}" \
    --dataset atri_roleplay \
    --dataset_dir "${DATASET_DIR}" \
    --template qwen \
    --finetuning_type lora \
    --lora_target all \
    --lora_rank 32 \
    --lora_alpha 64 \
    --output_dir "${OUTPUT_DIR}" \
    --overwrite_cache true \
    --overwrite_output_dir true \
    --quantization_bit 4 \
    --quantization_method bnb \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 100 \
    --learning_rate 2e-4 \
    --num_train_epochs 3.0 \
    --max_grad_norm 1.0 \
    --warmup_ratio 0.1 \
    --plot_loss true \
    --bf16 true \
    --flash_attn auto \
    --report_to none \
    --ddp_timeout 180000000

echo "✅ Training Complete! Checkpoints saved to: ${OUTPUT_DIR}"
