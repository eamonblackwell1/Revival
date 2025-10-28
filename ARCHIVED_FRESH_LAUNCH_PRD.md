# ⚠️ ARCHIVED - DO NOT USE

**This document describes the "fresh launch sniper" approach (0-12 hour tokens) which has been replaced by the Revival Scanner strategy (24-72 hour tokens).**

**See [REVIVAL_SCANNER_PRD.md](REVIVAL_SCANNER_PRD.md) for the current, active approach.**

Archived for reference only. Do not implement this approach - it competes with sniper bots, requires expensive APIs, and has lower win rates than the Revival Scanner.

---

# Meme Coin Trading Bot - Product Requirements Document (PRD)

## Executive Summary

This PRD outlines the requirements for building an algorithmic trading bot for Solana meme coins. The system must filter 30,000+ daily token launches to identify 10-50 tradeable opportunities while avoiding the 95%+ that are scams, rug pulls, or immediate failures.

**Key Learning from HMM Bitcoin Trader**: Our previous Bitcoin trading system taught us that transaction costs compound catastrophically with over-trading. The best performing system made only 403 trades with 48-hour minimum holds, achieving +36% returns. The worst system made 13,361 trades and lost 100% due to fees alone.

## Problem Statement

### Current Challenges
1. **Volume**: 30,000+ new tokens launch daily on Solana
2. **Scam Rate**: 95%+ are scams, honeypots, or rug pulls
3. **Speed Required**: Winners are decided in minutes, not hours
4. **Social-Driven**: Price driven by Twitter/TikTok hype, not fundamentals
5. **High Failure Rate**: Even legitimate projects often fail within 48 hours

### Why HMM Approach Failed for Crypto
- Hidden Markov Models require stable statistical patterns
- Crypto markets (especially memes) are regime-less chaos
- Social sentiment changes faster than any model can adapt
- Each meme coin is unique - patterns don't transfer

### Target User
- Crypto traders comfortable with high risk
- Technical users who can run Python scripts
- Risk capital of $1,000-$5,000
- Understanding that this is closer to gambling than investing

## Success Criteria

### Primary Metrics
| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| False Negative Rate | <5% | <10% |
| Rug Pull Avoidance | >99% | >95% |
| Processing Time | <5 min | <10 min |
| Win Rate | 30% | 20% |
| Average Winner | 5x | 3x |
| Average Loser | -40% | -50% |
| Monthly Return | +50% | Break-even |

### Secondary Metrics
- Daily tokens filtered: From 30,000 to 10-50
- Smart money accuracy: 60%+ of copied wallets profitable
- Social signal correlation: 70%+ accuracy on viral predictions
- Transaction costs: <10% of profits
- Maximum drawdown: <70%

### Risk Metrics (Must Monitor)
- Largest single loss: Must not exceed 5% of portfolio
- Consecutive losses: System stops after 10 straight losses
- Daily loss limit: -10% triggers shutdown
- Exposure limit: Never >20% in meme coins total

## Functional Requirements

### 1. Data Ingestion Layer

**Required Data Sources:**
- **DexScreener API** (PRIMARY)
  - Real-time token launches
  - Liquidity and volume data
  - Transaction counts
  - Price feeds
  - Free tier sufficient

- **GoPlus Security API** (CRITICAL)
  - Honeypot detection
  - Contract security analysis
  - Mintable function detection
  - Historical rug pull database
  - Free tier available

- **GMGN API** (ESSENTIAL)
  - Smart money wallet tracking
  - Copy trading capabilities
  - Holder distribution analysis
  - Free, no API key required

- **Social APIs** (IMPORTANT)
  - Twitter/X API or alternatives
  - Telegram monitoring
  - Discord webhooks (optional)
  - TikTok scraping (optional)

**Performance Requirements:**
- Ingest 30,000+ tokens per day
- Process each token in <100ms
- Parallel processing required
- Cache results for 1 hour
- Retry failed API calls 3x

### 2. Filtering Pipeline

**Stage 1: Technical Filters (30,000 → 1,000)**
- Liquidity ≥ $10,000 USD
- Volume (24h) ≥ $5,000 USD
- Age ≤ 12 hours
- Transactions ≥ 60 in first hour
- Security score ≥ 60/100
- Not honeypot (verified 2+ sources)
- Not mintable
- Contract verified
- **Target Processing Time**: <1 minute

