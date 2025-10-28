"""
🔔 Moon Dev's Meme Notifier Agent
Multi-channel alert system for revival opportunities
Built with love by Moon Dev 🚀

Notification channels:
1. Console (colored output)
2. CSV logging
3. Browser auto-open (like sniper_agent)
4. Optional: Telegram/Discord (if configured)
"""

import os
import sys
import time
import webbrowser
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from termcolor import colored
import platform

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class MemeNotifierAgent:
    """
    Sends alerts when high-confidence opportunities are found

    Priority levels:
    🔴 HIGH: Immediate action required (revival score > 0.8)
    🟡 MEDIUM: Worth watching (revival score 0.6-0.8)
    🟢 LOW: Informational (revival score 0.4-0.6)
    """

    def __init__(self):
        """Initialize the notifier"""
        print(colored("🔔 Meme Notifier initialized!", "cyan"))

        # Configuration
        self.auto_open_browser = True  # Auto-open high priority in browser
        self.play_sound = True        # Play alert sound
        self.save_to_csv = True       # Log all alerts

        # Priority thresholds
        self.high_priority_threshold = 0.8
        self.medium_priority_threshold = 0.6
        self.low_priority_threshold = 0.4

        # Data storage
        self.data_dir = Path(__file__).parent.parent / "data" / "meme_notifier"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Alert history (prevent duplicate alerts)
        self.alert_history = self.load_alert_history()

    def load_alert_history(self) -> set:
        """Load previous alerts to avoid duplicates"""
        history_file = self.data_dir / "alert_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('alerted_tokens', []))
            except:
                pass
        return set()

    def save_alert_history(self):
        """Save alert history"""
        history_file = self.data_dir / "alert_history.json"
        with open(history_file, 'w') as f:
            json.dump({'alerted_tokens': list(self.alert_history)}, f)

    def get_priority_level(self, revival_score: float) -> str:
        """Determine priority level from score"""
        if revival_score >= self.high_priority_threshold:
            return "HIGH"
        elif revival_score >= self.medium_priority_threshold:
            return "MEDIUM"
        elif revival_score >= self.low_priority_threshold:
            return "LOW"
        else:
            return "NONE"

    def format_alert_message(self, token_data: Dict, priority: str) -> str:
        """Format alert message with all key info"""
        symbol = token_data.get('token_symbol', 'Unknown')
        name = token_data.get('token_name', 'Unknown')
        score = token_data.get('revival_score', 0)
        age = token_data.get('age_hours', 0)
        liquidity = token_data.get('liquidity_usd', 0)
        volume = token_data.get('volume_24h', 0)
        price_change = token_data.get('price_change_24h', 0)

        # Get sub-scores
        price_score = token_data.get('price_score', 0)
        smart_score = token_data.get('smart_score', 0)
        volume_score = token_data.get('volume_score', 0)

        message = f"""
{'='*60}
🎯 REVIVAL OPPORTUNITY DETECTED - {priority} PRIORITY
{'='*60}
Token: {symbol} ({name})
Address: {token_data.get('token_address', 'Unknown')[:8]}...

📊 REVIVAL SCORE: {score:.2f} / 1.00
   Price Pattern: {price_score:.2f}
   Smart Money:   {smart_score:.2f}
   Volume Signal: {volume_score:.2f}

📈 MARKET DATA:
   Age:           {age:.1f} hours
   Liquidity:     ${liquidity:,.0f}
   Volume (24h):  ${volume:,.0f}
   Price Change:  {price_change:+.1f}%

🔗 LINKS:
   DexScreener: {token_data.get('dexscreener_url', 'N/A')}
{'='*60}
"""
        return message

    def send_alert(self, token_data: Dict):
        """Send alert through all configured channels"""
        # Check if already alerted for this token
        token_address = token_data.get('token_address')
        if token_address in self.alert_history:
            return  # Skip duplicate alerts

        # Get priority level
        revival_score = token_data.get('revival_score', 0)
        priority = self.get_priority_level(revival_score)

        if priority == "NONE":
            return  # Don't alert for low scores

        # Format message
        message = self.format_alert_message(token_data, priority)

        # 1. Console output (with colors)
        self.console_alert(message, priority)

        # 2. Save to CSV
        if self.save_to_csv:
            self.log_to_csv(token_data, priority)

        # 3. Auto-open in browser (for high priority)
        if self.auto_open_browser and priority == "HIGH":
            self.open_in_browser(token_data)

        # 4. Play sound (for high priority)
        if self.play_sound and priority == "HIGH":
            self.play_alert_sound()

        # Add to history
        self.alert_history.add(token_address)
        self.save_alert_history()

    def console_alert(self, message: str, priority: str):
        """Print alert to console with colors"""
        color_map = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "green"
        }

        attrs_map = {
            "HIGH": ["bold", "blink"],
            "MEDIUM": ["bold"],
            "LOW": []
        }

        color = color_map.get(priority, "white")
        attrs = attrs_map.get(priority, [])

        print(colored(message, color, attrs=attrs))

    def log_to_csv(self, token_data: Dict, priority: str):
        """Log alert to CSV file"""
        try:
            csv_file = self.data_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.csv"

            # Prepare row data
            row_data = {
                'timestamp': datetime.now().isoformat(),
                'priority': priority,
                'token_symbol': token_data.get('token_symbol'),
                'token_address': token_data.get('token_address'),
                'revival_score': token_data.get('revival_score'),
                'age_hours': token_data.get('age_hours'),
                'liquidity_usd': token_data.get('liquidity_usd'),
                'volume_24h': token_data.get('volume_24h'),
                'price_change_24h': token_data.get('price_change_24h'),
                'dexscreener_url': token_data.get('dexscreener_url')
            }

            # Append to CSV (create if doesn't exist)
            df = pd.DataFrame([row_data])
            if csv_file.exists():
                df.to_csv(csv_file, mode='a', header=False, index=False)
            else:
                df.to_csv(csv_file, index=False)

            print(colored(f"📝 Alert logged to {csv_file.name}", "green"))

        except Exception as e:
            print(colored(f"⚠️ Could not log to CSV: {str(e)}", "yellow"))

    def open_in_browser(self, token_data: Dict):
        """Open token in browser (DexScreener)"""
        try:
            url = token_data.get('dexscreener_url')
            if not url:
                # Construct DexScreener URL if not provided
                token_address = token_data.get('token_address')
                url = f"https://dexscreener.com/solana/{token_address}"

            print(colored(f"🌐 Opening in browser: {url}", "cyan"))
            webbrowser.open(url)

        except Exception as e:
            print(colored(f"⚠️ Could not open browser: {str(e)}", "yellow"))

    def play_alert_sound(self):
        """Play alert sound (system beep)"""
        try:
            if platform.system() == "Darwin":  # macOS
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            elif platform.system() == "Linux":
                os.system("beep")
            elif platform.system() == "Windows":
                import winsound
                winsound.Beep(1000, 200)  # Frequency, Duration
            else:
                print("\a")  # Terminal bell

        except Exception as e:
            print(colored("🔔 ALERT! (sound unavailable)", "yellow"))

    def batch_alert(self, tokens: List[Dict]):
        """Send alerts for multiple tokens"""
        if not tokens:
            return

        print(colored(f"\n🔔 Processing {len(tokens)} potential alerts...", "cyan"))

        # Sort by score (highest first)
        tokens.sort(key=lambda x: x.get('revival_score', 0), reverse=True)

        # Count by priority
        high_count = sum(1 for t in tokens if t.get('revival_score', 0) >= self.high_priority_threshold)
        medium_count = sum(1 for t in tokens if self.medium_priority_threshold <= t.get('revival_score', 0) < self.high_priority_threshold)
        low_count = sum(1 for t in tokens if self.low_priority_threshold <= t.get('revival_score', 0) < self.medium_priority_threshold)

        if high_count > 0:
            print(colored(f"🔴 {high_count} HIGH PRIORITY alerts!", "red", attrs=['bold']))
        if medium_count > 0:
            print(colored(f"🟡 {medium_count} MEDIUM priority alerts", "yellow"))
        if low_count > 0:
            print(colored(f"🟢 {low_count} low priority alerts", "green"))

        # Send individual alerts
        for token in tokens:
            self.send_alert(token)
            time.sleep(0.5)  # Small delay between alerts

    def create_daily_summary(self) -> str:
        """Create a summary of daily alerts"""
        try:
            csv_file = self.data_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.csv"

            if not csv_file.exists():
                return "No alerts today"

            df = pd.read_csv(csv_file)

            summary = f"""
📊 DAILY ALERT SUMMARY - {datetime.now().strftime('%Y-%m-%d')}
{'='*50}
Total Alerts: {len(df)}

By Priority:
🔴 HIGH:   {len(df[df['priority'] == 'HIGH'])}
🟡 MEDIUM: {len(df[df['priority'] == 'MEDIUM'])}
🟢 LOW:    {len(df[df['priority'] == 'LOW'])}

Top 5 Tokens by Revival Score:
"""
            top_5 = df.nlargest(5, 'revival_score')
            for idx, row in top_5.iterrows():
                summary += f"\n{row['token_symbol']}: Score {row['revival_score']:.2f}"

            summary += f"\n\nAverage Revival Score: {df['revival_score'].mean():.2f}"
            summary += f"\nAverage Liquidity: ${df['liquidity_usd'].mean():,.0f}"

            return summary

        except Exception as e:
            return f"Could not create summary: {str(e)}"

