const signals = [
  {
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
  },
  {
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
  },
  {
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
  },
  {
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
  },
  {
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
  },
  {
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
  },
];

const assets = [
  ["美股", "中性偏谨慎", "高估值板块对利率和盈利指引敏感，适合等待财报和收益率确认。", "watch"],
  ["A股 / 港股", "观察政策验证", "需要看盈利修复、外资流入、地产风险缓和和政策落地强度。", "watch"],
  ["债券基金", "等待确认", "如果经济数据降温且通胀回落，久期资产胜率会上升。", "watch"],
  ["黄金", "中期偏强", "实际利率、央行购金和避险需求仍是核心支撑。", "positive"],
  ["原油", "事件驱动", "库存、OPEC 和地缘冲突决定短线波动，注意对通胀的二次影响。", "watch"],
  ["美元", "短期偏强", "降息预期后移时美元通常获得支撑，新兴市场承压。", "positive"],
  ["商品基金", "结构分化", "铜、油、农产品要分别看供需、库存和中国需求。", "watch"],
  ["新兴市场", "谨慎选择", "美元和全球风险偏好是关键变量，资金流更重要。", "negative"],
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
            <h3 class="feed-title"><a href="agent.html">${item.title}</a></h3>
            <p class="summary">${item.summary}</p>
            <div class="tags">${item.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
            <p class="reason"><strong>推荐理由：</strong>${item.reason}</p>
          </div>
        </article>
      `;
    })
    .join("");
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

setActiveNav();
renderFeed("#featuredList");
renderFeed("#allSignalList");
renderAssets();
renderScenarios();
bindFilters();
