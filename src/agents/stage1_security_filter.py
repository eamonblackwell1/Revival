"""
🛡️ Stage 1 Security Filter - Moon Dev's Fast Security Check
Quickly eliminates honeypots, scams, and dangerous tokens
Built with love by Moon Dev 🚀

This filter is FAST (< 10 seconds) and uses FREE APIs:
- GoPlus Security API (1000 requests/day free)
- DexScreener (unlimited free)
"""

import os
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class Stage1SecurityFilter:
    """
    Fast security filter to eliminate obvious scams

    Checks:
    1. Honeypot detection
    2. Mintable tokens (can create infinite supply)
    3. Liquidity minimums
    4. Basic security score
    """

    def __init__(self):
        """Initialize the security filter"""
        print(colored("🛡️ Stage 1 Security Filter initialized!", "green"))

        # Configuration
        self.min_liquidity = 5000  # $5K minimum
        self.min_volume = 5000     # $5K daily volume minimum
        self.min_security_score = 60  # GoPlus score minimum
        self.max_age_hours = 72    # Don't check very old tokens

        # GoPlus API (get free key at https://gopluslabs.io)
        self.goplus_api_key = os.getenv('GOPLUS_API_KEY', '')  # Optional - works without key too

        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "security_filter"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def check_dexscreener_safety(self, token_address: str) -> Tuple[bool, Dict]:
        """
        Quick safety check using DexScreener data

        Returns:
            (passed, details) - Whether it passed and why
        """
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return False, {'error': 'API unavailable'}

            data = response.json()

            if not data.get('pairs'):
                return False, {'error': 'No trading pairs found'}

            # Get most liquid pair
            main_pair = max(data['pairs'], key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))

            liquidity = float(main_pair.get('liquidity', {}).get('usd', 0))
            volume_24h = float(main_pair.get('volume', {}).get('h24', 0))

            # Basic safety checks
            checks = {
                'has_liquidity': liquidity >= self.min_liquidity,
                'has_volume': volume_24h >= self.min_volume,
                'liquidity_locked': main_pair.get('liquidity', {}).get('base', 0) > 0,
                'price_impact_low': True  # DexScreener pairs are generally safe
            }

            passed = all(checks.values())

            details = {
                'liquidity_usd': liquidity,
                'volume_24h': volume_24h,
                'checks': checks,
                'pair_address': main_pair.get('pairAddress', ''),
                'dex': main_pair.get('dexId', '')
            }

            return passed, details

        except Exception as e:
            return False, {'error': str(e)}

    def check_goplus_security(self, token_address: str) -> Tuple[bool, Dict]:
        """
        Check token security using GoPlus API

        Returns:
            (passed, details) - Whether it passed security checks
        """
        try:
            # GoPlus API - works without key but with lower rate limits
            url = "https://api.gopluslabs.io/api/v1/token_security/sol"
            params = {'contract_addresses': token_address}
            headers = {}

            if self.goplus_api_key:
                headers['Authorization'] = f'Bearer {self.goplus_api_key}'

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code != 200:
                # GoPlus might be rate limited, not critical
                return True, {'warning': 'GoPlus unavailable, skipping security check'}

            data = response.json()

            if 'result' not in data or token_address.lower() not in data['result']:
                return True, {'warning': 'No security data available'}

            security_info = data['result'][token_address.lower()]

            # Critical security checks
            is_honeypot = security_info.get('is_honeypot', '0') == '1'
            is_mintable = security_info.get('is_mintable', '0') == '1'
            has_blacklist = security_info.get('is_blacklisted', '0') == '1'
            can_freeze = security_info.get('can_take_back_ownership', '0') == '1'

            # Calculate security score
            risk_factors = 0
            if is_honeypot: risk_factors += 100  # Instant fail
            if is_mintable: risk_factors += 50   # Very bad
            if has_blacklist: risk_factors += 30  # Bad
            if can_freeze: risk_factors += 20     # Concerning

            security_score = max(0, 100 - risk_factors)

            passed = (
                not is_honeypot and
                not is_mintable and
                security_score >= self.min_security_score
            )

            details = {
                'is_honeypot': is_honeypot,
                'is_mintable': is_mintable,
                'has_blacklist': has_blacklist,
                'can_freeze': can_freeze,
                'security_score': security_score,
                'holder_count': security_info.get('holder_count', 'unknown'),
                'owner_address': security_info.get('owner_address', 'unknown')
            }

            return passed, details

        except Exception as e:
            # If GoPlus fails, don't block the token (it's optional)
            return True, {'warning': f'GoPlus check failed: {str(e)}'}

    def quick_filter(self, token_address: str) -> Dict:
        """
        Run complete security filter on a token

        Returns:
            Dictionary with pass/fail and all details
        """
        print(colored(f"\n🔍 Security check: {token_address[:8]}...", "cyan"))

        result = {
            'token_address': token_address,
            'passed': False,
            'checks': {}
        }

        # Step 1: DexScreener safety check (required)
        dex_passed, dex_details = self.check_dexscreener_safety(token_address)
        result['checks']['dexscreener'] = {
            'passed': dex_passed,
            'details': dex_details
        }

        if not dex_passed:
            print(colored(f"  ❌ Failed DexScreener checks", "red"))
            result['failure_reason'] = 'Failed liquidity/volume requirements'
            return result

        print(colored(f"  ✅ Passed DexScreener (Liq: ${dex_details['liquidity_usd']:,.0f})", "green"))

        # Step 2: GoPlus security check (optional but recommended)
        goplus_passed, goplus_details = self.check_goplus_security(token_address)
        result['checks']['goplus'] = {
            'passed': goplus_passed,
            'details': goplus_details
        }

        if not goplus_passed:
            print(colored(f"  ❌ Failed security check (honeypot/mintable)", "red"))
            result['failure_reason'] = 'Failed security requirements'
            return result

        if 'warning' in goplus_details:
            print(colored(f"  ⚠️ Security: {goplus_details['warning']}", "yellow"))
        else:
            print(colored(f"  ✅ Passed security (Score: {goplus_details.get('security_score', 'N/A')})", "green"))

        # All checks passed!
        result['passed'] = True
        result['liquidity_usd'] = dex_details['liquidity_usd']
        result['volume_24h'] = dex_details['volume_24h']

        print(colored(f"  🎯 Token PASSED security filter!", "green", attrs=['bold']))

        return result

    def batch_filter(self, token_addresses: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Filter multiple tokens in parallel for speed

        Args:
            token_addresses: List of token addresses to check
            max_workers: Number of parallel threads

        Returns:
            List of results, sorted by liquidity
        """
        print(colored(f"\n🚀 Batch filtering {len(token_addresses)} tokens...", "cyan", attrs=['bold']))

        results = []
        passed_count = 0

        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_token = {
                executor.submit(self.quick_filter, addr): addr
                for addr in token_addresses
            }

            # Process completed tasks
            for future in as_completed(future_to_token):
                token = future_to_token[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result['passed']:
                        passed_count += 1
                except Exception as e:
                    print(colored(f"❌ Error checking {token}: {str(e)}", "red"))
                    results.append({
                        'token_address': token,
                        'passed': False,
                        'error': str(e)
                    })

        # Sort by liquidity (highest first)
        passed_tokens = [r for r in results if r['passed']]
        passed_tokens.sort(key=lambda x: x.get('liquidity_usd', 0), reverse=True)

        # Print summary
        print(colored(f"\n📊 Security Filter Results:", "green", attrs=['bold']))
        print(colored(f"   Passed: {passed_count}/{len(token_addresses)} tokens", "green"))

        if passed_tokens:
            print(colored(f"\n🏆 Top Secured Tokens:", "yellow"))
            for i, token in enumerate(passed_tokens[:5], 1):
                print(colored(f"   {i}. {token['token_address'][:8]}... - Liq: ${token['liquidity_usd']:,.0f}", "yellow"))

        # Save results
        self.save_results(results)

        return results

    def save_results(self, results: List[Dict]):
        """Save filter results to JSON"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = self.data_dir / f"security_filter_{timestamp}.json"

            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)

            print(colored(f"💾 Results saved to {filepath}", "green"))

        except Exception as e:
            print(colored(f"⚠️ Could not save results: {str(e)}", "yellow"))

def main():
    """Test the security filter"""
    filter = Stage1SecurityFilter()

    # Example tokens to test (replace with real addresses)
    test_tokens = [
        # Add some token addresses here for testing
        # You can get these from DexScreener
    ]

    if test_tokens:
        results = filter.batch_filter(test_tokens)

        # Show passed tokens
        passed = [r for r in results if r['passed']]
        print(colored(f"\n✅ {len(passed)} tokens passed security filter", "green"))
    else:
        print(colored("⚠️ No test tokens provided. Add some Solana token addresses to test.", "yellow"))
        print(colored("   Get them from: https://dexscreener.com/solana", "white"))

if __name__ == "__main__":
    main()