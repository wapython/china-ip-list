# China IP Rules for Clash

本项目通过 GitHub Actions 每小时自动拉取 [chnroute.txt](https://raw.githubusercontent.com/mayaxcn/china-ip-list/master/chnroute.txt) 中的中国 IP 段，生成一个可直接用于 Clash 覆写（Override）或脚本（Script）模式的 JavaScript 规则文件 `ip-rules.js`。

## 文件说明

| 文件 | 说明 |
| :--- | :--- |
| `.github/workflows/update-ip-rules.yml` | GitHub Actions 工作流定义，每小时触发一次 |
| `scripts/generate-ip-rules.py` | Python 脚本，负责下载并生成规则文件 |
| `ip-rules.js` | 最终生成的规则文件（自动提交到仓库） |

## 如何使用生成的规则文件

### 方式一：直接引用（在线加载）

你可以通过以下 URL 直接在线引用该文件（需替换 `<owner>` 和 `<repo>` 为你的 GitHub 仓库信息）：

```
https://raw.githubusercontent.com/<owner>/<repo>/main/ip-rules.js
```

### 方式二：通过 CDN 加速引用（推荐）

为提升国内访问速度，推荐使用以下加速方式：

| 加速方式 | URL 格式 |
| :--- | :--- |
| **jsDelivr 官方 CDN** | `https://cdn.jsdelivr.net/gh/<owner>/<repo>/ip-rules.js` |
| **国内镜像站（推荐）** | `https://jsd.cdn.zzko.cn/gh/<owner>/<repo>/ip-rules.js` |
| **国内镜像站（备选）** | `https://jsdelivr.topthink.com/gh/<owner>/<repo>/ip-rules.js` |
| **国内镜像站（备选）** | `https://jsd.onmicrosoft.cn/gh/<owner>/<repo>/ip-rules.js` |

### Clash 配置示例

在 Clash 的配置文件中，通过 `script` 功能引入该规则：

```yaml
script:
  code: |
    // 方式一：直接从 GitHub Raw 获取（国内可能较慢）
    // const response = await fetch("https://raw.githubusercontent.com/<owner>/<repo>/main/ip-rules.js");

    // 方式二：通过国内镜像站加速（推荐）
    const response = await fetch("https://jsd.cdn.zzko.cn/gh/<owner>/<repo>/ip-rules.js");
    const script = await response.text();
    eval(script);
    // 调用 main(config) 将中国 IP 段以 IP-CIDR 规则注入
    main(config);
```

如果你使用的是 Clash Meta（mihomo）内核，也可以直接在 `rule-providers` 中引用：

```yaml
rule-providers:
  china-ip:
    type: http
    behavior: classical
    url: "https://jsd.cdn.zzko.cn/gh/<owner>/<repo>/ip-rules.js"
    path: ./ruleset/china-ip.yaml
    interval: 3600
```

## 规则内容

生成的文件包含两个核心部分：

1. **`directIPs` 数组** – 包含所有中国 IP 段的 CIDR 列表
2. **`main(config)` 函数** – 将 `directIPs` 中的每个 IP 段以 `IP-CIDR,<cidr>,DIRECT` 的形式插入到 `config.rules` 数组中（采用**从后往前插入**的方式，以确保原有规则顺序优先）

### 生成的 JS 文件结构示例

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

## 自动更新机制

- **⏰ 触发频率**：每小时执行一次（UTC 时间的每个整点，即北京时间每早 8 点至次日早 7 点的整点）
- **🧠 智能判断**：仅当远程 `chnroute.txt` 内容发生变化时，才会更新 `ip-rules.js` 并自动提交；无变化则跳过，避免冗余提交记录
- **👆 手动触发**：你也可以在 GitHub 仓库的 Actions 页面点击 "Run workflow" 手动触发更新

## 高级用法

### 1. 添加自定义直连域名

如果你需要额外添加一些直连域名，可以修改 `scripts/generate-ip-rules.py`，在生成逻辑中加入自定义域名列表：

```python
# 在 generate_content 函数中增加自定义域名规则
custom_domains = [
    "example.com",
    "my-internal.net"
]
# 然后在 main 函数中额外插入 DOMAIN-SUFFIX 规则
```

### 2. 调整插入顺序

默认使用 `unshift` 从数组头部插入，以保证原有规则（如用户自定义规则）优先级更高。如需改为追加到末尾，可将 `unshift` 改为 `push`：

```javascript
// 原代码（从头部插入）
config.rules.unshift(`IP-CIDR,${directIPs[i]},DIRECT`);

// 改为从尾部追加
config.rules.push(`IP-CIDR,${directIPs[i]},DIRECT`);
```

### 3. 配合 GEOIP 规则使用

如果你希望中国 IP 走直连，而非中国 IP 走代理，可以结合 Clash 的 `GEOIP` 规则：

```yaml
rules:
  - GEOIP,CN,DIRECT
  - MATCH,PROXY
```

但 `GEOIP` 依赖 Clash 内置的 IP 数据库（可能更新不及时），使用本项目的 `IP-CIDR` 规则可以**更精确、更细粒度**地控制路由。

## 常见问题

### Q1: 生成的规则文件太大，Clash 加载失败怎么办？
A: `chnroute.txt` 目前包含约 9000+ 条 IP 段，Clash 完全能够处理。如果遇到性能问题，可以考虑在生成时合并相邻的 CIDR（需要修改 Python 脚本）。

### Q2: 能否同时支持 IPv6？
A: 目前只从 `chnroute.txt` 获取 IPv4 段。如需 IPv6，可以改用 [china-ip-list 的 ipv6 分支](https://github.com/mayaxcn/china-ip-list/tree/ipv6) 并调整脚本中的 URL。

### Q3: 更新后 Clash 会自动加载新规则吗？
A: 如果你使用的是 `script` 方式（`eval` 加载），每次 Clash 重启或重新加载配置时会重新拉取。如果使用 `rule-providers`，需要配合 `interval` 参数自动刷新。

## 许可

本仓库仅用于自动化生成规则，数据来源于 [mayaxcn/china-ip-list](https://github.com/mayaxcn/china-ip-list)，请遵守其许可证。

---

## 贡献

欢迎提交 Issue 或 Pull Request 来完善本项目，例如：
- 优化 CIDR 合并算法，减少规则数量
- 增加 IPv6 支持
- 添加更多镜像站地址

---
