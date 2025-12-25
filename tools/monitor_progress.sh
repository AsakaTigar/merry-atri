#!/bin/bash
# ATRI 模型下载进度监控 - 带可视化进度条
# 使用: watch -n 5 bash monitor_progress.sh  或直接运行

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# 目标大小 (MB)
QWEN_TARGET=28000
DEEPSEEK_TARGET=28000
MISTRAL_TARGET=28000  # 改成14B了，约28GB

# 目录
WEIGHTS_DIR="/mnt/t2-6tb/Linpeikai/Voice/ATRI/weights/llm"

# 进度条函数
draw_progress_bar() {
    local current=$1
    local total=$2
    local width=40
    local percent=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    # 颜色根据进度变化
    local color=$RED
    if [ $percent -ge 100 ]; then
        color=$GREEN
    elif [ $percent -ge 50 ]; then
        color=$YELLOW
    elif [ $percent -ge 25 ]; then
        color=$CYAN
    fi
    
    printf "${color}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%${NC}" $percent
}

# 获取大小 (MB)
get_size_mb() {
    local dir=$1
    if [ -d "$dir" ]; then
        du -sm "$dir" 2>/dev/null | awk '{print $1}'
    else
        echo 0
    fi
}

# 清屏
clear

# 获取各模型大小
qwen_size=$(get_size_mb "$WEIGHTS_DIR/Qwen3-14B-Base")
deepseek_size=$(get_size_mb "$WEIGHTS_DIR/DeepSeek-R1-Distill-Qwen-14B")
mistral_size=$(get_size_mb "$WEIGHTS_DIR/Ministral-3-14B-Instruct")

# 限制最大值
[ "$qwen_size" -gt "$QWEN_TARGET" ] && qwen_size=$QWEN_TARGET
[ "$deepseek_size" -gt "$DEEPSEEK_TARGET" ] && deepseek_size=$DEEPSEEK_TARGET
[ "$mistral_size" -gt "$MISTRAL_TARGET" ] && mistral_size=$MISTRAL_TARGET

# 计算总进度
total_current=$((qwen_size + deepseek_size + mistral_size))
total_target=$((QWEN_TARGET + DEEPSEEK_TARGET + MISTRAL_TARGET))

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           🚀 ATRI 模型下载进度监控                           ║${NC}"
echo -e "${BOLD}║           $(date '+%Y-%m-%d %H:%M:%S')                              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Qwen3-14B
echo -e "${BOLD}📦 Qwen3-14B-Base${NC}"
printf "   "
draw_progress_bar $qwen_size $QWEN_TARGET
printf "  ${CYAN}%5dMB / %5dMB${NC}\n" $qwen_size $QWEN_TARGET
if [ "$qwen_size" -ge "$QWEN_TARGET" ]; then
    echo -e "   ${GREEN}✅ 下载完成${NC}"
else
    echo -e "   ${YELLOW}⏳ 下载中...${NC}"
fi
echo ""

# DeepSeek-14B
echo -e "${BOLD}📦 DeepSeek-R1-Distill-Qwen-14B${NC}"
printf "   "
draw_progress_bar $deepseek_size $DEEPSEEK_TARGET
printf "  ${CYAN}%5dMB / %5dMB${NC}\n" $deepseek_size $DEEPSEEK_TARGET
if [ "$deepseek_size" -ge "$DEEPSEEK_TARGET" ]; then
    echo -e "   ${GREEN}✅ 下载完成${NC}"
else
    echo -e "   ${YELLOW}⏳ 下载中...${NC}"
fi
echo ""

# Mistral-24B
echo -e "${BOLD}📦 Ministral-3-14B-Instruct${NC}"
printf "   "
draw_progress_bar $mistral_size $MISTRAL_TARGET
printf "  ${CYAN}%5dMB / %5dMB${NC}\n" $mistral_size $MISTRAL_TARGET
if [ "$mistral_size" -ge "$MISTRAL_TARGET" ]; then
    echo -e "   ${GREEN}✅ 下载完成${NC}"
elif [ "$mistral_size" -eq 0 ]; then
    echo -e "   ${BLUE}🔜 等待中...${NC}"
else
    echo -e "   ${YELLOW}⏳ 下载中...${NC}"
fi
echo ""

# 总进度
echo -e "${BOLD}────────────────────────────────────────────────────────────────${NC}"
echo -e "${BOLD}📊 总体进度${NC}"
printf "   "
draw_progress_bar $total_current $total_target
printf "  ${CYAN}%.1fGB / %.1fGB${NC}\n" $(echo "scale=1; $total_current/1024" | bc) $(echo "scale=1; $total_target/1024" | bc)
echo ""

# 检查是否全部完成
if [ "$qwen_size" -ge "$QWEN_TARGET" ] && [ "$deepseek_size" -ge "$DEEPSEEK_TARGET" ] && [ "$mistral_size" -ge "$MISTRAL_TARGET" ]; then
    echo -e "${GREEN}${BOLD}🎉🎉🎉 所有模型下载完成！可以开始训练了！ 🎉🎉🎉${NC}"
fi
echo ""
echo -e "${BOLD}提示:${NC} 使用 ${CYAN}watch -n 10 bash $(realpath $0)${NC} 自动刷新"
echo ""
