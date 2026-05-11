let signals = [
  {
    id: "us-jobs-rate-path",
    date: "5月11日",
    time: "10:40",
    source: "Federal Reserve / BLS",
    avatar: "F",
    score: 92,
    category: "macro",
    horizon: "short",
    asset: "equity bond gold fx",
    title: "美国就业数据强于预期，降息预期继续后移",
    summary:
      "就业韧性会直接影响美联储路径。若工资和岗位增长继续强于预期，市场对降息的定价会被压缩，成长股、长久期债券和黄金都更容易受到实际利率上行的扰动。",
    tags: ["货币政策", "就业", "美债收益率", "美元"],
    reason:
      "这条信息影响的是全球资产估值锚。它不是单一数据点，而是在重定价降息路径，股票、债券、黄金和汇率都会被牵动。",
    sourceRank: "S级",
    absorbed: "部分消化",
    shortTerm: "短期压制成长股、黄金和长久期债券，美元偏强。",
    midTerm: "中期取决于后续 CPI 与就业是否连续强于预期。",
    longTerm: "长期影响在于利率中枢是否维持高位。",
    decision:
      "避免在强数据后追高高估值资产；等待通胀和就业连续确认后再提高进攻仓位。",
  },
  {
    id: "gold-etf-central-bank",
    date: "5月11日",
    time: "09:25",
    source: "ETF Flow Monitor",
    avatar: "E",
    score: 84,
    category: "gold",
    horizon: "mid",
    asset: "gold commodity",
    title: "黄金 ETF 连续净流入，央行购金逻辑仍在发酵",
    summary:
      "黄金的中期逻辑不仅来自避险，还包括实际利率、央行储备多元化和 ETF 资金回流。短线仍需警惕美元反弹，但中期配置需求没有明显消失。",
    tags: ["黄金", "资金流", "央行购金", "避险"],
    reason:
      "黄金同时有避险、货币体系和资金流三条线索支撑。短线看美元，中期看实际利率，长期看央行储备结构变化。",
    sourceRank: "A级",
    absorbed: "尚未完全消化",
    shortTerm: "短线受美元和实际利率扰动，容易震荡。",
    midTerm: "中期若 ETF 和央行买盘延续，黄金仍有支撑。",
    longTerm: "长期取决于全球储备多元化和财政赤字压力。",
    decision:
      "更适合分批配置或作为组合对冲，不适合只因单日上涨追入。",
  },
  {
    id: "ai-earnings-capex",
    date: "5月11日",
    time: "08:50",
    source: "Earnings Watch",
    avatar: "Q",
    score: 79,
    category: "equity",
    horizon: "mid",
    asset: "equity",
    title: "大型科技公司财报指引分化，AI 资本开支进入验证期",
    summary:
      "市场不再只奖励 AI 叙事，而是开始看收入兑现、毛利率和资本开支回报。指数层面需要警惕少数龙头拥挤交易，主动基金可能向盈利确定性更强的公司切换。",
    tags: ["美股", "AI", "盈利", "基金调仓"],
    reason:
      "科技股估值已经包含很高预期，财报指引一旦分化，会影响纳指、半导体 ETF 和全球成长风格基金。",
    sourceRank: "S级",
    absorbed: "等待财报验证",
    shortTerm: "短期波动会集中在财报窗口和指引措辞。",
    midTerm: "中期看 AI 投入能否兑现收入和毛利率。",
    longTerm: "长期仍是生产率和资本开支周期主线。",
    decision:
      "降低单一龙头拥挤交易，关注盈利兑现和现金流质量。",
  },
  {
    id: "fiscal-deficit-term-premium",
    date: "5月10日",
    time: "22:15",
    source: "Treasury / Macro Desk",
    avatar: "T",
    score: 76,
    category: "bond",
    horizon: "long",
    asset: "bond equity gold fx",
    title: "财政赤字和长期发债压力抬升期限溢价",
    summary:
      "如果财政赤字长期维持高位，长端利率中枢可能难以回到过去低位。长期配置需要重新评估股债相关性，以及黄金在组合中的风险对冲价值。",
    tags: ["债务周期", "长期利率", "资产配置", "期限溢价"],
    reason:
      "这不是短线新闻，而是影响未来数年资产配置框架的慢变量。它会改变股票估值、债券久期和黄金长期逻辑。",
    sourceRank: "A级",
    absorbed: "长期定价中",
    shortTerm: "短期通过长端收益率波动影响风险资产。",
    midTerm: "中期会影响债券久期选择和股债相关性。",
    longTerm: "长期可能抬高实际利率中枢，改变组合配置框架。",
    decision:
      "长期配置里降低对低利率回归的单一路径依赖，增加情景约束。",
  },
  {
    id: "oil-inventory-geopolitics",
    date: "5月10日",
    time: "20:30",
    source: "Commodity Desk",
    avatar: "O",
    score: 71,
    category: "commodity",
    horizon: "short",
    asset: "commodity equity",
    title: "原油库存下降叠加地缘风险，能源价格风险溢价上升",
    summary:
      "油价短期冲击会通过通胀预期影响利率，也会改变能源股、航空、消费和商品基金的相对表现。重点观察库存、OPEC 表态和冲突升级概率。",
    tags: ["原油", "地缘", "通胀", "商品基金"],
    reason:
      "原油是通胀预期和风险偏好的连接点。它涨得太快，会重新压制降息预期，并拖累高估值风险资产。",
    sourceRank: "A级",
    absorbed: "快速交易中",
    shortTerm: "短期推升能源和通胀预期，压制航空和消费。",
    midTerm: "中期看库存、OPEC 供给纪律和地缘风险是否延续。",
    longTerm: "长期取决于能源转型、供需投资周期和地缘格局。",
    decision:
      "把原油作为通胀风险监控指标，不把单一库存数据当趋势确认。",
  },
  {
    id: "volatility-risk-repricing",
    date: "5月10日",
    time: "17:40",
    source: "Risk Monitor",
    avatar: "R",
    score: 69,
    category: "risk",
    horizon: "short",
    asset: "equity bond gold fx",
    title: "波动率指数回升，市场对尾部风险重新定价",
    summary:
      "当 VIX 与美元同时上行，通常意味着市场从追逐收益转向管理风险。短线需要观察信用利差、日元波动和高收益债 ETF 是否同步承压。",
    tags: ["波动率", "风险偏好", "信用利差", "美元"],
    reason:
      "这类信号不一定指向趋势反转，但能提醒仓位管理。尤其当多个风险指标同步恶化时，优先考虑防守。",
    sourceRank: "B级",
    absorbed: "低度消化",
    shortTerm: "短期提示市场风险偏好转弱，仓位和杠杆要更保守。",
    midTerm: "中期需要观察信用利差、美元和日元是否同步恶化。",
    longTerm: "长期意义有限，除非演化为流动性或信用事件。",
    decision:
      "当 VIX、美元、信用利差同时上行时，优先控制回撤。",
  },
];

