# Revival Scanner - Product Requirements Document (PRD)
## "Second Life" Token Trading Strategy for Solana Meme Coins

### Version 1.0 - October 2024

---

## Executive Summary

This PRD defines requirements for the **Revival Scanner**, a specialized trading system that identifies and trades Solana meme coins experiencing "second life" patterns 24-72 hours after launch. Unlike traditional meme coin scanners that compete with sniper bots for fresh launches, the Revival Scanner targets tokens that have already dumped and are showing signs of genuine recovery.

### Key Differentiators
- **Timing Window**: 24-72 hours old (vs 0-12 hours for snipers)
- **Competition**: Low (most bots focus on fresh launches)
- **Risk Profile**: Medium (vs extreme for fresh tokens)
- **Win Rate**: 30-40% (vs 10-20% for fresh launches)
- **Data Requirements**: Minimal (works on FREE API tiers)

### Investment Thesis
"Buy fear, sell greed - but only after the initial rug pull window has passed."

---

## Problem Statement

### The Meme Coin Lifecycle Reality

```
Hour 0-6:   🚀 Launch pump (bots & insiders)
Hour 6-12:  📉 Initial dump (paperhands exit)
Hour 12-24: 😴 Consolidation (finding floor)
Hour 24-48: 🤔 Decision point (death or revival)
Hour 48-72: 📈 Revival pump (if community forms)
Hour 72+:   ❓ Unknown (moon or zero)
```

### Current Market Inefficiencies

1. **Sniper Bot Dominance** (Hour 0-12)
   - Millisecond execution required
   - $1000s in MEV bribes
   - 90% controlled by 10 wallets
   - Retail cannot compete

2. **Information Overload** (30,000+ daily launches)
   - 95% are scams/rugs
   - 4% die naturally
   - 1% have potential
   - Finding the 1% is nearly impossible

3. **Missed Opportunities** (Hour 24-72)
   - Most scanners ignore "old" tokens
   - Smart money quietly accumulates
   - Community begins forming
   - Pattern recognition possible

### Our Solution: The Revival Scanner

Focus exclusively on tokens showing "second life" patterns:
- Already survived initial rug window
- Community proven resilient
- Smart money entering
- Technical patterns forming
- Less competition for entry

---

## Market Opportunity Analysis

### Total Addressable Market (TAM)
- **Daily**: ~30,000 new Solana tokens
- **Survive 24h**: ~1,500 tokens (5%)
- **Show revival patterns**: ~150 tokens (0.5%)
- **Tradeable opportunities**: ~15 tokens (0.05%)

### Competitive Landscape

| Strategy | Competition | Win Rate | Avg Return | Risk Level |
|----------|------------|----------|------------|------------|
| Fresh Sniping (0-1h) | Extreme | 5-10% | 10-100x | Extreme |
| Early Entry (1-12h) | High | 10-20% | 5-50x | Very High |
| **Revival (24-72h)** | **Low** | **30-40%** | **3-10x** | **Medium** |
| Late Entry (72h+) | Medium | 20-30% | 2-5x | Low-Medium |

### Why Revival Trading Works

1. **Natural Selection**: Weak tokens already dead
2. **Community Test**: Survived first dump
3. **Smart Money Signal**: Professionals entering
4. **Technical Setup**: Clear patterns visible
5. **Reduced Fraud**: Scammers already exited

---

## Success Criteria

### Primary Metrics (MVP)

| Metric | Target | Minimum | Measurement |
|--------|--------|---------|-------------|
| Tokens Scanned Daily | 500 | 100 | Count |
| Revival Patterns Found | 10-15 | 5 | Count |
| False Positive Rate | <20% | <40% | % incorrect signals |
| Processing Time | <30 min | <60 min | Per scan cycle |
| API Cost | $0 | <$50/mo | Monthly spend |

### Trading Performance (Production)

| Metric | Target | Minimum | Notes |
|--------|--------|---------|-------|
| Win Rate | 40% | 30% | Profitable trades / Total |
| Risk/Reward | 1:3 | 1:2 | Average loss vs gain |
| Average Winner | 5x | 3x | Profitable trade return |
| Average Loser | -30% | -40% | Losing trade return |
| Monthly ROI | +50% | +20% | After all costs |
| Max Drawdown | 30% | 50% | Peak to trough |

### Risk Management

| Metric | Limit | Action |
|--------|-------|--------|
| Single Position Size | 5% max | Hard limit |
| Total Meme Exposure | 25% max | Stop new positions |
| Consecutive Losses | 5 trades | Pause system |
| Daily Loss | -10% | Stop trading |
| Correlation Risk | 0.7 max | Diversify tokens |

---

## Functional Requirements

### 1. Age-Based Token Discovery

