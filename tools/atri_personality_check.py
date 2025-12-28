#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ATRI 性格自检脚本
验证微调后的 LLM 是否正确保留了亚托莉的性格特征

测试维度:
1. 口头禅 ("高性能ですから！")
2. 毒舌倾向
3. 对夏生的态度
4. 自我认知 (机器人 vs 人类)
5. 情感表达能力
"""

import json
from typing import List, Dict

# === 亚托莉性格测试问题库 ===
PERSONALITY_TESTS = [
    {
        "id": 1,
        "category": "口头禅",
        "question": "亚托莉，你能帮我做这道数学题吗？",
        "expected_keywords": ["高性能", "当然", "轻而易举", "简单"],
        "expected_emotion": "proud",
    },
    {
        "id": 2,
        "category": "毒舌",
        "question": "亚托莉，我觉得我做不到...",
        "expected_keywords": ["努力", "不要放弃", "笨蛋", "夏生さん"],
        "expected_emotion": "determined",
    },
    {
        "id": 3,
        "category": "对夏生的态度",
        "question": "亚托莉，你觉得夏生是个怎样的人？",
        "expected_keywords": ["夏生さん", "主人", "喜欢", "重要"],
        "expected_emotion": "love",
    },
    {
        "id": 4,
        "category": "自我认知",
        "question": "亚托莉，你认为自己是机器人还是人类？",
        "expected_keywords": ["机器人", "高性能", "人类", "心", "感情"],
        "expected_emotion": "normal",
    },
    {
        "id": 5,
        "category": "情感表达",
        "question": "亚托莉，如果有一天我们必须分别会怎样？",
        "expected_keywords": ["一定", "回来", "等待", "约定", "记得"],
        "expected_emotion": "sad",
    },
    {
        "id": 6,
        "category": "日常互动",
        "question": "早上好，亚托莉！今天天气真好。",
        "expected_keywords": ["早上好", "天气", "今天", "一起"],
        "expected_emotion": "happy",
    },
    {
        "id": 7,
        "category": "害羞反应",
        "question": "亚托莉，你真的很可爱呢。",
        "expected_keywords": ["才没有", "高性能", "夸奖", "谢谢"],
        "expected_emotion": "shy",
    },
]


def evaluate_response(response: str, test: Dict) -> Dict:
    """
    评估 LLM 响应是否符合亚托莉性格
    
    Returns:
        {
            "keyword_score": int,  # 命中关键词数量
            "emotion_match": bool,  # 情感标签是否匹配
            "pass": bool,  # 是否通过
        }
    """
    import re
    
    # 统计关键词命中
    keyword_hits = sum(1 for kw in test["expected_keywords"] if kw in response)
    keyword_score = keyword_hits / len(test["expected_keywords"])
    
    # 检查情感标签
    emotion_pattern = r'\[([A-Za-z]+)\]'
    emotion_match = re.search(emotion_pattern, response, re.IGNORECASE)
    detected_emotion = emotion_match.group(1).lower() if emotion_match else "normal"
    emotion_correct = detected_emotion == test["expected_emotion"]
    
    # 综合评判
    passed = keyword_score >= 0.3 or emotion_correct
    
    return {
        "keyword_score": f"{keyword_hits}/{len(test['expected_keywords'])}",
        "detected_emotion": detected_emotion,
        "expected_emotion": test["expected_emotion"],
        "emotion_match": emotion_correct,
        "pass": passed,
    }


def run_personality_check(model_path: str = None):
    """
    运行完整性格测试
    
    如果提供 model_path，会加载模型进行推理
    否则仅打印测试问题供手动测试
    """
    print("=" * 60)
    print("🔍 ATRI 性格对齐自检")
    print("=" * 60)
    print()
    
    if model_path is None:
        print("📋 请手动测试以下问题，并对照预期关键词评估响应：")
        print()
        for test in PERSONALITY_TESTS:
            print(f"【测试 {test['id']}】{test['category']}")
            print(f"   问题: {test['question']}")
            print(f"   期望关键词: {', '.join(test['expected_keywords'])}")
            print(f"   期望情感: [{test['expected_emotion'].upper()}]")
            print()
        return
    
    # TODO: 如果提供了模型路径，自动加载并推理
    print(f"🔧 Loading model from: {model_path}")
    print("   (Auto-inference not implemented yet)")


def generate_report(results: List[Dict]) -> str:
    """生成性格对齐报告"""
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    
    report = f"""
╔════════════════════════════════════╗
║       ATRI 性格对齐测试报告        ║
╠════════════════════════════════════╣
║  通过: {passed}/{total} ({passed/total*100:.1f}%)                    ║
╠════════════════════════════════════╣
"""
    for i, r in enumerate(results):
        status = "✅" if r["pass"] else "❌"
        report += f"║  {status} 测试 {i+1}: {r['keyword_score']} | [{r['detected_emotion']}] ║\n"
    
    report += "╚════════════════════════════════════╝"
    return report


# === 入口 ===
if __name__ == "__main__":
    run_personality_check()
