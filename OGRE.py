import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Crypto Arbitrage Scanner + Price Impact Simulator",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

st.title("🚀 Crypto Arbitrage Scanner + Price Impact Simulator")
st.markdown("""
**Tokens:** WETH • ETH • BNB • WBTC • LINK • USDC • USDT • AAVE • SUSHI • CAKE 
**DEXes:** Uniswap V2/V3 • Curve V2/V3 • Sushiswap V2/V3 • PancakeSwap V2/V3 • Balancer V2/V3
""")

# ====================== CONFIG (same as before) ======================
CHAINS = {
    "ethereum": {"dex_id": "ethereum", "oneinch_id": 1, "name": "Ethereum"},
    "base": {"dex_id": "base", "oneinch_id": 8453, "name": "Base"},
    "arbitrum": {"dex_id": "arbitrum", "oneinch_id": 42161, "name": "Arbitrum"},
    "polygon": {"dex_id": "polygon", "oneinch_id": 137, "name": "Polygon"},
    "bsc": {"dex_id": "bsc", "oneinch_id": 56, "name": "BSC"},
    "optimism": {"dex_id": "optimism", "oneinch_id": 10, "name": "Optimism"},
    "avalanche": {"dex_id": "avalanche", "oneinch_id": 43114, "name": "Avalanche"},
}

TOKEN_ADDRESSES = { ... }  # ← (same full dictionary as in the previous version – I kept it identical for brevity here)

SUPPORTED_DEX_IDS = ["uniswap", "uniswap-v2", "uniswap-v3", "sushi", "sushiswap",
                     "pancake", "pancakeswap", "curve", "curve-v2", "balancer", "balancer-v2"]

# ====================== SIDEBAR (Arbitrage Scanner) ======================
with st.sidebar:
    st.header("🔍 Arbitrage Scanner")
    from_token = st.selectbox("From Token", options=..., index=0)  # ← same as before
    amount = st.number_input("Amount to Swap", value=10.0, min_value=0.001, step=0.01)
    selected_chains = st.multiselect("Networks", options=list(CHAINS.keys()), default=["ethereum", "base", "arbitrum", "bsc"])
    target_token = st.selectbox("Target Token", ["USDC", "USDT"], index=0)
    slippage_tolerance = st.slider("Max Slippage (%)", 0.1, 5.0, 1.0, 0.1)
    openai_key = st.text_input("OpenAI API Key (optional)", type="password")
    refresh_btn = st.button("🔄 Run Arbitrage Scan", type="primary", use_container_width=True)

# ====================== HELPERS (same + new simulator helpers) ======================
@st.cache_data(ttl=25)
def fetch_dexscreener_pools(chain_id: str, token_addr: str):
    # ← same function as before
    ...

def is_supported_dex(dex_id: str) -> bool:
    # ← same
    ...

def calculate_slippage_and_output(pool: dict, amount_in: float):
    # ← same
    ...

# ====================== NEW: PRICE IMPACT SIMULATOR HELPERS ======================
def get_pair_pools(chain_id: str, token_a_addr: str, token_b_addr: str):
    """Fetch pools for exact token pair (A/B) and filter to supported DEXes"""
    pools = fetch_dexscreener_pools(chain_id, token_a_addr)
    pair_pools = []
    for p in pools:
        if not is_supported_dex(p.get("dexId", "")):
            continue
        base = p.get("baseToken", {}).get("address", "").lower()
        quote = p.get("quoteToken", {}).get("address", "").lower()
        if (base == token_a_addr.lower() and quote == token_b_addr.lower()) or \
           (base == token_b_addr.lower() and quote == token_a_addr.lower()):
            pair_pools.append(p)
    return pair_pools

