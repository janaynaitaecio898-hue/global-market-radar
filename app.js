const signals = [
  {
    title: "美国就业数据强于预期，降息预期继续后移",
    level: "S级 · 官方数据",
    score: 92,
    horizon: "short",
    asset: "equity bond gold fx",
    tags: ["货币政策", "就业", "美债收益率"],
    impact: ["美股偏负面", "美债承压", "黄金短线承压", "美元偏强"],
    digest:
      "这类数据会直接影响美联储路径。若就业韧性持续，市场对降息的定价会被压缩，成长股和长久期资产更敏感。",
  },
  {
    title: "黄金 ETF 连续净流入，央行购金逻辑仍在发酵",
    level: "A级 · 资金流",
    score: 84,
    horizon: "mid",
    asset: "gold commodity",
    tags: ["黄金", "资金流", "避险"],
    impact: ["黄金偏正面", "美元对冲", "资源股关注"],
    digest:
      "黄金的中期逻辑不仅来自避险，还包括实际利率、央行储备多元化和 ETF 资金回流。短线仍需警惕美元反弹。",
  },
  {
    title: "大型科技公司财报指引分化，AI 资本开支仍是主线",
    level: "S级 · 公司财报",
    score: 79,
    horizon: "mid",
    asset: "equity",
    tags: ["美股", "AI", "盈利"],
    impact: ["纳指分化", "半导体波动", "主动基金调仓"],
    digest:
      "市场不再只奖励 AI 故事，而是开始看收入兑现、毛利率和资本开支回报。指数层面需要警惕少数龙头拥挤交易。",
  },
  {
    title: "财政赤字和长期发债压力抬升期限溢价",
    level: "A级 · 宏观趋势",
    score: 76,
    horizon: "long",
    asset: "bond equity gold fx",
    tags: ["债务周期", "长期利率", "资产配置"],
    impact: ["长债波动", "股市估值压力", "黄金长期受益"],
    digest:
      "如果财政赤字长期维持高位，长端利率中枢可能难以回到过去低位。长期配置需要重新评估股债相关性。",
  },
  {
    title: "原油库存下降叠加地缘风险，能源价格风险溢价上升",
    level: "A级 · 商品供需",
    score: 71,
    horizon: "short",
    asset: "commodity equity",
    tags: ["原油", "地缘", "通胀"],
    impact: ["原油偏强", "航空消费承压", "通胀预期抬升"],
    digest:
      "油价的短期冲击会通过通胀预期影响利率，也会改变能源股和消费股的相对表现。重点看库存与冲突升级概率。",
  },
];

const assets = [
  ["美股", "中性偏谨慎", "高估值板块对利率和盈利指引敏感。", "tone-flat"],
  ["A股 / 港股", "观察政策验证", "需要看盈利修复、外资流入和地产风险缓和。", "tone-flat"],
  ["债券基金", "等待确认", "若经济数据降温，久期资产胜率上升。", "tone-flat"],
  ["黄金", "中期偏强", "实际利率、央行购金和避险需求共同支撑。", "tone-up"],
  ["原油", "事件驱动", "库存、OPEC 和地缘冲突决定短线波动。", "tone-flat"],
  ["美元", "短期偏强", "降息预期后移时美元通常获得支撑。", "tone-up"],
  ["商品基金", "结构分化", "铜、油、农产品需分别看供需和库存。", "tone-flat"],
  ["新兴市场", "谨慎选择", "美元和全球风险偏好是关键变量。", "tone-down"],
];

const scenarios = [
  {
    name: "乐观情景",
    probability: "25%",
    summary: "通胀温和回落，盈利继续修复，降息预期重新升温。",
    result: "股票和债券同时受益，黄金保持配置价值。",
  },
  {
    name: "基准情景",
    probability: "50%",
    summary: "经济保持韧性但通胀回落缓慢，市场在利率和盈利之间摇摆。",
    result: "资产分化，适合降低追高，关注黄金、短债和现金流稳定资产。",
  },
  {
    name: "悲观情景",
    probability: "25%",
    summary: "通胀再起或信用风险暴露，收益率和波动率同时上行。",
    result: "风险资产承压，美元和避险资产受益，仓位控制优先。",
  },
];

let currentFilter = "all";

function setActiveNav() {
  const page = document.body.dataset.page;
  document.querySelectorAll("[data-nav]").forEach((link) => {
    link.classList.toggle("active", link.dataset.nav === page);
  });
}

function horizonName(value) {
  return { short: "短期影响", mid: "中期影响", long: "长期影响" }[value];
}

function renderSignals() {
  const list = document.querySelector("#signalList");
  if (!list) return;

  const keyword = (document.querySelector("#searchInput")?.value || "").trim().toLowerCase();
  const asset = document.querySelector("#assetSelect")?.value || "all";
  const filtered = signals.filter((item) => {
    const horizonMatch = currentFilter === "all" || item.horizon === currentFilter;
    const assetMatch = asset === "all" || item.asset.includes(asset);
    const haystack = `${item.title} ${item.level} ${item.tags.join(" ")} ${item.impact.join(" ")} ${item.digest}`.toLowerCase();
    return horizonMatch && assetMatch && (!keyword || haystack.includes(keyword));
  });

  list.innerHTML = filtered
    .map(
      (item) => `
        <article class="signal-card">
          <div class="signal-head">
            <h3>${item.title}</h3>
            <span class="score-pill">${item.score}</span>
          </div>
          <div class="signal-meta">
            <span class="source-pill">${item.level}</span>
            <span class="impact-pill">${horizonName(item.horizon)}</span>
            ${item.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}
          </div>
          <div class="signal-impact">
            ${item.impact.map((impact) => `<span class="tag">${impact}</span>`).join("")}
          </div>
          <p>${item.digest}</p>
        </article>
      `,
    )
    .join("");
}

function renderAssets() {
  const grid = document.querySelector("#assetGrid");
  if (!grid) return;
  grid.innerHTML = assets
    .map(
      ([name, stance, detail, tone]) => `
        <article class="asset-card">
          <span class="tag">${name}</span>
          <strong class="${tone}">${stance}</strong>
          <p>${detail}</p>
        </article>
      `,
    )
    .join("");
}

function renderScenarios() {
  const grid = document.querySelector("#scenarioGrid");
  if (!grid) return;
  grid.innerHTML = scenarios
    .map(
      (item) => `
        <article class="scenario-card">
          <span class="score-pill">${item.probability}</span>
          <strong>${item.name}</strong>
          <p>${item.summary}</p>
          <p><b>资产结果：</b>${item.result}</p>
        </article>
      `,
    )
    .join("");
}

function bindFilters() {
  document.querySelectorAll(".segmented button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".segmented button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      currentFilter = button.dataset.filter;
      renderSignals();
    });
  });

  document.querySelector("#searchInput")?.addEventListener("input", renderSignals);
  document.querySelector("#assetSelect")?.addEventListener("change", renderSignals);
}

setActiveNav();
renderSignals();
renderAssets();
renderScenarios();
bindFilters();

if (window.lucide) {
  window.lucide.createIcons();
}
