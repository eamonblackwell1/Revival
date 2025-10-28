# ⚠️ ARCHIVED - DO NOT USE

**This document describes implementation details for the "fresh launch sniper" approach which has been replaced by the Revival Scanner strategy.**

**See [REVIVAL_SCANNER_PRD.md](REVIVAL_SCANNER_PRD.md) for the current, active approach.**

Archived for reference only. The Revival Scanner focuses on 24-72 hour old tokens instead of competing for fresh launches.

---

# MEME_COIN_BOT.md

This file provides comprehensive technical guidance for building a Solana meme coin trading bot, incorporating lessons learned from our HMM Bitcoin trading system.

## Critical Context: Lessons from HMM Bitcoin Trader

### What Failed in Bitcoin Trading (Avoid These)
- **Over-trading destroyed returns**: Original system made 1,377 trades, lost 75%. Transaction costs (0.1% × 2 per trade) compound catastrophically.
- **Too many filters = no trades**: Combining confidence threshold + minimum hold + trend filter + max trades blocked ALL signals
- **HMM doesn't work for crypto bull markets**: Model trained on 2018-2023 was too conservative for 2023-2025 bull run (+319% BTC)
- **Complex doesn't mean better**: Simple momentum strategy (+36%) beat sophisticated walk-forward optimization

### What Worked (Apply These)
- **Minimum hold times are critical**: 24-48 hour holds prevented churning, our best system used 48 hours
- **Fewer trades = better returns**: Best system made 403 trades vs 13,361 in worst system
- **Risk management > signal quality**: Stop losses and position sizing matter more than perfect entry
- **Transaction costs must be modeled**: Every trade costs 0.2% minimum (0.1% × 2), this adds up fast

## Project Overview

Meme Coin Trading Bot - An algorithmic trading system for Solana meme coins that filters 30,000+ daily token launches down to 10-50 tradeable opportunities using multi-stage security, liquidity, holder distribution, and social signal analysis.

**Core Challenge**: 95%+ of meme coins are scams, pump & dumps, or fail within days. Success requires extreme filtering and aggressive risk management.

**Why Different from BTC**: Meme coins are social-driven, not technical. Traditional indicators (RSI, MACD, HMM regimes) are useless. Speed and social momentum are everything.

## System Architecture

```
New Token Stream → Stage 1 Filter → Stage 2 Filter → Stage 3 Filter → Stage 4 Filter → Trading Engine
       ↓                ↓               ↓                ↓               ↓              ↓
   30,000/day      Security &       Holder           Social          Smart Money    Execute
                   Liquidity      Distribution       Signals          Tracking      10-50 tokens
                   (~1,000)         (~200)           (~60)            (~20)
```

## Complete Filtering Pipeline Implementation

### Stage 1: Mass Elimination (30,000 → 1,000 tokens)
**Execution Time**: <1 minute via parallel API calls

```python
import requests
from concurrent.futures import ThreadPoolExecutor
import asyncio

class Stage1Filter:
    def __init__(self):
        self.dexscreener_base = "https://api.dexscreener.com"
        self.goplus_api_key = "YOUR_GOPLUS_KEY"

    def filter_batch(self, tokens):
        """Hard filters to eliminate obvious scams"""
        passed = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Parallel API calls for speed
            futures = []
            for token in tokens:
                futures.append(executor.submit(self.check_token, token))

            for future in futures:
                result = future.result()
                if result['passed']:
                    passed.append(result['token'])

        return passed

    def check_token(self, token_address):
        # DexScreener check
        dex_data = self.get_dexscreener_data(token_address)

        # Critical thresholds
        if dex_data['liquidity']['usd'] < 10000:  # $10K minimum
            return {'passed': False}
        if dex_data['volume24h'] < 5000:  # $5K minimum volume
            return {'passed': False}
        if dex_data['pairAge'] > 12 * 3600:  # 12 hours max age
            return {'passed': False}
        if dex_data['txns']['h24']['buys'] < 60:  # Minimum activity
            return {'passed': False}

        # GoPlus security check
        security = self.check_goplus_security(token_address)
        if security['is_honeypot'] == '1':
            return {'passed': False}
        if security['is_mintable'] == '1':
            return {'passed': False}
        if int(security.get('security_score', 0)) < 60:
            return {'passed': False}

        return {
            'passed': True,
            'token': {
                'address': token_address,
                'liquidity': dex_data['liquidity']['usd'],
                'volume': dex_data['volume24h'],
                'age_hours': dex_data['pairAge'] / 3600,
                'security_score': security.get('security_score', 0)
            }
        }

    def get_dexscreener_data(self, address):
        """Fetch real-time data from DexScreener"""
        url = f"{self.dexscreener_base}/latest/dex/tokens/{address}"
        response = requests.get(url)
        return response.json()['pairs'][0]  # Get primary pair

    def check_goplus_security(self, address):
        """Check honeypot and security issues"""
        url = f"https://api.gopluslabs.io/api/v1/token_security/sol"
        params = {'contract_addresses': address}
        headers = {'Authorization': f'Bearer {self.goplus_api_key}'}
        response = requests.get(url, params=params, headers=headers)
        return response.json()['result'][address]
```

