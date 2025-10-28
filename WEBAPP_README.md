# 🌐 Revival Scanner Web Dashboard

Beautiful web interface for Moon Dev's Meme Coin Revival Detection System

## 🎯 What Is This?

A modern, easy-to-use dashboard that lets you:
- **Scan** for revival opportunities in meme coins
- **Monitor** 24-48 hour old tokens showing "second life" patterns
- **Get Alerts** when high-confidence opportunities are found
- **Track Performance** with historical data

## 🚀 Quick Start

### Option 1: Using the Startup Script (Easiest)
```bash
./start_webapp.sh
```

Then open your browser to: **http://localhost:5000**

### Option 2: Manual Start
```bash
# Install dependencies
pip3 install flask flask-cors requests --user

# Start the server
python3 src/web_app.py
```

## 📊 Features

### Dashboard Overview
- **Real-time Stats**: Total scans, opportunities found, high priority alerts
- **Visual Token Cards**: Beautiful cards showing revival scores and metrics
- **Priority System**: Color-coded by urgency (High/Medium/Low)
- **One-Click Actions**: Start/stop scanning, refresh results

### Scanner Controls
1. **Start Auto Scan** - Runs every 5 minutes automatically
2. **Stop Scanner** - Stops automatic scanning
3. **Scan Once** - Run a single scan manually
4. **Refresh Results** - Update the display with latest data

### Token Cards Show:
- **Revival Score** (0-1 scale)
  - 🔴 **0.8-1.0** = HIGH PRIORITY (act fast!)
  - 🟡 **0.6-0.8** = MEDIUM (worth watching)
  - 🟢 **0.4-0.6** = LOW (informational)

- **Sub-Scores**:
  - Price Pattern Score
  - Smart Money Score
  - Volume Score

- **Key Metrics**:
  - Token Age (hours)
  - Liquidity (USD)
  - 24h Volume
  - Price Change %

- **Quick Actions**:
  - Direct link to DexScreener

## 🎨 Interface Walkthrough

### Header
```
🔄 Revival Scanner Dashboard
Finding "second life" opportunities in 24-48hr old meme coins
```

### Control Panel
- Green "Start Auto Scan" button (enables continuous scanning)
- Red "Stop Scanner" button (disables auto-scan)
- Blue "Scan Once" button (runs one scan immediately)
- Status badge shows: RUNNING or STOPPED

### Stats Row
```
Total Scans | Opportunities Found | High Priority | Last Scan
     0      |         0           |      0        |   Never
```

### Token Grid
Cards arranged in a responsive grid, each showing:
- Token symbol and name
- Priority badge (HIGH/MEDIUM/LOW)
- Revival score (big number, 0-1)
- Three sub-scores (Price, Smart Money, Volume)
- Four key metrics (Age, Liquidity, Volume, Price Change)
- Link to view on DexScreener

## 🔧 API Endpoints

The backend provides these endpoints:

### Status & Control
- `GET /api/status` - Get scanner status
- `POST /api/scan/start` - Start auto-scanning
- `POST /api/scan/stop` - Stop auto-scanning
- `POST /api/scan/once` - Run single scan

### Data
- `GET /api/results?min_score=0.4` - Get filtered results
- `GET /api/token/<address>` - Get details for specific token
- `GET /api/history` - Get past scan history
- `GET /api/alerts` - Get today's alerts

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

## 📁 File Structure

```
src/
├── web_app.py              # Flask backend server
├── web_templates/
│   └── index.html          # Frontend dashboard
└── data/
    ├── meme_scanner/       # Scan results
    ├── meme_notifier/      # Alert logs
    ├── revival_detector/   # Revival analysis
    └── security_filter/    # Security checks
```

## ⚙️ Configuration

### Scan Settings
Edit in `web_app.py`:
```python
scanner_state = {
    'settings': {
        'scan_interval': 300,       # 5 minutes (300 seconds)
        'min_revival_score': 0.4,   # Minimum score to display
        'auto_scan': False          # Start with auto-scan off
    }
}
```

### Port Configuration
Default port is 5000. To change:
```python
# In web_app.py, bottom of file:
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🎯 How to Use

### First Time Setup
1. Start the web server: `./start_webapp.sh`
2. Open browser to: `http://localhost:5000`
3. Click "Scan Once" to test
4. Wait 1-2 minutes for results
5. Review the token cards that appear

### Regular Use
1. Click "Start Auto Scan" to enable continuous monitoring
2. Server will scan every 5 minutes automatically
3. High-priority opportunities will appear at the top
4. Click "View on DexScreener" to research tokens
5. Results auto-refresh every 30 seconds

