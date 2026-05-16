#!/usr/bin/env python3
"""Generate static data files for 全球资产雷达.

The site is hosted on GitHub Pages, so the first production version uses a
static-data pipeline: this script fetches lightweight market quotes, combines
them with the editorial rule set below, and writes JSON consumed by app.js.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCES_PATH = ROOT / "sources.json"

MARKET_INSTRUMENTS = [
    {
        "symbol": "spy.us",
        "name": "标普500 ETF",
        "asset": "equity",
        "fallback_close": 520.0,
    },
    {
        "symbol": "qqq.us",
        "name": "纳斯达克100 ETF",
        "asset": "equity",
        "fallback_close": 445.0,
    },
    {
        "symbol": "tlt.us",
        "name": "20年以上美债 ETF",
        "asset": "bond",
        "fallback_close": 90.0,
    },
    {
        "symbol": "gld.us",
        "name": "黄金 ETF",
        "asset": "gold",
        "fallback_close": 215.0,
    },
    {
        "symbol": "uso.us",
        "name": "原油 ETF",
        "asset": "commodity",
        "fallback_close": 75.0,
    },
    {
        "symbol": "uup.us",
        "name": "美元指数 ETF",
        "asset": "fx",
        "fallback_close": 29.0,
    },
]

FACTOR_INSTRUMENTS = [
    {
        "symbol": "hyg.us",
        "name": "高收益债 ETF",
        "asset": "credit",
        "fallback_close": 79.0,
    },
    {
        "symbol": "lqd.us",
        "name": "投资级债 ETF",
        "asset": "credit",
        "fallback_close": 108.0,
    },
    {
        "symbol": "ief.us",
        "name": "7-10年美债 ETF",
        "asset": "bond",
        "fallback_close": 94.0,
    },
    {
        "symbol": "shy.us",
        "name": "1-3年美债 ETF",
        "asset": "bond",
        "fallback_close": 82.0,
    },
    {
        "symbol": "dx.f",
        "name": "美元指数期货",
        "asset": "fx",
        "fallback_close": 99.0,
    },
    {
        "symbol": "xauusd",
        "name": "现货黄金",
        "asset": "gold",
        "fallback_close": 4500.0,
    },
    {
        "symbol": "cl.f",
        "name": "WTI 原油期货",
        "asset": "commodity",
        "fallback_close": 100.0,
    },
    {
        "symbol": "hg.f",
        "name": "铜期货",
        "asset": "commodity",
        "fallback_close": 620.0,
    },
]

BASE_SIGNALS = [
    {
        "id": "us-jobs-rate-path",
        "date": "5月11日",
        "time": "10:40",
        "source": "美联储 / 美国劳工统计局",
        "avatar": "F",
        "score": 92,
        "category": "macro",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "title": "美国就业数据强于预期，降息预期继续后移",
        "summary": "就业韧性会直接影响美联储路径。若工资和岗位增长继续强于预期，市场对降息的定价会被压缩，成长股、长久期债券和黄金都更容易受到实际利率上行的扰动。",
        "tags": ["货币政策", "就业", "美债收益率", "美元"],
        "reason": "这条信息影响的是全球资产估值锚。它不是单一数据点，而是在重定价降息路径，股票、债券、黄金和汇率都会被牵动。",
        "sourceRank": "S级",
        "absorbed": "部分消化",
        "shortTerm": "短期压制成长股、黄金和长久期债券，美元偏强。",
        "midTerm": "中期取决于后续 CPI 与就业是否连续强于预期。",
        "longTerm": "长期影响在于利率中枢是否维持高位。",
        "decision": "避免在强数据后追高高估值资产；等待通胀和就业连续确认后再提高进攻仓位。",
    },
    {
        "id": "gold-etf-central-bank",
        "date": "5月11日",
        "time": "09:25",
        "source": "ETF 资金流监测",
        "avatar": "E",
        "score": 84,
        "category": "gold",
        "horizon": "mid",
        "asset": "gold commodity",
        "title": "黄金 ETF 连续净流入，央行购金逻辑仍在发酵",
        "summary": "黄金的中期逻辑不仅来自避险，还包括实际利率、央行储备多元化和 ETF 资金回流。短线仍需警惕美元反弹，但中期配置需求没有明显消失。",
        "tags": ["黄金", "资金流", "央行购金", "避险"],
        "reason": "黄金同时有避险、货币体系和资金流三条线索支撑。短线看美元，中期看实际利率，长期看央行储备结构变化。",
        "sourceRank": "A级",
        "absorbed": "尚未完全消化",
        "shortTerm": "短线受美元和实际利率扰动，容易震荡。",
        "midTerm": "中期若 ETF 和央行买盘延续，黄金仍有支撑。",
        "longTerm": "长期取决于全球储备多元化和财政赤字压力。",
        "decision": "更适合分批配置或作为组合对冲，不适合只因单日上涨追入。",
    },
    {
        "id": "ai-earnings-capex",
        "date": "5月11日",
        "time": "08:50",
        "source": "财报观察",
        "avatar": "Q",
        "score": 79,
        "category": "equity",
        "horizon": "mid",
        "asset": "equity",
        "title": "大型科技公司财报指引分化，AI 资本开支进入验证期",
        "summary": "市场不再只奖励 AI 叙事，而是开始看收入兑现、毛利率和资本开支回报。指数层面需要警惕少数龙头拥挤交易，主动基金可能向盈利确定性更强的公司切换。",
        "tags": ["美股", "AI", "盈利", "基金调仓"],
        "reason": "科技股估值已经包含很高预期，财报指引一旦分化，会影响纳指、半导体 ETF 和全球成长风格基金。",
        "sourceRank": "S级",
        "absorbed": "等待财报验证",
        "shortTerm": "短期波动会集中在财报窗口和指引措辞。",
        "midTerm": "中期看 AI 投入能否兑现收入和毛利率。",
        "longTerm": "长期仍是生产率和资本开支周期主线。",
        "decision": "降低单一龙头拥挤交易，关注盈利兑现和现金流质量。",
    },
    {
        "id": "fiscal-deficit-term-premium",
        "date": "5月10日",
        "time": "22:15",
        "source": "美国财政部 / 宏观台",
        "avatar": "T",
        "score": 76,
        "category": "bond",
        "horizon": "long",
        "asset": "bond equity gold fx",
        "title": "财政赤字和长期发债压力抬升期限溢价",
        "summary": "如果财政赤字长期维持高位，长端利率中枢可能难以回到过去低位。长期配置需要重新评估股债相关性，以及黄金在组合中的风险对冲价值。",
        "tags": ["债务周期", "长期利率", "资产配置", "期限溢价"],
        "reason": "这不是短线新闻，而是影响未来数年资产配置框架的慢变量。它会改变股票估值、债券久期和黄金长期逻辑。",
        "sourceRank": "A级",
        "absorbed": "长期定价中",
        "shortTerm": "短期通过长端收益率波动影响风险资产。",
        "midTerm": "中期会影响债券久期选择和股债相关性。",
        "longTerm": "长期可能抬高实际利率中枢，改变组合配置框架。",
        "decision": "长期配置里降低对低利率回归的单一路径依赖，增加情景约束。",
    },
    {
        "id": "oil-inventory-geopolitics",
        "date": "5月10日",
        "time": "20:30",
        "source": "商品研究台",
        "avatar": "O",
        "score": 71,
        "category": "commodity",
        "horizon": "short",
        "asset": "commodity equity",
        "title": "原油库存下降叠加地缘风险，能源价格风险溢价上升",
        "summary": "油价短期冲击会通过通胀预期影响利率，也会改变能源股、航空、消费和商品基金的相对表现。重点观察库存、OPEC 表态和冲突升级概率。",
        "tags": ["原油", "地缘", "通胀", "商品基金"],
        "reason": "原油是通胀预期和风险偏好的连接点。它涨得太快，会重新压制降息预期，并拖累高估值风险资产。",
        "sourceRank": "A级",
        "absorbed": "快速交易中",
        "shortTerm": "短期推升能源和通胀预期，压制航空和消费。",
        "midTerm": "中期看库存、OPEC 供给纪律和地缘风险是否延续。",
        "longTerm": "长期取决于能源转型、供需投资周期和地缘格局。",
        "decision": "把原油作为通胀风险监控指标，不把单一库存数据当趋势确认。",
    },
    {
        "id": "volatility-risk-repricing",
        "date": "5月10日",
        "time": "17:40",
        "source": "风险监测",
        "avatar": "R",
        "score": 69,
        "category": "risk",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "title": "波动率指数回升，市场对尾部风险重新定价",
        "summary": "当 VIX 与美元同时上行，通常意味着市场从追逐收益转向管理风险。短线需要观察信用利差、日元波动和高收益债 ETF 是否同步承压。",
        "tags": ["波动率", "风险偏好", "信用利差", "美元"],
        "reason": "这类信号不一定指向趋势反转，但能提醒仓位管理。尤其当多个风险指标同步恶化时，优先考虑防守。",
        "sourceRank": "B级",
        "absorbed": "低度消化",
        "shortTerm": "短期提示市场风险偏好转弱，仓位和杠杆要更保守。",
        "midTerm": "中期需要观察信用利差、美元和日元是否同步恶化。",
        "longTerm": "长期意义有限，除非演化为流动性或信用事件。",
        "decision": "当 VIX、美元、信用利差同时上行时，优先控制回撤。",
    },
]

ASSETS = [
    ["美股", "中性偏谨慎", "高估值板块对利率和盈利指引敏感，适合等待财报和收益率确认。", "watch"],
    ["A股 / 港股", "观察政策验证", "需要看盈利修复、外资流入、地产风险缓和和政策落地强度。", "watch"],
    ["债券基金", "等待确认", "如果经济数据降温且通胀回落，久期资产胜率会上升。", "watch"],
    ["黄金", "中期偏强", "实际利率、央行购金和避险需求仍是核心支撑。", "positive"],
    ["原油", "事件驱动", "库存、OPEC 和地缘冲突决定短线波动，注意对通胀的二次影响。", "watch"],
    ["美元", "短期偏强", "降息预期后移时美元通常获得支撑，新兴市场承压。", "positive"],
    ["商品基金", "结构分化", "铜、油、农产品要分别看供需、库存和中国需求。", "watch"],
    ["新兴市场", "谨慎选择", "美元和全球风险偏好是关键变量，资金流更重要。", "negative"],
]

SCENARIOS = [
    {
        "name": "乐观情景",
        "probability": "25%",
        "summary": "通胀温和回落，盈利继续修复，降息预期重新升温。",
        "result": "股票和债券同时受益，黄金保持配置价值。",
    },
    {
        "name": "基准情景",
        "probability": "50%",
        "summary": "经济保持韧性但通胀回落缓慢，市场在利率和盈利之间摇摆。",
        "result": "资产分化，降低追高，关注黄金、短债和现金流稳定资产。",
    },
    {
        "name": "悲观情景",
        "probability": "25%",
        "summary": "通胀再起或信用风险暴露，收益率和波动率同时上行。",
        "result": "风险资产承压，美元和避险资产受益，仓位控制优先。",
    },
]


def fetch_stooq_quote(symbol: str) -> dict[str, Any]:
    url = f"https://stooq.com/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv"
    request = Request(url, headers={"User-Agent": "GlobalMarketRadar/1.0"})
    with urlopen(request, timeout=20) as response:
        text = response.read().decode("utf-8", errors="replace")

    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        raise ValueError(f"No rows returned for {symbol}")
    row = rows[0]
    close_value = row.get("Close") or ""
    if close_value.upper() == "N/D" or not close_value:
        raise ValueError(f"No quote returned for {symbol}: {row}")
    return row


def pct_change(close: float, open_value: float | None) -> float | None:
    if open_value is None or open_value == 0:
        return None
    return round((close - open_value) / open_value * 100, 2)


def quote_snapshot(instrument: dict[str, Any], generated_at: str, errors: list[str]) -> dict[str, Any]:
    try:
        row = fetch_stooq_quote(instrument["symbol"])
        status = "live"
        close = float(row["Close"])
        open_value = parse_float(row.get("Open"))
        date = row.get("Date")
        time = row.get("Time")
    except Exception as exc:  # noqa: BLE001 - generation should degrade gracefully
        status = "fallback"
        close = instrument["fallback_close"]
        open_value = None
        date = generated_at[:10]
        time = generated_at[11:16]
        errors.append(f"{instrument['symbol']}: {exc}")

    return {
        "symbol": instrument["symbol"],
        "name": instrument["name"],
        "asset": instrument["asset"],
        "close": close,
        "open": open_value,
        "changePct": pct_change(close, open_value),
        "date": date,
        "time": time,
        "status": status,
    }


def build_market_snapshot() -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    quotes: list[dict[str, Any]] = []
    errors: list[str] = []

    for instrument in MARKET_INSTRUMENTS:
        quotes.append(quote_snapshot(instrument, generated_at, errors))

    return {
        "generated_at": generated_at,
        "quotes": quotes,
        "status": "live" if not errors else "degraded",
        "errors": errors,
        "source": "Stooq 延迟行情 CSV；源不可用时使用内置兜底值",
    }


def quote_lookup(quotes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["symbol"].lower(): item for item in quotes}


def average_change(quotes: dict[str, dict[str, Any]], symbols: list[str]) -> float | None:
    values = [
        quote["changePct"]
        for symbol in symbols
        if (quote := quotes.get(symbol.lower())) and quote.get("changePct") is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def factor_tone(value: float | None, positive_label: str, negative_label: str, neutral_label: str) -> tuple[str, str]:
    if value is None:
        return neutral_label, "watch"
    if value >= 0.2:
        return positive_label, "positive"
    if value <= -0.2:
        return negative_label, "negative"
    return neutral_label, "watch"


def format_metric(quote: dict[str, Any] | None) -> str:
    if not quote:
        return "暂无"
    change = quote.get("changePct")
    suffix = "" if change is None else f" / {change:+.2f}%"
    return f"{quote['close']}{suffix}"


def metric_items(quotes: dict[str, dict[str, Any]], symbols: list[str]) -> list[dict[str, Any]]:
    items = []
    for symbol in symbols:
        quote = quotes.get(symbol.lower())
        if not quote:
            continue
        items.append(
            {
                "name": quote["name"],
                "symbol": quote["symbol"],
                "value": quote["close"],
                "changePct": quote.get("changePct"),
                "status": quote["status"],
            }
        )
    return items


def build_factor_snapshot(market_snapshot: dict[str, Any]) -> dict[str, Any]:
    generated_at = market_snapshot["generated_at"]
    errors: list[str] = []
    extra_quotes = [quote_snapshot(instrument, generated_at, errors) for instrument in FACTOR_INSTRUMENTS]
    quotes = quote_lookup(market_snapshot["quotes"] + extra_quotes)

    risk_value = average_change(quotes, ["spy.us", "qqq.us", "hyg.us"])
    duration_value = average_change(quotes, ["tlt.us", "ief.us"])
    credit_value = None
    if (hyg := quotes.get("hyg.us")) and (lqd := quotes.get("lqd.us")):
        if hyg.get("changePct") is not None and lqd.get("changePct") is not None:
            credit_value = round(hyg["changePct"] - lqd["changePct"], 2)
    dollar_value = average_change(quotes, ["dx.f", "uup.us"])
    gold_value = average_change(quotes, ["xauusd", "gld.us"])
    commodity_value = average_change(quotes, ["cl.f", "uso.us", "hg.f"])

    risk_stance, risk_tone = factor_tone(risk_value, "风险偏好升温", "风险偏好转弱", "风险偏好观望")
    duration_stance, duration_tone = factor_tone(duration_value, "久期压力缓和", "长端利率压力上行", "久期信号中性")
    credit_stance, credit_tone = factor_tone(credit_value, "信用风险缓和", "信用风险升温", "信用利差观望")
    dollar_stance, dollar_tone = factor_tone(dollar_value, "美元走强", "美元走弱", "美元震荡")
    gold_stance, gold_tone = factor_tone(gold_value, "黄金获得支撑", "黄金短线承压", "黄金震荡")
    commodity_stance, commodity_tone = factor_tone(commodity_value, "商品通胀线索升温", "商品需求线索转弱", "商品信号分化")

    factors = [
        {
            "id": "risk-appetite",
            "title": "风险偏好验证",
            "stance": risk_stance,
            "tone": risk_tone,
            "summary": f"用标普500、纳指100和高收益债 ETF 观察风险资产是否同步确认。当前综合变化：{risk_value if risk_value is not None else '暂无'}%。",
            "decision": "若新闻利好但风险资产和高收益债不同步，先降低对单条消息的信任度。",
            "metrics": metric_items(quotes, ["spy.us", "qqq.us", "hyg.us"]),
        },
        {
            "id": "duration-pressure",
            "title": "利率与久期压力",
            "stance": duration_stance,
            "tone": duration_tone,
            "summary": f"用长久期和中久期美债 ETF 代理利率压力。TLT：{format_metric(quotes.get('tlt.us'))}，IEF：{format_metric(quotes.get('ief.us'))}。",
            "decision": "久期资产下跌时，成长股、黄金和长债基金的短线胜率通常下降。",
            "metrics": metric_items(quotes, ["tlt.us", "ief.us", "shy.us"]),
        },
        {
            "id": "credit-pressure",
            "title": "信用风险确认",
            "stance": credit_stance,
            "tone": credit_tone,
            "summary": f"用高收益债相对投资级债的表现观察信用风险。HYG-LQD 日内相对变化：{credit_value if credit_value is not None else '暂无'} 个百分点。",
            "decision": "如果股票上涨但高收益债弱于投资级债，说明风险偏好可能不够扎实。",
            "metrics": metric_items(quotes, ["hyg.us", "lqd.us"]),
        },
        {
            "id": "dollar",
            "title": "美元与汇率压力",
            "stance": dollar_stance,
            "tone": dollar_tone,
            "summary": f"用美元指数期货和美元 ETF 观察外汇压力。综合变化：{dollar_value if dollar_value is not None else '暂无'}%。",
            "decision": "美元走强通常压制黄金、新兴市场和商品货币，需和利率信号一起看。",
            "metrics": metric_items(quotes, ["dx.f", "uup.us"]),
        },
        {
            "id": "gold",
            "title": "黄金避险与实际利率",
            "stance": gold_stance,
            "tone": gold_tone,
            "summary": f"用现货黄金和黄金 ETF 检查避险需求。综合变化：{gold_value if gold_value is not None else '暂无'}%。",
            "decision": "黄金上涨若同时伴随美元和利率上行，要重点判断是避险买盘还是通胀交易。",
            "metrics": metric_items(quotes, ["xauusd", "gld.us"]),
        },
        {
            "id": "commodity-inflation",
            "title": "商品通胀线索",
            "stance": commodity_stance,
            "tone": commodity_tone,
            "summary": f"用原油、能源 ETF 和铜观察商品通胀与周期需求。综合变化：{commodity_value if commodity_value is not None else '暂无'}%。",
            "decision": "原油和铜同步上行更偏通胀/需求确认；只有原油上行则更像供给或地缘冲击。",
            "metrics": metric_items(quotes, ["cl.f", "uso.us", "hg.f"]),
        },
    ]

    return {
        "generated_at": generated_at,
        "items": factors,
        "quotes": extra_quotes,
        "status": "live" if not errors else "degraded",
        "errors": errors,
        "source": "Stooq ETF、期货与现货代理指标；用于验证新闻是否被市场价格确认",
    }


KEYWORD_RULES = [
    {
        "category": "macro",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "terms": [
            "federal reserve",
            "fomc",
            "ecb",
            "bank of japan",
            "boj",
            "central bank",
            "monetary policy",
            "interest rate",
            "policy rate",
            "inflation",
            "consumer price",
            "cpi",
            "payroll",
            "employment",
            "unemployment",
            "wage",
            "gdp",
            "retail sales",
            "inventories",
            "trade",
        ],
    },
    {
        "category": "bond",
        "horizon": "mid",
        "asset": "bond equity fx gold",
        "terms": ["treasury", "yield", "debt", "auction", "deficit", "fiscal", "financing", "bond", "liquidity"],
    },
    {
        "category": "commodity",
        "horizon": "short",
        "asset": "commodity equity bond",
        "terms": ["oil", "gas", "crude", "energy", "inventory", "inventories", "eia", "opec", "petroleum"],
    },
    {
        "category": "equity",
        "horizon": "mid",
        "asset": "equity",
        "terms": ["earnings", "sec", "securities", "company", "disclosure", "fund", "etf", "retail sales"],
    },
    {
        "category": "risk",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "terms": ["risk", "volatility", "sanction", "bank", "credit", "liquidity", "enforcement", "margin", "derivatives"],
    },
    {
        "category": "gold",
        "horizon": "mid",
        "asset": "gold fx bond",
        "terms": ["gold", "reserve", "central bank"],
    },
]

CATEGORY_LABELS = {
    "macro": "宏观",
    "bond": "债券",
    "commodity": "商品",
    "equity": "股票",
    "risk": "风险",
    "gold": "黄金",
}

ASSET_LABELS = {
    "equity": "股票",
    "bond": "债券",
    "gold": "黄金",
    "fx": "汇率",
    "commodity": "商品",
}

HIGH_IMPACT_PHRASES = [
    "fomc statement",
    "monetary policy",
    "federal funds rate",
    "interest rate",
    "policy rate",
    "consumer price",
    "cpi",
    "inflation",
    "unemployment",
    "nonfarm payroll",
    "payrolls",
    "treasury yields",
    "refunding",
    "auction",
    "oil inventory",
    "crude oil",
    "retail sales",
    "global liquidity",
    "sanction",
    "insider trading",
]

LOW_IMPACT_PHRASES = [
    "approval of application",
    "approval of related applications",
    "does not object",
    "names",
    "resignation",
    "termination of enforcement actions",
    "former employee",
    "community bankshares",
    "commencement",
    "conference",
    "retirement plans for small businesses",
]


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "GlobalMarketRadar/1.1"})
    with urlopen(request, timeout=25) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="replace")


def fetch_json_post(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "GlobalMarketRadar/1.2",
        },
    )
    with urlopen(request, timeout=25) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8", errors="replace"))


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def child_text(node: ET.Element, name: str) -> str:
    for child in list(node):
        if child.tag.lower().endswith(name.lower()):
            return child.text or ""
    return ""


def child_link(node: ET.Element) -> str:
    link = child_text(node, "link")
    if link:
        return link.strip()
    for child in list(node):
        if child.tag.lower().endswith("link"):
            return child.attrib.get("href", "").strip()
    return ""


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            parsed = datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_cn_date(dt: datetime) -> str:
    return f"{dt.month}月{dt.day}日"


def format_period_cn(value: str) -> str:
    month_names = {
        "january": "1月",
        "february": "2月",
        "march": "3月",
        "april": "4月",
        "may": "5月",
        "june": "6月",
        "july": "7月",
        "august": "8月",
        "september": "9月",
        "october": "10月",
        "november": "11月",
        "december": "12月",
    }
    return month_names.get(value.lower(), value)


def slugify(value: str, prefix: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if slug:
        return f"{prefix}-{slug[:52]}-{digest}"
    return f"{prefix}-{digest}"


TOPIC_RULES = [
    (["fomc", "federal funds", "interest rate", "policy rate", "monetary policy"], "利率政策和央行路径"),
    (["inflation", "consumer price", "cpi", "price"], "通胀压力和实际利率"),
    (["unemployment", "payroll", "employment", "wage"], "就业和工资趋势"),
    (["retail sales", "sales"], "消费需求和企业收入"),
    (["inventories", "inventory"], "库存周期和供需变化"),
    (["treasury", "auction", "debt", "deficit", "fiscal"], "财政融资和美债供给"),
    (["oil", "gas", "crude", "petroleum", "energy"], "能源供需和通胀传导"),
    (["sec", "securities", "disclosure", "fraud", "insider"], "资本市场监管和公司风险"),
    (["liquidity", "banking", "credit", "margin", "derivatives", "reserve balances", "discount window"], "全球流动性和金融稳定"),
    (["sanction", "geopolitical"], "地缘政策和风险偏好"),
    (["gold", "bullion"], "黄金和官方储备变化"),
]


def infer_topic_cn(entry: dict[str, Any], category: str) -> str:
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    for terms, topic in TOPIC_RULES:
        if any(term in text for term in terms):
            return topic

    source_id = entry["source"].get("id", "")
    if source_id == "ecb_press":
        return "欧元区政策、通胀和金融稳定"
    if source_id == "boj_whatsnew":
        return "日本利率、日元和套息交易环境"
    if source_id.startswith("bis_"):
        return "全球流动性和银行体系风险"
    if source_id == "census_indicators":
        return "美国实体经济和需求变化"

    return {
        "macro": "宏观数据和政策预期",
        "bond": "利率、债务和期限溢价",
        "commodity": "商品供需和通胀线索",
        "equity": "股票市场监管、盈利和资金流",
        "risk": "风险偏好和金融稳定",
        "gold": "黄金、实际利率和储备配置",
    }.get(category, "市场影响因素")


def display_title_cn(source: dict[str, Any], topic: str) -> str:
    if source.get("class") == "media":
        return f"{source.get('name', '媒体源')}观察：{topic}"
    return f"{source.get('name', '官方信源')}更新：{topic}"


def display_summary_cn(source: dict[str, Any], category: str, asset_text: str, topic: str) -> str:
    category_label = CATEGORY_LABELS.get(category, "市场")
    if source.get("class") == "media":
        return (
            f"{source.get('name', '媒体源')}报道了与{topic}相关的市场线索，系统将其归入{category_label}类影响因素。"
            f"它更适合帮助理解市场叙事和资金情绪，仍需用一手数据和价格反应验证。"
        )
    return (
        f"{source.get('name', '官方信源')}发布与{topic}相关的新信息，系统将其归入{category_label}类影响因素，"
        f"重点观察它对{asset_text}的传导。正式决策应结合原文链接、后续数据和价格确认。"
    )


def analysis_channel(category: str) -> str:
    return {
        "macro": "利率预期、美元方向和估值折现率",
        "bond": "收益率曲线、期限溢价和美元流动性",
        "commodity": "通胀预期、成本压力和周期资产表现",
        "equity": "盈利预期、估值风险和资金偏好",
        "risk": "波动率、信用利差和避险需求",
        "gold": "实际利率、美元和央行储备偏好",
    }.get(category, "风险偏好和资产定价")


def build_ai_brief(entry: dict[str, Any], category: str, asset_text: str, score: int, topic: str) -> str:
    channel = analysis_channel(category)
    score_text = "优先级很高" if score >= 85 else "值得跟踪" if score >= 70 else "先作为线索观察"
    if entry["source"].get("class") == "media":
        return (
            f"AI速读：这是一条媒体解释源，主要讲{topic}，{score_text}。"
            f"它有助于理解市场正在交易什么叙事，但不能替代官方数据；需要观察{asset_text}是否给出价格确认。"
        )
    return (
        f"AI速读：这条信息主要讲{topic}，{score_text}。它可能通过{channel}影响{asset_text}，"
        "需要和原文、价格反应以及后续数据一起确认。"
    )


def build_watch_points(category: str, asset_text: str) -> list[str]:
    common = [f"{asset_text}是否出现同向价格确认", "同主题是否出现第二个一手信源确认"]
    category_points = {
        "macro": ["美债收益率和美元是否同步反应", "降息或加息概率是否重新定价"],
        "bond": ["长端收益率是否突破近期区间", "财政融资或拍卖需求是否继续恶化"],
        "commodity": ["库存、供给和现货价格是否同向变化", "通胀预期是否被重新抬升"],
        "equity": ["相关板块 ETF 和龙头股是否放量反应", "盈利预期或监管风险是否扩散"],
        "risk": ["VIX、信用利差和美元是否同时上行", "避险资产是否获得持续买盘"],
        "gold": ["实际利率和美元是否压制金价", "黄金 ETF 或央行购金线索是否延续"],
    }
    return (category_points.get(category, []) + common)[:4]


def load_sources() -> list[dict[str, Any]]:
    try:
        payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    return payload.get("sources", [])


def parse_rss_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    text = fetch_text(source["url"])
    root = ET.fromstring(text)
    nodes = [
        node
        for node in root.iter()
        if node.tag.lower().endswith("item") or node.tag.lower().endswith("entry")
    ]
    entries = []
    for node in nodes[:12]:
        title = strip_html(child_text(node, "title"))
        if not title:
            continue
        description = strip_html(child_text(node, "description") or child_text(node, "summary"))
        published = parse_datetime(
            child_text(node, "pubDate")
            or child_text(node, "published")
            or child_text(node, "updated")
            or child_text(node, "date")
        )
        entries.append(
            {
                "title": title,
                "summary": description,
                "link": child_link(node),
                "published": published,
                "source": source,
            }
        )
    return entries


def parse_treasury_html_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    text = fetch_text(source["url"])
    matches = re.findall(
        r'<a[^>]+href="([^"]*press-releases/[^"]+)"[^>]*>(.*?)</a>',
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    entries = []
    seen: set[str] = set()
    for href, raw_title in matches:
        title = strip_html(raw_title)
        if not title or title in seen:
            continue
        seen.add(title)
        link = href if href.startswith("http") else f"https://home.treasury.gov{href}"
        entries.append(
            {
                "title": title,
                "summary": "",
                "link": link,
                "published": datetime.now(timezone.utc),
                "source": source,
            }
        )
        if len(entries) >= 8:
            break
    return entries


def parse_float(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def parse_bls_api_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    series_configs = source.get("series", [])
    series_ids = [item["id"] for item in series_configs if item.get("id")]
    if not series_ids:
        return []

    now = datetime.now(timezone.utc)
    payload = {
        "seriesid": series_ids,
        "startyear": str(now.year - 1),
        "endyear": str(now.year),
    }
    response = fetch_json_post(source["url"], payload)
    if response.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS API status: {response.get('status')} {response.get('message')}")

    config_by_id = {item["id"]: item for item in series_configs}
    entries = []
    for series in response.get("Results", {}).get("series", []):
        series_id = series.get("seriesID") or series.get("seriesId")
        config = config_by_id.get(series_id, {})
        points = series.get("data", [])
        if not points:
            continue

        latest = points[0]
        previous = points[1] if len(points) > 1 else None
        latest_value = parse_float(latest.get("value"))
        previous_value = parse_float(previous.get("value")) if previous else None
        if latest_value is None:
            continue

        if previous_value is None:
            change_text = "暂无上一期对比数据"
        else:
            delta = latest_value - previous_value
            change_text = f"较上一期变化 {delta:+.2f}"

        period = format_period_cn(latest.get("periodName") or latest.get("period") or "最新周期")
        year = latest.get("year") or str(now.year)
        unit = config.get("unit", "")
        title = f"{config.get('name', series_id)}最新读数：{latest_value:g} {unit}（{year}年{period}）"
        asset_text = config.get("asset", source.get("asset_hint", "equity bond gold fx"))
        summary = (
            f"美国劳工统计局官方序列 {series_id} 在 {year}年{period} 的读数为 {latest_value:g} {unit}；"
            f"{change_text}。这是判断利率、股票、债券、黄金和汇率的重要{config.get('topic', '宏观')}输入。"
        )
        entries.append(
            {
                "title": title,
                "summary": summary,
                "link": source["url"],
                "published": now,
                "source": source,
                "category": config.get("category", source.get("category_hint", "macro")),
                "horizon": config.get("horizon", "short"),
                "asset": asset_text,
                "topic_cn": config.get("topic", "宏观数据"),
            }
        )
    return entries


def classify_entry(entry: dict[str, Any]) -> dict[str, str]:
    if entry.get("category") and entry.get("horizon") and entry.get("asset"):
        return {
            "category": entry["category"],
            "horizon": entry["horizon"],
            "asset": entry["asset"],
            "hits": "4",
        }

    source = entry["source"]
    text = f"{entry['title']} {entry.get('summary', '')}".lower()
    best_rule = None
    best_hits = 0
    for rule in KEYWORD_RULES:
        hits = sum(1 for term in rule["terms"] if term in text)
        if hits > best_hits:
            best_rule = rule
            best_hits = hits

    if not best_rule:
        return {
            "category": source.get("category_hint", "macro"),
            "horizon": "mid",
            "asset": source.get("asset_hint", "equity bond gold fx"),
            "hits": "0",
        }

    return {
        "category": best_rule["category"],
        "horizon": best_rule["horizon"],
        "asset": best_rule["asset"],
        "hits": str(best_hits),
    }


def score_entry(entry: dict[str, Any], classification: dict[str, str]) -> int:
    source = entry["source"]
    score = int(source.get("base_score", 70))
    hits = int(classification["hits"])
    score += min(8, hits * 2)
    age_hours = max(0.0, (datetime.now(timezone.utc) - entry["published"]).total_seconds() / 3600)
    if age_hours <= 24:
        score += 5
    elif age_hours > 168:
        score -= 8
    if source.get("rank") == "S":
        score += 3
    if hits == 0:
        score -= 18

    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    high_hits = sum(1 for phrase in HIGH_IMPACT_PHRASES if phrase in text)
    low_hits = sum(1 for phrase in LOW_IMPACT_PHRASES if phrase in text)
    score += min(18, high_hits * 6)
    score -= min(35, low_hits * 14)
    return max(45, min(98, score))


def build_signal_from_entry(entry: dict[str, Any]) -> dict[str, Any]:
    source = entry["source"]
    classification = classify_entry(entry)
    score = score_entry(entry, classification)
    category = classification["category"]
    assets = [
        label
        for key, label in ASSET_LABELS.items()
        if key in classification["asset"]
    ]
    asset_text = "、".join(assets) or "多类资产"
    topic = entry.get("topic_cn") or infer_topic_cn(entry, category)
    title = entry.get("title_cn") or (
        entry["title"] if entry.get("category") else display_title_cn(source, topic)
    )
    summary = entry.get("summary_cn") or (
        entry.get("summary") if entry.get("category") else display_summary_cn(source, category, asset_text, topic)
    )
    summary = summary or f"{title}。"
    if len(summary) > 220:
        summary = f"{summary[:220].rstrip()}..."
    source_kind = "媒体解释源" if source.get("class") == "media" else source.get("rank", "A") + "级信源"

    return {
        "id": slugify(entry["title"], source["id"]),
        "date": format_cn_date(entry["published"]),
        "time": entry["published"].strftime("%H:%M"),
        "sourceId": source["id"],
        "source": source["name"],
        "sourceUrl": entry.get("link", source["url"]),
        "sourceBrief": source.get("role", "用于辅助判断市场方向和风险偏好的数据来源。"),
        "originalTitle": entry["title"],
        "originalSummary": entry.get("summary", ""),
        "avatar": source.get("avatar", source["name"][:1]),
        "score": score,
        "category": category,
        "horizon": classification["horizon"],
        "asset": classification["asset"],
        "title": title,
        "summary": summary,
        "aiBrief": build_ai_brief(entry, category, asset_text, score, topic),
        "watchPoints": build_watch_points(category, asset_text),
        "tags": [CATEGORY_LABELS.get(category, "市场"), source_kind, asset_text],
        "reason": f"来自 {source['name']} 的高优先级信息，可能影响{asset_text}。评分综合信源等级、关键词命中、发布时间和影响资产范围。",
        "sourceRank": source.get("rank", "A") + "级",
        "absorbed": "尚未完全消化" if score >= 80 else "部分消化",
        "shortTerm": f"短期观察该信息是否在{asset_text}价格中形成确认。",
        "midTerm": f"中期结合后续数据和资金流，判断{CATEGORY_LABELS.get(category, '市场')}主线是否延续。",
        "longTerm": "长期意义取决于它是否改变利率、盈利、通胀或风险溢价的基准假设。",
        "decision": "仅作为研究和风控输入，不作为单独交易信号；等待价格、数据和信源交叉确认。",
    }


def build_live_signals() -> tuple[list[dict[str, Any]], list[str]]:
    signals: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_titles: set[str] = set()
    for source in load_sources():
        try:
            if source.get("type") == "rss":
                entries = parse_rss_source(source)
            elif source.get("type") == "bls_api":
                entries = parse_bls_api_source(source)
            elif source.get("type") == "treasury_html":
                entries = parse_treasury_html_source(source)
            else:
                entries = []
        except Exception as exc:  # noqa: BLE001 - keep the pipeline alive
            errors.append(f"{source.get('id', 'source')}: {exc}")
            continue

        for entry in entries:
            normalized_title = entry["title"].casefold()
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)
            signals.append(build_signal_from_entry(entry))

    signals.sort(key=lambda item: (item["score"], item["date"], item["time"]), reverse=True)
    return diversify_signals(signals, limit=40, max_per_source=4), errors


def diversify_signals(signals: list[dict[str, Any]], limit: int, max_per_source: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    selected_ids: set[str] = set()

    # First keep one strong item from every available source, so the feed feels like
    # a radar instead of a scoreboard dominated by one institution.
    for item in signals:
        source_id = item.get("sourceId", item.get("source", "source"))
        if source_id not in counts:
            selected.append(item)
            selected_ids.add(item["id"])
            counts[source_id] = 1
        if len(selected) >= limit:
            return selected

    for item in signals:
        if item["id"] in selected_ids:
            continue
        source_id = item.get("sourceId", item.get("source", "source"))
        if counts.get(source_id, 0) >= max_per_source:
            continue
        selected.append(item)
        selected_ids.add(item["id"])
        counts[source_id] = counts.get(source_id, 0) + 1
        if len(selected) >= limit:
            break
    return selected


def build_daily(signals: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    sections = []
    for category, label in CATEGORY_LABELS.items():
        titles = [item["title"] for item in signals if item.get("category") == category][:4]
        if titles:
            sections.append({"title": label, "items": titles})
    if not sections:
        sections.append({"title": "市场", "items": [item["title"] for item in signals[:5]]})

    top = signals[0] if signals else {"title": "暂无高优先级事件"}
    now = datetime.now(timezone.utc)
    return {
        "generated_at": generated_at,
        "title": f"{now.month}月{now.day}日",
        "summary": f"今日最高优先级事件：{top['title']}。日报根据官方信源等级、关键词、影响资产范围和发布时间自动生成。",
        "sections": sections,
        "watch": ["CPI / 通胀数据", "美债收益率", "美元指数", "黄金 ETF 资金流", "主要央行表态"],
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    market_snapshot = build_market_snapshot()
    factor_snapshot = build_factor_snapshot(market_snapshot)
    generated_at = market_snapshot["generated_at"]
    live_signals, source_errors = build_live_signals()
    output_signals = live_signals or BASE_SIGNALS

    write_json(DATA_DIR / "signals.json", {"generated_at": generated_at, "items": output_signals})
    write_json(DATA_DIR / "assets.json", {"generated_at": generated_at, "items": ASSETS})
    write_json(DATA_DIR / "scenarios.json", {"generated_at": generated_at, "items": SCENARIOS})
    write_json(DATA_DIR / "market_snapshot.json", market_snapshot)
    write_json(DATA_DIR / "factors.json", factor_snapshot)
    write_json(DATA_DIR / "daily.json", build_daily(output_signals, generated_at))
    write_json(
        DATA_DIR / "meta.json",
        {
            "generated_at": generated_at,
            "version": "1.5",
            "status": "live" if live_signals and market_snapshot["status"] == "live" and factor_snapshot["status"] == "live" else "degraded",
            "notes": [
                f"已从多层信源生成 {len(output_signals)} 条市场影响因素，并加入 AI 速读。",
                "新增 WSJ、CNBC、MarketWatch、Yahoo Finance、Bloomberg、FT、BBC、Guardian 等媒体解释源。",
                "市场动态会结合官方信源、媒体叙事和价格代理指标，辅助判断信息是否被市场确认。",
            ],
            "source_errors": market_snapshot["errors"] + factor_snapshot["errors"] + source_errors,
        },
    )
    all_errors = market_snapshot["errors"] + factor_snapshot["errors"] + source_errors
    if all_errors:
        print("数据已生成，但部分行情或信源降级：", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