def simulate_price_impact(pool: dict, amount_in: float, sell_token_is_base: bool):
    """Simulate large trade and return before/after price + impact"""
    if not pool or "liquidity" not in pool:
        return None
    liq = pool["liquidity"]
    base_amt = float(liq.get("base", 0))
    quote_amt = float(liq.get("quote", 0))
    if base_amt <= 0 or quote_amt <= 0:
        return None

    current_price = quote_amt / base_amt if sell_token_is_base else base_amt / quote_amt

    # Constant-product AMM math
    if sell_token_is_base:  # selling base for quote
        new_base = base_amt + amount_in
        new_quote = (base_amt * quote_amt) / new_base
        new_price = new_quote / new_base
    else:
        new_quote = quote_amt + amount_in
        new_base = (base_amt * quote_amt) / new_quote
        new_price = new_base / new_quote

    price_impact_pct = abs((new_price - current_price) / current_price) * 100
    return {
        "Current Price": round(current_price, 8),
        "New Price": round(new_price, 8),
        "Price Impact %": round(price_impact_pct, 3),
        "New Base Reserve": round(new_base, 4),
        "New Quote Reserve": round(new_quote, 4),
        "TVL": f"${float(liq.get('usd', 0)):,.0f}"
    }

# ====================== MAIN ARBITRAGE SCANNER (unchanged) ======================
if refresh_btn or "scan_results" not in st.session_state:
    # ← (exact same logic as previous version)
    ...

df = st.session_state.get("scan_results", pd.DataFrame())

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Best Arbitrage Routes",
    "📊 Pool Details",
    "📈 Charts",
    "🤖 AI Insights",
    "💧 Price Impact Simulator"
])

# (tab1 to tab4 remain exactly the same as previous version)

with tab5:
    st.subheader("💧 Liquidity Pool Price Impact Simulator")
    st.caption("See how a large trade (e.g. 10 million tokens) changes the price in every pool of the same pair")

    col1, col2 = st.columns(2)
    with col1:
        token_a = st.selectbox("Token A", options=sorted(list(set(t for d in TOKEN_ADDRESSES.values() for t in d.keys()))), index=0, key="sim_a")
    with col2:
        token_b = st.selectbox("Token B", options=sorted(list(set(t for d in TOKEN_ADDRESSES.values() for t in d.keys()))), index=1, key="sim_b")

    sim_amount = st.number_input("Trade Amount of Token A", value=10000000.0, min_value=1000.0, step=1000.0, key="sim_amount")
    direction = st.radio("Direction", ["Sell Token A (buy Token B)", "Buy Token A (sell Token B)"], horizontal=True, key="sim_dir")

    sim_chains = st.multiselect("Networks to simulate", options=list(CHAINS.keys()), default=["ethereum", "base", "arbitrum"], key="sim_chains")
    sim_btn = st.button("🚀 Simulate Price Impact Across All Pools", type="primary")

    if sim_btn:
        with st.spinner("Fetching pools and simulating large trade..."):
            sim_results = []
            for chain_name in sim_chains:
                chain = CHAINS[chain_name]
                addr_a = TOKEN_ADDRESSES.get(chain_name, {}).get(token_a)
                addr_b = TOKEN_ADDRESSES.get(chain_name, {}).get(token_b)
                if not addr_a or not addr_b:
                    continue

                pools = get_pair_pools(chain["dex_id"], addr_a, addr_b)
                sell_base = direction.startswith("Sell Token A")

                for pool in pools[:5]:  # limit to top 5 pools per chain
                    dex_name = pool.get("dexId", "Unknown").upper()
                    impact = simulate_price_impact(pool, sim_amount, sell_base)
                    if impact:
                        sim_results.append({
                            "Chain": chain["name"],
                            "DEX": dex_name,
                            "Pool TVL": impact["TVL"],
                            "Current Price": impact["Current Price"],
                            "New Price": impact["New Price"],
                            "Price Impact %": impact["Price Impact %"],
                            "New Reserves": f"{impact['New Base Reserve']} {token_a} / {impact['New Quote Reserve']} {token_b}",
                        })

            sim_df = pd.DataFrame(sim_results)
            if not sim_df.empty:
                st.dataframe(sim_df.sort_values("Price Impact %", ascending=False), use_container_width=True, height=600)
                st.success(f"✅ Simulated {sim_amount:,.0f} {token_a} trade across {len(sim_df)} pools")
               
                # Visual chart
                fig = px.bar(sim_df, x="DEX", y="Price Impact %", color="Chain",
                             title=f"Price Impact of {sim_amount:,.0f} {token_a} trade",
                             hover_data=["Current Price", "New Price", "Pool TVL"])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No matching pools found for this pair on the selected networks.")

st.caption("Real-time DexScreener + 1inch data • Full price impact balancer now included") 
