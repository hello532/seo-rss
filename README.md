# seo-rss

给「哥飞 / Web.Cafe 社群 + 中文出海 SEO」做的 RSS 源，补上 X、公众号、社群站没有原生 feed 的缺口。

## 订阅地址（可直接粘进任何 RSS 阅读器）

| Feed | URL | 内容 |
|---|---|---|
| Web.Cafe 最新教程 | https://hello532.github.io/seo-rss/feeds/webcafe-all.xml | 新.web.cafe `/all` 最新 10 篇 |
| Web.Cafe 社群帖子 | https://hello532.github.io/seo-rss/feeds/webcafe-topics.xml | 社群成员最新讨论（含作者名） |

OPML（一次导入全部）：
https://hello532.github.io/seo-rss/gefei-seo.opml

## 怎么更新

- `fetch.py`：抓 `new.web.cafe` 列表页（SSR HTML，无需浏览器），与 `state.json` 比对，新增条目累积，输出 RSS 2.0 到 `feeds/`。
- `publish.sh`：跑 fetch，有变化就 commit + push，GitHub Pages 立即生效。
- launchd `com.doi.seorss`：每小时执行一次（`~/Library/LaunchAgents/com.doi.seorss.plist`）。

手动跑：`bash publish.sh`

## 已知限制

- 公众号、X 没有可信的公共 RSS 通道：nitter 实例全部 403/451，公共 RSSHub 的 `/twitter/*` 全是 503（实例未配 X token），`wechat2rss` 公共实例 500/404。
- 因此 web.cafe 的社群流实际覆盖了「哥飞 + 社群成员」的日常更新；公众号与 X 需要单独补通道（见下）。
- 抓到的只有标题、作者、链接与时间，不含 VIP 正文。
