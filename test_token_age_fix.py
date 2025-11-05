#!/usr/bin/env python3
"""
Test script to verify the Helius pagination fix
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.helius_utils import get_token_age_hours
from termcolor import colored

# Test token that was incorrectly showing as 0.95 hours old
TEST_TOKEN = "GMvCfcZg8YvkkQmwDaAzCtHDrrEtgE74nQpQ7xNabonk"

# Get RPC URL from environment (prefer HELIUS_RPC_ENDPOINT as it has the actual URL)
rpc_url = os.getenv('HELIUS_RPC_ENDPOINT') or os.getenv('RPC_ENDPOINT')

if not rpc_url:
    print(colored("❌ ERROR: No RPC_ENDPOINT or HELIUS_RPC_ENDPOINT found in environment", "red"))
    print("Please set your Helius RPC endpoint in .env file")
    sys.exit(1)

print(colored("\n🧪 Testing Helius Token Age Fix", "cyan", attrs=['bold']))
print(colored("=" * 50, "cyan"))

print(f"\n📍 Testing token: {TEST_TOKEN}")
print("   Symbol: 1")
print("   Name: 1 coin can change your life")
print("   Expected age: ~48 days (1 month 18 days)")
print("   Previous (buggy) result: 0.95 hours\n")

print(colored("🔍 Fetching actual token age with fixed pagination...", "yellow"))

# Get the token age
try:
    age_hours = get_token_age_hours(TEST_TOKEN, rpc_url)
except Exception as e:
    print(colored(f"❌ Exception occurred: {str(e)}", "red"))
    import traceback
    traceback.print_exc()
    sys.exit(1)

if age_hours is None:
    print(colored("❌ Failed to get token age (returned None)", "red"))
    print(colored("   This might be due to RPC rate limits or network issues", "yellow"))
    sys.exit(1)

# Convert to days for easier reading
age_days = age_hours / 24

print(colored("\n✅ Results:", "green", attrs=['bold']))
print(f"   Age in hours: {age_hours:.1f}")
print(f"   Age in days: {age_days:.1f}")
print(f"   Age in months: {age_days/30:.1f}")

# Check if the fix worked
if age_hours > 72:  # Should be much older than 72 hours
    print(colored(f"\n🎉 SUCCESS! Token is correctly showing as {age_days:.1f} days old", "green", attrs=['bold']))
    print(colored("   The pagination fix is working correctly!", "green"))
    print(colored(f"   Token would now PASS the 72-hour age filter (age: {age_hours:.1f}h > 72h)", "green"))
else:
    print(colored(f"\n❌ PROBLEM: Token is still showing as too young ({age_hours:.1f} hours)", "red", attrs=['bold']))
    print(colored("   The fix might not be working correctly", "red"))

print(colored("\n" + "=" * 50, "cyan"))