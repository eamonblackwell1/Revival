"""
📱 DexScreener Social Sentiment Utilities
Extract social signals and community data from DexScreener API
Built with love by Moon Dev 🚀

Provides:
- Boost counts (trending indicators)
- Social links (Twitter, Telegram, Discord)
- Community engagement metrics
- Volume and liquidity data
"""

import time
import requests
from typing import Optional, Dict, List
from termcolor import colored


def get_token_social_data(token_address: str) -> Optional[Dict]:
    """
    Get comprehensive social sentiment data from DexScreener

    Args:
        token_address: Solana token mint address

    Returns:
        Dictionary with social data, or None if failed
        {
            'token_address': str,
            'symbol': str,
            'name': str,
            'boosts': int,  # Trending indicator (higher = more visibility)
            'twitter': str,  # Twitter URL or None
            'telegram': str,  # Telegram URL or None
            'discord': str,  # Discord URL or None
            'website': str,  # Website URL or None
            'pair_created_at': int,  # Timestamp (ms)
            'liquidity_usd': float,
            'volume_1h': float,
            'volume_24h': float,
            'price_change_1h': float,
            'price_change_24h': float,
            'buys_24h': int,
            'sells_24h': int,
            'buy_sell_ratio': float,  # Sentiment indicator
            'dexscreener_url': str
        }

    API: https://api.dexscreener.com/latest/dex/tokens/{token_address}
    Rate Limit: 300 requests/minute (FREE)
    Cost: FREE
    """
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        pairs = data.get('pairs', [])

        if not pairs:
            return None

        # Get the most liquid pair (main trading pair)
        pairs = sorted(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
        main_pair = pairs[0]

        # Extract social links from info object
        info = main_pair.get('info', {})
        socials = info.get('socials', []) if info else []

        # Parse social links
        twitter_url = None
        telegram_url = None
        discord_url = None
        for social in socials:
            social_type = social.get('type', '').lower()
            if 'twitter' in social_type:
                twitter_url = social.get('url')
            elif 'telegram' in social_type:
                telegram_url = social.get('url')
            elif 'discord' in social_type:
                discord_url = social.get('url')

        # Get website from info
        websites = info.get('websites', []) if info else []
        website_url = websites[0].get('url') if websites else None

        # Extract boost data (premium feature on DexScreener)
        boosts = main_pair.get('boosts', {}).get('active', 0) if main_pair.get('boosts') else 0

        # Extract transaction data
        txns_24h = main_pair.get('txns', {}).get('h24', {})
        buys_24h = txns_24h.get('buys', 0)
        sells_24h = txns_24h.get('sells', 0)

        # Calculate buy/sell ratio (sentiment indicator)
        buy_sell_ratio = buys_24h / max(sells_24h, 1)  # Avoid division by zero

        # Extract volume data
        volume = main_pair.get('volume', {})
        volume_1h = float(volume.get('h1', 0))
        volume_24h = float(volume.get('h24', 0))

        # Extract price changes
        price_change = main_pair.get('priceChange', {})
        price_change_1h = float(price_change.get('h1', 0))
        price_change_24h = float(price_change.get('h24', 0))

        result = {
            'token_address': token_address,
            'symbol': main_pair.get('baseToken', {}).get('symbol', 'Unknown'),
            'name': main_pair.get('baseToken', {}).get('name', 'Unknown'),
            'boosts': boosts,
            'twitter': twitter_url,
            'telegram': telegram_url,
            'discord': discord_url,
            'website': website_url,
            'pair_created_at': main_pair.get('pairCreatedAt'),
            'liquidity_usd': float(main_pair.get('liquidity', {}).get('usd', 0)),
            'volume_1h': volume_1h,
            'volume_24h': volume_24h,
            'price_change_1h': price_change_1h,
            'price_change_24h': price_change_24h,
            'buys_24h': buys_24h,
            'sells_24h': sells_24h,
            'buy_sell_ratio': buy_sell_ratio,
            'dexscreener_url': main_pair.get('url', f'https://dexscreener.com/solana/{token_address}')
        }

        return result

    except Exception as e:
        print(colored(f"⚠️ Error fetching DexScreener data for {token_address[:8]}...: {str(e)}", "yellow"))
        return None


def batch_enrich_tokens(token_addresses: List[str], rate_limit_delay: float = 0.2) -> List[Dict]:
    """
    Batch enrich multiple tokens with social sentiment data

    Args:
        token_addresses: List of token mint addresses
        rate_limit_delay: Delay between requests (seconds)

    Returns:
        List of dictionaries with social data (excludes failed tokens)

    Rate Limiting:
        DexScreener FREE: 300 requests/minute = 5 req/sec
        We use 0.2s delay = 5 req/sec max (safe)

    Cost: FREE
    """
    results = []

    print(colored(f"\n📱 Enriching {len(token_addresses)} tokens with DexScreener social data...", "cyan"))

    for i, token_address in enumerate(token_addresses, 1):
        try:
            social_data = get_token_social_data(token_address)

            if social_data:
                results.append(social_data)

                # Pretty print key social signals
                symbol = social_data['symbol']
                boosts = social_data['boosts']
                has_twitter = "✅" if social_data['twitter'] else "❌"
                has_telegram = "✅" if social_data['telegram'] else "❌"
                buy_sell = social_data['buy_sell_ratio']

                print(colored(
                    f"  [{i}/{len(token_addresses)}] {symbol:<10} | "
                    f"Boosts: {boosts:>2} | Twitter: {has_twitter} | TG: {has_telegram} | "
                    f"B/S: {buy_sell:.2f}",
                    "green"
                ))
            else:
                print(colored(f"  [{i}/{len(token_addresses)}] {token_address[:8]}... = no data", "grey"))

            # Rate limiting
            if i < len(token_addresses):
                time.sleep(rate_limit_delay)

        except Exception as e:
            print(colored(f"  ❌ Error processing {token_address[:8]}...: {str(e)}", "red"))
            continue

    print(colored(f"\n✅ Successfully enriched {len(results)}/{len(token_addresses)} tokens", "green"))

    return results


def get_social_score(social_data: Dict) -> float:
    """
    Calculate a social sentiment score (0-1) based on available data

    Scoring factors:
    - Has boosts: +0.3
    - Has Twitter: +0.2
    - Has Telegram: +0.2
    - Has Discord: +0.1
    - Buy/sell ratio > 1.5: +0.2

    Args:
        social_data: Dictionary from get_token_social_data()

    Returns:
        Score from 0.0 to 1.0
    """
    score = 0.0

    # Boosts indicate community paid for visibility
    if social_data.get('boosts', 0) > 0:
        score += 0.3

    # Social presence indicates legitimacy
    if social_data.get('twitter'):
        score += 0.2

    if social_data.get('telegram'):
        score += 0.2

    if social_data.get('discord'):
        score += 0.1

    # Buying pressure indicates demand
    buy_sell_ratio = social_data.get('buy_sell_ratio', 0)
    if buy_sell_ratio >= 1.5:  # More buyers than sellers
        score += 0.2

    return min(score, 1.0)  # Cap at 1.0


def filter_by_social_criteria(
    enriched_tokens: List[Dict],
    min_social_score: float = 0.3,
    require_socials: bool = False
) -> List[Dict]:
    """
    Filter tokens based on social criteria

    Args:
        enriched_tokens: List of tokens from batch_enrich_tokens()
        min_social_score: Minimum social score (0-1)
        require_socials: If True, require at least Twitter or Telegram

    Returns:
        Filtered list of tokens
    """
    filtered = []

    for token in enriched_tokens:
        # Calculate social score
        score = get_social_score(token)
        token['social_score'] = score

        # Check minimum score
        if score < min_social_score:
            continue

        # Check social requirement
        if require_socials:
            has_socials = token.get('twitter') or token.get('telegram')
            if not has_socials:
                continue

        filtered.append(token)

    print(colored(f"🎯 {len(filtered)}/{len(enriched_tokens)} tokens passed social filters", "cyan"))

    return filtered


if __name__ == "__main__":
    # Test the module
    print(colored("\n📊 DexScreener Social Data Tester", "cyan", attrs=['bold']))
    print(colored("=" * 60, "cyan"))

    # Test with a known Solana token (replace with real address)
    print(colored("\n⚠️ To test, provide a Solana token mint address", "yellow"))
    print(colored("   Example: python src/dexscreener_utils.py <mint_address>", "white"))
    print(colored("\n   Or test batch enrichment:", "yellow"))
    print(colored("   python src/dexscreener_utils.py <mint1> <mint2> <mint3>", "white"))

    import sys
    if len(sys.argv) > 1:
        test_addresses = sys.argv[1:]
        print(colored(f"\n🔍 Testing with {len(test_addresses)} token(s)...", "cyan"))

        if len(test_addresses) == 1:
            # Single token test
            data = get_token_social_data(test_addresses[0])
            if data:
                print(colored("\n✅ Social Data Retrieved:", "green"))
                for key, value in data.items():
                    print(colored(f"  {key}: {value}", "white"))
            else:
                print(colored("\n❌ Failed to retrieve data", "red"))
        else:
            # Batch test
            results = batch_enrich_tokens(test_addresses)
            filtered = filter_by_social_criteria(results, min_social_score=0.3)

            print(colored(f"\n🏆 Tokens passing social filter:", "green"))
            for token in filtered:
                print(colored(
                    f"  {token['symbol']}: Score {token['social_score']:.2f} | "
                    f"Boosts: {token['boosts']} | Twitter: {bool(token['twitter'])}",
                    "yellow"
                ))
