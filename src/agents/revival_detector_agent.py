"""
🌙 Moon Dev's Revival Pattern Detector
Identifies meme coins showing "second life" patterns 24-48 hours after launch
Built with love by Moon Dev 🚀

This agent looks for tokens that:
1. Had an initial pump and dump (normal for meme coins)
2. Found a price floor after 12-24 hours
3. Show signs of renewed interest (revival pattern)
"""

import os
import sys
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from termcolor import colored
from typing import Dict, List, Optional, Tuple
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import existing utilities
from src.nice_funcs import (
    get_data,  # OHLCV data function
    token_overview,
    token_price
)
from src.config import *

class RevivalDetectorAgent:
    """
    Detects tokens showing revival patterns 24-48 hours after launch.

    Revival Pattern:
    - Hour 0-6: Initial pump
    - Hour 6-12: Dump (paperhands exit)
    - Hour 12-24: Consolidation
    - Hour 24-48: Revival signals emerge
    """

    def __init__(self):
        """Initialize the Revival Detector"""
        print(colored("🔄 Moon Dev's Revival Detector initialized!", "cyan"))

        # Configuration
        self.min_age_hours = MIN_AGE_HOURS  # Don't look at tokens younger than this
        self.max_age_hours = MAX_AGE_HOURS  # Maximum 6 months - prevents analyzing years-old tokens
        self.min_liquidity = MIN_LIQUIDITY_STRICT  # Minimum liquidity (serious projects only)
        self.min_holders = 50  # Minimum holder count

        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "revival_detector"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Cache for API calls (reduce rate limit issues)
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache

    def get_token_age_hours(self, token_address: str) -> Optional[float]:
        """
        Get token age in hours using DexScreener (FREE API)

        Returns:
            Age in hours, or None if not found
        """
        try:
            # Check cache first
            cache_key = f"age_{token_address}"
            if cache_key in self.cache:
                cached_time, cached_value = self.cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    return cached_value

            # DexScreener API - completely free, no key needed
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()

            # Find the oldest pair (original launch)
            if not data.get('pairs'):
                return None

            oldest_timestamp = min(pair['pairCreatedAt'] for pair in data['pairs'])
            age_hours = (time.time() * 1000 - oldest_timestamp) / (1000 * 3600)

            # Cache the result
            self.cache[cache_key] = (time.time(), age_hours)

            return age_hours

        except Exception as e:
            print(colored(f"❌ Error getting token age: {str(e)}", "red"))
            return None

    def get_token_overview(self, token_address: str) -> Optional[Dict]:
        """
        Get comprehensive token data from BirdEye Token Overview API
        This provides FDV, holder count, creation info in ONE API call (more efficient!)

        Returns:
            Dictionary with comprehensive token metrics
        """
        try:
            # Check cache first
            cache_key = f"overview_{token_address}"
            if cache_key in self.cache:
                cached_time, cached_value = self.cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    return cached_value

            # BirdEye Token Overview API
            url = f"https://public-api.birdeye.so/defi/token_overview?address={token_address}"
            headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(colored(f"    ⚠️ BirdEye Token Overview API error: HTTP {response.status_code}", "yellow"))
                return None

            data = response.json()

            if not data.get('success'):
                print(colored(f"    ⚠️ BirdEye API returned success=false", "yellow"))
                return None

            token_data = data.get('data', {})

            # Calculate age from creation timestamp
            creation_time = token_data.get('creationTime')
            age_hours = None
            if creation_time:
                age_hours = (time.time() - creation_time) / 3600  # Convert seconds to hours

            overview = {
                'token_address': token_address,
                'symbol': token_data.get('symbol', 'Unknown'),
                'name': token_data.get('name', 'Unknown'),
                'decimals': token_data.get('decimals', 9),
                'liquidity_usd': float(token_data.get('liquidity', 0)),
                'market_cap': float(token_data.get('mc', 0)),
                'fdv': float(token_data.get('realMc', 0)),  # Fully diluted valuation
                'price_usd': float(token_data.get('price', 0)),
                'price_change_24h': float(token_data.get('v24hChangePercent', 0)),
                'volume_24h': float(token_data.get('v24hUSD', 0)),
                'holder_count': int(token_data.get('holder', 0)),
                'creation_time': creation_time,  # Unix timestamp
                'age_hours': age_hours,
                'creator': token_data.get('creator'),
            }

            # Cache the result
            self.cache[cache_key] = (time.time(), overview)

            return overview

        except Exception as e:
            print(colored(f"❌ Error fetching token overview: {str(e)}", "red"))
            return None

    def get_dexscreener_data(self, token_address: str) -> Optional[Dict]:
        """
        Get comprehensive data from DexScreener

        Returns:
            Dictionary with liquidity, volume, price changes
        """
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()

            if not data.get('pairs'):
                return None

            # Get the most liquid pair
            pairs = sorted(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
            main_pair = pairs[0]

            return {
                'token_address': token_address,
                'token_symbol': main_pair.get('baseToken', {}).get('symbol', 'Unknown'),
                'token_name': main_pair.get('baseToken', {}).get('name', 'Unknown'),
                'age_hours': self.get_token_age_hours(token_address),
                'liquidity_usd': float(main_pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(main_pair.get('volume', {}).get('h24', 0)),
                'price_usd': float(main_pair.get('priceUsd', 0)),
                'price_change_24h': float(main_pair.get('priceChange', {}).get('h24', 0)),
                'price_change_6h': float(main_pair.get('priceChange', {}).get('h6', 0)),
                'price_change_1h': float(main_pair.get('priceChange', {}).get('h1', 0)),
                'txns_24h': main_pair.get('txns', {}).get('h24', {}).get('buys', 0) +
                           main_pair.get('txns', {}).get('h24', {}).get('sells', 0),
                'buys_24h': main_pair.get('txns', {}).get('h24', {}).get('buys', 0),
                'sells_24h': main_pair.get('txns', {}).get('h24', {}).get('sells', 0),
                'url': main_pair.get('url', ''),
            }

        except Exception as e:
            print(colored(f"❌ Error fetching DexScreener data: {str(e)}", "red"))
            return None

    def analyze_price_pattern(self, token_address: str, token_data: Dict) -> Tuple[float, Dict]:
        """
        Analyze price action for revival patterns

        Returns:
            (score, details) - Score 0-1, details dictionary
        """
        try:
            print(colored(f"  📊 Analyzing price pattern...", "yellow"))

            # Get OHLCV data from BirdEye (we already have this API)
            ohlcv = get_data(token_address, days_back_4_data=3, timeframe='1H')

            if ohlcv is None or len(ohlcv) < 24:
                return 0.0, {'error': 'Insufficient price data'}

            # Convert to list for easier analysis
            prices = ohlcv['Close'].tolist()
            volumes = ohlcv['Volume'].tolist()

            # Find the peak in first 12 hours
            early_peak = max(prices[:min(12, len(prices))])

            # Find the floor after dump (hours 12-24)
            if len(prices) >= 24:
                floor_price = min(prices[12:24])
            else:
                floor_price = min(prices[12:])

            # Current price (last available)
            current_price = prices[-1]

            # Calculate key metrics
            dump_severity = (floor_price / early_peak) if early_peak > 0 else 1
            recovery_ratio = (current_price / floor_price) if floor_price > 0 else 1

            # Check for higher lows in recent hours (bullish pattern)
            recent_prices = prices[-6:] if len(prices) >= 6 else prices
            higher_lows = self.check_higher_lows(recent_prices)

            # Volume analysis - is volume returning?
            recent_volume_avg = np.mean(volumes[-6:]) if len(volumes) >= 6 else 0
            older_volume_avg = np.mean(volumes[12:18]) if len(volumes) >= 18 else recent_volume_avg
            volume_increase = (recent_volume_avg / older_volume_avg) if older_volume_avg > 0 else 1

            # Calculate revival score
            score = 0.0

            # 1. Did it dump enough? (Need 40-80% dump for good entry)
            if 0.2 <= dump_severity <= 0.6:
                score += 0.25

            # 2. Is it recovering? (Up 20%+ from floor)
            if recovery_ratio >= 1.2:
                score += 0.25

            # 3. Higher lows pattern?
            if higher_lows:
                score += 0.25

            # 4. Volume returning?
            if volume_increase >= 1.5:
                score += 0.25

            details = {
                'early_peak': early_peak,
                'floor_price': floor_price,
                'current_price': current_price,
                'dump_severity': dump_severity,
                'recovery_ratio': recovery_ratio,
                'higher_lows': higher_lows,
                'volume_increase': volume_increase,
                'price_data_points': len(prices)
            }

            return score, details

        except Exception as e:
            print(colored(f"    ❌ Price pattern analysis error: {str(e)}", "red"))
            return 0.0, {'error': str(e)}

    def check_higher_lows(self, prices: List[float]) -> bool:
        """Check if prices show higher lows (uptrend starting)"""
        if len(prices) < 3:
            return False

        lows = []
        for i in range(1, len(prices) - 1):
            if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                lows.append(prices[i])

        if len(lows) < 2:
            return False

        # Check if lows are ascending
        return all(lows[i] < lows[i+1] for i in range(len(lows)-1))

    def check_holder_distribution(self, token_address: str) -> Tuple[bool, Dict]:
        """
        Check holder distribution using BirdEye Holder API
        Rejects tokens with too much concentration (whale/rug risk)

        Returns:
            (is_safe, details) - True if distribution is healthy, details dictionary
        """
        try:
            print(colored(f"  👥 Checking holder distribution...", "yellow"))

            # BirdEye Token Holders API
            url = f"https://public-api.birdeye.so/defi/v3/token/holder?address={token_address}&offset=0&limit=10"
            headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(colored(f"    ⚠️ BirdEye Holder API error: HTTP {response.status_code}", "yellow"))
                # If we can't get holder data, don't block the token
                return True, {'error': f'BirdEye API error: HTTP {response.status_code}'}

            data = response.json()

            if not data.get('success'):
                print(colored(f"    ⚠️ BirdEye API returned success=false", "yellow"))
                return True, {'error': 'BirdEye API returned success=false'}

            # Get holder data
            holders = data.get('data', {}).get('items', [])

            if not holders:
                print(colored(f"    ⚠️ No holder data available", "yellow"))
                return True, {'error': 'No holder data available'}

            # Calculate top 10 concentration
            total_supply = sum(float(h.get('uiAmount', 0)) for h in holders)
            top_10_holdings = sum(float(h.get('uiAmount', 0)) for h in holders[:10])

            if total_supply > 0:
                top_10_percentage = (top_10_holdings / total_supply) * 100
            else:
                top_10_percentage = 0

            # Safety threshold: Reject if top 10 holders own > 70%
            is_safe = top_10_percentage <= 70.0

            details = {
                'top_10_percentage': top_10_percentage,
                'total_supply_checked': total_supply,
                'holder_count': len(holders),
                'is_safe': is_safe
            }

            if is_safe:
                print(colored(f"    ✅ Distribution OK: Top 10 hold {top_10_percentage:.1f}%", "green"))
            else:
                print(colored(f"    ⚠️ CONCENTRATED: Top 10 hold {top_10_percentage:.1f}% (>70% threshold)", "red"))

            return is_safe, details

        except Exception as e:
            print(colored(f"    ❌ Holder distribution check error: {str(e)}", "red"))
            # On error, don't block the token
            return True, {'error': str(e)}

    def check_smart_money(self, token_address: str) -> Tuple[float, Dict]:
        """
        Check for smart money activity using BirdEye Top Traders API

        Returns:
            (score, details) - Score 0-1, details dictionary
        """
        try:
            print(colored(f"  💰 Checking smart money activity (BirdEye Top Traders)...", "yellow"))

            # BirdEye Top Traders API
            url = f"https://public-api.birdeye.so/defi/v2/tokens/top_traders?address={token_address}"
            headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(colored(f"    ⚠️ BirdEye Top Traders API error: HTTP {response.status_code}", "yellow"))
                return 0.0, {'error': f'BirdEye API error: HTTP {response.status_code}'}

            data = response.json()

            if not data.get('success'):
                print(colored(f"    ⚠️ BirdEye API returned success=false", "yellow"))
                return 0.0, {'error': 'BirdEye API returned success=false'}

            # Get top traders data
            traders = data.get('data', {}).get('items', [])

            if not traders:
                print(colored(f"    ⚠️ No trader data available", "yellow"))
                return 0.0, {'error': 'No trader data available'}

            # Analyze whale wallets (>$100K holdings)
            whale_wallets = 0
            total_traders = len(traders[:20])  # Check top 20 traders
            total_value_usd = 0

            for trader in traders[:20]:
                value_usd = float(trader.get('value_usd', 0))
                total_value_usd += value_usd

                # Consider wallet a "whale" if holdings > $100K
                if value_usd > 100000:
                    whale_wallets += 1

            # Calculate average holding value
            avg_holding_usd = total_value_usd / max(total_traders, 1)

            # Calculate score based on whale wallet presence
            # More whales = more smart money confidence
            score = 0.0
            if whale_wallets >= 5:
                score = 1.0
            elif whale_wallets >= 3:
                score = 0.75
            elif whale_wallets >= 2:
                score = 0.5
            elif whale_wallets >= 1:
                score = 0.25

            details = {
                'whale_wallets': whale_wallets,
                'total_traders_checked': total_traders,
                'whale_percentage': (whale_wallets / max(total_traders, 1)) * 100,
                'avg_holding_usd': avg_holding_usd,
                'total_smart_money_usd': total_value_usd
            }

            print(colored(f"    🐋 Found {whale_wallets} whale wallets (>${100000:,})", "cyan"))

            return score, details

        except Exception as e:
            print(colored(f"    ❌ Smart money check error: {str(e)}", "red"))
            return 0.0, {'error': str(e)}

    def calculate_revival_score(self, token_address: str) -> Dict:
        """
        Calculate comprehensive revival score for a token

        Returns:
            Dictionary with score and all details
        """
        print(colored(f"\n🔍 Analyzing token: {token_address[:8]}...", "cyan"))

        # Get comprehensive data from BirdEye Token Overview (more efficient than DexScreener)
        token_overview = self.get_token_overview(token_address)

        if not token_overview:
            print(colored("  ⚠️ Could not fetch token overview, falling back to DexScreener...", "yellow"))
            # Fallback to DexScreener if BirdEye fails
            token_data = self.get_dexscreener_data(token_address)
            if not token_data:
                return {
                    'token_address': token_address,
                    'revival_score': 0.0,
                    'error': 'Could not fetch token data from any source'
                }
        else:
            # Use BirdEye overview data (preferred)
            token_data = token_overview

        # Check age requirements (both minimum and maximum)
        age = token_data.get('age_hours', 0)
        if age < self.min_age_hours:
            return {
                'token_address': token_address,
                'revival_score': 0.0,
                'error': f'Token age {age:.1f}h below minimum {self.min_age_hours}h'
            }

        if self.max_age_hours and age > self.max_age_hours:
            return {
                'token_address': token_address,
                'revival_score': 0.0,
                'error': f'Token age {age:.1f}h above maximum {self.max_age_hours}h ({self.max_age_hours/24:.0f} days)'
            }

        # Check liquidity requirement
        liquidity = token_data.get('liquidity_usd', 0)
        if liquidity < self.min_liquidity:
            return {
                'token_address': token_address,
                'revival_score': 0.0,
                'error': f'Liquidity ${liquidity:.0f} below minimum ${self.min_liquidity}'
            }

        # Check holder distribution (safety check before analysis)
        is_safe, holder_details = self.check_holder_distribution(token_address)
        if not is_safe:
            return {
                'token_address': token_address,
                'revival_score': 0.0,
                'error': f'Unsafe holder distribution: Top 10 hold {holder_details.get("top_10_percentage", 0):.1f}%'
            }

        # Analyze price pattern
        price_score, price_details = self.analyze_price_pattern(token_address, token_data)

        # Check smart money
        smart_score, smart_details = self.check_smart_money(token_address)

        # Calculate volume score from DexScreener data
        volume_score = 0.0
        if token_data.get('volume_24h', 0) > 50000:  # $50K volume (sustained activity)
            volume_score += 0.5
        if token_data.get('buys_24h', 0) > token_data.get('sells_24h', 0):  # More buys than sells
            volume_score += 0.5

        # Calculate final revival score (weighted average)
        revival_score = (
            price_score * 0.5 +      # 50% weight on price pattern
            smart_score * 0.3 +      # 30% weight on smart money
            volume_score * 0.2       # 20% weight on volume
        )

        result = {
            'token_address': token_address,
            'token_symbol': token_data.get('token_symbol') or token_data.get('symbol'),
            'token_name': token_data.get('token_name') or token_data.get('name'),
            'age_hours': age,
            'liquidity_usd': liquidity,
            'volume_24h': token_data.get('volume_24h'),
            'price_change_24h': token_data.get('price_change_24h'),
            'holder_count': token_data.get('holder_count', 0),
            'market_cap': token_data.get('market_cap', 0),
            'fdv': token_data.get('fdv', 0),
            'revival_score': revival_score,
            'price_score': price_score,
            'smart_score': smart_score,
            'volume_score': volume_score,
            'price_details': price_details,
            'smart_details': smart_details,
            'holder_details': holder_details,
            'dexscreener_url': token_data.get('url'),
            'timestamp': datetime.now().isoformat()
        }

        # Print summary
        print(colored(f"  ✅ {token_data.get('token_symbol', 'Unknown')} Revival Score: {revival_score:.2f}", "green"))
        print(colored(f"     Price: {price_score:.2f} | Smart: {smart_score:.2f} | Volume: {volume_score:.2f}", "white"))

        return result

    def scan_tokens(self, token_list: Optional[List[str]] = None) -> List[Dict]:
        """
        Scan a list of tokens for revival patterns

        Args:
            token_list: Optional list of token addresses. If None, will fetch from sniper_agent data

        Returns:
            List of tokens sorted by revival score
        """
        print(colored("\n🚀 Starting Revival Pattern Scan...", "cyan", attrs=['bold']))

        # If no token list provided, try to get recent tokens from sniper_agent data
        if token_list is None:
            token_list = self.get_recent_tokens()

        if not token_list:
            print(colored("❌ No tokens to scan!", "red"))
            return []

        print(colored(f"📊 Scanning {len(token_list)} tokens...", "cyan"))

        results = []
        for token_address in token_list:
            try:
                result = self.calculate_revival_score(token_address)
                if result['revival_score'] > 0:
                    results.append(result)

                # Rate limiting - be nice to free APIs
                time.sleep(1)

            except Exception as e:
                print(colored(f"❌ Error scanning {token_address}: {str(e)}", "red"))
                continue

        # Sort by revival score
        results.sort(key=lambda x: x['revival_score'], reverse=True)

        # Save results
        self.save_results(results)

        # Print summary
        print(colored(f"\n📈 Revival Scan Complete!", "green", attrs=['bold']))
        print(colored(f"   Found {len(results)} potential revivals", "green"))

        if results:
            print(colored(f"\n🏆 Top Revival Candidates:", "yellow", attrs=['bold']))
            for i, token in enumerate(results[:5], 1):
                print(colored(f"   {i}. {token['token_symbol']} - Score: {token['revival_score']:.2f}", "yellow"))
                print(colored(f"      Age: {token['age_hours']:.1f}h | Liquidity: ${token['liquidity_usd']:,.0f} | Volume: ${token['volume_24h']:,.0f}", "white"))

        return results

    def get_recent_tokens(self) -> List[str]:
        """
        Get recent tokens from sniper_agent data or other sources

        Returns:
            List of token addresses
        """
        try:
            # Try to read from sniper_agent data
            sniper_file = Path(__file__).parent.parent / "data" / "sniper_agent" / "recent_tokens.csv"

            if sniper_file.exists():
                df = pd.read_csv(sniper_file)
                # Get unique token addresses
                if 'token_address' in df.columns:
                    return df['token_address'].unique().tolist()
                elif 'address' in df.columns:
                    return df['address'].unique().tolist()

            # If no sniper data, return empty list
            return []

        except Exception as e:
            print(colored(f"⚠️ Could not load recent tokens: {str(e)}", "yellow"))
            return []

    def save_results(self, results: List[Dict]):
        """Save scan results to CSV and JSON"""
        try:
            if not results:
                return

            # Save as CSV
            df = pd.DataFrame(results)
            csv_path = self.data_dir / f"revival_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(csv_path, index=False)
            print(colored(f"💾 Results saved to {csv_path}", "green"))

            # Also save as JSON for detailed data
            json_path = self.data_dir / f"revival_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)

        except Exception as e:
            print(colored(f"⚠️ Could not save results: {str(e)}", "yellow"))

def main():
    """Test the revival detector with sample tokens"""
    detector = RevivalDetectorAgent()

    # Example: Test with specific tokens (replace with real addresses)
    test_tokens = [
        # Add some 24-48 hour old token addresses here for testing
        # You can get these from DexScreener or your sniper_agent data
    ]

    if not test_tokens:
        print(colored("\n📝 No test tokens specified. Trying to load from sniper data...", "yellow"))
        test_tokens = detector.get_recent_tokens()[:10]  # Test with first 10

    if test_tokens:
        results = detector.scan_tokens(test_tokens)
    else:
        print(colored("⚠️ No tokens available for testing. Please provide token addresses.", "yellow"))
        print(colored("   You can get these from https://dexscreener.com/solana", "white"))

if __name__ == "__main__":
    main()