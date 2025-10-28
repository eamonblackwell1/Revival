# 🚀 Quick Start - Revival Scanner Web App

## ⚡ 3-Step Setup (2 minutes)

### Step 1: Start the Server
```bash
cd "/Users/eamonblackwell/Meme Coin Trading Bot/moon-dev-ai-agents"
./start_webapp.sh
```

### Step 2: Open Browser
Go to: **http://localhost:5000**

### Step 3: Run Your First Scan
Click the **"🔄 Scan Once"** button

---

## 🎨 What You'll See

### Dashboard Layout
```
┌─────────────────────────────────────────────────┐
│  🔄 Revival Scanner Dashboard                   │
│  Finding "second life" opportunities...          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ ▶️ Start Auto | ⏹️ Stop | 🔄 Scan Once | ↻ Refresh│
│                              Status: STOPPED     │
└─────────────────────────────────────────────────┘

┌──────────┬──────────┬──────────┬──────────┐
│ Total    │ Oppor-   │ High     │ Last     │
│ Scans    │ tunities │ Priority │ Scan     │
│   0      │    0     │    0     │  Never   │
└──────────┴──────────┴──────────┴──────────┘

┌───────────────────────────────────────────┐
│                                            │
│         🔍 No Results Yet                 │
│                                            │
│   Click "Scan Once" to start finding      │
│      revival opportunities!                │
│                                            │
└───────────────────────────────────────────┘
```

### After First Scan
```
┌─────────────────────────────────────┐
│ PEPE        [HIGH]        Score: 0.85│
│ Pepe Coin                            │
│ ┌──────┬──────┬──────┐              │
│ │Price │Smart │Volume│              │
│ │ 0.9  │ 0.8  │ 0.85 │              │
│ └──────┴──────┴──────┘              │
│ Age: 36.2h  | Liq: $25K             │
│ Vol: $50K   | Change: +45%          │
│ 📊 View on DexScreener →            │
└─────────────────────────────────────┘
```

---

## 🎯 Button Guide

### ▶️ Start Auto Scan
- Runs every 5 minutes automatically
- Good for: Continuous monitoring
- **When to use**: Leave it running while you work

### ⏹️ Stop Scanner
- Stops automatic scanning
- **When to use**: When you're done for the day

### 🔄 Scan Once
- Runs a single scan right now
- Takes 1-2 minutes
- Good for: Testing or manual checks
- **When to use**: First time, or checking specific times

### ↻ Refresh Results
- Updates the display with latest data
- **When to use**: To see if new results came in

---

## 📊 Understanding Token Cards

### Priority Levels

**🔴 HIGH PRIORITY (Score 0.8-1.0)**
- Red border
- **Action**: Research immediately
- **Meaning**: Strong revival pattern detected
- **Example**: Token dumped 70%, recovering with smart money

**🟡 MEDIUM PRIORITY (Score 0.6-0.8)**
- Orange border
- **Action**: Add to watchlist
- **Meaning**: Decent revival signals
- **Example**: Some recovery, moderate smart money

**🟢 LOW PRIORITY (Score 0.4-0.6)**
- Green border
- **Action**: Informational only
- **Meaning**: Weak revival signals
- **Example**: Minor recovery, low smart money

---

## 🔢 Reading the Scores

### Revival Score (Big Number)
```
Score: 0.85
```
- **0.8-1.0** = 🔥 Hot opportunity
- **0.6-0.8** = 👀 Worth watching
- **0.4-0.6** = 📝 Just FYI
- **<0.4** = ❌ Filtered out

### Sub-Scores
```
┌──────┬──────┬──────┐
│Price │Smart │Volume│
│ 0.9  │ 0.8  │ 0.85 │
└──────┴──────┴──────┘
```

**Price Score** = Pattern quality
- Did it dump enough?
- Is it recovering?
- Bullish chart pattern?

**Smart Money Score** = Wallet quality
- How many smart wallets?
- Are they profitable?
- Did they enter after dump?

**Volume Score** = Buying pressure
- Is volume increasing?
- More buys than sells?

---

## 📈 Key Metrics Explained

### Age
```
Age: 36.2h
```
- **24-36h** = Early revival (riskier)
- **36-48h** = Sweet spot (better data)
- **48-72h** = Late revival (safer)

### Liquidity
```
Liq: $25K
```
- **<$5K** = Too risky (filtered out)
- **$5-20K** = Minimum viable
- **$20-50K** = Good liquidity
- **>$50K** = Very liquid

### Volume 24h
```
Vol: $50K
```
- **<$5K** = Dead (filtered out)
- **$5-20K** = Low activity
- **$20-50K** = Moderate activity
- **>$50K** = High activity

### Price Change
```
Change: +45%
```
- Shows last 24h price movement
- Positive = Recovering
- Negative = Still dumping

---

## ⚠️ Important Notes

### What This Does
✅ Finds revival opportunities
✅ Filters out scams
✅ Shows you good entry points
✅ Tracks performance

### What This Doesn't Do
❌ Execute trades automatically
❌ Guarantee profits
❌ Predict the future
❌ Replace your judgment

---

## 🎓 Usage Tips

### For Beginners
1. Click "Scan Once" a few times
2. Watch what tokens show up
3. Check them on DexScreener
4. Learn the patterns
5. **Don't trade yet!** Paper trade first

### For Intermediate
1. Run "Start Auto Scan"
2. Check dashboard every few hours
3. Research HIGH priority tokens
4. Track results manually
5. Paper trade for 30 days

### For Advanced
1. Auto-scan continuously
2. Set up alerts (coming soon)
3. Integrate with paper trader
4. Refine filters based on results
5. Scale slowly with real money

---

## 🚨 Common Issues

### "No Results Yet"
- **Reason**: No tokens found in 24-72hr range
- **Solution**: Wait and scan later, or manually add tokens

### Scan takes long time
- **Normal**: 1-2 minutes is expected
- **Why**: Checking multiple APIs for each token

### Results disappear after refresh
- **Reason**: Scanner hasn't run yet
- **Solution**: Results persist once a scan completes

### Browser says "Can't connect"
- **Check**: Is server running? (terminal should show messages)
- **Solution**: Restart with `./start_webapp.sh`

---

## 📱 Mobile View

The dashboard works on mobile! Just visit from your phone's browser:
```
http://YOUR_COMPUTER_IP:5000
```

(Find your IP with `ifconfig` on Mac/Linux or `ipconfig` on Windows)

---

## 🎯 Next Steps

Once comfortable with the basics:

1. **Learn the Patterns**
   - Which tokens actually revived?
   - What scores worked best?
   - How long did revivals last?

2. **Test Different Settings**
   - Try different minimum scores
   - Experiment with age ranges
   - Track what works for you

3. **Paper Trade**
   - Track hypothetical trades
   - Record entry/exit prices
   - Calculate P&L manually

4. **Start Small**
   - Only after 30 days paper trading
   - Max 0.5% position sizes
   - Max 5 positions total

---

## 💡 Pro Tips

🎯 **Best Scan Times**
- Morning (9-11 AM EST)
- Evening (5-7 PM EST)
- Late night (11 PM - 1 AM EST)

🔍 **What to Look For**
- High score + low age = Early opportunity
- High score + high age = Safer entry
- All sub-scores >0.7 = Strong signal

⚠️ **Red Flags**
- Score >0.8 but no smart wallets = Suspicious
- High volume but low liquidity = Risky
- Age <24h or >72h = Outside sweet spot

---

**Ready to start?**

Run: `./start_webapp.sh`

Then open: **http://localhost:5000**

Click: **"🔄 Scan Once"**

Happy hunting! 🚀