**Requirements:**
- Identify tokens 24-72 hours old
- Track from DexScreener pairs endpoint
- Cache token age to reduce API calls
- Filter tokens outside age range

**Data Sources:**
- DexScreener `/latest/dex/pairs/solana` (FREE)
- Cache duration: 6 hours (age changes slowly)

**Performance:**
- Process 1000 tokens in <60 seconds
- Age calculation accuracy: ±1 hour

### 2. Revival Pattern Detection

**The Revival Pattern Formula:**

```python
Revival Score = (
    0.30 × Price_Recovery_Score +    # From floor to current
    0.25 × Volume_Resurgence_Score +  # Increasing activity
    0.20 × Smart_Money_Score +        # Quality holders entering
    0.15 × Higher_Lows_Score +        # Technical pattern
    0.10 × Community_Growth_Score     # Social metrics
)
```

**Price Recovery Indicators:**
- Initial pump high (H1)
- Dump low (L1)
- Current price (C)
- Recovery Ratio = (C - L1) / (H1 - L1)
- Target: Recovery Ratio > 0.3

**Volume Resurgence Indicators:**
- Volume Hour 12-24 (V1)
- Volume Hour 36-48 (V2)
- Growth Rate = V2 / V1
- Target: Growth Rate > 1.5

**Technical Patterns:**
- Higher lows in last 12 hours
- Breakout from consolidation
- Volume-supported moves
- Decreasing sell pressure

### 3. Smart Money Tracking

**GMGN Integration (FREE):**
- Track top 20 holders
- Identify "Smart Money" tagged wallets
- Monitor accumulation patterns
- Check wallet win rates

**Scoring Criteria:**
- Smart wallets holding: +1 point per wallet
- Average wallet win rate > 60%: +2 points
- New smart entries last 6h: +3 points
- No smart exits last 6h: +2 points

### 4. Security Filtering

**Multi-Layer Security (24h+ advantage):**

Layer 1 - Basic Security:
- Liquidity > $5,000
- Not honeypot (DexScreener flag)
- Contract verified
- No mint function

Layer 2 - Holder Analysis:
- Top 10 holders < 40% (more distributed after 24h)
- Developer wallet < 10%
- No suspicious clusters
- Minimum 100 holders

Layer 3 - Behavioral Analysis:
- No wash trading patterns
- Natural buy/sell ratio
- Organic growth curve
- No pump group signals

### 5. Data Pipeline Architecture

```
┌─────────────────────────────────────────┐
│         Token Discovery (FREE)           │
│  DexScreener: Age 24-72h filtering      │
└─────────────┬───────────────────────────┘
              │ ~500 tokens
              ▼
┌─────────────────────────────────────────┐
│      Quick Filter (FREE)                 │
│  Liquidity, Volume, Holder checks       │
└─────────────┬───────────────────────────┘
              │ ~100 tokens
              ▼
┌─────────────────────────────────────────┐
│    Pattern Detection (MIXED)             │
│  DexScreener: Price changes (FREE)      │
│  BirdEye: OHLCV for top 10 only         │
└─────────────┬───────────────────────────┘
              │ ~20 tokens
              ▼
┌─────────────────────────────────────────┐
│     Smart Money Check (FREE)             │
│  GMGN: Holder quality analysis          │
└─────────────┬───────────────────────────┘
              │ ~10 tokens
              ▼
┌─────────────────────────────────────────┐
│      Final Scoring & Ranking             │
│  Composite score, risk adjustment       │
└─────────────┬───────────────────────────┘
              │
              ▼
         [5-10 Revival Candidates]
```

### 6. Web Dashboard Requirements

**Real-Time Monitoring:**
- Current scan status
- Tokens in pipeline
- Revival candidates found
- API usage tracking
- Performance metrics

**Token Cards Display:**
- Revival score (0-1)
- Age in hours
- Price recovery %
- Volume trend
- Smart money count
- Risk level (Low/Med/High)
- DexScreener link

**Controls:**
- Start/Stop scanning
- Adjust scan frequency
- Set minimum scores
- Export results
- Paper trade tracking

---

## Non-Functional Requirements

### Performance Requirements

| Component | Requirement | Target |
|-----------|------------|--------|
| Scan Frequency | Configurable | 5-60 minutes |
| Processing Speed | Full pipeline | <5 min per cycle |
| API Rate Limits | Respect all | 100% compliance |
| Caching | Reduce API calls | 50% reduction |
| Uptime | System availability | 95% |
| Error Recovery | Auto-restart | Within 1 minute |

### Scalability

**Current State (MVP):**
- 500 tokens/day
- 5-minute processing
- Single thread
- Local deployment

**Future State (Scale):**
- 5,000 tokens/day
- 1-minute processing
- Multi-threaded
- Cloud deployment
- Multiple chains

