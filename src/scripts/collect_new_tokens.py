"""
🚀 Token Collection Script
Fetches new Solana token launches from various sources
Built for Moon Dev's Revival Scanner
"""

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from termcolor import colored

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class TokenCollector:
    """Collects new token launches from multiple sources"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data" / "sniper_agent"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_age_hours = 72  # Only collect tokens < 72 hours old
        self.min_liquidity = 1000  # Minimum $1K liquidity

    def get_dexscreener_new_pairs(self, limit=100):
        """
        Get new Solana pairs from DexScreener

        Returns:
            List of token dictionaries
        """
        print(colored("\n🔍 Fetching new pairs from DexScreener...", "cyan"))

        tokens = []

        try:
            # DexScreener has multiple endpoints we can use
            # 1. Latest pairs for Solana
            url = "https://api.dexscreener.com/latest/dex/pairs/solana"
            response = requests.get(url, timeout=15)

            if response.status_code != 200:
                print(colored(f"⚠️ DexScreener returned status {response.status_code}", "yellow"))
                return tokens

            data = response.json()
            pairs = data.get('pairs', [])

            print(colored(f"📊 Found {len(pairs)} pairs from DexScreener", "green"))

            # Filter and process tokens
            current_time = time.time() * 1000  # Convert to milliseconds

            for pair in pairs:
                try:
                    # Get pair creation time
                    pair_created = pair.get('pairCreatedAt', 0)
                    if pair_created == 0:
                        continue

                    # Calculate age in hours
                    age_hours = (current_time - pair_created) / (1000 * 3600)

                    # Skip if too old
                    if age_hours > self.max_age_hours:
                        continue

                    # Get liquidity
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0))

                    # Skip if liquidity too low
                    if liquidity < self.min_liquidity:
                        continue

                    # Get base token address
                    token_address = pair.get('baseToken', {}).get('address')
                    if not token_address:
                        continue

                    # Create token record
                    token = {
                        'token_address': token_address,
                        'token_symbol': pair.get('baseToken', {}).get('symbol', 'Unknown'),
                        'token_name': pair.get('baseToken', {}).get('name', 'Unknown'),
                        'pair_address': pair.get('pairAddress', ''),
                        'dex': pair.get('dexId', ''),
                        'liquidity_usd': liquidity,
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                        'price_usd': float(pair.get('priceUsd', 0)),
                        'age_hours': age_hours,
                        'pair_created_at': pair_created,
                        'discovered_at': datetime.now().isoformat(),
                        'source': 'dexscreener'
                    }

                    tokens.append(token)

                except Exception as e:
                    continue

            print(colored(f"✅ Collected {len(tokens)} tokens under {self.max_age_hours}h old", "green"))

            # Rate limiting
            time.sleep(1)

        except Exception as e:
            print(colored(f"❌ Error fetching from DexScreener: {str(e)}", "red"))

        return tokens

    def get_dexscreener_boosted(self):
        """
        Get boosted/promoted tokens from DexScreener
        These are often new launches with marketing
        """
        print(colored("\n🎯 Fetching boosted tokens from DexScreener...", "cyan"))

        tokens = []

        try:
            url = "https://api.dexscreener.com/token-boosts/latest/v1"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()

                for item in data:
                    # Filter for Solana only
                    if item.get('chainId') != 'solana':
                        continue

                    token_address = item.get('tokenAddress')
                    if not token_address:
                        continue

                    # Get more details about this token
                    detail_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
                    detail_response = requests.get(detail_url, timeout=10)

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        pairs = detail_data.get('pairs', [])

                        if pairs:
                            main_pair = pairs[0]

                            # Calculate age
                            pair_created = main_pair.get('pairCreatedAt', 0)
                            if pair_created:
                                age_hours = (time.time() * 1000 - pair_created) / (1000 * 3600)

                                if age_hours <= self.max_age_hours:
                                    token = {
                                        'token_address': token_address,
                                        'token_symbol': main_pair.get('baseToken', {}).get('symbol', 'Unknown'),
                                        'token_name': main_pair.get('baseToken', {}).get('name', 'Unknown'),
                                        'pair_address': main_pair.get('pairAddress', ''),
                                        'dex': main_pair.get('dexId', ''),
                                        'liquidity_usd': float(main_pair.get('liquidity', {}).get('usd', 0)),
                                        'volume_24h': float(main_pair.get('volume', {}).get('h24', 0)),
                                        'price_usd': float(main_pair.get('priceUsd', 0)),
                                        'age_hours': age_hours,
                                        'pair_created_at': pair_created,
                                        'discovered_at': datetime.now().isoformat(),
                                        'source': 'dexscreener_boosted',
                                        'is_boosted': True
                                    }
                                    tokens.append(token)

                    time.sleep(0.5)  # Rate limiting

                print(colored(f"✅ Found {len(tokens)} boosted tokens", "green"))

        except Exception as e:
            print(colored(f"⚠️ Could not fetch boosted tokens: {str(e)}", "yellow"))

        return tokens

    def collect_all_tokens(self):
        """
        Collect tokens from all available sources

        Returns:
            DataFrame with all collected tokens
        """
        print(colored("="*60, "cyan"))
        print(colored("🚀 TOKEN COLLECTION STARTING", "cyan", attrs=['bold']))
        print(colored("="*60, "cyan"))

        all_tokens = []

        # Source 1: DexScreener new pairs
        tokens_dex = self.get_dexscreener_new_pairs(limit=100)
        all_tokens.extend(tokens_dex)

        # Source 2: DexScreener boosted tokens
        tokens_boosted = self.get_dexscreener_boosted()
        all_tokens.extend(tokens_boosted)

        if not all_tokens:
            print(colored("\n❌ No tokens collected!", "red"))
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(all_tokens)

        # Remove duplicates (same token from different sources)
        original_count = len(df)
        df = df.drop_duplicates(subset=['token_address'], keep='first')

        if len(df) < original_count:
            print(colored(f"🔄 Removed {original_count - len(df)} duplicate tokens", "yellow"))

        # Sort by age (newest first)
        df = df.sort_values('age_hours', ascending=True)

        print(colored(f"\n📊 Total unique tokens collected: {len(df)}", "green", attrs=['bold']))

        return df

    def save_tokens(self, df):
        """Save collected tokens to CSV"""
        if df.empty:
            print(colored("⚠️ No tokens to save", "yellow"))
            return

        try:
            # Save to recent_tokens.csv (used by revival scanner)
            recent_path = self.data_dir / "recent_tokens.csv"
            df.to_csv(recent_path, index=False)
            print(colored(f"💾 Saved to {recent_path}", "green"))

            # Also save timestamped version for history
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_path = self.data_dir / f"tokens_{timestamp}.csv"
            df.to_csv(history_path, index=False)
            print(colored(f"💾 Saved history to {history_path}", "green"))

            # Print summary
            self.print_summary(df)

        except Exception as e:
            print(colored(f"❌ Error saving tokens: {str(e)}", "red"))

    def print_summary(self, df):
        """Print collection summary"""
        print(colored("\n" + "="*60, "cyan"))
        print(colored("📈 COLLECTION SUMMARY", "cyan", attrs=['bold']))
        print(colored("="*60, "cyan"))

        # Age breakdown
        under_24h = len(df[df['age_hours'] < 24])
        between_24_48h = len(df[(df['age_hours'] >= 24) & (df['age_hours'] < 48)])
        between_48_72h = len(df[(df['age_hours'] >= 48) & (df['age_hours'] < 72)])

        print(colored(f"Age Distribution:", "yellow"))
        print(colored(f"  < 24 hours:     {under_24h} tokens", "white"))
        print(colored(f"  24-48 hours:    {between_24_48h} tokens (REVIVAL WINDOW)", "green"))
        print(colored(f"  48-72 hours:    {between_48_72h} tokens", "white"))

        # Liquidity stats
        avg_liq = df['liquidity_usd'].mean()
        max_liq = df['liquidity_usd'].max()

        print(colored(f"\nLiquidity Stats:", "yellow"))
        print(colored(f"  Average: ${avg_liq:,.0f}", "white"))
        print(colored(f"  Maximum: ${max_liq:,.0f}", "white"))

        # Show top 5 newest tokens
        print(colored(f"\n🏆 Top 5 Newest Tokens:", "yellow"))
        for i, row in df.head(5).iterrows():
            symbol = row['token_symbol']
            age = row['age_hours']
            liq = row['liquidity_usd']
            print(colored(f"  {symbol:<10} Age: {age:>5.1f}h | Liq: ${liq:>10,.0f}", "white"))

def main():
    """Run token collection"""
    collector = TokenCollector()

    # Collect tokens
    df = collector.collect_all_tokens()

    # Save results
    collector.save_tokens(df)

    print(colored("\n✅ Token collection complete!", "green", attrs=['bold']))
    print(colored("   Run the revival scanner to analyze these tokens", "cyan"))

if __name__ == "__main__":
    main()
