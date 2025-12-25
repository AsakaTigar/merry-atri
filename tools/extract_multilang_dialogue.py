import re
import json
import glob
import os
import time

# ================= 配置 =================
SOURCE_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/dataset/phase2_import"
OUTPUT_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/dataset/llm_finetune"
DATASET_INFO_PATH = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/frameworks/LLaMA-Factory/data/dataset_info.json"

# 角色映射表
ROLE_MAP = {
    # ATRI (AI)
    "アトリ": "gpt",
    "ATR": "gpt",
    
    # HUMANS (User)
    "夏生": "human",
    "NAT": "human",
    "水菜萌": "human",
    "MIN": "human", 
    "キャサリン": "human",
    "CAT": "human",
    "竜司": "human",
    "RYU": "human",
    "リリカ": "human",
    "RIR": "human",
    # 只要是不认识的，如果有名字，大概率是配角，视为 human
}

def clean_text(text):
    if not text: return ""
    text = text.replace('\\"', '"').replace('\\n', '\n')
    text = re.sub(r'%f[^;]+;', '', text) # 去除字体标记
    # 去除引号
    text = re.sub(r'^[「"““]', '', text)
    text = re.sub(r'[」"””]$', '', text)
    return text.strip()

def extract():
    print("🚀 开始提取多语言对话数据...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = glob.glob(os.path.join(SOURCE_DIR, "*.json"))
    print(f"📂 扫描 {len(files)} 个文件 in {SOURCE_DIR}")
    
    all_conversations = []
    
    # 核心 Regex:
    # 匹配 ["Char", ..., [[JA], [EN], [CN], ...]]
    # 我们捕捉 Group 1 (Char) 和 Group 2 (CN Text)
    # 如果 CN 不存在，我们暂时也不要 JA (因为我们需要训练中文模型)
    
    # 注意：JSON 里的结构是 [[null,"JA"], [null,"EN"], [null,"CN"]]
    # 而且之间可能有换行，因为 grep 显示在一行是 grep 的行为，实际文件即使被压缩成一行，Regex 也要能匹配。
    # 我们先读取整个文件，然后移除换行，再匹配。
    
    pattern = re.compile(
        r'\[\s*"([^"]+)"\s*,\s*(?:null|"[^"]*")\s*,\s*\[\s*'       # ["Char", DisplayName, [
        r'\[\s*(?:null|"[^"]*")\s*,\s*"(?:[^"\\]|\\.)*"\s*\]\s*,\s*' # JA
        r'\[\s*(?:null|"[^"]*")\s*,\s*"(?:[^"\\]|\\.)*"\s*\]\s*,\s*' # EN
        r'\[\s*(?:null|"[^"]*")\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'      # CN -> Group 2
    )
    
    total_found = 0
    
    for fpath in files:
        if fpath.endswith(".resx.json"): continue
        
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                # 暴力移除换行，确保 Regex 能在一行内匹配所有内容
                # 这对于处理格式化/非格式化的 JSON 都最稳健
                content = f.read().replace('\n', ' ') 
        except Exception as e:
            print(f"Skipping {fpath}: {e}")
            continue
            
        # 查找所有匹配
        matches = pattern.findall(content)
        if not matches:
             # 有些文件可能只有日文，没有 EN/CN，这些正则会失败。
             # 但我们要的是中文数据。
             continue
             
        # print(f"File {os.path.basename(fpath)}: Found {len(matches)} lines")
        total_found += len(matches)
        
        current_conv = []
        
        for char_id, raw_text in matches:
            text = clean_text(raw_text)
            if not text: continue
            
            # 确定角色
            role = ROLE_MAP.get(char_id)
            if not role:
                # 如果不在 Map 里，但也不是 "envupdate" 这种命令
                # 我们假设它是配角 human
                # 排除纯指令
                if len(char_id) > 20 or "update" in char_id:
                    continue
                role = "human"
            
            # 构建对话流
            if not current_conv:
                # 必须由 human/gpt 开头。如果第一句就是 gpt，我们怎么处理？
                # ShareGPT 格式最好是 human 开头。
                # 但如果是 gpt 开头，我们可以补一个空 human，或者允许 gpt 开头 (LLaMA Factory warning)
                current_conv.append({"from": role, "value": text})
            else:
                last_msg = current_conv[-1]
                if last_msg["from"] == role:
                    # 合并同一个人连续发话
                    last_msg["value"] += " " + text
                else:
                    current_conv.append({"from": role, "value": text})
        
        # 保存该文件的对话
        if len(current_conv) >= 2:
            # 只有包含 GPT 的对话才有意义
            if any(msg["from"] == "gpt" for msg in current_conv):
                all_conversations.append({
                    "conversations": current_conv,
                    "system": "你叫亚托莉（Atri），是一个高性能的机器人少女。你说话语气略带骄傲，但内心温柔。"
                })

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"atri_sharegpt_{timestamp}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print(f"✅ 处理完成！")
    print(f"   - 原始提取行数: {total_found}")
    print(f"   - 生成对话组数: {len(all_conversations)}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_conversations, f, ensure_ascii=False, indent=2)
        
    return output_path, timestamp

if __name__ == "__main__":
    path, ts = extract()
    
    # 注册
    try:
        with open(DATASET_INFO_PATH, 'r', encoding='utf-8') as f:
            info = json.load(f)
        
        key = f"atri_corpus_{ts}"
        info[key] = {
            "file_name": path,
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "system": "system"}
        }
        
        with open(DATASET_INFO_PATH, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
            
        # 写入 key 给 bash
        with open("/mnt/t2-6tb/Linpeikai/Voice/ATRI/latest_dataset_key.tmp", "w") as f:
            f.write(key)
            
        print(f"Key registered: {key}")
        
    except Exception as e:
        print(f"Registration failed: {e}")
