import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Crypto Arbitrage Scanner",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

st.title("🚀 Crypto Arbitrage Scanner")
st.markdown("""
**Real-time best arbitrage & optimal swap routes** 
Tokens: **WETH • ETH • BNB • WBTC • LINK • USDC • USDT • AAVE • SUSHI • CAKE** 
DEXes: **Uniswap V2/V3 • Curve V2/V3 • Sushiswap V2/V3 • PancakeSwap V2/V3 • Balancer V2/V3**
""")

# ====================== CHAIN & TOKEN CONFIG ======================
CHAINS = {
    "ethereum": {"dex_id": "ethereum", "oneinch_id": 1, "name": "Ethereum"},
    "base": {"dex_id": "base", "oneinch_id": 8453, "name": "Base"},
    "arbitrum": {"dex_id": "arbitrum", "oneinch_id": 42161, "name": "Arbitrum"},
    "polygon": {"dex_id": "polygon", "oneinch_id": 137, "name": "Polygon"},
    "bsc": {"dex_id": "bsc", "oneinch_id": 56, "name": "BSC"},
    "optimism": {"dex_id": "optimism", "oneinch_id": 10, "name": "Optimism"},
    "avalanche": {"dex_id": "avalanche", "oneinch_id": 43114, "name": "Avalanche"},
}

TOKEN_ADDRESSES = {
    "ethereum": {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "ETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "SUSHI": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
    },
    "base": {
        "WETH": "0x4200000000000000000000000000000000000006",
        "ETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa05d6F",
    },
    "arbitrum": {
        "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "ETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "WBTC": "0x2f2a2543B76A4166549F7Aab2e75Bef0AefC5B0f",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    },
    "polygon": {
        "WETH": "0x7ceB23FD6bC0adD59E62ac25578270cFf1b9f619",
        "WBTC": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "LINK": "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
    },
    "bsc": {
        "BNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "WETH": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "SUSHI": "0x947950BbC0fC0e0c0fD9C9bE8b7e0C9c7b0B0",
    },
    "optimism": {
        "WETH": "0x4200000000000000000000000000000000000006",
        "ETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8eD8d9",
    },
    "avalanche": {
        "WETH": "0x49D5c2A4F0B3eA5d2aA0F9dA8c7A8A3d0d9c3d0",
        "USDC": "0xB97EF7Ef7133f4E4A9b9f0cC3c6c0dE8e3c1c0",
        "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
    },
}

SUPPORTED_DEX_IDS = ["uniswap", "uniswap-v2", "uniswap-v3", "sushi", "sushiswap",
                     "pancake", "pancakeswap", "curve", "curve-v2", "balancer", "balancer-v2"]

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🔍 Scanner Input")
    from_token = st.selectbox("From Token", options=sorted(list(set(t for chain_tokens in TOKEN_ADDRESSES.values() for t in chain_tokens.keys()))), index=0)
    amount = st.number_input("Amount to Swap", value=10.0, min_value=0.001, step=0.01)
    selected_chains = st.multiselect("Networks to Scan", options=list(CHAINS.keys()), default=["ethereum", "base", "arbitrum", "bsc"])
    target_token = st.selectbox("Target Token (max extraction)", ["USDC", "USDT"], index=0)
    slippage_tolerance = st.slider("Max Slippage (%)", 0.1, 5.0, 1.0, 0.1)
   
    st.divider()
    openai_key = st.text_input("OpenAI API Key (optional – AI insights)", type="password")
    refresh_btn = st.button("🔄 Run Full Arbitrage Scan", type="primary", use_container_width=True)

# ====================== HELPERS ======================
@st.cache_data(ttl=25)
def fetch_dexscreener_pools(chain_id: str, token_addr: str):
    url = f"https://api.dexscreener.com/token-pairs/v1/{chain_id}/{token_addr}"
    try:
        r = requests.get(url, timeout=12)
        return r.json() if r.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=25)
def fetch_1inch_quote(oneinch_chain_id: int, src: str, dst: str, amount_wei: int, slippage: float):
    if not oneinch_chain_id:
        return None
    url = f"https://api.1inch.io/swap/v6.1/{oneinch_chain_id}/quote"
    params = {"src": src, "dst": dst, "amount": str(amount_wei), "slippage": int(slippage * 100)}
    try:
        r = requests.get(url, params=params, timeout=12)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def is_supported_dex(dex_id: str) -> bool:
    if not dex_id:
        return False
    d = dex_id.lower()
    return any(k in d for k in SUPPORTED_DEX_IDS)

