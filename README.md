# seo-rss

给「哥飞 / Web.Cafe 社群 + 中文出海 SEO」补 RSS：这些站点没有原生 feed，这里按小时生成。

## 订阅地址（可直接粘进任何 RSS 阅读器）

| Feed | URL | 内容 |
|---|---|---|
| Web.Cafe 最新教程 | https://hello532.github.io/seo-rss/feeds/webcafe-all.xml | `new.web.cafe/all`：哥飞与社群最新教程流 |
| Web.Cafe 社群帖子 | https://hello532.github.io/seo-rss/feeds/webcafe-topics.xml | 社群成员最新讨论，带作者名 |
| Web.Cafe 教程专栏 | https://hello532.github.io/seo-rss/feeds/webcafe-columns.xml | 专栏索引（新专栏/系列出现时提示） |

一次导入全部（OPML）：
https://hello532.github.io/seo-rss/gefei-seo.opml

OPML 里另含原生 feed：Google Search Central、Ahrefs、Search Engine Journal、Search Engine Roundtable、Moz、Backlinko、Yoast、Justin Yan（出海独立开发）、人人都是产品经理、阮一峰、少数派。

## 在 iPhone 上导入 SmartRSS

1. App Store 安装 SmartRSS（https://apps.apple.com/app/id6749771900）。Mac App Store 搜不到/装不了，只能在 iPhone 或 iPad 上装。
2. Safari 打开上面的 OPML 链接 → 下载。
3. SmartRSS → 设置 → 导入 OPML → 选择刚下载的文件。

## 更新机制

- `fetch.py`：抓 `new.web.cafe` 列表页（服务端渲染 HTML，不需要浏览器），与 `state.json` 比对后累积新条目，输出 RSS 2.0 到 `feeds/`。
- `publish.sh`：跑 fetch，有变化就 commit + push，GitHub Pages 生效（约 30–60 秒）。
- launchd `com.doi.seorss`：每小时执行一次（`~/Library/LaunchAgents/com.doi.seorss.plist`，日志在 `logs/`）。

手动跑：`bash publish.sh`

## 已知限制

- **X（@gefei55）**：nitter 镜像全部 403/451，公共 RSSHub 的 `/twitter/*` 均 503（实例未配 X token），gallery-dl 用现有 cookie（2026-10-14）与 Chrome cookie 抓取均返回空。要接 X 需二选一：重新导出 x.com 的 cookie，或用付费桥（rss.app 等）。
- **微信公众号**：公共 wechat2rss 实例 500/404，需自建 wechat2rss 并配置公众号 biz。
- 抓到的只有标题、作者、链接、时间，不含 VIP 正文。
