# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an experimental AI trading system that orchestrates 48+ specialized AI agents to analyze markets, execute strategies, and manage risk across cryptocurrency markets (primarily Solana). The project uses a modular agent architecture with unified LLM provider abstraction supporting Claude, GPT-4, DeepSeek, Groq, Gemini, and local Ollama models.

## ⭐ Primary Focus: Revival Scanner

**The main active project is the Revival Scanner** - a specialized system that identifies "second life" meme coin opportunities 24+ hours after launch using a 3-API hybrid architecture.

### Why Revival Trading vs Fresh Launches:
- **Lower Competition**: Not competing with sniper bots for 0-12 hour tokens
- **Better Risk/Reward**: Tokens already survived initial rug pull window
- **FREE APIs**: Works within free tier limits (BirdEye, Helius, DexScreener, GMGN)
- **Higher Win Rate**: 30-40% vs 10-20% for fresh launches
- **Sustainable**: Pattern-based approach, not speed-based
- **No Maximum Age**: Revivals can happen at any time (removed 72h limit)

### Revival Scanner Architecture (7-Phase Pipeline)

**Phase 1: BirdEye Native Meme Token Discovery**
- Uses `/defi/v3/token/meme/list` endpoint - guaranteed pure memecoins
- Pass 1: Native Meme List (200 tokens) - pump.fun, Moonshot, Raydium launches
- Pass 2: Price Change Sort (200 tokens) - potential revivals
- Bonus: Trending List (20 tokens) - hottest tokens
- Result: ~400 unique tokens, 100% memecoins (no keyword filtering needed)

**Phase 2: Simplified Pre-Filter**
- **Liquidity Filter**: Minimum $20K (quick filter before expensive blockchain calls)
- **Market Cap Filter**: Maximum $20M (room for growth)
- No memecoin detection needed (Phase 1 guarantees memecoins)
- Result: ~150-200 tokens ready for age check

**Phase 3: Helius Blockchain Age Verification**
- Minimum age: 24 hours (avoid fresh launch chaos)
- **Maximum age: 180 days (6 months)** - prevents analyzing years-old tokens
- Uses `src/helius_utils.py` with RPC calls
- Result: Tokens in the 24h-6month "revival window"

**Phase 4: Strict Market Filters (DexScreener)**
- Liquidity > $50K strict threshold
- 1-hour volume > $15K (sustained activity)
- Uses `src/dexscreener_utils.py`

**Phase 5: DexScreener Social Enrichment**
- Extracts boosts (trending indicators)
- Social links (Twitter, Telegram, Discord)
- Buy/sell ratios and community engagement metrics

**Phase 6: Security Filter**
- Stage 1 security filter removes scams
- Holder distribution analysis (rejects if top 10 holders own >70%)
- Uses BirdEye `/defi/v3/token/holder` endpoint

**Phase 7: Revival Pattern Detection**
- Price pattern analysis: dump → floor → recovery (OHLCV from BirdEye)
- **Smart money analysis via BirdEye Top Traders** (replaced GMGN)
- Whale wallet detection (>$100K holdings)
- Weighted scoring: 50% price pattern, 30% smart money, 20% volume

### Key Components:
- **Core Agents**: `revival_detector_agent.py`, `meme_scanner_orchestrator.py`, `stage1_security_filter.py`, `meme_notifier_agent.py`
- **Utility Modules**: `src/helius_utils.py`, `src/dexscreener_utils.py`
- **Web Dashboard**: `web_app.py` at http://localhost:8080 (port 8080, not 5000)
- **Documentation**: See `REVIVAL_SCANNER_PRD.md` for complete strategy
- **Quick Start**: Run `./start_webapp.sh` to launch the web dashboard

### Running Revival Scanner:
```bash
# Start web dashboard (auto-scans every 2 hours)
./start_webapp.sh

# Run single scan manually (for testing)
PYTHONPATH=/Users/eamonblackwell/Meme\ Coin\ Trading\ Bot/moon-dev-ai-agents python3 src/agents/meme_scanner_orchestrator.py --once
```

### API Requirements:
- **BirdEye API**: Native meme list, OHLCV, token overview, top traders, holder distribution (set `BIRDEYE_API_KEY` in .env)
  - All endpoints fully integrated with BirdEye Standard tier
  - Token Overview: `/defi/token_overview` - comprehensive metrics in one call
  - Top Traders: `/defi/v2/tokens/top_traders` - smart money analysis
  - Holder Distribution: `/defi/v3/token/holder` - concentration risk
  - Meme List: `/defi/v3/token/meme/list` - guaranteed pure memecoins
