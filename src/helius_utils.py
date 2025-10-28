"""
🔗 Helius RPC Utilities
Get accurate token creation timestamps from Solana blockchain
Built with love by Moon Dev 🚀

Uses Helius RPC to query on-chain data for token age verification
"""

import os
import time
import requests
from typing import Optional, Dict, List
from termcolor import colored


def get_token_creation_timestamp(mint_address: str, rpc_url: str) -> Optional[int]:
    """
    Get token creation timestamp from Solana blockchain using Helius RPC

    Args:
        mint_address: Token mint address (base58 string)
        rpc_url: Helius RPC endpoint URL with API key

    Returns:
        Unix timestamp (seconds) of token creation, or None if failed

    Method:
        1. Call getSignaturesForAddress to get first transaction signature
        2. Call getTransaction to get block time

    Cost: 2 Helius credits (1 per RPC call)
    """
    try:
        # Step 1: Get the oldest signature for this mint address
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                mint_address,
                {
                    "limit": 1000  # Max limit to find oldest transaction
                }
            ]
        }

        response = requests.post(rpc_url, json=payload, timeout=15)

        if response.status_code != 200:
            print(colored(f"❌ Helius RPC error: HTTP {response.status_code}", "red"))
            return None

        data = response.json()

        if 'error' in data:
            print(colored(f"❌ RPC error: {data['error']}", "red"))
            return None

        signatures = data.get('result', [])

        if not signatures:
            return None

        # Get the oldest signature (last in the list, as they're returned newest-first)
        oldest_sig = signatures[-1]['signature']

        # Step 2: Get transaction details to extract block time
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "getTransaction",
            "params": [
                oldest_sig,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }

        response = requests.post(rpc_url, json=payload, timeout=15)

        if response.status_code != 200:
            return None

        data = response.json()

        if 'error' in data:
            return None

        # Extract blockTime (Unix timestamp)
        block_time = data.get('result', {}).get('blockTime')

        return block_time

    except Exception as e:
        print(colored(f"⚠️ Error getting token age for {mint_address[:8]}...: {str(e)}", "yellow"))
        return None


def get_token_age_hours(mint_address: str, rpc_url: str) -> Optional[float]:
    """
    Get token age in hours

    Args:
        mint_address: Token mint address
        rpc_url: Helius RPC endpoint URL

    Returns:
        Age in hours (float), or None if failed
    """
    timestamp = get_token_creation_timestamp(mint_address, rpc_url)

    if timestamp is None:
        return None

    current_time = time.time()
    age_seconds = current_time - timestamp
    age_hours = age_seconds / 3600

    return age_hours


def batch_get_token_ages(mint_addresses: List[str], rpc_url: str, rate_limit_delay: float = 0.1) -> Dict[str, float]:
    """
    Batch process multiple tokens to get their ages

    Args:
        mint_addresses: List of token mint addresses
        rpc_url: Helius RPC endpoint URL
        rate_limit_delay: Delay between requests (seconds) to respect 10 req/sec limit

    Returns:
        Dictionary mapping {address: age_hours}

    Rate Limiting:
        Helius FREE tier: 10 requests/second
        We use 0.1s delay = 10 req/sec max

    Cost:
        2 credits per token (getSignaturesForAddress + getTransaction)
    """
    results = {}

    print(colored(f"\n⏰ Checking ages for {len(mint_addresses)} tokens via Helius blockchain...", "cyan"))

    for i, mint_address in enumerate(mint_addresses, 1):
        try:
            age_hours = get_token_age_hours(mint_address, rpc_url)

            if age_hours is not None:
                results[mint_address] = age_hours
                print(colored(f"  [{i}/{len(mint_addresses)}] {mint_address[:8]}... = {age_hours:.1f}h", "green"))
            else:
                print(colored(f"  [{i}/{len(mint_addresses)}] {mint_address[:8]}... = failed", "grey"))

            # Rate limiting - respect Helius 10 req/sec limit
            if i < len(mint_addresses):  # Don't sleep after last request
                time.sleep(rate_limit_delay)

        except Exception as e:
            print(colored(f"  ❌ Error processing {mint_address[:8]}...: {str(e)}", "red"))
            continue

    print(colored(f"\n✅ Successfully retrieved {len(results)}/{len(mint_addresses)} token ages", "green"))

    return results


# Quick test function
def test_helius_connection(rpc_url: str) -> bool:
    """
    Test Helius RPC connection

    Args:
        rpc_url: Helius RPC endpoint URL

    Returns:
        True if connection successful, False otherwise
    """
    try:
        print(colored("\n🔍 Testing Helius RPC connection...", "cyan"))

        # Simple getHealth check
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getHealth"
        }

        response = requests.post(rpc_url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'result' in data and data['result'] == 'ok':
                print(colored("✅ Helius RPC connection successful!", "green"))
                return True

        print(colored("❌ Helius RPC connection failed", "red"))
        return False

    except Exception as e:
        print(colored(f"❌ Connection test error: {str(e)}", "red"))
        return False


if __name__ == "__main__":
    # Test the module
    from dotenv import load_dotenv
    load_dotenv()

    rpc_url = os.getenv('HELIUS_RPC_ENDPOINT')

    if not rpc_url or 'your_' in rpc_url:
        print(colored("❌ HELIUS_RPC_ENDPOINT not configured in .env", "red"))
        exit(1)

    # Test connection
    test_helius_connection(rpc_url)

    # Test with a known token (you can replace with a real Solana token address)
    print(colored("\n📊 To test with a real token, provide a mint address:", "yellow"))
    print(colored("   Example: python src/helius_utils.py <mint_address>", "white"))