### Stage 2: Holder Distribution Analysis (1,000 → 200)
**Execution Time**: 2-3 minutes

```python
from solana.rpc.api import Client
import requests

class Stage2Filter:
    def __init__(self):
        self.solana_client = Client("https://api.mainnet-beta.solana.com")
        self.birdeye_api_key = "YOUR_BIRDEYE_KEY"  # Optional

    def filter_by_holders(self, tokens):
        """Analyze holder distribution"""
        passed = []

        for token in tokens:
            holder_data = self.analyze_holders(token['address'])

            # Critical holder thresholds
            if holder_data['dev_percentage'] > 15:
                continue  # Dev holds too much
            if holder_data['top_10_percentage'] > 30:
                continue  # Too concentrated
            if holder_data['sniper_percentage'] > 5:
                continue  # Too many snipers
            if holder_data['holder_count'] < 50:
                continue  # Not enough holders
            if holder_data['lp_burned_percentage'] < 50:
                continue  # Liquidity not locked

            # Check for suspicious clusters (Bubblemaps logic)
            if self.has_suspicious_clusters(holder_data):
                continue

            token['holder_metrics'] = holder_data
            passed.append(token)

        return passed

    def analyze_holders(self, token_address):
        """Get holder distribution metrics"""
        # Use Solscan API or Helius for holder data
        url = f"https://api.solscan.io/token/holders"
        params = {'token': token_address, 'limit': 100}
        response = requests.get(url, params=params)
        holders = response.json()['data']

        total_supply = sum(h['amount'] for h in holders)

        # Calculate key metrics
        dev_wallet = holders[0]  # Usually largest holder
        top_10 = holders[:10]

        # Sniper detection (wallets that bought in first minute)
        snipers = self.detect_snipers(token_address)

        return {
            'dev_percentage': (dev_wallet['amount'] / total_supply) * 100,
            'top_10_percentage': (sum(h['amount'] for h in top_10) / total_supply) * 100,
            'sniper_percentage': snipers['percentage'],
            'holder_count': len(holders),
            'lp_burned_percentage': self.check_lp_burn(token_address),
            'holders': holders
        }

    def detect_snipers(self, token_address):
        """Identify sniper bots"""
        # Check first 100 transactions
        early_txs = self.get_early_transactions(token_address)

        # Wallets that bought in first 60 seconds
        snipers = set()
        launch_time = early_txs[0]['timestamp']

        for tx in early_txs:
            if tx['timestamp'] - launch_time < 60:
                snipers.add(tx['wallet'])

        return {
            'count': len(snipers),
            'percentage': (len(snipers) / len(early_txs)) * 100,
            'wallets': list(snipers)
        }

    def has_suspicious_clusters(self, holder_data):
        """Detect coordinated wallet clusters"""
        holders = holder_data['holders']

        # Look for similar holding amounts (likely coordinated)
        amounts = [h['amount'] for h in holders[:20]]

        # Check for round numbers
        round_count = sum(1 for a in amounts if a % 1000000 == 0)
        if round_count > 5:
            return True  # Too many round numbers

        # Check for similar wallet creation times
        # (Implementation depends on available API)

        return False
```

### Stage 3: Social Signal Validation (200 → 60)
**Execution Time**: 3-5 minutes

