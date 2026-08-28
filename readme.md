# China IP Rules for Clash

本项目通过 GitHub Actions 每小时自动拉取 [chnroute.txt](https://raw.githubusercontent.com/mayaxcn/china-ip-list/master/chnroute.txt) 中的中国 IP 段，生成一个可直接用于 Clash 覆写的 JavaScript 规则文件 `ip-rules.js`。

## 文件说明

- `.github/workflows/update-ip-rules.yml` – GitHub Actions 工作流定义
- `scripts/generate-ip-rules.py` – Python 脚本，负责下载并生成规则文件
- `ip-rules.js` – 最终生成的规则文件（自动提交到仓库）

## 如何使用生成的规则文件

你可以通过以下 URL 直接在线引用该文件（需替换 `<owner>` 和 `<repo>` 为你的 GitHub 仓库信息）：

```

[https://raw.githubusercontent.com/](https://raw.githubusercontent.com/)<owner>/<repo>/main/ip-rules.js

```

在 Clash 的配置中，通过 `override` 或 `script` 功能引入该文件，例如：

```yaml
script:
  code: |
    // 引入远程规则
    const response = await fetch("https://raw.githubusercontent.com/<owner>/<repo>/main/ip-rules.js");
    const script = await response.text();
    eval(script);
    // 然后调用 main(config) 将直连规则注入
```

或直接将其内容复制到你的本地覆写文件中。

## 规则内容

生成的文件包含两个部分：

1. `directIPs` 数组 – 所有中国 IP 段的 CIDR 列表
2. `main(config)` 函数 – 将 `directIPs` 中的每个 IP 段以 `IP-CIDR,<cidr>,DIRECT` 的形式插入到 `config.rules` 中（从后往前插入，以保证原有顺序优先）

## 自动更新机制

- **触发频率**：每小时执行一次（UTC 时间的每个整点）
- **智能判断**：仅当远程 `chnroute.txt` 内容发生变化时，才会更新 `ip-rules.js` 并提交；无变化则跳过，避免无用提交。
- **手动触发**：你也可以在 GitHub 仓库的 Actions 页面手动运行该工作流。

## 自定义修改

如需调整规则插入位置、添加额外的直连域名等，可以直接编辑 `scripts/generate-ip-rules.py` 中的逻辑，或修改 `ip-rules.js` 的生成模板。

## 许可

本仓库仅用于自动化生成规则，数据来源于 [mayaxcn/china-ip-list](https://github.com/mayaxcn/china-ip-list)，请遵守其许可证。