def calculate_slippage_and_output(pool: dict, amount_in: float):
    if not pool or "liquidity" not in pool:
        return 0.0, 0.0, "N/A"
    liq = pool["liquidity"]
    base = float(liq.get("base", 0))
    quote = float(liq.get("quote", 0))
    if base <= 0 or quote <= 0:
        return 0.0, 0.0, "N/A"
    amount_out = (quote * amount_in) / (base + amount_in)
    slippage_pct = (amount_in / (base + amount_in)) * 100
    fee_pct = 0.3
    amount_out_after_fee = amount_out * (1 - fee_pct / 100)
    tvl = f"${float(liq.get('usd', 0)):,.0f}"
    return round(amount_out_after_fee, 6), round(slippage_pct, 3), tvl

# ====================== MAIN SCANNER LOGIC ======================
if refresh_btn or "scan_results" not in st.session_state:
    with st.spinner("Scanning liquidity pools & 1inch routes across all networks..."):
        results = []
       
        for chain_name in selected_chains:
            chain = CHAINS[chain_name]
            src_addr = TOKEN_ADDRESSES.get(chain_name, {}).get(from_token)
            if not src_addr:
                continue
               
            pools = fetch_dexscreener_pools(chain["dex_id"], src_addr)
            dst_addr = TOKEN_ADDRESSES.get(chain_name, {}).get(target_token)
            if not dst_addr:
                continue
               
            amount_wei = int(amount * 10**18)  # 1inch handles decimal conversion
            quote = fetch_1inch_quote(chain["oneinch_id"], src_addr, dst_addr, amount_wei, slippage_tolerance)
           
            # Filter to only your requested DEX families
            supported_pools = [p for p in pools if is_supported_dex(p.get("dexId", ""))]
            top_pools = sorted(supported_pools, key=lambda x: float(x.get("liquidity", {}).get("usd", 0)), reverse=True)[:3]
           
            for pool in top_pools:
                dex_name = pool.get("dexId", "Unknown").upper()
                out_after_fee, slip_pct, tvl_str = calculate_slippage_and_output(pool, amount)
               
                oneinch_out = None
                oneinch_route = "—"
                if quote:
                    dst_decimals = 6 if target_token in ["USDC", "USDT"] else 18
                    oneinch_out = float(quote.get("dstAmount", 0)) / (10 ** dst_decimals)
                    try:
                        oneinch_route = " → ".join([step["name"] for step in quote.get("protocols", [[]])[0]])[:60]
                    except:
                        pass
               
                net_value = oneinch_out or out_after_fee
                score = net_value * (1 - slip_pct / 100) if net_value else 0
               
                results.append({
                    "Chain": chain["name"],
                    "DEX": dex_name,
                    "Pool TVL": tvl_str,
                    "Depth": f"{float(pool['liquidity'].get('base', 0)):.4f} {from_token}",
                    "Expected Output": f"{net_value:.4f} {target_token}" if net_value else "—",
                    "Slippage": f"{slip_pct:.2f}%",
                    "Fees": "0.3% + gas",
                    "1inch Best Route": oneinch_route,
                    "Score": round(score, 4),
                })
       
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("Score", ascending=False)
       
        st.session_state["scan_results"] = df
        st.session_state["scan_time"] = datetime.now()

df = st.session_state.get("scan_results", pd.DataFrame())

# ====================== RESULTS TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Best Arbitrage Routes", "📊 Pool Details", "📈 Charts", "🤖 AI Insights"])

with tab1:
    st.subheader(f"Best Routes — {amount} {from_token} → max {target_token}")
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=520)
        st.success(f"✅ Scan completed at {st.session_state['scan_time'].strftime('%H:%M:%S UTC')}")
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"arbitrage_scan_{from_token}.csv", type="secondary")
    else:
        st.warning("No supported pools found on selected networks. Try different token/chain.")

with tab2:
    st.subheader("Supported DEX Pool Breakdown")
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['Chain']} — {row['DEX']} — TVL {row['Pool TVL']}"):
                st.metric("Expected Output", row["Expected Output"])
                st.metric("Slippage", row["Slippage"])
                st.metric("Liquidity Depth", row["Depth"])

with tab3:
    st.subheader("Value Extraction by Chain")
    if not df.empty:
        fig = px.bar(df, x="Chain", y="Expected Output", color="Slippage",
                     hover_data=["DEX", "Pool TVL"],
                     title="Maximum Value Extraction (higher = better)")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("🤖 AI Arbitrage Expert")
    if openai_key and not df.empty:
        import openai
        openai.api_key = openai_key
        prompt = f"""You are a professional DeFi arbitrage scanner. Input: {amount} {from_token} → {target_token}
Data:\n{df.to_string()}\n
Give the SINGLE best route recommendation with reasoning (liquidity, slippage, fees, route). Use clear bullet points."""
        with st.spinner("AI analyzing routes..."):
            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"AI error: {e}")
    else:
        st.info("Enter OpenAI key in sidebar for AI-powered route explanation.")

st.caption("Real-time data from DexScreener + 1inch • Only requested tokens & DEXes • Built for Streamlit Cloud") 