```python
import tweepy
from telegram import Bot
import asyncio
from datetime import datetime, timedelta

class Stage3Filter:
    def __init__(self):
        # Twitter API (or alternative)
        self.twitter_bearer = "YOUR_TWITTER_BEARER"
        self.telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"

    def filter_by_social(self, tokens):
        """Validate social signals"""
        passed = []

        for token in tokens:
            social_data = self.analyze_social(token)

            # Minimum social requirements
            if social_data['twitter_mentions_1h'] < 10:
                continue
            if social_data['telegram_members'] < 100:
                continue
            if social_data['sentiment_score'] < 0.6:
                continue
            if social_data['platform_count'] < 2:
                continue
            if social_data['influencer_mentions'] < 1:
                continue

            token['social_metrics'] = social_data
            passed.append(token)

        return passed

    def analyze_social(self, token):
        """Aggregate social signals"""
        # Get token symbol/name for searching
        symbol = token.get('symbol', '')
        name = token.get('name', '')

        # Twitter analysis
        twitter_data = self.analyze_twitter(symbol, name)

        # Telegram analysis
        telegram_data = self.check_telegram(token.get('telegram', ''))

        # Calculate sentiment
        sentiment = self.calculate_sentiment(twitter_data['tweets'])

        return {
            'twitter_mentions_1h': twitter_data['mentions_1h'],
            'twitter_mentions_24h': twitter_data['mentions_24h'],
            'influencer_mentions': twitter_data['influencer_count'],
            'telegram_members': telegram_data['member_count'],
            'telegram_active': telegram_data['messages_per_hour'],
            'sentiment_score': sentiment,
            'platform_count': self.count_platforms(token),
            'virality_score': self.calculate_virality(twitter_data)
        }

    def analyze_twitter(self, symbol, name):
        """Check Twitter/X activity"""
        client = tweepy.Client(bearer_token=self.twitter_bearer)

        # Search for mentions in last hour
        query = f"({symbol} OR {name}) -is:retweet"
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)

        tweets = client.search_recent_tweets(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=100,
            tweet_fields=['author_id', 'created_at', 'public_metrics']
        )

        # Identify influencer mentions
        influencers = self.identify_influencers(tweets.data)

        return {
            'mentions_1h': len(tweets.data) if tweets.data else 0,
            'mentions_24h': self.get_24h_mentions(symbol, name),
            'influencer_count': len(influencers),
            'influencers': influencers,
            'tweets': tweets.data
        }

    def identify_influencers(self, tweets):
        """Find mentions from influential accounts"""
        influencers = []

        for tweet in tweets:
            # Get author metrics
            author_id = tweet.author_id
            # Would need additional API call for follower count
            # For now, use engagement as proxy
            if tweet.public_metrics['like_count'] > 100:
                influencers.append(author_id)

        return influencers
```

### Stage 4: Smart Money Tracking (60 → 20)
**Execution Time**: 5 minutes

