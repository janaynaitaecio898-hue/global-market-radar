#!/usr/bin/env python3
"""Generate static data files for Global Market Radar.

The site is hosted on GitHub Pages, so the first production version uses a
static-data pipeline: this script fetches lightweight market quotes, combines
them with the editorial rule set below, and writes JSON consumed by app.js.
"""

from __future__ import annotations

import csv
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
        "name": "S&P 500 ETF",
        "asset": "equity",
        "fallback_close": 520.0,
    },
    {
        "symbol": "qqq.us",
        "name": "Nasdaq 100 ETF",
        "asset": "equity",
        "fallback_close": 445.0,
    },
    {
        "symbol": "tlt.us",
        "name": "20+ Year Treasury ETF",
        "asset": "bond",
        "fallback_close": 90.0,
    },
    {
        "symbol": "gld.us",
        "name": "Gold ETF",
        "asset": "gold",
        "fallback_close": 215.0,
    },
    {
        "symbol": "uso.us",
        "name": "Oil ETF",
        "asset": "commodity",
        "fallback_close": 75.0,
    },
    {
        "symbol": "uup.us",
        "name": "US Dollar ETF",
        "asset": "fx",
        "fallback_close": 29.0,
    },
]

BASE_SIGNALS = [
    {
        "id": "us-jobs-rate-path",
        "date": "5月11日",
        "time": "10:40",
        "source": "Federal Reserve / BLS",
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
        "source": "ETF Flow Monitor",
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
        "source": "Earnings Watch",
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
        "source": "Treasury / Macro Desk",
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
        "source": "Commodity Desk",
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
        "source": "Risk Monitor",
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


def build_market_snapshot() -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    quotes: list[dict[str, Any]] = []
    errors: list[str] = []

    for instrument in MARKET_INSTRUMENTS:
        try:
            row = fetch_stooq_quote(instrument["symbol"])
            status = "live"
            close = float(row["Close"])
            date = row.get("Date")
            time = row.get("Time")
        except Exception as exc:  # noqa: BLE001 - generation should degrade gracefully
            status = "fallback"
            close = instrument["fallback_close"]
            date = generated_at[:10]
            time = generated_at[11:16]
            errors.append(f"{instrument['symbol']}: {exc}")

        quotes.append(
            {
                "symbol": instrument["symbol"],
                "name": instrument["name"],
                "asset": instrument["asset"],
                "close": close,
                "date": date,
                "time": time,
                "status": status,
            }
        )

    return {
        "generated_at": generated_at,
        "quotes": quotes,
        "status": "live" if not errors else "degraded",
        "errors": errors,
        "source": "Stooq delayed quote CSV with built-in fallback values",
    }


KEYWORD_RULES = [
    {
        "category": "macro",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "terms": [
            "federal reserve",
            "fomc",
            "interest rate",
            "inflation",
            "consumer price",
            "cpi",
            "payroll",
            "employment",
            "unemployment",
            "wage",
            "gdp",
        ],
    },
    {
        "category": "bond",
        "horizon": "mid",
        "asset": "bond equity fx gold",
        "terms": ["treasury", "yield", "debt", "auction", "deficit", "fiscal", "financing"],
    },
    {
        "category": "commodity",
        "horizon": "short",
        "asset": "commodity equity bond",
        "terms": ["oil", "gas", "crude", "energy", "inventory", "eia", "opec", "petroleum"],
    },
    {
        "category": "equity",
        "horizon": "mid",
        "asset": "equity",
        "terms": ["earnings", "sec", "securities", "company", "disclosure", "fund", "etf"],
    },
    {
        "category": "risk",
        "horizon": "short",
        "asset": "equity bond gold fx",
        "terms": ["risk", "volatility", "sanction", "bank", "credit", "liquidity", "enforcement"],
    },
    {
        "category": "gold",
        "horizon": "mid",
        "asset": "gold fx bond",
        "terms": ["gold", "reserve", "central bank"],
    },
]

CATEGORY_LABELS = {
    "macro": "Macro",
    "bond": "Bonds",
    "commodity": "Commodities",
    "equity": "Equities",
    "risk": "Risk",
    "gold": "Gold",
}

ASSET_LABELS = {
    "equity": "Equities",
    "bond": "Bonds",
    "gold": "Gold",
    "fx": "FX",
    "commodity": "Commodities",
}

HIGH_IMPACT_PHRASES = [
    "fomc statement",
    "federal funds rate",
    "interest rate",
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
    "sanction",
    "insider trading",
]

LOW_IMPACT_PHRASES = [
    "approval of application",
    "approval of related applications",
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


def slugify(value: str, prefix: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return f"{prefix}-{slug[:64] or 'item'}"


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
            change_text = "previous observation unavailable"
        else:
            delta = latest_value - previous_value
            change_text = f"change from previous observation {delta:+.2f}"

        period = latest.get("periodName") or latest.get("period") or "latest period"
        year = latest.get("year") or str(now.year)
        unit = config.get("unit", "")
        title = f"{config.get('name', series_id)} latest reading: {latest_value:g} {unit} ({period} {year})"
        asset_text = config.get("asset", source.get("asset_hint", "equity bond gold fx"))
        summary = (
            f"Official BLS series {series_id} reported {latest_value:g} {unit} for {period} {year}; "
            f"{change_text}. This is a core {config.get('topic', 'macro')} input for rates, equities, bonds, gold, and FX."
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
    asset_text = ", ".join(assets) or "multiple assets"
    summary = entry.get("summary") or f"{entry['title']}."
    if len(summary) > 220:
        summary = f"{summary[:220].rstrip()}..."

    return {
        "id": slugify(entry["title"], source["id"]),
        "date": format_cn_date(entry["published"]),
        "time": entry["published"].strftime("%H:%M"),
        "source": source["name"],
        "sourceUrl": entry.get("link", source["url"]),
        "avatar": source.get("avatar", source["name"][:1]),
        "score": score,
        "category": category,
        "horizon": classification["horizon"],
        "asset": classification["asset"],
        "title": entry["title"],
        "summary": summary,
        "tags": [CATEGORY_LABELS.get(category, "Market"), source.get("rank", "A") + "-rank source", asset_text],
        "reason": f"Official/high-priority source: {source['name']}. The item may affect {asset_text}. Score is based on source rank, keyword hits, freshness, and asset coverage.",
        "sourceRank": source.get("rank", "A") + "-rank",
        "absorbed": "Not fully priced" if score >= 80 else "Partly priced",
        "shortTerm": f"Watch whether this item triggers short-term price confirmation in {asset_text}.",
        "midTerm": f"Combine follow-up data and flows to judge whether the {CATEGORY_LABELS.get(category, 'Market')} theme persists.",
        "longTerm": "Long-term relevance depends on whether it changes the rate, earnings, inflation, or risk-premium baseline.",
        "decision": "Use as research and risk-control input, not as a standalone trading signal. Wait for price, data, and source confirmation.",
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
    return signals[:24], errors


def build_daily(signals: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    sections = []
    for category, label in CATEGORY_LABELS.items():
        titles = [item["title"] for item in signals if item.get("category") == category][:4]
        if titles:
            sections.append({"title": label, "items": titles})
    if not sections:
        sections.append({"title": "Market", "items": [item["title"] for item in signals[:5]]})

    top = signals[0] if signals else {"title": "No high-priority event yet"}
    now = datetime.now(timezone.utc)
    return {
        "generated_at": generated_at,
        "title": f"{now.month}/{now.day}",
        "summary": f"Top priority event: {top['title']}. The report is generated from source rank, keywords, asset coverage, and freshness.",
        "sections": sections,
        "watch": ["CPI / inflation data", "Treasury yields", "US dollar index", "Gold ETF flows", "Major central-bank remarks"],
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    market_snapshot = build_market_snapshot()
    generated_at = market_snapshot["generated_at"]
    live_signals, source_errors = build_live_signals()
    output_signals = live_signals or BASE_SIGNALS

    write_json(DATA_DIR / "signals.json", {"generated_at": generated_at, "items": output_signals})
    write_json(DATA_DIR / "assets.json", {"generated_at": generated_at, "items": ASSETS})
    write_json(DATA_DIR / "scenarios.json", {"generated_at": generated_at, "items": SCENARIOS})
    write_json(DATA_DIR / "market_snapshot.json", market_snapshot)
    write_json(DATA_DIR / "daily.json", build_daily(output_signals, generated_at))
    write_json(
        DATA_DIR / "meta.json",
        {
            "generated_at": generated_at,
            "version": "1.1",
            "status": "live" if live_signals and market_snapshot["status"] == "live" else "degraded",
            "notes": [
                f"Generated {len(output_signals)} market signals from configured official sources.",
                "Market quotes degrade to fallback values if a source is unavailable.",
                "Signals are classified by source rank, keywords, asset coverage, and freshness.",
            ],
            "source_errors": source_errors,
        },
    )
    all_errors = market_snapshot["errors"] + source_errors
    if all_errors:
        print("Generated with degraded quote data:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
