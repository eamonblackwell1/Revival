"""
🎯 Moon Dev's Meme Scanner Orchestrator
Main controller that combines all components for finding revival patterns
Built with love by Moon Dev 🚀

Enhanced 5-Phase Pipeline Flow:
1. Multi-pass BirdEye token discovery (3 sorting strategies, ~600 tokens)
2. Light liquidity pre-filter ($50K minimum, reduces Helius costs)
3. Helius blockchain age verification (24h+ minimum, NO maximum)
4. DexScreener strict market filters ($80K liquidity, $20K 1h volume)
5. DexScreener social enrichment (boosts, Twitter, Telegram, etc.)
6. Security filter (eliminate scams)
7. Revival pattern detection (smart money, price patterns)
8. Notifications for opportunities
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from termcolor import colored

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import our components
from src.agents.revival_detector_agent import RevivalDetectorAgent
from src.agents.stage1_security_filter import Stage1SecurityFilter
from src.agents.meme_notifier_agent import MemeNotifierAgent
from src.agents.api import MoonDevAPI
from src.config import *

class MemeScannerOrchestrator:
    """
    Main orchestrator that coordinates all meme scanning components

    Components:
    1. Security Filter - Eliminates scams
    2. Revival Detector - Finds revival patterns
    3. Notifier - Sends alerts
    4. Paper Trader - Tracks hypothetical performance
    """

    def __init__(self):
        """Initialize all components"""
        print(colored("=" * 60, "cyan"))
        print(colored("🎯 MEME SCANNER ORCHESTRATOR", "cyan", attrs=['bold']))
        print(colored("Finding revival patterns in 24-48hr old tokens", "cyan"))
        print(colored("=" * 60, "cyan"))

        # Initialize components
        self.security_filter = Stage1SecurityFilter()
        self.revival_detector = RevivalDetectorAgent()
        self.notifier = MemeNotifierAgent()

        # Try to initialize Moon Dev API for token sources
        try:
            self.moon_api = MoonDevAPI()
        except:
            self.moon_api = None
            print(colored("⚠️ Moon Dev API not configured (optional)", "yellow"))

        # Configuration
        self.scan_interval = 7200  # 120 minutes / 2 hours (optimized for API free tier limits)
        self.max_tokens_per_scan = BIRDEYE_TOKENS_PER_SORT * 3  # ~600 tokens per scan (3 sorting strategies)
        self.min_revival_score = 0.4  # Minimum score to consider

        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "meme_scanner"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Track scanning history
        self.scan_history = []

        # Track tokens through each phase (for dashboard funnel view)
        self.phase_tokens = {
            'phase1_birdeye': [],           # Raw tokens from BirdEye
            'phase2_prefiltered': [],       # After liquidity + memecoin filter
            'phase3_aged': [],              # After Helius age check
            'phase4_market_filtered': [],   # After DexScreener market filters
            'phase5_enriched': [],          # After social enrichment
            'phase6_security_passed': [],   # After security filter
            'phase7_revival_detected': []   # Final revival opportunities
        }

        # Callbacks for web UI (injected by web_app.py)
        self.log_activity = None
        self.log_error = None
        self.update_progress = None

    def _log(self, message, level='info'):
        """Internal logging that works both in CLI and web mode"""
        if self.log_activity:
            self.log_activity(message, level)
        # Always print to console too
        if level == 'error':
            print(colored(message, 'red'))
        elif level == 'warning':
            print(colored(message, 'yellow'))
        elif level == 'success':
            print(colored(message, 'green'))

    def _log_error(self, message):
        """Log error"""
        if self.log_error:
            self.log_error(message)
        print(colored(f"❌ {message}", 'red'))

    def _update_progress(self, phase, phase_number, message, **kwargs):
        """Update progress"""
        if self.update_progress:
            self.update_progress(phase, phase_number, message, **kwargs)

        # Known non-memecoin patterns
        self.non_memecoin_keywords = [
            # Stablecoins
            'usd', 'usdc', 'usdt', 'dai', 'busd', 'frax', 'ust', 'tusd', 'pax', 'gusd',
            # Liquid staking tokens
            'stsol', 'msol', 'jitosol', 'scnsol', 'bsol', 'lstsol', 'hsol', 'csol',
            'steth', 'reth', 'cbeth', 'frxeth', 'sfrxeth',
            # DeFi/Infrastructure
            'wrapped', 'wbtc', 'weth', 'wsol', 'staked', 'liquid', 'lido',
            'marinade', 'jito', 'socean', 'blazestake', 'daopool',
            # DEX/AMM tokens
            'raydium', 'orca', 'serum', 'saber', 'mercurial', 'aldrin', 'cyclos',
            # Lending/Borrowing
            'solend', 'mango', 'apricot', 'larix', 'port', 'oxygen',
            # Other DeFi
            'chainlink', 'link', 'oracle', 'bridge', 'cross-chain', 'interop',
            'yield', 'vault', 'farm', 'pool', 'liquidity', 'amm', 'dex'
        ]

        # Common memecoin patterns (positive indicators)
        self.memecoin_patterns = [
            'inu', 'doge', 'shib', 'pepe', 'wojak', 'chad', 'moon', 'rocket',
            'pump', 'based', 'gm', 'ser', 'fren', 'wagmi', 'ngmi', 'ape',
            'diamond', 'hands', 'hodl', 'lambo', 'tesla', 'elon', 'musk',
            'cat', 'dog', 'frog', 'bird', 'bear', 'bull', 'rat', 'hamster',
            'baby', 'mini', 'micro', 'safe', 'king', 'queen', 'lord',
            'meme', 'coin', 'token', 'finance', 'swap', 'defi',
            'pnut', 'banana', 'pizza', 'burger', 'taco', 'sushi',
            'bonk', 'bong', 'wif', 'hat', 'glasses', 'santa', 'xmas',
            'god', 'jesus', 'buddha', 'zen', 'karma', 'vibe',
            'nft', 'jpeg', 'art', 'pixel', 'punk', 'ape',
            'cum', 'ass', 'tits', 'dick', 'pussy', 'fuck', 'shit',
            'yolo', 'fomo', 'rekt', 'rug', 'scam', 'ponzi',
            '69', '420', '666', '777', '888', '1337'
        ]

    def get_candidate_tokens(self) -> List[str]:
        """
        ENHANCED 5-PHASE HYBRID PIPELINE:
        1. BirdEye → Multi-pass token discovery (3 sorting strategies, ~600 tokens)
        2. Light liquidity pre-filter → $50K minimum (reduce Helius costs)
        3. Helius → Age verification (24h+ minimum, NO maximum)
        4. DexScreener → Strict market filters ($80K liquidity, $20K 1h volume)
        5. DexScreener → Social enrichment (boosts, Twitter, Telegram, etc.)

        Returns: List of token addresses ready for security + revival analysis
        """
        print(colored("\n" + "="*60, "magenta"))
        print(colored("🚀 ENHANCED 5-PHASE HYBRID PIPELINE", "magenta", attrs=['bold']))
        print(colored("="*60, "magenta"))

        # Reset phase tracking
        self.phase_tokens = {
            'phase1_birdeye': [],
            'phase2_prefiltered': [],
            'phase3_aged': [],
            'phase4_market_filtered': [],
            'phase5_enriched': [],
            'phase6_security_passed': [],
            'phase7_revival_detected': []
        }

        # PHASE 1: Get tokens from BirdEye (multi-pass collection)
        print(colored("\n[PHASE 1/5] BirdEye Multi-Pass Token Discovery", "cyan", attrs=['bold']))
        self._update_progress("BirdEye Token Discovery", 1, "Fetching tokens from BirdEye API...")
        birdeye_tokens = self.get_birdeye_tokens(tokens_per_sort=BIRDEYE_TOKENS_PER_SORT)

        if not birdeye_tokens:
            print(colored("❌ No tokens from BirdEye - cannot proceed", "red"))
            self._log_error("No tokens from BirdEye - cannot proceed")
            return []

        # Store Phase 1 tokens (with metadata)
        self.phase_tokens['phase1_birdeye'] = birdeye_tokens

        self._log(f"Phase 1 complete: Collected {len(birdeye_tokens)} unique tokens", 'success')

        # PHASE 2: Simplified pre-filter (liquidity and market cap only - native meme list guarantees memecoins)
        print(colored("\n[PHASE 2/5] Pre-Filter (Liquidity & Market Cap)", "cyan", attrs=['bold']))
        self._update_progress("Pre-Filter", 2, "Filtering for adequate liquidity and market cap...",
                            tokens_collected=len(birdeye_tokens))
        prefiltered_tokens = self.liquidity_prefilter(
            birdeye_tokens,
            min_liquidity=MIN_LIQUIDITY_PREFILTER  # $50K minimum
        )

        if not prefiltered_tokens:
            print(colored("❌ No tokens passed enhanced pre-filter", "red"))
            self._log_error("No tokens passed enhanced pre-filter")
            return []

        # Store Phase 2 tokens
        self.phase_tokens['phase2_prefiltered'] = prefiltered_tokens

        self._log(f"Phase 2 complete: {len(prefiltered_tokens)} memecoins passed pre-filter", 'success')

        # Extract addresses from the filtered token dicts
        prefiltered_addresses = [token['address'] for token in prefiltered_tokens]

        # PHASE 3: Age filtering via Helius blockchain (24h+, no max)
        print(colored("\n[PHASE 3/5] Blockchain Age Verification (Helius)", "cyan", attrs=['bold']))
        self._update_progress("Age Verification", 3, "Checking token ages via Helius blockchain...",
                            tokens_filtered=len(prefiltered_addresses))
        aged_tokens = self.filter_by_age_helius(
            prefiltered_addresses,
            min_age_hours=MIN_AGE_HOURS  # Minimum 24 hours, no maximum
        )

        if not aged_tokens:
            print(colored("❌ No tokens passed age filter", "red"))
            self._log_error("No tokens passed age filter (all too young)")
            return []

        # Store Phase 3 tokens (addresses only at this point)
        self.phase_tokens['phase3_aged'] = [{'address': addr} for addr in aged_tokens]

        self._log(f"Phase 3 complete: {len(aged_tokens)} tokens are 24h+ old", 'success')

        # PHASE 4: Strict market filters via DexScreener (Liquidity > $80K, 1h Volume > $20K)
        print(colored("\n[PHASE 4/5] Strict Market Metrics Filtering (DexScreener)", "cyan", attrs=['bold']))
        self._update_progress("Market Filters", 4, "Applying strict liquidity and volume filters...",
                            tokens_filtered=len(aged_tokens))
        filtered_tokens = self.filter_by_market_metrics_strict(
            aged_tokens,
            min_liquidity=MIN_LIQUIDITY_STRICT,  # $80K minimum
            min_volume_1h=MIN_VOLUME_1H    # $20K 1-hour volume
        )

        if not filtered_tokens:
            print(colored("❌ No tokens passed strict market filters", "red"))
            self._log_error("No tokens passed strict market filters")
            return []

        # Store Phase 4 tokens
        self.phase_tokens['phase4_market_filtered'] = [{'address': addr} for addr in filtered_tokens]

        self._log(f"Phase 4 complete: {len(filtered_tokens)} tokens passed strict filters", 'success')

        # PHASE 5: Enrich with DexScreener social data
        print(colored("\n[PHASE 5/5] Social Sentiment Enrichment (DexScreener)", "cyan", attrs=['bold']))
        self._update_progress("Social Enrichment", 5, "Enriching with social sentiment data...",
                            tokens_filtered=len(filtered_tokens))
        enriched_tokens = self.enrich_with_social_data(filtered_tokens)

        # Store Phase 5 tokens (enriched with social data)
        self.phase_tokens['phase5_enriched'] = enriched_tokens

        self._log(f"Phase 5 complete: {len(enriched_tokens)} tokens enriched with social data", 'success')

        # Store enriched data for later use (revival detector will access this)
        self.enriched_token_data = {token['token_address']: token for token in enriched_tokens}

        # Extract just the addresses for next pipeline stages
        token_addresses = [token['token_address'] for token in enriched_tokens]

        print(colored("\n" + "="*60, "magenta"))
        print(colored(f"✅ PIPELINE COMPLETE: {len(token_addresses)} tokens ready for analysis", "magenta", attrs=['bold']))
        print(colored("="*60, "magenta"))

        return token_addresses

    def get_birdeye_meme_tokens(self, tokens_to_fetch: int = 200) -> List[Dict]:
        """
        Get meme tokens from BirdEye's Meme Token List endpoint
        This endpoint returns ONLY meme tokens (pump.fun, Moonshot, Raydium launches)

        Args:
            tokens_to_fetch: Total tokens to fetch

        Returns:
            List of dicts with: address, symbol, liquidity, volume_24h, mc
        """
        all_tokens = []
        tokens_per_page = BIRDEYE_TOKENS_PER_PAGE  # 50 tokens per API call
        num_pages = (tokens_to_fetch + tokens_per_page - 1) // tokens_per_page

        try:
            for page in range(num_pages):
                offset = page * tokens_per_page

                url = f"https://public-api.birdeye.so/defi/v3/token/meme/list?chain=solana&offset={offset}&limit={tokens_per_page}"
                headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

                print(colored(f"  📄 Page {page+1}/{num_pages} (meme-list, offset={offset})", "cyan"))

                response = requests.get(url, headers=headers, timeout=15)

                if response.status_code == 429:
                    print(colored(f"⚠️ Rate limit hit (HTTP 429) - waiting 60 seconds...", "yellow"))
                    time.sleep(60)
                    response = requests.get(url, headers=headers, timeout=15)

                if response.status_code != 200:
                    print(colored(f"❌ BirdEye API error: HTTP {response.status_code}", "red"))
                    break

                data = response.json()
                if not data.get('success'):
                    print(colored(f"⚠️ API returned success=false", "yellow"))
                    break

                for token_data in data.get('data', {}).get('tokens', []):
                    all_tokens.append({
                        'address': token_data.get('address'),
                        'symbol': token_data.get('symbol', 'Unknown'),
                        'name': token_data.get('name', ''),
                        'liquidity': token_data.get('liquidity', 0),
                        'volume_24h': token_data.get('v24hUSD', 0),
                        'mc': token_data.get('mc', 0),
                    })

                # Rate limiting: 1 request per second
                if page < num_pages - 1:
                    time.sleep(1.0)

            print(colored(f"  ✅ Retrieved {len(all_tokens)} MEME tokens", "green"))
            return all_tokens

        except Exception as e:
            print(colored(f"⚠️ BirdEye meme-list fetch error: {str(e)}", "yellow"))
            return all_tokens

    def get_birdeye_trending_tokens(self, tokens_to_fetch: int = 20) -> List[Dict]:
        """
        Get trending tokens from BirdEye's Trending List endpoint
        NOTE: This endpoint has a HARD LIMIT of 20 tokens max (no pagination)

        These are tokens that traders are actively chasing

        Args:
            tokens_to_fetch: Ignored - endpoint returns max 20 tokens

        Returns:
            List of dicts with: address, symbol, liquidity, volume_24h, mc
        """
        all_tokens = []

        try:
            # Trending endpoint: no params, returns top 20 only
            url = "https://public-api.birdeye.so/defi/token_trending"
            headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

            print(colored(f"  📄 Fetching top 20 trending tokens (API limit)", "cyan"))

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 429:
                print(colored(f"⚠️ Rate limit hit (HTTP 429) - waiting 60 seconds...", "yellow"))
                time.sleep(60)
                response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(colored(f"❌ BirdEye API error: HTTP {response.status_code}", "red"))
                return []

            data = response.json()
            if not data.get('success'):
                print(colored(f"⚠️ API returned success=false", "yellow"))
                return []

            for token_data in data.get('data', {}).get('tokens', []):
                all_tokens.append({
                    'address': token_data.get('address'),
                    'symbol': token_data.get('symbol', 'Unknown'),
                    'name': token_data.get('name', ''),
                    'liquidity': token_data.get('liquidity', 0),
                    'volume_24h': token_data.get('v24hUSD', 0),
                    'mc': token_data.get('mc', 0),
                })

            print(colored(f"  ✅ Retrieved {len(all_tokens)} trending tokens", "green"))
            return all_tokens

        except Exception as e:
            print(colored(f"⚠️ BirdEye trending fetch error: {str(e)}", "yellow"))
            return all_tokens

    def get_birdeye_tokens_paginated(self, sort_by: str, tokens_to_fetch: int = 200) -> List[Dict]:
        """
        Get tokens from BirdEye with pagination for a specific sort order

        Args:
            sort_by: Sort field (v24hUSD, liquidity, v1hUSD, etc.)
            tokens_to_fetch: Total tokens to fetch (will make multiple API calls if > 100)

        Returns:
            List of dicts with: address, symbol, liquidity, volume_24h
        """
        all_tokens = []
        tokens_per_page = BIRDEYE_TOKENS_PER_PAGE  # 100 tokens per API call (API limit)
        num_pages = (tokens_to_fetch + tokens_per_page - 1) // tokens_per_page  # Ceiling division

        try:
            for page in range(num_pages):
                offset = page * tokens_per_page

                url = f"https://public-api.birdeye.so/defi/tokenlist?sort_by={sort_by}&sort_type=desc&offset={offset}&limit={tokens_per_page}"
                headers = {'X-API-KEY': os.getenv('BIRDEYE_API_KEY')}

                print(colored(f"  📄 Page {page+1}/{num_pages} (sort={sort_by}, offset={offset})", "cyan"))

                response = requests.get(url, headers=headers, timeout=15)

                if response.status_code == 429:
                    print(colored(f"⚠️ Rate limit hit (HTTP 429) - waiting 60 seconds...", "yellow"))
                    time.sleep(60)
                    # Retry once after wait
                    response = requests.get(url, headers=headers, timeout=15)

                if response.status_code != 200:
                    print(colored(f"❌ BirdEye API error: HTTP {response.status_code}", "red"))
                    if response.status_code == 400:
                        try:
                            error_msg = response.json().get('message', 'Unknown error')
                            print(colored(f"   Error details: {error_msg}", "red"))
                        except:
                            pass
                    break

                data = response.json()
                if not data.get('success'):
                    print(colored(f"⚠️ API returned success=false", "yellow"))
                    break

                for token_data in data.get('data', {}).get('tokens', []):
                    all_tokens.append({
                        'address': token_data.get('address'),
                        'symbol': token_data.get('symbol', 'Unknown'),
                        'name': token_data.get('name', ''),
                        'liquidity': token_data.get('liquidity', 0),
                        'volume_24h': token_data.get('v24hUSD', 0),
                        'mc': token_data.get('mc', 0),  # Market cap
                    })

                # Rate limiting: 1 request per second (BirdEye Standard tier)
                if page < num_pages - 1:  # Don't sleep after last page
                    time.sleep(1.0)

            print(colored(f"  ✅ Retrieved {len(all_tokens)} tokens (sort={sort_by})", "green"))
            return all_tokens

        except Exception as e:
            print(colored(f"⚠️ BirdEye fetch error for {sort_by}: {str(e)}", "yellow"))
            return all_tokens  # Return what we got so far

    def get_birdeye_tokens(self, tokens_per_sort: int = 200) -> List[Dict]:
        """
        NATIVE MEMECOIN DISCOVERY - Uses BirdEye Meme Token List API!

        Strategy (100% memecoins, no keyword filtering needed):
        Strategy 1: Native Meme Token List - pump.fun, Moonshot, Raydium launches (PURE MEMECOINS)
        Strategy 2: Price Change Sort - High % movers in 24h (potential revivals from generic list)
        Bonus: Trending - Top 20 hottest tokens (API limit)

        This eliminates the 15-20% miss rate from keyword filtering!

        Args:
            tokens_per_sort: Tokens to fetch per sorting strategy

        Returns:
            Deduplicated list of unique tokens from all strategies
        """
        print(colored("🦅 NATIVE MEMECOIN DISCOVERY (BirdEye Meme List API)", "yellow", attrs=['bold']))
        print(colored(f"   Strategy: Native meme list + price movers + trending", "yellow"))

        all_tokens = {}  # Use dict to deduplicate by address

        # Pass 1: Native Meme Token List (GUARANTEED MEMECOINS!)
        print(colored("\n[Pass 1/3] Native Meme Token List - Pure Memecoins", "magenta", attrs=['bold']))
        tokens_pass1 = self.get_birdeye_meme_tokens(tokens_per_sort)
        for token in tokens_pass1:
            all_tokens[token['address']] = token

        # Only proceed with additional passes if first pass succeeded
        if not tokens_pass1:
            print(colored("⚠️ First pass failed - trying fallback strategies...", "yellow"))
            # Fallback to price change sort if meme list fails
            tokens_pass1 = self.get_birdeye_tokens_paginated('v24hChangePercent', tokens_per_sort)
            for token in tokens_pass1:
                all_tokens[token['address']] = token

        # Pass 2: Price change sort (catch revivals that might not be in meme list yet)
        print(colored("\n[Pass 2/3] Price Change Sort - Potential Revivals", "magenta", attrs=['bold']))
        tokens_pass2 = self.get_birdeye_tokens_paginated('v24hChangePercent', tokens_per_sort)
        duplicates_pass2 = 0
        for token in tokens_pass2:
            if token['address'] not in all_tokens:  # Only add if not duplicate
                all_tokens[token['address']] = token
            else:
                duplicates_pass2 += 1

        # BONUS Pass 3: Trending tokens (limited to 20 but high quality)
        print(colored("\n[BONUS] Trending List - Hottest 20 Tokens", "magenta", attrs=['bold']))
        tokens_bonus = self.get_birdeye_trending_tokens(20)  # API limit of 20
        duplicates_bonus = 0
        for token in tokens_bonus:
            if token['address'] not in all_tokens:  # Only add if not duplicate
                all_tokens[token['address']] = token
            else:
                duplicates_bonus += 1

        # Convert back to list
        unique_tokens = list(all_tokens.values())

        print(colored(f"\n✅ Total Unique Tokens Collected: {len(unique_tokens)}", "green", attrs=['bold']))
        print(colored(f"   Pass 1 (Native Meme List): {len(tokens_pass1)} tokens (100% memecoins)", "cyan"))
        print(colored(f"   Pass 2 (Price Change): {len(tokens_pass2)} tokens ({duplicates_pass2} duplicates)", "cyan"))
        print(colored(f"   Bonus (Trending): {len(tokens_bonus)} tokens ({duplicates_bonus} duplicates)", "cyan"))
        print(colored(f"   Deduplication: {len(tokens_pass1) + len(tokens_pass2) + len(tokens_bonus)} → {len(unique_tokens)}", "cyan"))

        return unique_tokens

    def is_likely_memecoin(self, symbol: str, name: str = "") -> bool:
        """
        Detect if a token is likely a memecoin based on symbol/name patterns

        Args:
            symbol: Token symbol
            name: Token name (optional)

        Returns:
            True if likely a memecoin, False otherwise
        """
        # Convert to lowercase for comparison
        symbol_lower = symbol.lower() if symbol else ""
        name_lower = name.lower() if name else ""
        combined = f"{symbol_lower} {name_lower}"

        # Check for non-memecoin indicators (negative signals)
        for keyword in self.non_memecoin_keywords:
            if keyword in combined:
                return False

        # Check for memecoin indicators (positive signals)
        for pattern in self.memecoin_patterns:
            if pattern in combined:
                return True

        # Additional heuristics for memecoins:
        # 1. Very short symbols (2-5 chars) are often memecoins
        if 2 <= len(symbol) <= 5:
            return True

        # 2. All caps with numbers often indicates memecoin
        if symbol.isupper() and any(c.isdigit() for c in symbol):
            return True

        # 3. Symbols ending in common memecoin suffixes
        memecoin_suffixes = ['INU', 'DOGE', 'MOON', 'PUMP', 'PEPE', 'CAT', 'DOG']
        for suffix in memecoin_suffixes:
            if symbol.upper().endswith(suffix):
                return True

        # Default to False if no clear indicators
        return False

    def liquidity_prefilter(self, tokens: List[Dict], min_liquidity: float = 50000) -> List[Dict]:
        """
        Simplified pre-filter: liquidity and market cap only
        (No memecoin detection needed - native meme list already guarantees memecoins!)

        Args:
            tokens: List of token dicts from BirdEye (with 'address', 'liquidity', 'symbol')
            min_liquidity: Minimum liquidity in USD

        Returns:
            List of token dicts that pass filters (including address, symbol, name)
        """
        print(colored(f"\n💧 Pre-filtering: Liquidity >${min_liquidity:,.0f}, Market Cap <${MAX_MARKET_CAP:,.0f}", "cyan"))

        passed = []

        for token in tokens:
            address = token['address']
            symbol = token.get('symbol', 'Unknown')
            name = token.get('name', '')
            liquidity = token.get('liquidity', 0)
            market_cap = token.get('mc', 0)  # BirdEye uses 'mc' for market cap

            # Skip if liquidity too low
            if liquidity < min_liquidity:
                self._log(f"⏭️ {symbol} - Liquidity too low: ${liquidity:,.0f}", 'info')
                continue

            # Skip if market cap too high (we want room to grow)
            if market_cap > MAX_MARKET_CAP:
                print(colored(f"  ⏭️ {symbol:<10} | MC: ${market_cap:>10,.0f} (too high)", "grey"))
                self._log(f"⏭️ {symbol} - Market cap too high: ${market_cap:,.0f}", 'info')
                continue

            # Passed all filters
            passed.append({
                'address': address,
                'symbol': symbol,
                'name': name,
                'liquidity': liquidity,
                'market_cap': market_cap
            })
            print(colored(f"  ✅ {symbol:<10} | Liq: ${liquidity:>10,.0f} | MC: ${market_cap:>10,.0f}", "green"))

        print(colored(f"\n📊 Filter Results: {len(passed)}/{len(tokens)} tokens passed", "cyan"))

        return passed

    def filter_by_market_metrics_strict(self, token_addresses: List[str], min_liquidity: float = 80000, min_volume_1h: float = 20000) -> List[str]:
        """
        Strict market filter using DexScreener data
        Applied AFTER age verification to ensure only quality aged tokens proceed

        Args:
            token_addresses: List of token addresses (already passed age filter)
            min_liquidity: Minimum liquidity in USD
            min_volume_1h: Minimum 1-hour volume in USD

        Returns:
            List of token addresses that pass strict filters
        """
        print(colored(f"\n💰 Strict Filtering: Liquidity >${min_liquidity:,.0f}, 1h Volume >${min_volume_1h:,.0f}", "cyan"))

        from src.dexscreener_utils import get_token_social_data

        passed = []
        for i, address in enumerate(token_addresses, 1):
            # Get fresh data from DexScreener for accurate liquidity and volume
            social_data = get_token_social_data(address)
            if not social_data:
                print(colored(f"  [{i}/{len(token_addresses)}] {address[:8]}... = no DexScreener data", "grey"))
                continue

            symbol = social_data.get('symbol', 'Unknown')
            liquidity = social_data.get('liquidity_usd', 0)
            volume_1h = social_data.get('volume_1h', 0)

            # Apply strict filters
            if liquidity < min_liquidity:
                print(colored(f"  [{i}/{len(token_addresses)}] {symbol:<10} | Liq: ${liquidity:>8,.0f} ❌ (too low)", "grey"))
                continue

            if volume_1h < min_volume_1h:
                print(colored(f"  [{i}/{len(token_addresses)}] {symbol:<10} | Vol(1h): ${volume_1h:>8,.0f} ❌ (too low)", "grey"))
                continue

            # Passed both filters
            passed.append(address)
            print(colored(f"  [{i}/{len(token_addresses)}] {symbol:<10} | Liq: ${liquidity:>8,.0f} | Vol(1h): ${volume_1h:>8,.0f} ✅", "green"))

            # Rate limiting: DexScreener 5 req/sec
            time.sleep(0.2)

        print(colored(f"\n📊 {len(passed)}/{len(token_addresses)} tokens passed strict market filters", "cyan"))
        return passed

    def filter_by_age_helius(self, token_addresses: List[str], min_age_hours: float = 24) -> List[str]:
        """
        Filter tokens by age using Helius blockchain data

        Args:
            token_addresses: List of token addresses to check
            min_age_hours: Minimum token age in hours (NO maximum - revivals can happen anytime)

        Returns:
            List of token addresses that meet minimum age requirement
        """
        from src.helius_utils import batch_get_token_ages

        print(colored(f"\n⏰ Age Filter: Minimum {min_age_hours}h (no maximum)", "cyan"))

        rpc_url = os.getenv('HELIUS_RPC_ENDPOINT')
        if not rpc_url:
            print(colored("❌ HELIUS_RPC_ENDPOINT not configured", "red"))
            return []

        ages = batch_get_token_ages(token_addresses, rpc_url)
        passed = [addr for addr, age in ages.items() if age and age >= min_age_hours]

        print(colored(f"\n📊 {len(passed)}/{len(token_addresses)} tokens passed age filter (≥{min_age_hours}h)", "cyan"))
        return passed

    def enrich_with_social_data(self, token_addresses: List[str]) -> List[Dict]:
        """Enrich tokens with DexScreener social sentiment data"""
        from src.dexscreener_utils import batch_enrich_tokens

        print(colored("\n📱 Enriching with social sentiment data...", "cyan"))
        return batch_enrich_tokens(token_addresses)

    def run_scan_cycle(self):
        """Run one complete scan cycle"""
        print(colored("\n" + "="*60, "cyan"))
        print(colored(f"🚀 SCAN CYCLE STARTING - {datetime.now().strftime('%H:%M:%S')}", "cyan", attrs=['bold']))
        print(colored("="*60, "cyan"))

        # Step 1: Get candidate tokens (5-phase pipeline)
        print(colored("\n[Step 1/3] Running 5-Phase Discovery Pipeline...", "yellow", attrs=['bold']))
        tokens = self.get_candidate_tokens()

        if not tokens:
            print(colored("❌ No tokens from discovery pipeline!", "red"))
            return []

        # Step 2: Security filter
        print(colored("\n[Step 2/3] Running security filter...", "yellow", attrs=['bold']))
        security_results = self.security_filter.batch_filter(tokens, max_workers=3)
        passed_security = [r['token_address'] for r in security_results if r['passed']]

        # Store Phase 6 tokens (security passed)
        self.phase_tokens['phase6_security_passed'] = [{'address': addr} for addr in passed_security]

        print(colored(f"🛡️ {len(passed_security)} tokens passed security", "green"))

        if not passed_security:
            print(colored("❌ No tokens passed security filter!", "red"))
            return []

        # Step 3: Check for revival patterns
        print(colored("\n[Step 3/3] Detecting revival patterns...", "yellow", attrs=['bold']))
        revival_results = []

        for token in passed_security[:40]:  # Analyze up to 40 tokens (optimized for 2-hour scans)
            try:
                result = self.revival_detector.calculate_revival_score(token)
                if result['revival_score'] >= self.min_revival_score:
                    revival_results.append(result)

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                print(colored(f"⚠️ Error checking {token}: {str(e)}", "yellow"))
                continue

        # Store Phase 7 tokens (final revival opportunities)
        self.phase_tokens['phase7_revival_detected'] = revival_results

        print(colored(f"🔄 {len(revival_results)} tokens show revival patterns", "green"))

        # Send notifications
        if revival_results:
            print(colored("\n📤 Sending notifications...", "yellow", attrs=['bold']))
            self.notifier.batch_alert(revival_results)

            # Save scan results
            self.save_scan_results(revival_results)
        else:
            print(colored("\n📤 No alerts to send", "grey"))

        # Print summary
        self.print_scan_summary(revival_results)

        return revival_results

    def save_scan_results(self, results: List[Dict]):
        """Save scan results to CSV"""
        try:
            if not results:
                return

            df = pd.DataFrame(results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.data_dir / f"scan_results_{timestamp}.csv"

            df.to_csv(filepath, index=False)
            print(colored(f"💾 Results saved to {filepath.name}", "green"))

            # Also save simplified version for easy viewing
            summary_df = df[['token_symbol', 'token_name', 'revival_score', 'age_hours',
                            'liquidity_usd', 'volume_24h', 'dexscreener_url']].copy()
            summary_path = self.data_dir / f"scan_summary_{timestamp}.csv"
            summary_df.to_csv(summary_path, index=False)

        except Exception as e:
            print(colored(f"⚠️ Could not save results: {str(e)}", "yellow"))

    def print_scan_summary(self, results: List[Dict]):
        """Print summary of scan results"""
        print(colored("\n" + "="*60, "cyan"))
        print(colored("📊 SCAN SUMMARY", "cyan", attrs=['bold']))
        print(colored("="*60, "cyan"))

        if not results:
            print(colored("No revival opportunities found this scan", "yellow"))
            return

        # Sort by score
        results.sort(key=lambda x: x['revival_score'], reverse=True)

        print(colored(f"Found {len(results)} revival opportunities:", "green"))
        print()

        # Show top 5
        for i, token in enumerate(results[:5], 1):
            symbol = token.get('token_symbol', 'Unknown')
            score = token.get('revival_score', 0)
            age = token.get('age_hours', 0)
            liq = token.get('liquidity_usd', 0)
            vol = token.get('volume_24h', 0)

            # Color based on score
            if score >= 0.8:
                color = "red"
            elif score >= 0.6:
                color = "yellow"
            else:
                color = "green"

            print(colored(f"{i}. {symbol:<10} Score: {score:.2f}", color, attrs=['bold']))
            print(colored(f"   Age: {age:.1f}h | Liq: ${liq:,.0f} | Vol: ${vol:,.0f}", "white"))
            print()

        # Statistics
        avg_score = sum(t['revival_score'] for t in results) / len(results)
        avg_liq = sum(t['liquidity_usd'] for t in results) / len(results)

        print(colored(f"Average Revival Score: {avg_score:.2f}", "cyan"))
        print(colored(f"Average Liquidity: ${avg_liq:,.0f}", "cyan"))

    def run_continuous(self):
        """Run continuous scanning loop"""
        print(colored("\n🔄 Starting continuous scanning mode...", "cyan", attrs=['bold']))
        print(colored(f"   Scan interval: {self.scan_interval} seconds", "cyan"))
        print(colored("   Press Ctrl+C to stop\n", "cyan"))

        scan_count = 0

        try:
            while True:
                scan_count += 1
                print(colored(f"\n📍 Scan #{scan_count}", "magenta", attrs=['bold']))

                # Run scan cycle
                results = self.run_scan_cycle()

                # Add to history
                self.scan_history.append({
                    'scan_number': scan_count,
                    'timestamp': datetime.now(),
                    'tokens_found': len(results),
                    'top_score': max([r['revival_score'] for r in results]) if results else 0
                })

                # Show next scan time
                next_scan = datetime.now() + timedelta(seconds=self.scan_interval)
                print(colored(f"\n⏰ Next scan at {next_scan.strftime('%H:%M:%S')}", "cyan"))
                print(colored("   Press Ctrl+C to stop", "grey"))

                # Wait for next scan
                time.sleep(self.scan_interval)

        except KeyboardInterrupt:
            print(colored("\n\n🛑 Scanning stopped by user", "yellow"))
            self.print_session_summary()

    def print_session_summary(self):
        """Print summary of scanning session"""
        if not self.scan_history:
            return

        print(colored("\n" + "="*60, "cyan"))
        print(colored("📊 SESSION SUMMARY", "cyan", attrs=['bold']))
        print(colored("="*60, "cyan"))

        total_scans = len(self.scan_history)
        total_tokens = sum(s['tokens_found'] for s in self.scan_history)
        best_score = max(s['top_score'] for s in self.scan_history)

        print(colored(f"Total Scans: {total_scans}", "green"))
        print(colored(f"Total Opportunities Found: {total_tokens}", "green"))
        print(colored(f"Best Revival Score: {best_score:.2f}", "green"))

        # Show scan history
        print(colored("\nScan History:", "cyan"))
        for scan in self.scan_history[-5:]:  # Last 5 scans
            time_str = scan['timestamp'].strftime('%H:%M:%S')
            count = scan['tokens_found']
            score = scan['top_score']
            print(colored(f"  {time_str}: Found {count} tokens (best: {score:.2f})", "white"))

def main():
    """Run the orchestrator"""
    orchestrator = MemeScannerOrchestrator()

    # Check for command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run single scan
        print(colored("Running single scan...", "cyan"))
        orchestrator.run_scan_cycle()
    else:
        # Run continuous scanning
        orchestrator.run_continuous()

if __name__ == "__main__":
    main()