```python
class Stage4Filter:
    def __init__(self):
        self.gmgn_base = "https://gmgn.ai/api"  # Free API
        self.smart_wallets = self.load_smart_wallets()

    def filter_by_smart_money(self, tokens):
        """Track smart money activity"""
        passed = []

        for token in tokens:
            smart_data = self.analyze_smart_money(token)

            # Smart money requirements
            if smart_data['smart_wallet_count'] < 3:
                continue  # Need multiple smart wallets
            if smart_data['avg_wallet_winrate'] < 0.6:
                continue  # Wallets must be profitable
            if smart_data['wash_trading_detected']:
                continue  # Avoid wash trading
            if not smart_data['natural_accumulation']:
                continue  # Must see gradual buying

            token['smart_money'] = smart_data
            passed.append(token)

        return passed

    def analyze_smart_money(self, token):
        """Check if smart money is buying"""
        # GMGN API call for smart money data
        url = f"{self.gmgn_base}/sol/token/{token['address']}/holders"
        response = requests.get(url)
        holders = response.json()

        # Identify smart wallets in holders
        smart_holders = []
        for holder in holders:
            if holder['address'] in self.smart_wallets:
                smart_holders.append({
                    'address': holder['address'],
                    'amount': holder['amount'],
                    'entry_time': holder['first_tx_time'],
                    'winrate': self.smart_wallets[holder['address']]['winrate']
                })

        # Check for wash trading patterns
        wash_trading = self.detect_wash_trading(token['address'])

        # Analyze accumulation pattern
        natural = self.check_natural_accumulation(token['address'])

        return {
            'smart_wallet_count': len(smart_holders),
            'smart_wallets': smart_holders,
            'avg_wallet_winrate': sum(w['winrate'] for w in smart_holders) / max(len(smart_holders), 1),
            'wash_trading_detected': wash_trading,
            'natural_accumulation': natural
        }

    def load_smart_wallets(self):
        """Load list of profitable wallets to track"""
        # GMGN provides smart money wallets
        url = f"{self.gmgn_base}/sol/smart_money/wallets"
        response = requests.get(url)
        wallets = response.json()

        # Filter for consistently profitable wallets
        smart = {}
        for wallet in wallets:
            if wallet['winrate'] > 0.6 and wallet['realized_pnl'] > 10000:
                smart[wallet['address']] = {
                    'winrate': wallet['winrate'],
                    'avg_return': wallet['avg_return'],
                    'total_pnl': wallet['realized_pnl']
                }

        return smart

    def detect_wash_trading(self, token_address):
        """Detect wash trading patterns"""
        # Get recent transactions
        txs = self.get_recent_transactions(token_address, limit=100)

        # Look for same wallet buying and selling repeatedly
        wallet_actions = {}
        for tx in txs:
            wallet = tx['wallet']
            if wallet not in wallet_actions:
                wallet_actions[wallet] = []
            wallet_actions[wallet].append(tx['type'])  # 'buy' or 'sell'

        # Check for wash patterns
        for wallet, actions in wallet_actions.items():
            if len(actions) > 4:  # Multiple trades
                # Check for alternating buy/sell pattern
                if self.is_alternating_pattern(actions):
                    return True

        return False
```

## Trading Execution Engine

```python
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58
import time

class MemeTrader:
    def __init__(self):
        # Wallet setup
        self.private_key = os.environ['SOLANA_PRIVATE_KEY']
        self.keypair = Keypair.from_secret_key(base58.b58decode(self.private_key))
        self.public_key = self.keypair.public_key

        # Solana connection
        self.client = Client("https://api.mainnet-beta.solana.com")

        # Trading parameters
        self.max_position_size = 0.02  # 2% max per trade
        self.stop_loss = 0.20  # 20% stop loss
        self.take_profit_levels = [2.0, 5.0, 10.0]  # 2x, 5x, 10x
        self.max_slippage = 0.05  # 5% max slippage

        # Track positions
        self.positions = {}

    def execute_trade(self, token, amount_sol):
        """Execute buy order via Jupiter"""
        try:
            # Build Jupiter swap transaction
            swap_tx = self.build_jupiter_swap(
                input_mint="So11111111111111111111111111111111111112",  # SOL
                output_mint=token['address'],
                amount=int(amount_sol * 10**9),  # Convert to lamports
                slippage=int(self.max_slippage * 10000)  # Basis points
            )

            # Add priority fee for faster execution
            swap_tx = self.add_priority_fee(swap_tx, priority_fee=0.001)  # 0.001 SOL

            # Send transaction
            signature = self.client.send_transaction(swap_tx, self.keypair)

            # Wait for confirmation
            self.client.confirm_transaction(signature)

            # Track position
            self.positions[token['address']] = {
                'entry_price': token['price'],
                'amount_sol': amount_sol,
                'entry_time': time.time(),
                'signature': signature
            }

            print(f"✅ Bought {token['symbol']} for {amount_sol} SOL")
            print(f"   TX: {signature}")

            return signature

        except Exception as e:
            print(f"❌ Trade failed: {str(e)}")
            return None

    def build_jupiter_swap(self, input_mint, output_mint, amount, slippage):
        """Build Jupiter aggregator swap"""
        # Jupiter API endpoint
        url = "https://quote-api.jup.ag/v6/quote"

        params = {
            'inputMint': input_mint,
            'outputMint': output_mint,
            'amount': amount,
            'slippageBps': slippage
        }

        # Get quote
        quote_response = requests.get(url, params=params)
        quote = quote_response.json()

        # Get swap transaction
        swap_url = "https://quote-api.jup.ag/v6/swap"
        swap_data = {
            'quoteResponse': quote,
            'userPublicKey': str(self.public_key),
            'wrapAndUnwrapSol': True
        }

        swap_response = requests.post(swap_url, json=swap_data)
        swap_tx = swap_response.json()['swapTransaction']

        return swap_tx

    def monitor_positions(self):
        """Monitor positions for stop loss and take profit"""
        while True:
            for token_address, position in self.positions.items():
                current_price = self.get_current_price(token_address)
                entry_price = position['entry_price']

                # Calculate P&L
                pnl = (current_price - entry_price) / entry_price

                # Check stop loss
                if pnl <= -self.stop_loss:
                    print(f"🛑 Stop loss triggered for {token_address}")
                    self.sell_position(token_address, 1.0)  # Sell 100%

                # Check take profit levels
                elif pnl >= self.take_profit_levels[0]:
                    if 'tp1_hit' not in position:
                        print(f"💰 Take profit 1 hit for {token_address} ({pnl*100:.1f}%)")
                        self.sell_position(token_address, 0.25)  # Sell 25%
                        position['tp1_hit'] = True

                elif pnl >= self.take_profit_levels[1]:
                    if 'tp2_hit' not in position:
                        print(f"💰 Take profit 2 hit for {token_address} ({pnl*100:.1f}%)")
                        self.sell_position(token_address, 0.25)  # Sell another 25%
                        position['tp2_hit'] = True

                elif pnl >= self.take_profit_levels[2]:
                    if 'tp3_hit' not in position:
                        print(f"🚀 Take profit 3 hit for {token_address} ({pnl*100:.1f}%)")
                        self.sell_position(token_address, 0.5)  # Sell remaining 50%
                        position['tp3_hit'] = True

            time.sleep(10)  # Check every 10 seconds
```