**Stage 2: Holder Analysis (1,000 → 200)**
- Developer holdings ≤ 15%
- Top 10 holders ≤ 30% combined
- Sniper bots ≤ 5%
- Minimum 50 holders
- LP tokens >50% burned
- No suspicious wallet clusters
- **Target Processing Time**: 2-3 minutes

**Stage 3: Social Validation (200 → 60)**
- Twitter mentions ≥ 10 in last hour
- Telegram group ≥ 100 members
- Cross-platform presence (2+ platforms)
- Positive sentiment score >0.6
- Influencer mentions ≥ 1
- No pump group coordination detected
- **Target Processing Time**: 3-5 minutes

**Stage 4: Smart Money (60 → 20)**
- Smart wallets holding ≥ 3
- Average wallet win rate ≥ 60%
- No wash trading patterns
- Natural accumulation visible
- Increasing unique holders
- **Target Processing Time**: 5 minutes

**Stage 5: Final Scoring (20 → 10)**
- Composite score calculation
- Risk-adjusted ranking
- Manual review triggers
- **Target Processing Time**: 2 minutes

### 3. Trading Execution

**Order Management:**
- Jupiter aggregator integration for best price
- Slippage tolerance: 5% default, 10% max
- Priority fees: 0.001-0.006 SOL
- MEV protection via Jito bundles
- Automatic retry on failure (3x max)

**Position Sizing:**
- Maximum 2% portfolio per trade
- Scale based on confidence score
- Never exceed 10 concurrent positions
- Reserve 20% portfolio for gas/fees

**Risk Management:**
- Stop loss: -20% mandatory
- Take profit ladder:
  - 25% at 2x
  - 25% at 5x
  - 25% at 10x
  - 25% at 20x
- Time stop: Exit after 48 hours
- Trailing stop after 3x gain

### 4. Monitoring & Alerts

**Real-time Monitoring:**
- Position P&L updates every 10 seconds
- Wallet balance tracking
- Gas fee tracking
- API rate limit monitoring
- Error rate tracking

**Alert Conditions:**
- New position opened
- Stop loss triggered
- Take profit hit
- System error
- Unusual activity detected
- Daily loss limit approached

**Notification Channels:**
- Telegram bot (primary)
- Discord webhook
- Email (for critical errors)
- Log files (all events)

### 5. Backtesting & Analysis

**Limited Backtesting Capability:**
- Historical filter validation only
- Cannot backtest social signals
- Paper trading mode required
- Track hypothetical P&L
- Measure filter accuracy

**Performance Analytics:**
- Win/loss ratio
- Average return per trade
- Sharpe ratio (expect negative)
- Maximum drawdown
- Transaction cost impact
- Filter effectiveness metrics

## Non-Functional Requirements

### Performance
- Process 30,000 tokens in <10 minutes
- Execute trades in <5 seconds
- API response time <500ms
- 99% uptime during market hours
- Support 100+ concurrent API requests

### Security
- Private keys encrypted at rest
- Environment variables for secrets
- No keys in code repository
- Wallet isolation (separate trading/holding)
- IP whitelist for API access
- 2FA on exchange accounts

### Scalability
- Handle 100,000+ tokens/day if needed
- Support multiple chains (future)
- Distributed processing capable
- Database for historical data
- Queue system for order processing

### Reliability
- Automatic restart on crash
- Graceful degradation on API failure
- Circuit breakers for bad states
- Health checks every minute
- Automated backup of positions

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Data Ingestion                       │
│  DexScreener ←→ GoPlus ←→ GMGN ←→ Social APIs          │
└────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  Filtering Pipeline                      │
│  Stage 1 → Stage 2 → Stage 3 �� Stage 4 → Stage 5       │
│  (1000)    (200)     (60)      (20)      (10)          │
└────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  Trading Engine                          │
│  Risk Manager ←→ Order Builder ←→ Jupiter/Raydium      │
└────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Monitoring & Analytics                      │
│  Position Tracker ←→ P&L Monitor ←→ Alert System       │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core:**
- Language: Python 3.10+
- Async: asyncio for parallel processing
- Web3: solana-py for blockchain interaction