### Security Requirements

- No private keys in code
- Environment variables for APIs
- Read-only token analysis
- No automated trading (MVP)
- Secure credential storage
- API key rotation support

---

## Technical Architecture

### Technology Stack

**Backend:**
- Language: Python 3.9+
- Framework: Flask (web server)
- Processing: asyncio for parallel API calls
- Caching: In-memory dict (MVP), Redis (production)

**Frontend:**
- HTML5 + Tailwind CSS
- Vanilla JavaScript
- Real-time updates via polling
- Mobile responsive

**APIs (All with FREE tiers):**
- DexScreener: No auth required
- GMGN: No auth required
- BirdEye: API key required (30k calls/mo free)
- Jupiter: Optional for prices

**Deployment:**
- Local: Python + SQLite
- Production: VPS + PostgreSQL
- Monitoring: Built-in dashboard
- Alerts: Console + optional Telegram

### Data Models

```python
@dataclass
class RevivalCandidate:
    # Identity
    token_address: str
    symbol: str
    name: str
    age_hours: float

    # Market Data
    price_usd: float
    liquidity_usd: float
    volume_24h: float
    holder_count: int

    # Revival Metrics
    revival_score: float  # 0-1
    price_recovery: float  # % from floor
    volume_growth: float   # vs yesterday
    smart_money_count: int
    higher_lows: bool

    # Risk Assessment
    security_score: float
    risk_level: str  # 'Low', 'Medium', 'High'

    # Metadata
    dexscreener_url: str
    scan_timestamp: datetime

@dataclass
class ScanResult:
    scan_id: str
    timestamp: datetime
    tokens_scanned: int
    tokens_filtered: Dict[str, int]  # stage -> count
    candidates_found: List[RevivalCandidate]
    processing_time: float
    api_calls_used: Dict[str, int]  # api -> count
```

---

## Implementation Roadmap

### Phase 1: MVP Foundation (Week 1)
**Goal:** Basic revival detection working locally

**Deliverables:**
- ✅ Age-based token discovery
- ✅ DexScreener integration
- ✅ Basic pattern detection
- ✅ Console output
- ✅ No trading, just identification

**Success Metrics:**
- Find 5+ revival patterns daily
- <$0 API costs
- <5 minute scan time

### Phase 2: Smart Filtering (Week 2)
**Goal:** Reduce false positives

**Deliverables:**
- ✅ Security filtering
- ✅ Smart money detection (GMGN)
- ✅ Composite scoring algorithm
- ✅ Web dashboard (basic)
- ✅ CSV export functionality

**Success Metrics:**
- False positive rate <30%
- Smart money correlation >60%
- Dashboard operational

### Phase 3: Web Interface (Week 3)
**Goal:** User-friendly monitoring

**Deliverables:**
- ✅ Full web dashboard
- ✅ Real-time updates
- ✅ Historical tracking
- ✅ Performance metrics
- Configuration UI

**Success Metrics:**
- Responsive on mobile
- <1s page load
- Auto-refresh working

### Phase 4: Optimization (Week 4)
**Goal:** Production ready

**Deliverables:**
- API call optimization
- Caching layer
- Error handling
- Alert system
- Documentation

**Success Metrics:**
- 50% reduction in API calls
- 99% uptime
- Full documentation

### Phase 5: Trading Integration (Month 2)
**Goal:** Execute trades on signals

**Deliverables:**
- Paper trading mode
- Wallet integration
- Jupiter aggregator
- Risk management
- P&L tracking

**Success Metrics:**
- Paper profit >20%
- <5s execution time
- Risk limits enforced

---

## Cost Analysis

### API Costs (Monthly)

| Service | Free Tier | Starter | Pro | Our Usage |
|---------|-----------|---------|-----|-----------|
| DexScreener | Unlimited | N/A | N/A | FREE ✅ |
| GMGN | Unlimited | N/A | N/A | FREE ✅ |
| BirdEye | 30k calls | $99 | $250 | FREE (MVP) ✅ |
| Jupiter | Unlimited | N/A | N/A | FREE ✅ |
| **Total** | **$0** | **$99** | **$250** | **$0-99** |

### Infrastructure Costs

**Local Deployment (MVP):**
- Cost: $0
- Requirements: Python, 2GB RAM
- Suitable for: Testing, <1000 tokens/day

**VPS Deployment (Production):**
- Cost: $20-50/month
- Provider: DigitalOcean, Linode
- Specs: 4GB RAM, 2 CPU
- Suitable for: 5000+ tokens/day

### Expected ROI

**Conservative Scenario:**
- Win Rate: 30%
- Avg Winner: +300%
- Avg Loser: -40%
- Monthly Return: +20%
- Payback: 5 months

