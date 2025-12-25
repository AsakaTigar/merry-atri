#!/usr/bin/env python3
"""
ATRI 模型下载监控 Web 面板
启动: python model_download_dashboard.py
访问: http://localhost:9877
"""

from flask import Flask, render_template_string, jsonify, request
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)

WEIGHTS_DIR = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/weights/llm"
DOWNLOAD_SCRIPT = "/mnt/t2-6tb/Linpeikai/Voice/ATRI/download_models_bg.sh"

# 模型配置
MODELS = {
    "Qwen3-14B-Base": {"target_mb": 28000, "source": "modelscope", "repo": "Qwen/Qwen3-14B-Base"},
    "DeepSeek-R1-Distill-Qwen-14B": {"target_mb": 28000, "source": "modelscope", "repo": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"},
    "Ministral-3-14B-Instruct": {"target_mb": 28000, "source": "hf-mirror", "repo": "mistralai/Ministral-3-14B-Instruct-2512"},
    "Qwen2.5-14B-Roleplay-ZH": {"target_mb": 28000, "source": "hf-mirror", "repo": "gctian/qwen2.5-14B-roleplay-zh"},
    "Yi-1.5-9B-Chat": {"target_mb": 18000, "source": "hf-mirror", "repo": "01-ai/Yi-1.5-9B-Chat"},
    "Qwen2.5-14B-MegaFusion-RP": {"target_mb": 28000, "source": "hf-mirror", "repo": "Lunzima/NQLSG-Qwen2.5-14B-MegaFusion-v5-roleplay"},
    "Aris-Qwen1.5-14B-DPO": {"target_mb": 28000, "source": "hf-mirror", "repo": "Aris-AI/Aris-Qwen1.5-14B-Chat-Agent-DPO-16K-20240531"},
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATRI 模型下载监控</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7b68ee, #ff6b9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle { color: #888; font-size: 1.1em; }
        .timestamp { color: #666; margin-top: 10px; }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .stat-item {
            text-align: center;
            padding: 20px 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #00d4ff;
        }
        .stat-label { color: #888; margin-top: 5px; }
        
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .model-card {
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0,212,255,0.2);
        }
        
        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .model-name {
            font-size: 1.1em;
            font-weight: 600;
            color: #fff;
        }
        .model-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 500;
        }
        .status-complete { background: #00c853; color: #fff; }
        .status-downloading { background: #ff9800; color: #fff; animation: pulse 1.5s infinite; }
        .status-waiting { background: #666; color: #fff; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .progress-container {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            height: 24px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85em;
            font-weight: 600;
        }
        .progress-low { background: linear-gradient(90deg, #ff6b6b, #ff8e53); }
        .progress-mid { background: linear-gradient(90deg, #ff9800, #ffc107); }
        .progress-high { background: linear-gradient(90deg, #00c853, #69f0ae); }
        
        .model-info {
            display: flex;
            justify-content: space-between;
            color: #888;
            font-size: 0.9em;
        }
        .model-source {
            margin-top: 10px;
            font-size: 0.8em;
            color: #666;
        }
        
        .add-model-section {
            margin-top: 40px;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
        }
        .add-model-section h2 {
            margin-bottom: 20px;
            color: #00d4ff;
        }
        .input-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 12px 20px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
        }
        input { flex: 1; min-width: 200px; }
        select { min-width: 150px; }
        button {
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 ATRI 模型下载监控</h1>
            <div class="subtitle">高性能ですから！</div>
            <div class="timestamp" id="timestamp"></div>
        </header>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-value" id="total-models">0</div>
                <div class="stat-label">总模型数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="completed-models">0</div>
                <div class="stat-label">已完成</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="total-size">0 GB</div>
                <div class="stat-label">已下载</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="avg-speed">-- MB/s</div>
                <div class="stat-label">平均速度</div>
            </div>
        </div>
        
        <div class="models-grid" id="models-grid"></div>
        
        <div class="add-model-section">
            <h2>➕ 添加新模型下载</h2>
            <div class="input-group">
                <input type="text" id="new-repo" placeholder="模型仓库 (如: Qwen/Qwen2.5-7B-Instruct)">
                <input type="text" id="new-name" placeholder="本地文件夹名">
                <select id="new-source">
                    <option value="hf-mirror">HF-Mirror (国内直连)</option>
                    <option value="modelscope">ModelScope (阿里)</option>
                </select>
                <button onclick="addModel()">开始下载</button>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="fetchData()">🔄</button>
    
    <script>
        let lastSizes = {};
        
        function fetchData() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    updateUI(data);
                    document.getElementById('timestamp').textContent = 
                        '更新于 ' + new Date().toLocaleTimeString();
                });
        }
        
        function updateUI(data) {
            const grid = document.getElementById('models-grid');
            grid.innerHTML = '';
            
            let totalSize = 0, completed = 0;
            
            for (const [name, info] of Object.entries(data.models)) {
                totalSize += info.current_mb;
                if (info.percent >= 100) completed++;
                
                const card = document.createElement('div');
                card.className = 'model-card';
                
                let statusClass = 'status-waiting';
                let statusText = '等待中';
                if (info.percent >= 100) {
                    statusClass = 'status-complete';
                    statusText = '✅ 完成';
                } else if (info.current_mb > 0) {
                    statusClass = 'status-downloading';
                    statusText = '⏳ 下载中';
                }
                
                let progressClass = 'progress-low';
                if (info.percent >= 75) progressClass = 'progress-high';
                else if (info.percent >= 25) progressClass = 'progress-mid';
                
                card.innerHTML = `
                    <div class="model-header">
                        <span class="model-name">${name}</span>
                        <span class="model-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar ${progressClass}" style="width: ${Math.min(info.percent, 100)}%">
                            ${info.percent.toFixed(1)}%
                        </div>
                    </div>
                    <div class="model-info">
                        <span>${(info.current_mb/1024).toFixed(1)} GB / ${(info.target_mb/1024).toFixed(1)} GB</span>
                    </div>
                    <div class="model-source">📦 ${info.source} | ${info.repo}</div>
                `;
                grid.appendChild(card);
            }
            
            document.getElementById('total-models').textContent = Object.keys(data.models).length;
            document.getElementById('completed-models').textContent = completed;
            document.getElementById('total-size').textContent = (totalSize/1024).toFixed(1) + ' GB';
        }
        
        function addModel() {
            const repo = document.getElementById('new-repo').value;
            const name = document.getElementById('new-name').value;
            const source = document.getElementById('new-source').value;
            
            if (!repo || !name) {
                alert('请填写模型仓库和本地文件夹名');
                return;
            }
            
            fetch('/api/download', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({repo, name, source})
            }).then(r => r.json()).then(data => {
                alert(data.message);
                fetchData();
            });
        }
        
        fetchData();
        setInterval(fetchData, 10000);
    </script>
</body>
</html>
'''

def get_dir_size_mb(path):
    """获取目录大小 (MB)"""
    try:
        result = subprocess.run(['du', '-sm', path], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return int(result.stdout.split()[0])
    except:
        pass
    return 0

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    models_status = {}
    for name, config in MODELS.items():
        path = os.path.join(WEIGHTS_DIR, name)
        current_mb = get_dir_size_mb(path)
        target_mb = config['target_mb']
        percent = (current_mb / target_mb * 100) if target_mb > 0 else 0
        
        models_status[name] = {
            "current_mb": current_mb,
            "target_mb": target_mb,
            "percent": min(percent, 100),
            "source": config['source'],
            "repo": config['repo']
        }
    
    return jsonify({"models": models_status, "timestamp": datetime.now().isoformat()})

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.json
    repo = data.get('repo')
    name = data.get('name')
    source = data.get('source', 'hf-mirror')
    
    if not repo or not name:
        return jsonify({"success": False, "message": "缺少参数"})
    
    local_dir = os.path.join(WEIGHTS_DIR, name)
    
    if source == 'hf-mirror':
        cmd = f'''
        export HF_ENDPOINT=https://hf-mirror.com
        nohup /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/huggingface-cli download {repo} --local-dir {local_dir} --exclude "*.gguf" > /tmp/download_{name}.log 2>&1 &
        '''
    else:
        cmd = f'''
        nohup /mnt/t2-6tb/Linpeikai/linux/envs/Aoduo/bin/python -c "
from modelscope import snapshot_download
snapshot_download('{repo}', local_dir='{local_dir}')
" > /tmp/download_{name}.log 2>&1 &
        '''
    
    subprocess.Popen(cmd, shell=True, executable='/bin/bash')
    
    # 添加到监控列表
    MODELS[name] = {"target_mb": 28000, "source": source, "repo": repo}
    
    return jsonify({"success": True, "message": f"已开始下载 {repo}"})

if __name__ == '__main__':
    print("🚀 ATRI 模型下载监控面板启动中...")
    print("📍 访问地址: http://localhost:9877")
    app.run(host='0.0.0.0', port=9877, debug=False)