**APIs:**
- DexScreener: REST API
- GoPlus: REST API with authentication
- GMGN: REST API (no auth)
- Jupiter: REST + WebSocket

**Infrastructure:**
- VPS: Low latency to Solana validators
- Database: PostgreSQL for historical data
- Cache: Redis for API responses
- Queue: RabbitMQ for order processing

**Monitoring:**
- Grafana for metrics
- Telegram bot for alerts
- CloudWatch/Datadog for system health

### Data Models

```python
@dataclass
class Token:
    address: str
    symbol: str
    name: str
    liquidity_usd: float
    volume_24h: float
    holder_count: int
    security_score: int
    social_score: float
    smart_money_count: int
    final_score: float
    timestamp: datetime

@dataclass
class Position:
    token_address: str
    entry_price: float
    amount_sol: float
    entry_time: datetime
    stop_loss: float
    take_profit_levels: List[float]
    current_value: float
    pnl_percent: float
    status: str  # 'open', 'closed', 'stopped'

@dataclass
class FilterResult:
    stage: int
    tokens_in: int
    tokens_out: int
    processing_time: float
    failed_reasons: Dict[str, int]
```

## Implementation Phases

### Phase 1: MVP (Week 1)
**Goal**: Basic filtering pipeline

**Deliverables:**
- Stage 1 filter implementation
- DexScreener integration
- GoPlus security checks
- Console output of filtered tokens
- No trading execution

**Success Criteria:**
- Processes 30,000 tokens in <10 minutes
- Reduces to <1,000 tokens
- 0% honeypots pass filter

### Phase 2: Enhanced Filtering (Week 2)
**Goal**: Complete filtering pipeline

**Deliverables:**
- Stage 2-4 filters implemented
- GMGN smart money integration
- Basic social signal checking
- Scoring algorithm
- Paper trading mode

**Success Criteria:**
- Reduces 30,000 to <50 tokens
- Paper trading tracks P&L
- Smart money correlation >60%

### Phase 3: Trading Integration (Week 3)
**Goal**: Live trading capability

**Deliverables:**
- Solana wallet integration
- Jupiter aggregator connection
- Order execution engine
- Risk management system
- Position tracking

**Success Criteria:**
- Executes trades in <5 seconds
- Stop losses work reliably
- Accurate P&L tracking

### Phase 4: Production Ready (Week 4)
**Goal**: Stable production system

**Deliverables:**
- Error handling and recovery
- Monitoring and alerting
- Performance optimization
- Documentation complete
- Deployment scripts

**Success Criteria:**
- 99% uptime
- <1% error rate
- Processes 30,000 tokens in <5 minutes

### Phase 5: Optimization (Month 2+)
**Goal**: Improve performance

**Deliverables:**
- Machine learning scoring
- Advanced social analysis
- Multi-chain support
- Copy trading automation
- Strategy backtesting

**Success Criteria:**
- Win rate >30%
- Monthly return >0%
- Reduced false positives

## Risk Analysis

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits | High | High | Multiple API keys, caching, queuing |
| Honeypot detection fails | Medium | Critical | Multiple detection services, manual verification |
| Slippage on trades | High | Medium | Limit orders, smaller position sizes |
| Wallet compromise | Low | Critical | Hardware wallet, key rotation |
| System crash during trade | Medium | High | Automatic position tracking, restart procedures |

### Market Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Rug pull | High | High | Multiple security checks, fast exits |
| Wash trading | High | Medium | Volume analysis, wallet clustering |
| Market manipulation | High | Medium | Avoid thin liquidity tokens |
| Regulatory changes | Medium | Critical | Stay informed, geographic flexibility |
| Bull market ends | Medium | Critical | Reduce position sizes, increase filters |

### Operational Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Over-trading | High | High | Hard limits, minimum hold times |
| FOMO decisions | High | Medium | Systematic rules, no manual override |
| Inadequate testing | Medium | High | Mandatory paper trading period |
| Poor risk management | Medium | Critical | Automated stops, position limits |
| Burnout from 24/7 monitoring | High | Medium | Automation, alerts only for critical events |

## Cost Analysis

### Development Costs
- Developer time: 4 weeks full-time
- API costs: $200-500/month
- Infrastructure: $100-200/month
- Testing capital: $500-1000 (expect to lose)

