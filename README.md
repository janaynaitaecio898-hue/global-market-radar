# Global Market Radar

全球资产雷达：参考 AIHOT 的信息流、精选、日报和 Agent 接入思路，把全球股票、基金、黄金、债券、商品和汇率的关键影响因素整理成可决策的信息流。

## 当前包含

- 精选市场影响因素信息流
- 单条影响因素详情页
- 短期 / 中期 / 长期决策视角
- 信息源等级、重要性评分、影响资产标签
- Agent 决策摘要
- 资产影响矩阵
- AI 市场日报模板
- 信源分层与重要性评分模型
- Agent / RSS / API 接入设计
- GitHub Actions 定时数据生成
- `data/*.json` 正式数据层
- `sources.json` 官方信源配置
- `data/daily.json` 自动日报数据
- v1.2：BLS 官方 API、宏观高影响事件升权、低影响公告降权
- v1.3：扩展欧洲央行、日本央行、BIS、美国人口普查局等多层信源，并为每条信息生成 AI 速读、信源简介和观察点
- v1.4：新增市场因子验证，用 ETF、期货和现货代理指标确认新闻是否被价格响应
- v1.5：新增 WSJ、CNBC、MarketWatch、Yahoo Finance、Bloomberg、FT、BBC、Guardian 等媒体解释源，扩展到 40 条混合信息流

## 文件

- `index.html`：精选信息流首页
- `signals.html`：全部市场动态
- `detail.html`：单条影响因素详情页
- `assets.html`：资产看板
- `agent.html`：Agent 分析中心
- `brief.html`：AI 市场日报模板
- `access.html`：Agent、RSS、API 接入设计
- `sources.html`：信源分层和评分逻辑
- `styles.css`：共享视觉样式和响应式布局
- `app.js`：示例数据、筛选和渲染逻辑
- `scripts/generate_data.py`：正式版 v1 数据生成脚本
- `.github/workflows/update-data.yml`：定时更新数据并提交到仓库
- `data/*.json`：前端读取的结构化数据
- `data/factors.json`：风险偏好、久期压力、信用风险、美元、黄金和商品通胀验证数据
- `sources.json`：Fed、BLS、EIA、SEC、Treasury、ECB、BOJ、BIS、Census、WSJ、CNBC、MarketWatch、Yahoo Finance、Bloomberg、FT、BBC、Guardian 等信源配置

## 后续可以接入的数据

- 官方宏观数据：CPI、PPI、PMI、GDP、就业
- 央行与监管：美联储、欧洲央行、日本央行、中国央行
- 市场行情：股指、债券收益率、黄金、原油、美元指数
- 新闻源：Reuters、Bloomberg、WSJ、FT、财新等
- 资金流：ETF 流入流出、基金仓位、北向资金、期货持仓
- Agent 分析：情景推演、风险归因、资产配置建议

> 这是研究辅助原型，不构成个性化投资建议。
