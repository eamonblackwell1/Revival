# Revival Scanner Dashboard - User Guide

## Getting Started

### 1. Start the Dashboard
```bash
cd "/Users/eamonblackwell/Meme Coin Trading Bot/moon-dev-ai-agents"
./start_webapp.sh
```

### 2. Open Your Browser
Navigate to: **http://localhost:8080**

---

## Dashboard Layout

### Header Section
- **Title**: "Revival Scanner Dashboard"
- **Subtitle**: Finding "second life" opportunities in 24-48hr old meme coins

### Control Panel
Three main buttons:
- **▶️ Start Auto Scan** - Run scans automatically every 2 hours
- **⏹️ Stop Scanner** - Stop automatic scanning
- **🔄 Scan Once** - Run a single scan manually
- **↻ Refresh Results** - Reload results without scanning
- **Status Badge**: Shows RUNNING (green) or STOPPED (gray)

### Statistics Cards (4 cards)
1. **Total Scans**: Number of scans completed
2. **Opportunities Found**: Tokens with revival_score ≥ 0.4
3. **High Priority**: Tokens with revival_score ≥ 0.8
4. **Last Scan**: Timestamp of most recent scan

---

## NEW: Scan Progress Section

### Visual Progress Bar
When a scan is running, you'll see:
- **Progress Bar**: 0% → 100% as scan progresses
- **Current Percentage**: Displayed inside the bar

### 5-Phase Indicators
Visual status for each phase:

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ 1. Discovery│ 2. Pre-Filter│ 3. Age Check│  4. Market  │  5. Social  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

**Colors**:
- **Gray**: Not started yet
- **Purple gradient with glow**: Currently running
- **Green**: Completed successfully

### Status Message
Below the progress bar:
- "Fetching tokens from BirdEye API..."
- "Filtering for memecoins with adequate liquidity..."
- "Checking token ages via Helius blockchain..."
- etc.

---

## NEW: Live Activity Feed

### What You'll See
A scrollable log showing real-time events:

```
┌─────────────────────────────────────────────────────────┐
│ Live Activity                              [Clear]      │
├─────────────────────────────────────────────────────────┤
│ 14:23:45  Starting manual scan                          │
│ 14:23:46  [Phase 1/5] Fetching tokens from BirdEye...  │
│ 14:23:47  Phase 1 complete: Collected 550 unique...    │
│ 14:23:48  [Phase 2/5] Filtering for memecoins...       │
│ 14:23:48  ⏭️ USDC - Not a memecoin (DeFi/stable)       │
│ 14:23:48  ⏭️ stSOL - Not a memecoin (DeFi/stable)      │
│ 14:23:50  Phase 2 complete: 150 memecoins passed...    │
│ ...                                                      │
└─────────────────────────────────────────────────────────┘
```

### Message Colors
- **Green background**: Success messages (phase completions)
- **Red background**: Errors
- **Yellow background**: Warnings
- **White background**: Info messages

### Auto-Updates
- Refreshes **every 2 seconds** automatically
- Auto-scrolls to show latest activity
- Shows last **50 messages**
- Click **Clear** button to reset

---

## Token Results Display

Each token card now shows:

### Header
- **Token Symbol** (large, bold)
- **Token Name** (smaller, gray)
- **Priority Badge**: HIGH (red) / MEDIUM (orange) / LOW (green)
- **Revival Score**: 0.00 - 1.00 (purple gradient box)

### NEW: Contract Address Section
```
┌───────────────────────────────────────────┐
│ Contract: EKpQ...pxT8     [📋 Copy]      │
└───────────────────────────────────────────┘
```
- **Shortened address**: First 4 + last 4 characters
- **Copy button**: Click to copy full address to clipboard
- **Click anywhere on address**: Also copies

### Sub-Scores (3 metrics)
- **Price**: Price pattern score (0.00 - 1.00)
- **Smart $**: Smart money activity score
- **Volume**: Volume pattern score

### Metrics Grid (4 boxes)
- **Age**: Hours since token creation (e.g., "32.5h")
- **Liquidity**: USD liquidity (e.g., "$85K")
- **Volume 24h**: 24-hour trading volume (e.g., "$120K")
- **Price Change**: 24h price change % (e.g., "+45.2%")

### NEW: Social Links & Actions
```
[📊 DexScreener]  [🐦 Twitter]  [📱 Telegram]  [🌐 Website]
```
- **DexScreener**: Always present - view price chart
- **Twitter**: If available - view community
- **Telegram**: If available - join chat
- **Website**: If available - project info

---

## What to Watch During a Scan

### 1. Phase Progress (30 seconds)
Watch the purple highlight move across phases:
```
✅ 1. Discovery → 🔵 2. Pre-Filter → ⬜ 3. Age Check → ⬜ 4. Market → ⬜ 5. Social
```

### 2. Activity Feed Messages
Look for these key messages:

**Phase 1 - Discovery**:
```
[Phase 1/5] Fetching tokens from BirdEye API...
📄 Page 1/2 (sort=v24hChangePercent, offset=0)
✅ Retrieved 200 tokens (sort=v24hChangePercent)
Phase 1 complete: Collected 550 unique tokens
```

