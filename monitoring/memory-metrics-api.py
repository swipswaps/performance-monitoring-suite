#!/usr/bin/env python3
"""
Memory Protection Metrics API
Provides real-time memory protection data for dashboard integration
"""

import json
import subprocess
import time
import psutil
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for Material UI integration

def get_protection_status():
    """Get current protection tier status"""
    try:
        result = subprocess.run([
            './tools/memory-pressure/unified-memory-manager.sh', 'status'
        ], capture_output=True, text=True, cwd='/home/owner/Documents/6854a1da-e23c-8008-a9fc-76b7fa3c1f92/kde-memory-guardian')
        
        output = result.stdout
        
        # Parse protection status
        earlyoom_active = "✅ Tier 1 (earlyoom): ACTIVE" in output
        nohang_active = "✅ Tier 2 (nohang): ACTIVE" in output
        systemd_oomd_active = "✅ Tier 3 (systemd-oomd): ACTIVE" in output
        
        return {
            'tier1_earlyoom': earlyoom_active,
            'tier2_nohang': nohang_active,
            'tier3_systemd_oomd': systemd_oomd_active,
            'total_active_tiers': sum([earlyoom_active, nohang_active, systemd_oomd_active])
        }
    except Exception as e:
        return {'error': str(e)}

def get_memory_stats():
    """Get current memory statistics"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'cached': getattr(memory, 'cached', 0),
                'buffers': getattr(memory, 'buffers', 0)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_top_processes():
    """Get top memory-consuming processes with OOM scores"""
    try:
        result = subprocess.run([
            'oom-sort', '--num', '10'
        ], capture_output=True, text=True)
        
        lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
        processes = []
        
        for line in lines:
            if line.strip():
                parts = line.split(None, 7)
                if len(parts) >= 7:
                    processes.append({
                        'oom_score': int(parts[0]),
                        'oom_score_adj': int(parts[1]),
                        'uid': int(parts[2]),
                        'pid': int(parts[3]),
                        'name': parts[4],
                        'vmrss': parts[5],
                        'vmswap': parts[6],
                        'cmdline': parts[7] if len(parts) > 7 else ''
                    })
        
        return processes
    except Exception as e:
        return {'error': str(e)}

def get_protection_processes():
    """Get information about protection processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if proc.info['name'] in ['earlyoom', 'nohang']:
                    processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                        'cpu_percent': proc.info['cpu_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    except Exception as e:
        return {'error': str(e)}

@app.route('/api/memory/status')
def memory_status():
    """Get comprehensive memory protection status"""
    return jsonify({
        'timestamp': time.time(),
        'protection': get_protection_status(),
        'memory': get_memory_stats(),
        'top_processes': get_top_processes(),
        'protection_processes': get_protection_processes()
    })

@app.route('/api/memory/protection')
def protection_only():
    """Get only protection status"""
    return jsonify({
        'timestamp': time.time(),
        'protection': get_protection_status()
    })

@app.route('/api/memory/stats')
def memory_stats_only():
    """Get only memory statistics"""
    return jsonify({
        'timestamp': time.time(),
        'memory': get_memory_stats()
    })

@app.route('/api/memory/processes')
def processes_only():
    """Get only process information"""
    return jsonify({
        'timestamp': time.time(),
        'top_processes': get_top_processes(),
        'protection_processes': get_protection_processes()
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'memory-metrics-api'
    })

if __name__ == '__main__':
    print("🛡️ Memory Protection Metrics API Starting...")
    print("📊 Available endpoints:")
    print("   http://localhost:3002/api/memory/status")
    print("   http://localhost:3002/api/memory/protection")
    print("   http://localhost:3002/api/memory/stats")
    print("   http://localhost:3002/api/memory/processes")
    print("   http://localhost:3002/api/health")
    print("🎨 Integrates with Material UI dashboard on port 3000")
    
    app.run(host='0.0.0.0', port=3002, debug=False)