- **Helius RPC**: Blockchain age verification (set `HELIUS_RPC_ENDPOINT` in .env)
- **DexScreener**: Social sentiment, volume (FREE, no key needed, fallback only)

### Recent Scanner Upgrades (Oct 2025 - BirdEye Integration):
- **Native Meme Discovery**: Switched to BirdEye meme list API - eliminates 15-20% miss rate
- **6-Month Age Limit**: Added `MAX_AGE_HOURS = 4320` - prevents analyzing years-old tokens
- **Smart Money via BirdEye**: Replaced GMGN with BirdEye Top Traders API
- **Holder Distribution**: Added concentration risk analysis (rejects >70% top 10)
- **Token Overview API**: Consolidated multiple endpoints into single call (30% fewer API calls)
- **Result**: 100% pure memecoins, better data quality, more efficient pipeline

### Legacy Agents (Not Actively Developed):
- `sniper_agent.py` - Fresh launch sniper (0-12 hours) - **Replaced by Revival Scanner**
- `solana_agent.py` - Coordinates sniper/tx agents - **Replaced by Revival Scanner**
- Old PRDs archived as `ARCHIVED_FRESH_LAUNCH_PRD.md` and `ARCHIVED_FRESH_LAUNCH_IMPLEMENTATION.md`

**When working on meme coin trading features, default to the Revival Scanner BirdEye-first approach unless specifically asked to work on legacy sniper agents.**

### Important BirdEye Integration Notes:
- **Always use BirdEye APIs first** for Revival Scanner features (token overview, top traders, holders)
- **DexScreener is fallback only** - use when BirdEye data unavailable
- **Token age** comes from BirdEye Token Overview `creationTime` field (Unix timestamp)
- **Smart money** uses Top Traders endpoint, not GMGN (GMGN removed)
- **Holder safety** checks via holder distribution endpoint (reject if top 10 >70%)
- **Native meme list** eliminates need for keyword filtering - all tokens are guaranteed memecoins

## Key Development Commands

### Environment Setup
```bash
# Use existing conda environment (DO NOT create new virtual environments)
conda activate tflow

# Install/update dependencies
pip install -r requirements.txt

# IMPORTANT: Update requirements.txt every time you add a new package
pip freeze > requirements.txt
```

### Running the System
```bash
# Run main orchestrator (controls multiple agents)
python src/main.py

# Run individual agents standalone
python src/agents/trading_agent.py
python src/agents/risk_agent.py
python src/agents/rbi_agent.py
python src/agents/chat_agent.py
# ... any agent in src/agents/ can run independently
```

### Backtesting
```bash
# Use backtesting.py library with pandas_ta or talib for indicators
# Sample OHLCV data available at:
# /Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv
```

## Architecture Overview

### Core Structure
```
src/
├── agents/              # 48+ specialized AI agents (each <800 lines)
├── models/              # LLM provider abstraction (ModelFactory pattern)
├── strategies/          # User-defined trading strategies
├── scripts/             # Standalone utility scripts
├── data/                # Agent outputs, memory, analysis results
├── config.py            # Global configuration (positions, risk limits, API settings)
├── main.py              # Main orchestrator for multi-agent loop
├── nice_funcs.py        # ~1,200 lines of shared trading utilities
├── nice_funcs_hl.py     # Hyperliquid-specific utilities
└── ezbot.py             # Legacy trading controller
```

### Agent Ecosystem

**Revival Scanner (Active)**: `revival_detector_agent`, `meme_scanner_orchestrator`, `stage1_security_filter`, `meme_notifier_agent`
**Trading Agents**: `trading_agent`, `strategy_agent`, `risk_agent`, `copybot_agent`
**Market Analysis**: `sentiment_agent`, `whale_agent`, `funding_agent`, `liquidation_agent`, `chartanalysis_agent`
**Content Creation**: `chat_agent`, `clips_agent`, `tweet_agent`, `video_agent`, `phone_agent`
**Strategy Development**: `rbi_agent` (Research-Based Inference - codes backtests from videos/PDFs), `research_agent`
**Other Specialized**: `tx_agent`, `million_agent`, `tiktok_agent`, `compliance_agent`
**Legacy/Archived**: `sniper_agent`, `solana_agent` (replaced by Revival Scanner)