## Complete Implementation Flow

```python
class MemeScanner:
    def __init__(self):
        # Initialize all stages
        self.stage1 = Stage1Filter()
        self.stage2 = Stage2Filter()
        self.stage3 = Stage3Filter()
        self.stage4 = Stage4Filter()
        self.trader = MemeTrader()

        # Config
        self.scan_interval = 60  # Scan every minute
        self.max_positions = 10  # Maximum concurrent positions

    def run(self):
        """Main bot loop"""
        print("🚀 Starting Meme Coin Scanner...")

        while True:
            try:
                # Get new token launches
                new_tokens = self.get_new_tokens()
                print(f"📊 Found {len(new_tokens)} new tokens")

                # Run filtering pipeline
                candidates = self.filter_pipeline(new_tokens)
                print(f"✅ {len(candidates)} tokens passed all filters")

                # Execute trades on best candidates
                for token in candidates[:3]:  # Top 3 only
                    if len(self.trader.positions) < self.max_positions:
                        # Calculate position size
                        portfolio_value = self.get_portfolio_value()
                        position_size = portfolio_value * 0.02  # 2% per trade

                        # Execute trade
                        self.trader.execute_trade(token, position_size)

                # Monitor existing positions
                self.trader.monitor_positions()

                # Wait before next scan
                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                time.sleep(30)  # Wait 30s on error

    def filter_pipeline(self, tokens):
        """Run complete filtering pipeline"""
        print("  Stage 1: Security & Liquidity...")
        stage1_passed = self.stage1.filter_batch(tokens)
        print(f"    → {len(stage1_passed)} passed")

        print("  Stage 2: Holder Distribution...")
        stage2_passed = self.stage2.filter_by_holders(stage1_passed)
        print(f"    → {len(stage2_passed)} passed")

        print("  Stage 3: Social Signals...")
        stage3_passed = self.stage3.filter_by_social(stage2_passed)
        print(f"    → {len(stage3_passed)} passed")

        print("  Stage 4: Smart Money...")
        stage4_passed = self.stage4.filter_by_smart_money(stage3_passed)
        print(f"    → {len(stage4_passed)} passed")

        # Score and rank final candidates
        scored = self.score_candidates(stage4_passed)
        scored.sort(key=lambda x: x['final_score'], reverse=True)

        return scored

    def score_candidates(self, tokens):
        """Score tokens for final ranking"""
        for token in tokens:
            score = 0

            # Liquidity score (0-20)
            liq = token['liquidity']
            if liq > 100000:
                score += 20
            elif liq > 50000:
                score += 15
            elif liq > 25000:
                score += 10
            else:
                score += 5

            # Volume score (0-20)
            volume = token['volume']
            if volume > 100000:
                score += 20
            elif volume > 50000:
                score += 15
            elif volume > 25000:
                score += 10
            else:
                score += 5

            # Holder score (0-20)
            holders = token['holder_metrics']
            if holders['dev_percentage'] < 5:
                score += 10
            if holders['holder_count'] > 200:
                score += 10

            # Social score (0-20)
            social = token['social_metrics']
            if social['twitter_mentions_1h'] > 50:
                score += 10
            if social['influencer_mentions'] > 3:
                score += 10

            # Smart money score (0-20)
            smart = token['smart_money']
            if smart['smart_wallet_count'] > 5:
                score += 10
            if smart['avg_wallet_winrate'] > 0.7:
                score += 10

            token['final_score'] = score

        return tokens

if __name__ == "__main__":
    scanner = MemeScanner()
    scanner.run()
```

