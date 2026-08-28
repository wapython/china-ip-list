#!/usr/bin/env python3
"""
从 chnroute.txt 获取中国 IP 段，生成 Clash 覆写用的 JavaScript 规则文件。
仅当远程数据与本地文件不一致时才写入，避免无意义的提交。
"""

import urllib.request
import os
from datetime import datetime

URL = "https://raw.githubusercontent.com/mayaxcn/china-ip-list/master/chnroute.txt"
OUTPUT_FILE = "ip-rules.js"

def fetch_cidrs():
    with urllib.request.urlopen(URL) as resp:
        data = resp.read().decode('utf-8')
    cidrs = []
    for line in data.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            cidrs.append(line)
    return cidrs

def generate_content(cidrs):
    timestamp = datetime.now().isoformat()
    lines = [f'    "{cidr}"' for cidr in cidrs]
    return f"""// 自动生成，请勿手动编辑
// 数据来源：{URL}
// 更新时间：{timestamp}

const directIPs = [
{',\n'.join(lines)}
];

function main(config) {{
    if (!config.rules) {{
        config.rules = [];
    }}
    // 从后往前插入，保持顺序
    for (let i = directIPs.length - 1; i >= 0; i--) {{
        config.rules.unshift(`IP-CIDR,${{directIPs[i]}},DIRECT`);
    }}
    return config;
}}
"""

def main():
    cidrs = fetch_cidrs()
    new_content = generate_content(cidrs)

    # 读取现有文件内容（如果存在）
    old_content = None
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            old_content = f.read()

    if old_content == new_content:
        print("No changes detected, skipping update.")
        return

    # 内容有变化，写入新文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("IP rules updated successfully.")

if __name__ == "__main__":
    main()
