#!/usr/bin/env python3
"""
🧪 Test Script for Revival Pattern Detection System
Tests with real Solana token addresses
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.agents.revival_detector_agent import RevivalDetectorAgent
from src.agents.stage1_security_filter import Stage1SecurityFilter
from src.agents.meme_notifier_agent import MemeNotifierAgent
from termcolor import colored
import time

def test_with_real_tokens():
    """Test the system with real Solana tokens"""

    print(colored("="*60, "cyan"))
    print(colored("🧪 TESTING REVIVAL DETECTION SYSTEM", "cyan", attrs=['bold']))
    print(colored("="*60, "cyan"))

    # Initialize components
    print(colored("\n📦 Initializing components...", "yellow"))
    security_filter = Stage1SecurityFilter()
    revival_detector = RevivalDetectorAgent()
    notifier = MemeNotifierAgent()

    # Test tokens - These are real Solana meme coins
    # You should replace these with 24-48 hour old tokens for best results
    test_tokens = [
        # Popular Solana meme coins (might be too old, but good for testing)
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
        "CULLycmZLei3uidSR5e8sjDJxG9u5WKipp6NU8CULLEN",  # CULLEN
        # Add more recent tokens here - get from:
        # https://dexscreener.com/solana/new-pairs
        # Look for tokens that are 24-48 hours old
    ]

    print(colored(f"\n🎯 Testing with {len(test_tokens)} tokens", "cyan"))
    print(colored("   (For best results, use 24-48 hour old tokens)", "yellow"))

    # Step 1: Test Security Filter
    print(colored("\n" + "="*40, "green"))
    print(colored("STEP 1: SECURITY FILTER TEST", "green", attrs=['bold']))
    print(colored("="*40, "green"))

    security_results = []
    for token in test_tokens:
        print(colored(f"\nChecking: {token[:16]}...", "cyan"))
        result = security_filter.quick_filter(token)
        security_results.append(result)

        if result['passed']:
            print(colored("✅ PASSED security", "green"))
        else:
            print(colored(f"❌ FAILED: {result.get('failure_reason', 'Unknown')}", "red"))

        time.sleep(1)  # Rate limiting

    passed_security = [r['token_address'] for r in security_results if r['passed']]
    print(colored(f"\n📊 Security Summary: {len(passed_security)}/{len(test_tokens)} passed", "cyan"))

    if not passed_security:
        print(colored("\n⚠️ No tokens passed security. Try different tokens.", "yellow"))
        print(colored("   Get fresh tokens from: https://dexscreener.com/solana", "white"))
        return

    # Step 2: Test Revival Detection
    print(colored("\n" + "="*40, "green"))
    print(colored("STEP 2: REVIVAL PATTERN TEST", "green", attrs=['bold']))
    print(colored("="*40, "green"))

    revival_results = []
    for token in passed_security:
        print(colored(f"\nAnalyzing revival pattern: {token[:16]}...", "cyan"))
        result = revival_detector.calculate_revival_score(token)
        revival_results.append(result)

        score = result.get('revival_score', 0)
        if score > 0:
            print(colored(f"🔄 Revival Score: {score:.2f}", "green"))
        else:
            print(colored(f"❌ No revival pattern (Score: {score:.2f})", "red"))

        time.sleep(2)  # Rate limiting

    # Filter for meaningful scores
    good_revivals = [r for r in revival_results if r.get('revival_score', 0) > 0.4]

    print(colored(f"\n📊 Revival Summary: {len(good_revivals)} tokens show revival patterns", "cyan"))

    # Step 3: Test Notifications
    if good_revivals:
        print(colored("\n" + "="*40, "green"))
        print(colored("STEP 3: NOTIFICATION TEST", "green", attrs=['bold']))
        print(colored("="*40, "green"))

        notifier.batch_alert(good_revivals)

        print(colored("\n✅ Notifications sent!", "green"))
    else:
        print(colored("\n⚠️ No revival patterns found to notify", "yellow"))

    # Final Summary
    print(colored("\n" + "="*60, "cyan"))
    print(colored("📊 TEST COMPLETE", "cyan", attrs=['bold']))
    print(colored("="*60, "cyan"))

    print(colored(f"""
Test Results:
- Tokens Tested: {len(test_tokens)}
- Passed Security: {len(passed_security)}
- Revival Patterns Found: {len(good_revivals)}
""", "white"))

    if good_revivals:
        print(colored("Top Revival Candidates:", "yellow", attrs=['bold']))
        for token in sorted(good_revivals, key=lambda x: x.get('revival_score', 0), reverse=True)[:3]:
            symbol = token.get('token_symbol', 'Unknown')
            score = token.get('revival_score', 0)
            age = token.get('age_hours', 0)
            print(colored(f"  • {symbol}: Score {score:.2f} (Age: {age:.1f}h)", "yellow"))

def get_fresh_tokens_from_dexscreener():
    """
    Helper to get fresh 24-48hr tokens from DexScreener
    Run this separately to find good test candidates
    """
    import requests
    from datetime import datetime

    print(colored("\n🔍 Fetching recent Solana tokens from DexScreener...", "cyan"))

    # This is a workaround - DexScreener doesn't have a direct API for this
    # You'll need to manually check their website for 24-48hr old tokens

    print(colored("""
To find good test tokens:
1. Go to: https://dexscreener.com/solana
2. Click "New Pairs" tab
3. Scroll to find tokens that are 24-48 hours old
4. Copy their addresses and add to test_tokens list above

Look for tokens with:
- Age: 24-48 hours
- Liquidity: >$5,000
- Volume: >$10,000
- Not rugged (price hasn't gone to zero)
""", "yellow"))

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(colored("""
Revival System Test Script

Usage:
  python test_revival_system.py           # Run tests with default tokens
  python test_revival_system.py --fresh   # Show how to get fresh tokens
  python test_revival_system.py --help    # Show this help

For best results:
1. Get 24-48 hour old tokens from DexScreener
2. Add them to the test_tokens list in the script
3. Run the test
""", "cyan"))
    elif len(sys.argv) > 1 and sys.argv[1] == "--fresh":
        get_fresh_tokens_from_dexscreener()
    else:
        test_with_real_tokens()