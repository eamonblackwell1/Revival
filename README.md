# 🤖 AI AGENTS FOR TRADING

<p align="center">
  <a href="https://www.moondev.com/"><img src="moondev.png" width="300" alt="Moon Dev"></a>
</p>

## 🎯 Vision
ai agents are clearly the future and the entire workforce will be replaced or atleast using ai agents. while i am a quant and building agents for algo trading i will be contributing to all different types of ai agent flows and placing all of the agents here for free, 100% open sourced because i beleive code is the great equalizer and we have never seen a regime shift like this so i need to get this code to the people

feel free to join our discord if you beleive ai agents will be integrated into the workforce

⭐️ [first full concise documentation video (watch here)](https://youtu.be/RlqzkSgDKDc)

## Video Updates & Training
📀 follow all updates here on youtube: https://www.youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz

## Featured Project: Revival Scanner 🔄

**The Revival Scanner identifies "second life" meme coin opportunities 24-72 hours after launch.**

Unlike sniper bots that compete for fresh launches (0-12 hours), the Revival Scanner targets tokens that have:
- Survived the initial rug pull window
- Established a price floor after dumping
- Show signs of renewed interest from smart money
- Developed organic community support

**Why Revival Trading?**
- Lower competition (most bots focus on fresh launches)
- Better risk/reward (tokens already survived initial scam period)
- FREE API tiers sufficient (no expensive real-time data needed)
- 30-40% win rate (vs 10-20% for fresh launches)
- Sustainable approach (less stressful than speed competition)

**Quick Start:**
```bash
# Start the web dashboard
./start_webapp.sh

# View at http://localhost:5000
```

**Documentation:**
- 📘 [Revival Scanner PRD](REVIVAL_SCANNER_PRD.md) - Complete strategy guide
- 🚀 [Quick Start Guide](QUICK_START_WEBAPP.md) - Get running in 2 minutes
- 🌐 [Web App Guide](WEBAPP_README.md) - Dashboard features

---

## Other Live Agents
- Trading Agent (`trading_agent.py`): Example agent that analyzes token data via LLM to make basic trade decisions
- Strategy Agent (`strategy_agent.py`): Manages and executes trading strategies placed in the strategies folder
- Risk Agent (`risk_agent.py`): Monitors and manages portfolio risk, enforcing position limits and PnL thresholds
- Copy Agent (`copy_agent.py`): monitors copy bot for potential trades
- Whale Agent (`whale_agent.py`): monitors whale activity and announces when a whale enters the market
- Sentiment Agent (`sentiment_agent.py`): analyzes Twitter sentiment for crypto tokens with voice announcements
- Listing Arbitrage Agent (`listingarb_agent.py`): identifies promising Solana tokens on CoinGecko before they reach major exchanges like Binance and Coinbase, using parallel AI analysis for technical and fundamental insights
- Focus Agent (`focus_agent.py`): randomly samples audio during coding sessions to maintain productivity, providing focus scores and voice alerts when focus drops (~$10/month, perfect for voice-to-code workflows)
- Funding Agent (`funding_agent.py`): monitors funding rates across exchanges and uses AI to analyze opportunities, providing voice alerts for extreme funding situations with technical context 🌙
- Liquidation Agent (`liquidation_agent.py`): tracks liquidation events with configurable time windows (15min/1hr/4hr), providing AI analysis and voice alerts for significant liquidation spikes 💦
- Chart Agent (`chartanalysis_agent.py`): looks at any crypto chart and then analyzes it with ai to make a buy/sell/nothing reccomendation.
- funding rate arbitrage agent (`fundingarb_agent.py`): tracks the funding rate on hyper liquid to find funding rate arbitrage opportunities between hl and solana
- rbi agent (`rbi_agent.py`): uses deepseek to research trading strategies based on the youtube video, pdf, or words you give it. then sends to his ai friend who codes out the backtest.
- twitter agent (`tweet_agent.py`): takes in text and creates tweets using deepseek or other models
- video agent (`video_agent.py`): takes in text to create videos by creating audio snippets using elevenlabs and combining with raw_video footage
- new or top tokens (`new_or_top_agent.py`): an agent that looks at the new tokens and the top tokens from coin gecko api
- chat agent (`chat_agent.py`): an agent that monitors youtube live stream chat, moderates & responds to known questions. absolute fire.
- clips agent (`clips_agent.py`): an agent that helps clip long videos into shorter ones so you can upload to your youtube and get paid more info is in the code notes and here: https://discord.gg/XAw8US9aHT
- phone agent (`phone_agent.py`): an ai agent that can take phone calls for you
- real time clips agent (`src/agents/realtime_clips_agent.py`): an ai agent that makes real time clips of streamers using obs

### Legacy/Experimental Agents
- sniper agent (`sniper_agent.py`): LEGACY - watches for new solana token launches (0-12 hours). Replaced by Revival Scanner
- tx agent (`tx_agent.py`): watches transactions made by copy list
- solana agent (`solana_agent.py`): LEGACY - looks at sniper + tx agents. Replaced by Revival Scanner
- million agent (`million_agent.py`): uses million context window from gemini
- tiktok agent (`tiktok_agent.py`): scrolls tiktok for consumer data
- compliance agent (`compliance_agent.py`): compliance agent for ads
- research agent (`research_agent`): fills ideas.txt for rbi agent

**⚠️ IMPORTANT: This is an experimental project. There are NO guarantees of profitability. Trading involves substantial risk of loss.**

## ⚠️ Critical Disclaimers

*There is no token associated with this project and there never will be. any token launched is not affiliated with this project, moon dev will never dm you. be careful. don't send funds anywhere*

**PLEASE READ CAREFULLY:**

1. This is an experimental research project, NOT a trading system
2. There are NO plug-and-play solutions for guaranteed profits
3. We do NOT provide trading strategies
4. Success depends entirely on YOUR:
   - Trading strategy
   - Risk management
   - Market research
   - Testing and validation
   - Overall trading approach

5. NO AI agent can guarantee profitable trading
6. You MUST develop and validate your own trading approach
7. Trading involves substantial risk of loss
8. Past performance does not indicate future results

## 👂 Looking for Updates?
Project updates will be posted in discord, join here: [moondev.com](http://moondev.com) 

## 🔗 Links
- Free Algo Trading Roadmap: [moondev.com](https://moondev.com)
- Algo Trading Education: [algotradecamp.com](https://algotradecamp.com)
- Business Contact [moon@algotradecamp.com](mailto:moon@algotradecamp.com)

## 🚀 Quick Start Guide

python 3.10.9 is what was used during dev

1. ⭐ **Star the Repo**
   - Click the star button to save it to your GitHub favorites

2. 🍴 **Fork the Repo**
   - Fork to your GitHub account to get your own copy
   - This lets you make changes and track updates

3. 💻 **Open in Your IDE**
   - Clone to your local machine
   - Recommended: Use [Cursor](https://www.cursor.com/) or [Windsurfer](https://codeium.com/) for AI-enabled coding

4. 🔑 **Set Environment Variables**
   - Check `.env.example` for required variables
   - Create a copy of above and name it `.env` file with your keys:
     - Anthropic API key
     - Other trading API keys
   - ⚠️ Never commit or share your API keys!

5. 🤖 **Customize Agent Prompts**
   - Navigate to `/agents` folder
   - Modify LLM prompts to fit your needs
   - Each agent has configurable parameters

6. 📈 **Implement Your Strategies**
   - Add your strategies to `/strategies` folder
   - Remember: Out-of-box code is NOT profitable
   - Thorough testing required before live trading

7. 🏃‍♂️ **Run the System**
   - Execute via `main.py`
   - Toggle agents on/off as needed
   - Monitor logs for performance

---
## ROADMAP

[] hyperliquid perps integration
   - build a nice funcs router to be able to pass in solana, hyperliquid, extended and then it points to the right nice_funcs -- then we simply change out the imports.
[] extended integration
   - same thing as above
[] hyperliquid spot
[] trending agent - spots the leaders on hl and trades those w/ data and some llm bias
[] update the rbi agent. my fav so keep pushing

Other ideas

[] lighter integration
[] pacifica integration
[] hibachi integration
[] aster integration
[] hyperevm stuff


---
*Built with love by Moon Dev - Pioneering the future of AI-powered trading*


## 📜 Detailed Disclaimer
The content presented is for educational and informational purposes only and does not constitute financial advice. All trading involves risk and may not be suitable for all investors. You should carefully consider your investment objectives, level of experience, and risk appetite before investing.

Past performance is not indicative of future results. There is no guarantee that any trading strategy or algorithm discussed will result in profits or will not incur losses.

**CFTC Disclaimer:** Commodity Futures Trading Commission (CFTC) regulations require disclosure of the risks associated with trading commodities and derivatives. There is a substantial risk of loss in trading and investing.

I am not a licensed financial advisor or a registered broker-dealer. Content & code is based on personal research perspectives and should not be relied upon as a guarantee of success in trading.