**Phase 2 - Pre-Filter**:
```
[Phase 2/5] Filtering for memecoins with adequate liquidity...
⏭️ USDC - Not a memecoin (DeFi/stable/LST)
⏭️ BONK - Market cap too high: $25,000,000
✅ PEPE - Passed ($120K liq, $5M MC)
Phase 2 complete: 150 memecoins passed pre-filter
```

**Phase 3 - Age Verification**:
```
[Phase 3/5] Checking token ages via Helius blockchain...
⏰ Age Filter: Minimum 24h (no maximum)
Phase 3 complete: 45 tokens are 24h+ old
```

**Phase 4 - Market Filters**:
```
[Phase 4/5] Applying strict liquidity and volume filters...
💰 Strict Filtering: Liquidity >$50,000, 1h Volume >$15,000
Phase 4 complete: 12 tokens passed strict filters
```

**Phase 5 - Social Enrichment**:
```
[Phase 5/5] Enriching with social sentiment data...
📱 Enriching with social sentiment data...
Phase 5 complete: 12 tokens enriched with social data
```

### 3. Pipeline Funnel
Watch the funnel in action:
```
600 tokens (BirdEye)
  ↓
150 memecoins (Pre-filter)
  ↓
45 tokens (Age 24h+)
  ↓
12 tokens (Strict filters)
  ↓
3 opportunities (Revival patterns)
```

---

## Understanding Results

### Priority Levels

**HIGH PRIORITY (Red border)**
- Revival score ≥ 0.8
- Strong revival pattern detected
- Multiple positive signals
- **Action**: Research immediately

**MEDIUM PRIORITY (Orange border)**
- Revival score 0.6 - 0.79
- Moderate revival signals
- Some risk factors present
- **Action**: Monitor closely

**LOW PRIORITY (Green border)**
- Revival score 0.4 - 0.59
- Weak revival signals
- Higher risk
- **Action**: Watch list only

### How to Use Contract Addresses

1. **Copy the address**:
   - Click the "📋 Copy" button
   - Or click anywhere on the shortened address

2. **Research the token**:
   - Paste into DexScreener search
   - Check on Solscan.io
   - Verify on BirdEye
   - Look up on GMGN.ai

3. **Trading**:
   - Use in Jupiter swap
   - Check liquidity on Raydium
   - Verify contract on Solana Explorer

---

## Troubleshooting

### No Activity Updates
- Check that the scan is actually running (progress bar moving)
- Refresh the page manually
- Check browser console for errors (F12)

### Progress Stuck
- Wait 60 seconds - some phases take time
- Check activity feed for error messages
- Look for rate limit warnings

### No Results Found
Common reasons (check activity feed):
- All tokens too young (<24h)
- All tokens failed liquidity filter
- No memecoins found (all stablecoins/DeFi)
- All tokens failed security filter

### Error Messages
Look in activity feed for:
- `❌ ERROR:` messages (red background)
- `⚠️` warning symbols (yellow background)
- Check if API keys are set correctly

---

## Best Practices

### 1. Monitor First Scan
- Watch the full scan process
- Understand the funnel (600 → 3)
- Note which filters remove most tokens

### 2. Check Activity Feed Regularly
- Errors appear in real-time
- See why specific tokens were rejected
- Identify API issues early

### 3. Use Contract Addresses
- Always verify tokens independently
- Don't trust the scanner blindly
- Do your own research (DYOR)

### 4. Watch for Patterns
- Which phases take longest?
- Where do most tokens get filtered?
- Are you getting any results?

### 5. API Rate Limits
If you see:
```
⚠️ Rate limit hit (HTTP 429) - waiting 60 seconds...
```
- This is normal for free tier APIs
- Scanner will retry automatically
- Don't restart the scan

---

## Quick Reference

### Scan Duration
- **Typical**: 2-4 minutes for full scan
- **Phase 1**: ~30 seconds (BirdEye fetches)
- **Phase 2**: ~10 seconds (filtering)
- **Phase 3**: ~20-40 seconds (Helius blockchain checks)
- **Phase 4**: ~10-20 seconds (DexScreener checks)
- **Phase 5**: ~10 seconds (social enrichment)

### Update Frequencies
- **Activity Feed**: Every 2 seconds
- **Status/Progress**: Every 1 second during scan
- **Results**: On demand (manual refresh)

### Data Retention
- **Activity Log**: Last 500 messages
- **Error Log**: Last 200 errors
- **Results**: Last scan only (auto-saved to CSV)

---

## Example Workflow

1. **Start Scan**: Click "🔄 Scan Once"
2. **Watch Progress**: See phase indicators update
3. **Monitor Activity**: Read messages in real-time
4. **Wait**: ~3 minutes for completion
5. **Review Results**: Scroll to token cards
6. **Copy Addresses**: Click 📋 Copy buttons
7. **Research**: Open DexScreener, check Twitter
8. **Decide**: Make trading decisions based on research

---

## Need Help?

If something isn't working:
1. Check the activity feed for error messages
2. Verify API keys are set in `.env`
3. Ensure BirdEye and Helius APIs are configured
4. Check that you're not hitting rate limits
5. Review the console logs (terminal where webapp is running)

**Enjoy your enhanced dashboard! 🚀**
