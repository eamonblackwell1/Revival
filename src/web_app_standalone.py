"""
🌐 Moon Dev's Revival Scanner Web App - Standalone Version
Beautiful web interface for the meme coin revival detection system
This version works without the full moon-dev dependencies
Built with love by Moon Dev 🚀
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import json
import threading
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__,
            template_folder='web_templates',
            static_folder='web_static')
CORS(app)

# Global state
scanner_state = {
    'running': False,
    'current_scan': None,
    'results': [],
    'scan_count': 0,
    'last_scan_time': None,
    'settings': {
        'scan_interval': 300,
        'min_revival_score': 0.7,
        'auto_scan': False
    }
}

scanner_thread = None

# Standalone token analysis functions (no dependencies)
def get_token_age_hours(token_address):
    """Get token age using DexScreener"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('pairs'):
                oldest = min(pair['pairCreatedAt'] for pair in data['pairs'])
                age_hours = (time.time() * 1000 - oldest) / (1000 * 3600)
                return age_hours
    except:
        pass
    return None

def analyze_token_simple(token_address):
    """Simple token analysis without heavy dependencies"""
    try:
        # Get DexScreener data
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data.get('pairs'):
            return None

        pair = data['pairs'][0]

        # Calculate age
        age_hours = get_token_age_hours(token_address)
        if not age_hours or age_hours < 24 or age_hours > 72:
            return None

        # Basic data
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        volume_24h = float(pair.get('volume', {}).get('h24', 0))

        if liquidity < 5000 or volume_24h < 5000:
            return None

        # Calculate simple revival score
        price_score = 0.5 if volume_24h > 10000 else 0.3
        volume_score = 0.7 if liquidity > 10000 else 0.5
        smart_score = 0.5  # Placeholder

        revival_score = (price_score * 0.5) + (smart_score * 0.3) + (volume_score * 0.2)

        return {
            'token_address': token_address,
            'token_symbol': pair.get('baseToken', {}).get('symbol', 'Unknown'),
            'token_name': pair.get('baseToken', {}).get('name', 'Unknown'),
            'age_hours': age_hours,
            'liquidity_usd': liquidity,
            'volume_24h': volume_24h,
            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
            'revival_score': revival_score,
            'price_score': price_score,
            'smart_score': smart_score,
            'volume_score': volume_score,
            'dexscreener_url': pair.get('url', ''),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error analyzing {token_address}: {str(e)}")
        return None

def scan_tokens(token_list):
    """Scan a list of tokens"""
    results = []

    for token in token_list[:10]:  # Limit to 10 for speed
        result = analyze_token_simple(token)
        if result:
            results.append(result)
        time.sleep(1)  # Rate limiting

    return results

def get_sample_tokens():
    """Get sample tokens for testing"""
    # These are well-known Solana tokens for testing
    # In production, would fetch from sniper_agent or DexScreener
    return [
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
    ]

def background_scanner():
    """Background thread for continuous scanning"""
    global scanner_state

    while scanner_state['running']:
        try:
            print(f"🔄 Starting scan #{scanner_state['scan_count'] + 1}")

            scanner_state['current_scan'] = 'running'
            scanner_state['last_scan_time'] = datetime.now().isoformat()

            # Get tokens and scan
            tokens = get_sample_tokens()
            results = scan_tokens(tokens)

            scanner_state['results'] = results
            scanner_state['scan_count'] += 1
            scanner_state['current_scan'] = 'completed'

            # Wait for next scan
            time.sleep(scanner_state['settings']['scan_interval'])

        except Exception as e:
            print(f"❌ Scanner error: {str(e)}")
            scanner_state['current_scan'] = f'error: {str(e)}'
            time.sleep(60)

# Flask routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get scanner status"""
    return jsonify({
        'running': scanner_state['running'],
        'current_scan': scanner_state['current_scan'],
        'scan_count': scanner_state['scan_count'],
        'last_scan_time': scanner_state['last_scan_time'],
        'settings': scanner_state['settings'],
        'results_count': len(scanner_state['results'])
    })

@app.route('/api/results')
def get_results():
    """Get latest scan results"""
    default_min = scanner_state['settings'].get('min_revival_score', 0.7)
    min_score = request.args.get('min_score', default_min, type=float)

    filtered_results = [
        r for r in scanner_state['results']
        if r.get('revival_score', 0) >= min_score
    ]

    filtered_results.sort(key=lambda x: x.get('revival_score', 0), reverse=True)

    return jsonify({
        'results': filtered_results,
        'total': len(scanner_state['results']),
        'filtered': len(filtered_results)
    })

@app.route('/api/scan/start', methods=['POST'])
def start_scanner():
    """Start continuous scanning"""
    global scanner_state, scanner_thread

    if scanner_state['running']:
        return jsonify({'error': 'Scanner already running'}), 400

    scanner_state['running'] = True
    scanner_state['settings']['auto_scan'] = True

    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()

    return jsonify({
        'status': 'started',
        'message': 'Scanner started successfully'
    })

@app.route('/api/scan/stop', methods=['POST'])
def stop_scanner():
    """Stop continuous scanning"""
    global scanner_state

    scanner_state['running'] = False
    scanner_state['settings']['auto_scan'] = False

    return jsonify({
        'status': 'stopped',
        'message': 'Scanner stopped successfully'
    })

@app.route('/api/scan/once', methods=['POST'])
def scan_once():
    """Run a single scan"""
    try:
        scanner_state['current_scan'] = 'running'
        scanner_state['last_scan_time'] = datetime.now().isoformat()

        # Get tokens and scan
        tokens = get_sample_tokens()
        results = scan_tokens(tokens)

        scanner_state['results'] = results
        scanner_state['scan_count'] += 1
        scanner_state['current_scan'] = 'completed'

        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        scanner_state['current_scan'] = f'error: {str(e)}'
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    if request.method == 'POST':
        data = request.json

        if 'scan_interval' in data:
            scanner_state['settings']['scan_interval'] = int(data['scan_interval'])
        if 'min_revival_score' in data:
            scanner_state['settings']['min_revival_score'] = max(float(data['min_revival_score']), 0.7)

        return jsonify({
            'status': 'updated',
            'settings': scanner_state['settings']
        })

    return jsonify(scanner_state['settings'])

def main():
    """Run the web app"""
    print("="*60)
    print("🌐 Moon Dev's Revival Scanner Web App (Standalone)")
    print("="*60)
    print("\n🚀 Starting server...")
    print("📡 Dashboard will be available at: http://localhost:5001")
    print("⌨️  Press Ctrl+C to stop\n")
    print("ℹ️  NOTE: Using simplified scanning (DexScreener only)")
    print("    For full features, install all dependencies\n")

    # Create necessary directories
    Path(__file__).parent.joinpath('web_templates').mkdir(exist_ok=True)
    Path(__file__).parent.joinpath('web_static').mkdir(exist_ok=True)

    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()