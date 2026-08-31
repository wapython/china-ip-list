# China IP Rules for Clash

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/wapython/china-ip-list/update-ip-rules.yml?branch=main&label=Update%20IP%20Rules)](https://github.com/wapython/china-ip-list/actions/workflows/update-ip-rules.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/wapython/china-ip-list)](https://github.com/wapython/china-ip-list/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wapython/china-ip-list)](https://github.com/wapython/china-ip-list)

本项目通过 GitHub Actions **每小时**自动拉取 [chnroute.txt](https://raw.githubusercontent.com/mayaxcn/china-ip-list/master/chnroute.txt) 中的中国 IP 段，生成一个可直接用于 Clash 覆写（Override）或脚本（Script）模式的 JavaScript 规则文件 `ip-rules.js`，让你始终拥有最新的国内 IP 直连规则。

## ✨ 特性

- ⏱️ **每小时自动更新** – 始终保持最新 IP 段
- 🧠 **智能变更检测** – 仅当源数据变化时才提交新文件，避免冗余提交
- 🌐 **多 CDN 加速引用** – 提供国内镜像站，快速加载
- 🔧 **易于定制** – 可轻松添加自定义直连域名或调整插入顺序
- 📦 **即拿即用** – 生成的 `ip-rules.js` 可直接在 Clash 中通过 `eval` 注入

## 📁 文件说明

| 文件 | 说明 |
| :--- | :--- |
| `.github/workflows/update-ip-rules.yml` | GitHub Actions 工作流定义，每小时触发一次 |
| `scripts/generate-ip-rules.py` | Python 脚本，负责下载并生成规则文件 |
| `ip-rules.js` | 最终生成的规则文件（自动提交到仓库） |

## 🚀 快速开始

### 1. 直接引用（在线加载）
你可以通过以下 URL 直接在线引用该文件：

```
https://raw.githubusercontent.com/wapython/china-ip-list/main/ip-rules.js
```

### 2. 通过 CDN 加速引用（推荐国内用户）
为提高国内访问速度，推荐使用以下任一 CDN 地址：

| 加速方式 | URL 格式 |
| :--- | :--- |
| **jsDelivr 官方 CDN** | `https://cdn.jsdelivr.net/gh/wapython/china-ip-list/ip-rules.js` |
| **国内镜像站（推荐）** | `https://jsd.cdn.zzko.cn/gh/wapython/china-ip-list/ip-rules.js` |
| **国内镜像站（备选）** | `https://jsdelivr.topthink.com/gh/wapython/china-ip-list/ip-rules.js` |
| **国内镜像站（备选）** | `https://jsd.onmicrosoft.cn/gh/wapython/china-ip-list/ip-rules.js` |

### 3. 在 Clash 中集成
**方式 A – 使用 script 模式（适用于 Clash Premium / Meta）**

在 Clash 配置文件中添加：

```yaml
script:
  code: |
    // 推荐使用国内镜像加速
    const response = await fetch("https://jsd.cdn.zzko.cn/gh/wapython/china-ip-list/ip-rules.js");
    const script = await response.text();
    eval(script);
    // 调用 main(config) 将中国 IP 段以 IP-CIDR 规则插入
    main(config);
```

**方式 B – 使用 rule-providers（适用于 Clash Meta）**

```yaml
rule-providers:
  china-ip:
    type: http
    behavior: classical
    url: "https://jsd.cdn.zzko.cn/gh/wapython/china-ip-list/ip-rules.js"
    path: ./ruleset/china-ip.yaml
    interval: 3600
```

## 📝 规则内容

生成的 `ip-rules.js` 包含两个核心部分：

1. **`directIPs` 数组** – 所有中国 IP 段的 CIDR 列表（约 9000+ 条）
2. **`main(config)` 函数** – 将 `directIPs` 中的每个 IP 段以 `IP-CIDR,<cidr>,DIRECT` 的形式插入到 `config.rules` 中（采用**从后往前插入**，确保原有规则优先级更高）

**生成的 JS 文件结构示例**：

```javascript
const directIPs = [
    "1.0.1.0/24",
    "1.0.2.0/23",
    // ... 数千个 CIDR 段
];

function main(config) {
    if (!config.rules) {
        config.rules = [];
    }
    for (let i = directIPs.length - 1; i >= 0; i--) {
        config.rules.unshift(`IP-CIDR,${directIPs[i]},DIRECT`);
    }
    return config;
}
```

## ⏰ 自动更新机制

- **触发频率**：每小时执行一次（UTC 时间的每个整点，即北京时间 08:00 至次日 07:00 的每个整点）
- **智能判断**：仅当远程 `chnroute.txt` 内容发生变化时，才会更新 `ip-rules.js` 并自动提交；无变化则跳过，避免无用提交。
- **手动触发**：你也可以在 [GitHub Actions 页面](https://github.com/wapython/china-ip-list/actions/workflows/update-ip-rules.yml) 点击 **"Run workflow"** 手动触发更新。

## 🔧 高级用法

### 1. 添加自定义直连域名
如果你希望额外直连某些域名，可以修改 `scripts/generate-ip-rules.py`，在生成逻辑中增加自定义域名列表。例如，在 `generate_content` 函数中：

```python
custom_domains = [
    "my-internal.com",
    "office.local"
]
# 然后在 main 函数中将这些域名以 DOMAIN-SUFFIX 形式插入
```

### 2. 调整插入顺序
默认使用 `unshift` 从数组头部插入，以保证原有规则（如用户自定义规则）优先级更高。如需改为追加到末尾，将 `unshift` 改为 `push`：

```javascript
// 原代码（从头部插入）
config.rules.unshift(`IP-CIDR,${directIPs[i]},DIRECT`);

// 改为从尾部追加
config.rules.push(`IP-CIDR,${directIPs[i]},DIRECT`);
```

### 3. 合并相邻 CIDR 减少规则数量
若希望优化性能，可修改 Python 脚本，使用 `netaddr` 等库合并连续的 CIDR 段，大幅减少规则条目数。

### 4. 结合 GEOIP 规则使用
如果你已经使用了 `GEOIP,CN,DIRECT`，可以配合本项目进一步增强精确性：

```yaml
rules:
  - GEOIP,CN,DIRECT       # 基础直连
  - IP-CIDR,10.0.0.0/8,DIRECT  # 内网直连
  - MATCH,PROXY           # 其余走代理
```

但 `GEOIP` 依赖 Clash 内置 IP 数据库（可能更新滞后），使用本项目的 `IP-CIDR` 规则可**更精细、更及时**地控制路由。

## ❓ 常见问题

**Q1: 生成的规则文件太大，Clash 加载失败怎么办？**  
A: `chnroute.txt` 目前包含约 9000+ 条 IP 段，Clash 完全能够处理。如果遇到性能问题，可以考虑在生成时合并相邻的 CIDR（需要修改 Python 脚本）。

**Q2: 能否同时支持 IPv6？**  
A: 目前只从 `chnroute.txt` 获取 IPv4 段。如需 IPv6，可以改用 [china-ip-list 的 ipv6 分支](https://github.com/mayaxcn/china-ip-list/tree/ipv6) 并调整脚本中的 URL。

**Q3: 更新后 Clash 会自动加载新规则吗？**  
A: 若使用 `script` 方式（`eval` 加载），每次 Clash 重启或重新加载配置时会重新拉取。若使用 `rule-providers`，需配合 `interval` 参数（如 `interval: 3600`）实现自动刷新。

**Q4: 如何确认规则已生效？**  
A: 在 Clash 日志中查看规则匹配情况，或使用 `curl` 访问国内站点，观察是否直连。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来完善本项目，例如：
- 优化 CIDR 合并算法，减少规则数量
- 增加 IPv6 支持
- 添加更多镜像站地址
- 改进文档或提供更丰富的配置示例

## 📄 许可

本仓库仅用于自动化生成规则，数据来源于 [mayaxcn/china-ip-list](https://github.com/mayaxcn/china-ip-list)，请遵守其许可证。

## 🙏 致谢

- 数据源：[mayaxcn/china-ip-list](https://github.com/mayaxcn/china-ip-list)
- 加速镜像：[jsDelivr](https://www.jsdelivr.com/) 及其国内镜像站
- Clash 社区提供的脚本和覆写机制
```