## API Keys and Services Required

### Essential (Free Tier Available)
1. **DexScreener API**: No key needed, free
2. **GoPlus Security**: Free tier, register at gopluslabs.io
3. **GMGN**: Free API, no key required
4. **Solscan**: Free tier available

### Recommended (Paid)
1. **Birdeye**: Better Solana data ($50-300/month)
2. **Twitter API or twitterapi.io**: Social signals (~$100/month)
3. **Helius RPC**: Faster Solana node (~$50/month)

### Optional (Premium)
1. **Nansen**: Institutional analytics ($150-1800/month)
2. **TweetScout**: Advanced Twitter analysis (~$100/month)
3. **QuillCheck**: Enhanced security (~$200/month)

## Environment Setup

```bash
# 1. Create Python environment
python3 -m venv meme_env
source meme_env/bin/activate

# 2. Install dependencies
pip install solana
pip install python-binance  # If tracking CEX listings
pip install tweepy  # Twitter API
pip install python-telegram-bot
pip install pandas numpy
pip install requests aiohttp
pip install web3  # If multi-chain

# 3. Create .env file
echo "SOLANA_PRIVATE_KEY=your_wallet_private_key" > .env
echo "GOPLUS_API_KEY=your_goplus_key" >> .env
echo "TWITTER_BEARER=your_twitter_bearer" >> .env
echo "TELEGRAM_BOT_TOKEN=your_telegram_token" >> .env

# 4. Fund wallet
# Send 0.5-1 SOL to wallet for trading
# Keep extra for transaction fees (~0.001 SOL per trade)
```

## Risk Management Critical Rules

### Position Sizing
- **Never exceed 2% per trade**: Even on highest conviction
- **Total exposure limit**: Max 20% of portfolio in meme coins
- **Scaling strategy**: Start with 0.5% positions, increase as you validate

### Exit Strategy
```python
# Mandatory stop loss and take profit levels
RISK_CONFIG = {
    'stop_loss': 0.20,  # -20% max loss
    'take_profit': [
        {'level': 2.0, 'sell_pct': 0.25},   # 2x: sell 25%
        {'level': 5.0, 'sell_pct': 0.25},   # 5x: sell 25%
        {'level': 10.0, 'sell_pct': 0.25},  # 10x: sell 25%
        {'level': 20.0, 'sell_pct': 0.25},  # 20x: sell remaining
    ],
    'time_stop': 48,  # Exit after 48 hours regardless
}
```

### Expected Performance Metrics
- **Win Rate**: 20-30% (most will fail)
- **Average Win**: 3-10x
- **Average Loss**: -50%
- **Monthly Return Range**: -50% to +200%
- **Maximum Drawdown**: Expect -70% at some point

## Common Pitfalls to Avoid

1. **Not checking liquidity locks**: Always verify LP tokens are burned/locked
2. **Ignoring transaction costs**: 0.1% adds up fast with many trades
3. **FOMO buying after pumps**: Never buy tokens up >100% in 24h
4. **Holding too long**: Most meme coins die within 48 hours
5. **Not using stop losses**: One rug pull can wipe out 10 wins
6. **Trading with money you need**: Only risk what you can lose 100%
7. **Trusting social signals alone**: Bots can fake Twitter activity
8. **Not checking contract code**: Even with security APIs, verify critical functions