let assets = [
  ["美股", "中性偏谨慎", "高估值板块对利率和盈利指引敏感，适合等待财报和收益率确认。", "watch"],
  ["A股 / 港股", "观察政策验证", "需要看盈利修复、外资流入、地产风险缓和和政策落地强度。", "watch"],
  ["债券基金", "等待确认", "如果经济数据降温且通胀回落，久期资产胜率会上升。", "watch"],
  ["黄金", "中期偏强", "实际利率、央行购金和避险需求仍是核心支撑。", "positive"],
  ["原油", "事件驱动", "库存、OPEC 和地缘冲突决定短线波动，注意对通胀的二次影响。", "watch"],
  ["美元", "短期偏强", "降息预期后移时美元通常获得支撑，新兴市场承压。", "positive"],
  ["商品基金", "结构分化", "铜、油、农产品要分别看供需、库存和中国需求。", "watch"],
  ["新兴市场", "谨慎选择", "美元和全球风险偏好是关键变量，资金流更重要。", "negative"],
];

let scenarios = [
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
    result: "资产分化，降低追高，关注黄金、短债和现金流稳定资产。",
  },
  {
    name: "悲观情景",
    probability: "25%",
    summary: "通胀再起或信用风险暴露，收益率和波动率同时上行。",
    result: "风险资产承压，美元和避险资产受益，仓位控制优先。",
  },
];

const state = {
  category: "all",
  horizon: "all",
};