Each agent can run independently or as part of the main orchestrator loop.

### LLM Integration (Model Factory)

Located at `src/models/model_factory.py` and `src/models/README.md`

**Unified Interface**: All agents use `ModelFactory.create_model()` for consistent LLM access
**Supported Providers**: Anthropic Claude (default), OpenAI, DeepSeek, Groq, Google Gemini, Ollama (local)
**Key Pattern**:
```python
from src.models.model_factory import ModelFactory

model = ModelFactory.create_model('anthropic')  # or 'openai', 'deepseek', 'groq', etc.
response = model.generate_response(system_prompt, user_content, temperature, max_tokens)
```

### Configuration Management

**Primary Config**: `src/config.py`
- Trading settings: `MONITORED_TOKENS`, `EXCLUDED_TOKENS`, position sizing (`usd_size`, `max_usd_order_size`)
- Risk management: `CASH_PERCENTAGE`, `MAX_POSITION_PERCENTAGE`, `MAX_LOSS_USD`, `MAX_GAIN_USD`, `MINIMUM_BALANCE_USD`
- Agent behavior: `SLEEP_BETWEEN_RUNS_MINUTES`, `ACTIVE_AGENTS` dict in `main.py`
- AI settings: `AI_MODEL`, `AI_MAX_TOKENS`, `AI_TEMPERATURE`
- Revival Scanner settings:
  - `MIN_LIQUIDITY_PREFILTER = 20000` - Initial liquidity filter
  - `MIN_LIQUIDITY_STRICT = 50000` - Strict liquidity after age check
  - `MIN_VOLUME_1H = 15000` - Minimum 1-hour volume
  - `MIN_AGE_HOURS = 24` - Minimum token age (24 hours)
  - `MAX_AGE_HOURS = 4320` - Maximum token age (180 days / 6 months)
  - `MAX_MARKET_CAP = 20_000_000` - Maximum market cap ($20M)

**Environment Variables**: `.env` (see `.env_example`)
- **Revival Scanner APIs**: `BIRDEYE_API_KEY` (required), `HELIUS_RPC_ENDPOINT` (required for age verification)
- Other Trading APIs: `MOONDEV_API_KEY`, `COINGECKO_API_KEY`
- AI Services: `ANTHROPIC_KEY`, `OPENAI_KEY`, `DEEPSEEK_KEY`, `GROQ_API_KEY`, `GEMINI_KEY`
- Blockchain: `SOLANA_PRIVATE_KEY`, `HYPER_LIQUID_ETH_PRIVATE_KEY`, `RPC_ENDPOINT`

### Shared Utilities

**`src/nice_funcs.py`** (~1,200 lines): Core trading functions
- Data: `token_overview()`, `token_price()`, `get_position()`, `get_data()` (OHLCV)
- Trading: `market_buy()`, `market_sell()`, `chunk_kill()`, `open_position()`
- Analysis: Technical indicators, PnL calculations, rug pull detection

**`src/helius_utils.py`**: Helius RPC blockchain utilities (Revival Scanner)
- `get_token_creation_timestamp()`: Query blockchain for token mint creation time
- `get_token_age_hours()`: Get accurate token age in hours
- `batch_get_token_ages()`: Process multiple tokens with rate limiting (10 req/sec)

**`src/dexscreener_utils.py`**: DexScreener social sentiment utilities (Revival Scanner)
- `get_token_social_data()`: Extract boosts, Twitter, Telegram, Discord, volume
- `batch_enrich_tokens()`: Process multiple tokens with rate limiting (5 req/sec)
- `get_social_score()`: Calculate social sentiment score (0-1)

**`src/agents/api.py`**: `MoonDevAPI` class for custom Moon Dev API endpoints
- `get_liquidation_data()`, `get_funding_data()`, `get_oi_data()`, `get_copybot_follow_list()`

### Data Flow Pattern

```
Config/Input → Agent Init → API Data Fetch → Data Parsing →
LLM Analysis (via ModelFactory) → Decision Output →
Result Storage (CSV/JSON in src/data/) → Optional Trade Execution
```

## Development Rules

### File Management
- **Keep files under 800 lines** - if longer, split into new files and update README
- **DO NOT move files without asking** - you can create new files but no moving
- **NEVER create new virtual environments** - use existing `conda activate tflow`
- **Update requirements.txt** after adding any new package