## Testing Strategy

### Phase 1: Paper Trading (Week 1)
```python
# Run in monitoring mode only
scanner = MemeScanner()
scanner.paper_trading_mode = True  # No real trades
scanner.run()
# Track hypothetical P&L
```

### Phase 2: Micro Testing (Week 2)
- Start with $100 total capital
- $2 per trade maximum (2% rule)
- Track every trade meticulously
- Expect to lose most of it (learning cost)

### Phase 3: Scaled Testing (Week 3-4)
- If paper trading showed promise, increase to $500-1000
- Maintain 2% position sizing
- Add more sophisticated filters based on learnings

### Phase 4: Production (Month 2+)
- Only scale if consistently profitable
- Never exceed risk you can afford to lose
- Consider it gambling, not investing

## Quick Start Checklist

- [ ] Set up Python environment
- [ ] Get free API keys (DexScreener, GoPlus, GMGN)
- [ ] Create Solana wallet programmatically
- [ ] Fund with 0.5 SOL for testing
- [ ] Run Stage 1 filter on live data
- [ ] Verify you're getting <1000 tokens from 30,000
- [ ] Add Stage 2-4 filters incrementally
- [ ] Run paper trading for 1 week minimum
- [ ] Start with $100 real capital
- [ ] Track every trade in spreadsheet
- [ ] Adjust filters based on results
- [ ] Scale only if profitable after 1 month

## Critical Reminders

1. **95% of meme coins go to zero** - This is not an exaggeration
2. **You will lose money initially** - Consider first $500 education cost
3. **Speed matters more than perfect analysis** - First movers win
4. **Community/social momentum > technicals** - Memes don't follow TA
5. **Take profits aggressively** - Don't be greedy, 2x is a win
6. **The house (DEX) always wins** - They collect fees on every trade
7. **Rug pulls are common** - Even with all checks, you'll hit some
8. **Tax implications** - Every trade is a taxable event

## Alternative Approach: Copy Trading via GMGN

If building from scratch seems complex, consider using GMGN's copy trading:

```python
# Simple GMGN copy trading setup
import requests

class GMGNCopyTrader:
    def __init__(self, wallet_address):
        self.wallet = wallet_address
        self.gmgn_api = "https://gmgn.ai/api"

    def find_smart_wallets(self):
        """Find profitable wallets to copy"""
        url = f"{self.gmgn_api}/sol/smart_money/wallets"
        params = {
            'min_winrate': 0.6,
            'min_realized_pnl': 10000,
            'days': 30
        }
        response = requests.get(url, params=params)
        return response.json()

    def copy_wallet_trades(self, target_wallet):
        """Mirror trades from profitable wallet"""
        # Set up WebSocket connection to monitor wallet
        # When wallet buys, you buy (with your position sizing)
        # When wallet sells, you sell
        pass
```

This is simpler but gives less control. You're trusting someone else's strategy.

## Final Architecture Decision Tree

```
Start Here
    ↓
Do you want full control?
    ├─ Yes → Build custom bot (this guide)
    └─ No → Use GMGN/BullX copy trading
           ↓
       How technical are you?
           ├─ Very → Build from scratch with APIs
           ├─ Moderate → Use existing bot + custom filters
           └─ Low → Use Telegram bots (Maestro, Photon)
                ↓
            Risk tolerance?
                ├─ High → 2% position sizes, 10+ positions
                ├─ Medium → 1% positions, 5 positions max
                └─ Low → Don't trade meme coins
```

## Next Steps for Implementation

1. **Start with data collection only** - Run Stage 1 filter for 24 hours, see what passes
2. **Add security checks** - Ensure GoPlus integration works
3. **Test holder analysis** - Verify you can get accurate holder data
4. **Skip social initially** - Can add later, not critical for MVP
5. **Focus on execution** - Get buying working before complex filtering
6. **Paper trade first** - No exceptions, even if you're confident

Remember: The goal isn't to catch every meme coin. It's to catch a few 10x winners while avoiding the 95% that go to zero. One 10x win covers many small losses.