let dataMeta = {
  status: "fallback",
  generated_at: null,
  notes: ["Using bundled fallback data."],
};

let marketSnapshot = null;

function setActiveNav() {
  const page = document.body.dataset.page;
  document.querySelectorAll("[data-nav]").forEach((link) => {
    link.classList.toggle("active", link.dataset.nav === page);
  });
}

function matchesSearch(item) {
  const input = document.querySelector("#searchInput");
  const keyword = (input?.value || "").trim().toLowerCase();
  if (!keyword) return true;
  const text = `${item.title} ${item.source} ${item.summary} ${item.tags.join(" ")} ${item.reason}`.toLowerCase();
  return text.includes(keyword);
}

function filteredSignals() {
  const asset = document.querySelector("#assetSelect")?.value || "all";
  return signals.filter((item) => {
    const categoryMatch = state.category === "all" || item.category === state.category;
    const horizonMatch = state.horizon === "all" || item.horizon === state.horizon;
    const assetMatch = asset === "all" || item.asset.includes(asset);
    return categoryMatch && horizonMatch && assetMatch && matchesSearch(item);
  });
}

function renderFeed(targetId) {
  const list = document.querySelector(targetId);
  if (!list) return;
  const items = filteredSignals();
  if (!items.length) {
    list.innerHTML = `<p class="empty-state">没有匹配的市场动态。</p>`;
    return;
  }

  let currentDate = "";
  list.innerHTML = items
    .map((item) => {
      const heading = item.date !== currentDate ? `<h2 class="date-heading">${item.date}</h2>` : "";
      currentDate = item.date;
      return `
        ${heading}
        <article class="feed-item">
          <div class="feed-time">${item.time}<small>${horizonName(item.horizon)}</small></div>
          <div class="feed-main">
            <div class="item-topline">
              <span class="avatar">${item.avatar}</span>
              <span>${item.source}</span>
              <span class="score">精选 ${item.score}</span>
            </div>
            <h3 class="feed-title"><a href="detail.html?id=${item.id}">${item.title}</a></h3>
            <p class="summary">${item.summary}</p>
            <div class="tags">${item.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
            <p class="reason"><strong>推荐理由：</strong>${item.reason}</p>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderDetail() {
  const root = document.querySelector("#detailRoot");
  if (!root) return;
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const item = signals.find((signal) => signal.id === id) || signals[0];

  root.innerHTML = `
    <div class="detail-meta">
      <span>${item.date} ${item.time}</span>
      <span>${item.source}</span>
      <span>${item.sourceRank}</span>
      <span>精选 ${item.score}</span>
    </div>
    <h1>${item.title}</h1>
    <p class="detail-summary">${item.summary}</p>
    <div class="tags">${item.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>

    <section class="detail-section">
      <h2>推荐理由</h2>
      <p>${item.reason}</p>
    </section>

    <section class="detail-grid">
      <article><strong>短期</strong><p>${item.shortTerm}</p></article>
      <article><strong>中期</strong><p>${item.midTerm}</p></article>
      <article><strong>长期</strong><p>${item.longTerm}</p></article>
    </section>

    <section class="detail-section">
      <h2>资产影响</h2>
      <div class="impact-list">
        ${impactLabels(item.asset).map((label) => `<span>${label}</span>`).join("")}
      </div>
    </section>

    <section class="detail-section">
      <h2>市场消化状态</h2>
      <p>${item.absorbed}</p>
    </section>

    <section class="detail-section">
      <h2>决策提示</h2>
      <p>${item.decision}</p>
    </section>
  `;
}

function impactLabels(assetText) {
  const map = {
    equity: "股票",
    bond: "债券",
    gold: "黄金",
    fx: "汇率",
    commodity: "商品",
  };
  return Object.entries(map)
    .filter(([key]) => assetText.includes(key))
    .map(([, label]) => label);
}

function horizonName(value) {
  return { short: "短期", mid: "中期", long: "长期" }[value] || "全部";
}

function renderAssets() {
  const grid = document.querySelector("#assetGrid");
  if (!grid) return;
  grid.innerHTML = assets
    .map(
      ([name, stance, detail, tone]) => `
        <article class="asset-card">
          <strong class="${tone}">${name}</strong>
          <div>
            <h2 class="${tone}">${stance}</h2>
            <p>${detail}</p>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderMarketSnapshot() {
  const root = document.querySelector("#marketSnapshot");
  if (!root) return;

  if (!marketSnapshot || !Array.isArray(marketSnapshot.quotes)) {
    root.innerHTML = `<p class="empty-state">行情快照暂不可用。</p>`;
    return;
  }

  root.innerHTML = `
    <div class="snapshot-head">
      <h2>核心资产快照</h2>
      <span>${marketSnapshot.status === "live" ? "Live" : "Degraded"} · ${marketSnapshot.generated_at || ""}</span>
    </div>
    <div class="snapshot-grid">
      ${marketSnapshot.quotes
        .map(
          (quote) => `
            <article>
              <span>${quote.name}</span>
              <strong>${quote.close}</strong>
              <small>${quote.symbol} · ${quote.status}</small>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderScenarios() {
  const grid = document.querySelector("#scenarioGrid");
  if (!grid) return;
  grid.innerHTML = scenarios
    .map(
      (item) => `
        <article class="scenario-card">
          <div class="meta-line">概率 ${item.probability}</div>
          <h2>${item.name}</h2>
          <p>${item.summary}</p>
          <p><strong>资产结果：</strong>${item.result}</p>
        </article>
      `,
    )
    .join("");
}

function bindFilters() {
  document.querySelectorAll("[data-category]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-category]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.category = button.dataset.category;
      renderFeed("#featuredList");
    });
  });

  document.querySelectorAll("[data-horizon]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-horizon]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.horizon = button.dataset.horizon;
      renderFeed("#allSignalList");
    });
  });

  document.querySelector("#searchInput")?.addEventListener("input", () => {
    renderFeed("#featuredList");
    renderFeed("#allSignalList");
  });
  document.querySelector("#assetSelect")?.addEventListener("change", () => renderFeed("#allSignalList"));
}