def main():
    """Test the notifier with sample data"""
    notifier = MemeNotifierAgent()

    # Test with sample token data
    sample_tokens = [
        {
            'token_address': 'SampleToken123456789',
            'token_symbol': 'TEST',
            'token_name': 'Test Token',
            'revival_score': 0.85,  # High priority
            'age_hours': 36,
            'liquidity_usd': 25000,
            'volume_24h': 50000,
            'price_change_24h': 45.5,
            'price_score': 0.9,
            'smart_score': 0.8,
            'volume_score': 0.85,
            'dexscreener_url': 'https://dexscreener.com/solana/test'
        },
        {
            'token_address': 'SampleToken987654321',
            'token_symbol': 'MED',
            'token_name': 'Medium Token',
            'revival_score': 0.65,  # Medium priority
            'age_hours': 28,
            'liquidity_usd': 15000,
            'volume_24h': 20000,
            'price_change_24h': 15.2,
            'price_score': 0.7,
            'smart_score': 0.6,
            'volume_score': 0.65,
            'dexscreener_url': 'https://dexscreener.com/solana/med'
        }
    ]

    # Send batch alerts
    notifier.batch_alert(sample_tokens)

    # Show daily summary
    print(colored("\n" + notifier.create_daily_summary(), "cyan"))

if __name__ == "__main__":
    main()