### Finding Good Tokens
The scanner looks for these patterns:
- **Age**: 24-72 hours old (survived initial dump)
- **Price Pattern**: Dumped 40-80%, now recovering
- **Smart Money**: 2+ profitable wallets entered after 24hrs
- **Volume**: Increasing volume (buyers returning)

## 🔒 Security Notes

- **Local Only**: Server runs on localhost (127.0.0.1)
- **No External Access**: Not exposed to internet by default
- **Read-Only**: Dashboard doesn't execute trades
- **API Rate Limits**: Respects free tier limits

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip3 install flask flask-cors requests pandas --user
```

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in web_app.py
```

### No results appear
- Check that token addresses are 24-72 hours old
- Verify APIs are responding (test with `test_simple_revival.py`)
- Check browser console for errors (F12)

### Scanner says "RUNNING" but no new results
- Check terminal for error messages
- Verify scan_interval (default 5 minutes)
- Try clicking "Scan Once" manually

## 📊 Understanding the Scores

### Revival Score (0-1)
Weighted combination of:
- **50%** Price Pattern (dump → recovery)
- **30%** Smart Money Activity
- **20%** Volume Profile

### Sub-Scores

**Price Score (0-1)**:
- Did it dump enough? (40-80% drop)
- Is it recovering? (20%+ from bottom)
- Higher lows pattern?
- Volume returning?

**Smart Money Score (0-1)**:
- 3+ smart wallets = 1.0
- 2 smart wallets = 0.66
- 1 smart wallet = 0.33
- 0 smart wallets = 0.0

**Volume Score (0-1)**:
- Volume >$10K = 0.5
- More buys than sells = +0.5

## 🎨 Customization

### Change Color Scheme
Edit CSS in `web_templates/index.html`:
```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* High priority color */
.high-priority { border-left-color: #f56565; }
```

### Adjust Card Layout
```css
/* Number of columns */
.results-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}
```

### Modify Refresh Rate
```javascript
// In index.html, bottom of file:
setInterval(updateStatus, 60000); // 60 seconds
```

## 🚀 Advanced Usage

### Running on Different Machine
```bash
# In web_app.py, change:
app.run(host='0.0.0.0', port=5000)

# Then access from other devices:
http://YOUR_IP_ADDRESS:5000
```

### Integrating with Paper Trading
Results are automatically logged to CSV files:
```python
# Access scan results
import pandas as pd
df = pd.read_csv('src/data/meme_scanner/scan_results_*.csv')
```

### Custom Token Lists
Modify `get_candidate_tokens()` in `meme_scanner_orchestrator.py`:
```python
def get_candidate_tokens(self):
    # Add your custom token list
    custom_tokens = [
        'YOUR_TOKEN_ADDRESS_1',
        'YOUR_TOKEN_ADDRESS_2',
    ]
    return custom_tokens
```

## 📈 Performance Tips

1. **Limit Concurrent Scans**: Scanner processes 20 tokens max per cycle
2. **Cache Results**: Uses 5-minute caching to reduce API calls
3. **Batch Processing**: Filters run in parallel (3 threads)
4. **Auto-Cleanup**: Old results are kept for history

## 🎯 Next Steps

After getting comfortable with the dashboard:

1. **Paper Trade** - Track hypothetical performance
2. **Refine Filters** - Adjust minimum scores based on results
3. **Monitor Patterns** - Learn what revival patterns work best
4. **Add Alerts** - Set up notifications (Telegram/Discord)
5. **Integrate Trading** - Connect to actual trading (carefully!)

## 💡 Pro Tips

- **Best Time to Scan**: Every 4-6 hours is usually sufficient
- **Focus on HIGH Priority**: Scores >0.8 have the best chance
- **Check Age**: Sweet spot is 30-48 hours old
- **Verify Manually**: Always check DexScreener before trading
- **Start Small**: Paper trade for 30 days minimum

## 🆘 Support

If you encounter issues:
1. Check terminal output for errors
2. Test APIs with `test_simple_revival.py`
3. Verify token addresses are valid Solana addresses
4. Check that tokens are actually 24-72 hours old

## 📝 Changelog

### Version 1.0
- Initial release
- Auto-scanning every 5 minutes
- Beautiful card-based UI
- Priority system (High/Medium/Low)
- Real-time status updates
- DexScreener integration

---

Built with ❤️ by Moon Dev
Happy hunting! 🚀