async function fetchJson(path) {
  const response = await fetch(`${path}?v=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

async function loadProductionData() {
  if (window.location.protocol === "file:") {
    dataMeta = {
      status: "fallback",
      generated_at: null,
      notes: ["Local file preview uses bundled fallback data. GitHub Pages reads data/*.json."],
    };
    return;
  }

  try {
    const [signalsData, assetsData, scenariosData, metaData, marketData] = await Promise.all([
      fetchJson("data/signals.json"),
      fetchJson("data/assets.json"),
      fetchJson("data/scenarios.json"),
      fetchJson("data/meta.json"),
      fetchJson("data/market_snapshot.json"),
    ]);

    if (Array.isArray(signalsData.items)) signals = signalsData.items;
    if (Array.isArray(assetsData.items)) assets = assetsData.items;
    if (Array.isArray(scenariosData.items)) scenarios = scenariosData.items;
    dataMeta = {
      status: metaData.status || "live",
      generated_at: metaData.generated_at || signalsData.generated_at || null,
      notes: metaData.notes || [],
    };
    marketSnapshot = marketData;
  } catch (error) {
    dataMeta = {
      status: "fallback",
      generated_at: null,
      notes: [`Failed to load data/*.json: ${error.message}`],
    };
  }
}

function renderDataStatus() {
  const title = document.querySelector(".page-title");
  if (!title || document.querySelector(".data-status")) return;

  const label =
    dataMeta.status === "live"
      ? "正式数据"
      : dataMeta.status === "degraded"
        ? "正式数据（部分降级）"
        : "内置兜底数据";
  const status = document.createElement("section");
  status.className = `data-status ${dataMeta.status === "live" ? "live" : ""}`;
  const generated = dataMeta.generated_at ? new Date(dataMeta.generated_at).toLocaleString() : "fallback";
  status.innerHTML = `
    <strong>${label}</strong>
    <span>更新时间：${generated}</span>
    <small>${(dataMeta.notes || []).join(" ")}</small>
  `;
  title.insertAdjacentElement("afterend", status);
}

async function init() {
  setActiveNav();
  await loadProductionData();
  renderDataStatus();
  renderFeed("#featuredList");
  renderFeed("#allSignalList");
  renderAssets();
  renderMarketSnapshot();
  renderScenarios();
  renderDetail();
  bindFilters();
}

init();