### Backtesting
- Use `backtesting.py` library (NOT their built-in indicators)
- Use `pandas_ta` or `talib` for technical indicators instead
- Sample data available at `/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv`

### Code Style
- **No fake/synthetic data** - always use real data or fail the script
- **Minimal error handling** - user wants to see errors, not over-engineered try/except blocks
- **No API key exposure** - never show keys from `.env` in output

### Agent Development Pattern

When creating new agents:
1. Inherit from base patterns in existing agents
2. Use `ModelFactory` for LLM access
3. Store outputs in `src/data/[agent_name]/`
4. Make agent independently executable (standalone script)
5. Add configuration to `config.py` if needed
6. Follow naming: `[purpose]_agent.py`

### Testing Strategies

Place strategy definitions in `src/strategies/` folder:
```python
class YourStrategy(BaseStrategy):
    name = "strategy_name"
    description = "what it does"

    def generate_signals(self, token_address, market_data):
        return {
            "action": "BUY"|"SELL"|"NOTHING",
            "confidence": 0-100,
            "reasoning": "explanation"
        }
```

## Important Context

### Risk-First Philosophy
- Risk Agent runs first in main loop before any trading decisions
- Configurable circuit breakers (`MAX_LOSS_USD`, `MINIMUM_BALANCE_USD`)
- AI confirmation for position-closing decisions (configurable via `USE_AI_CONFIRMATION`)

### Data Sources

**Revival Scanner (Primary - All BirdEye):**
1. **BirdEye API** - Primary data source for all revival scanner features:
   - Native meme token list (`/defi/v3/token/meme/list`)
   - Token overview with comprehensive metrics (`/defi/token_overview`)
   - OHLCV price data (`/defi/ohlcv`) via `get_data()` in `nice_funcs.py`
   - Top traders for smart money analysis (`/defi/v2/tokens/top_traders`)
   - Holder distribution for concentration risk (`/defi/v3/token/holder`)
2. **Helius RPC** - Blockchain queries for accurate token creation timestamps
3. **DexScreener API** - Social sentiment (FREE, fallback only if BirdEye unavailable)

**Other Trading Agents:**
5. **Moon Dev API** - Custom signals (liquidations, funding rates, OI, copybot data)
6. **CoinGecko API** - 15,000+ token metadata, market caps, sentiment

### Autonomous Execution
- Main loop runs every 15 minutes by default (`SLEEP_BETWEEN_RUNS_MINUTES`)
- Agents handle errors gracefully and continue execution
- Keyboard interrupt for graceful shutdown
- All agents log to console with color-coded output (termcolor)

### AI-Driven Strategy Generation (RBI Agent)
1. User provides: YouTube video URL / PDF / trading idea text
2. DeepSeek-R1 analyzes and extracts strategy logic
3. Generates backtesting.py compatible code
4. Executes backtest and returns performance metrics
5. Cost: ~$0.027 per backtest execution (~6 minutes)

## Common Patterns

### Adding New Agent
1. Create `src/agents/your_agent.py`
2. Implement standalone execution logic
3. Add to `ACTIVE_AGENTS` in `main.py` if needed for orchestration
4. Use `ModelFactory` for LLM calls
5. Store results in `src/data/your_agent/`

### Switching AI Models
Edit `config.py`:
```python
AI_MODEL = "claude-3-haiku-20240307"  # Fast, cheap
# AI_MODEL = "claude-3-sonnet-20240229"  # Balanced
# AI_MODEL = "claude-3-opus-20240229"  # Most powerful
```

Or use different models per agent via ModelFactory:
```python
model = ModelFactory.create_model('deepseek')  # Reasoning tasks
model = ModelFactory.create_model('groq')      # Fast inference
```

### Reading Market Data
```python
from src.nice_funcs import token_overview, get_ohlcv_data, token_price

# Get comprehensive token data
overview = token_overview(token_address)

# Get price history
ohlcv = get_ohlcv_data(token_address, timeframe='1H', days_back=3)

# Get current price
price = token_price(token_address)
```

## Project Philosophy

This is an **experimental, educational project** demonstrating AI agent patterns through algorithmic trading:
- No guarantees of profitability (substantial risk of loss)
- Open source and free for learning
- YouTube-driven development with weekly updates
- Community-supported via Discord
- No token associated with project (avoid scams)

The goal is to democratize AI agent development and show practical multi-agent orchestration patterns that can be applied beyond trading.