### Operational Costs

**Minimal Setup ($0-50/month):**
- Free API tiers only
- Local machine execution
- Manual monitoring
- Basic features only

**Professional Setup ($500-1500/month):**
- Paid APIs (Twitter, Birdeye, etc.)
- Cloud infrastructure
- Advanced monitoring
- Multiple data sources

**Enterprise Setup ($5000+/month):**
- Premium APIs
- Dedicated servers
- 24/7 monitoring team
- Custom development

### Transaction Costs
- Network fees: ~0.001 SOL per transaction
- DEX fees: 0.1-0.3% per trade
- Slippage: 1-5% average
- MEV: Variable, can be significant

### Expected ROI
**Realistic Scenarios:**
- **Bear Case**: -50% monthly (high failure rate)
- **Base Case**: +0-20% monthly (breaking even)
- **Bull Case**: +50-100% monthly (catching trends)
- **Unicorn Case**: +200%+ monthly (very rare)

## Success Metrics & KPIs

### Daily Metrics
- Tokens scanned
- Tokens passed each filter stage
- Trades executed
- Win/loss ratio
- Daily P&L

### Weekly Metrics
- Total return
- Sharpe ratio
- Maximum drawdown
- Transaction costs
- Filter accuracy

### Monthly Metrics
- Overall ROI
- System uptime
- Error rates
- API costs
- Strategy effectiveness

## Legal & Compliance

### Disclaimers Required
- Not financial advice
- High risk of total loss
- Gambling, not investing
- No guaranteed returns
- Tax obligations

### Regulatory Considerations
- Varies by jurisdiction
- May be considered securities trading
- Tax reporting required
- AML/KYC for large volumes

## Appendix A: Lessons from HMM Bitcoin Trader

### What Failed
1. **Over-optimization killed returns**: Walk-forward optimization took hours and performed worse than simple strategies
2. **Transaction costs ignored**: Initial models didn't account for 0.1% fees, leading to -100% returns
3. **Regime detection too slow**: HMM identified regimes after they changed, not before
4. **Conservative in bull market**: System stayed in cash during +319% Bitcoin rally

### What Succeeded
1. **Simple momentum strategy**: Best performer with +36% returns
2. **Minimum hold times**: 48-hour holds prevented over-trading
3. **Trade limits**: Capping at 20 trades/day improved performance
4. **Risk management**: Stop losses prevented catastrophic losses

### Key Insights for Meme Coins
- Meme coins are 100x more volatile than Bitcoin
- Social signals matter more than any technical indicator
- Speed of execution is critical (seconds, not hours)
- Position sizing must be much smaller (2% vs 10%)
- Expect 70%+ of trades to lose money
- Winners must be 5-10x to compensate for losers

## Appendix B: Recommended Reading Order

1. Read this PRD first (you are here)
2. Read MEME_COIN_BOT.md for implementation details
3. Review CLAUDE.md for HMM system learnings
4. Check config.yaml for risk parameters
5. Study main_momentum.py for best-performing strategy

## Appendix C: Quick Start Commands

```bash
# 1. Clone and setup
git clone [your-repo]
cd meme-coin-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and wallet

# 3. Run paper trading first
python main.py --paper-trading --verbose

# 4. After 1 week successful paper trading
python main.py --capital 100 --max-positions 5

# 5. Monitor performance
python analytics.py --period 7d

# 6. Emergency stop
python emergency_stop.py --sell-all
```

## Final Warnings

1. **This is extremely high risk** - Total loss is likely
2. **95% of meme coins go to zero** - This is not an exaggeration
3. **You are competing with bots** - Milliseconds matter
4. **Scammers are sophisticated** - They know how to pass filters
5. **Taxes are complex** - Every trade is a taxable event
6. **Mental health impact** - 24/7 markets are exhausting
7. **Addiction potential** - Set hard limits and stick to them
8. **Not sustainable long-term** - Meme coins are a bubble

## Contact & Support

For questions about this PRD:
- Review MEME_COIN_BOT.md for technical details
- Check implementation code for specific examples
- Test in paper trading mode first
- Start with minimal capital

Remember: If you're not comfortable losing 100% of your investment, do not trade meme coins.