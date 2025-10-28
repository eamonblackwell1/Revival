#!/usr/bin/env python3
"""
🧪 Simple Test for Revival Detection (No Complex Dependencies)
Tests the core functionality without needing the full environment
"""

import requests
import time
from datetime import datetime

def test_simple_revival():
    """Test revival detection with minimal dependencies"""

    print("="*60)
    print("🧪 SIMPLE REVIVAL DETECTION TEST")
    print("="*60)

    # Test tokens - Real Solana meme coins
    test_tokens = [
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
    ]

    for token_address in test_tokens:
        print(f"\n🔍 Testing token: {token_address[:16]}...")

        # Test 1: DexScreener API (FREE)
        print("\n1. Testing DexScreener API...")
        dex_data = test_dexscreener(token_address)
        if dex_data:
            print(f"   ✅ Token: {dex_data.get('symbol', 'Unknown')}")
            print(f"   ✅ Age: {dex_data.get('age_hours', 0):.1f} hours")
            print(f"   ✅ Liquidity: ${dex_data.get('liquidity', 0):,.0f}")
            print(f"   ✅ Volume: ${dex_data.get('volume', 0):,.0f}")

        # Test 2: GoPlus Security (FREE)
        print("\n2. Testing GoPlus Security API...")
        security = test_goplus(token_address)
        if security:
            print(f"   ✅ Honeypot: {security.get('honeypot', 'Unknown')}")
            print(f"   ✅ Mintable: {security.get('mintable', 'Unknown')}")

        # Test 3: GMGN API (FREE)
        print("\n3. Testing GMGN API...")
        gmgn_data = test_gmgn(token_address)
        if gmgn_data:
            print(f"   ✅ GMGN data retrieved")

        print("\n" + "-"*40)
        time.sleep(1)  # Rate limiting

def test_dexscreener(token_address):
    """Test DexScreener API"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('pairs'):
                pair = data['pairs'][0]

                # Calculate age
                created_at = pair.get('pairCreatedAt', 0)
                age_hours = (time.time() * 1000 - created_at) / (1000 * 3600)

                return {
                    'symbol': pair.get('baseToken', {}).get('symbol'),
                    'name': pair.get('baseToken', {}).get('name'),
                    'age_hours': age_hours,
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                    'volume': float(pair.get('volume', {}).get('h24', 0)),
                    'url': pair.get('url')
                }
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def test_goplus(token_address):
    """Test GoPlus Security API"""
    try:
        url = "https://api.gopluslabs.io/api/v1/token_security/sol"
        params = {'contract_addresses': token_address}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                # Handle case-insensitive address matching
                for key in data['result']:
                    if key.lower() == token_address.lower():
                        security = data['result'][key]
                        return {
                            'honeypot': 'Yes' if security.get('is_honeypot') == '1' else 'No',
                            'mintable': 'Yes' if security.get('is_mintable') == '1' else 'No',
                            'holders': security.get('holder_count', 'Unknown')
                        }
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def test_gmgn(token_address):
    """Test GMGN API"""
    try:
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return True
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def check_revival_pattern(token_data):
    """Simple revival pattern check"""
    if not token_data:
        return 0.0

    age = token_data.get('age_hours', 0)
    liquidity = token_data.get('liquidity', 0)
    volume = token_data.get('volume', 0)

    score = 0.0

    # Age score (24-72 hours is ideal)
    if 24 <= age <= 72:
        score += 0.33

    # Liquidity score
    if liquidity >= 10000:
        score += 0.33

    # Volume score
    if volume >= 10000:
        score += 0.34

    return score

def main():
    print("🚀 Testing Revival Detection APIs\n")
    print("This test checks if all FREE APIs are working correctly.\n")

    # Run simple test
    test_simple_revival()

    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)
    print("""
Next Steps:
1. If all APIs work, the system is ready
2. Get fresh 24-48hr tokens from: https://dexscreener.com/solana
3. Add them to the test_tokens list
4. Run the full orchestrator

To get better test tokens:
- Go to DexScreener
- Filter by age: 24-48 hours
- Look for liquidity > $5,000
- Copy token addresses
""")

if __name__ == "__main__":
    main()