**Realistic Scenario:**
- Win Rate: 35%
- Avg Winner: +400%
- Avg Loser: -35%
- Monthly Return: +40%
- Payback: 2.5 months

**Optimistic Scenario:**
- Win Rate: 40%
- Avg Winner: +500%
- Avg Loser: -30%
- Monthly Return: +80%
- Payback: 1.2 months

---

## Risk Analysis

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limits | High | Low | Caching, rotation |
| Pattern detection fails | High | Medium | Multiple indicators |
| False positives | Medium | Medium | Strict filtering |
| System downtime | Medium | Low | Auto-restart |

### Market Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Revival patterns stop working | High | Low | Continuous optimization |
| Market downturn | High | Medium | Reduced position sizes |
| Liquidity issues | Medium | Low | Minimum liquidity filter |
| Competition increases | Medium | Medium | Unique indicators |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Overconfidence | High | High | Strict risk limits |
| Over-optimization | Medium | Medium | Out-of-sample testing |
| Alert fatigue | Low | High | Adjustable thresholds |

---

## Success Metrics & KPIs

### Daily Metrics
- Tokens scanned
- Revival patterns found
- API calls used
- Processing time
- Error rate

### Weekly Metrics
- Pattern accuracy
- False positive rate
- Smart money correlation
- System uptime
- Cost per signal

### Monthly Metrics
- Total opportunities found
- Hypothetical P&L
- API costs
- Best performing patterns
- System improvements

---

## Competitive Advantages

### Why We Win

1. **Timing Arbitrage**
   - Others fight over 0-12h tokens
   - We calmly analyze 24-72h patterns
   - Less competition = better entries

2. **Risk Reduction**
   - Survived initial rug window
   - Community already tested
   - Patterns more reliable

3. **Cost Efficiency**
   - Works on FREE API tiers
   - No MEV bribes needed
   - Lower gas competition

4. **Data Advantage**
   - 24h of price history available
   - Smart money movements visible
   - Social signals clearer

5. **Sustainable Strategy**
   - Not dependent on being first
   - Reproducible patterns
   - Lower stress operation

---

## Appendices

### Appendix A: Revival Pattern Examples

**Classic Revival Pattern:**
```
Hour 0-6:   Price 10x (launch pump)
Hour 6-12:  Price 0.3x (panic dump)
Hour 12-24: Price 0.3-0.4x (consolidation)
Hour 24-36: Price 0.5x (early revival)
Hour 36-48: Price 0.8x (momentum builds)
Hour 48-72: Price 2-5x (revival pump)
```

**Smart Money Revival:**
```
- 3+ known profitable wallets enter
- Each buys $1000-10000
- Entries spread over 6-12 hours
- No immediate sells
- Social media activity follows
```

### Appendix B: API Optimization Strategies

1. **Cascade Filtering:**
   - Use FREE APIs first
   - Only call paid APIs for final candidates
   - Cache everything possible

2. **Batch Processing:**
   - Group API calls
   - Process during low-traffic hours
   - Parallel processing where allowed

3. **Smart Caching:**
   - Token age: 6-hour cache
   - Holder data: 1-hour cache
   - Price data: 5-minute cache

### Appendix C: Quick Start Guide

```bash
# 1. Clone repository
git clone [repository]
cd moon-dev-ai-agents

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env_example .env
# Add your BirdEye API key (optional for MVP)

# 4. Run scanner
python src/agents/meme_scanner_orchestrator.py

# 5. View dashboard
open http://localhost:5000

# 6. Monitor results
tail -f src/data/meme_scanner/scan_results_*.csv
```

### Appendix D: Lessons Learned

**From Fresh Token Trading:**
- Speed is everything (milliseconds matter)
- Bots always win
- 95% rug in first hour
- Unsustainable stress

**From Revival Trading:**
- Patience pays off
- Patterns are predictable
- Smart money leaves traces
- Sustainable approach

---

## Conclusion

The Revival Scanner represents a paradigm shift in meme coin trading - from competing on speed to competing on pattern recognition. By focusing on the 24-72 hour "second life" window, we avoid the chaos of fresh launches while capturing the upside of genuine revivals.

This approach is:
- **Technically feasible** with FREE APIs
- **Financially viable** with 20-50% monthly returns
- **Operationally sustainable** without 24/7 stress
- **Competitively advantaged** in an uncrowded niche

The MVP can be built in 2 weeks with $0 in API costs, providing rapid validation of the revival pattern thesis.

---

*Remember: This is high-risk trading. Never invest more than you can afford to lose completely.*

**Document Version:** 1.0
**Last Updated:** October 2024
**Next Review:** After MVP completion
**Contact:** Moon Dev AI Agents Team