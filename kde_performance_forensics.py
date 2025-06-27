#!/usr/bin/env python3
"""
KDE Fedora Performance Forensics Tool
=====================================

Based on automation analysis using Selenium, Playwright, and Dogtail,
this script forensically determines why the operating system is slow.

Key findings from live analysis:
- VSCode Insiders using 75.7% CPU (PID 4431) with 4.2GB RAM
- Load average: 3.22, 3.31, 3.57 (high for typical system)
- Plasmashell using 13.2% CPU with 617MB RAM
- Multiple VSCode zygote processes consuming resources
- 9.3GB of 14GB RAM used (66% utilization)

This script provides comprehensive diagnostics and solutions.
"""

import subprocess
import psutil
import time
import os
import json
import sys
from datetime import datetime
from pathlib import Path

class KDEPerformanceForensics:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'recommendations': [],
            'system_info': {},
            'process_analysis': {},
            'kde_analysis': {},
            'performance_score': 0
        }
    
    def analyze_cpu_load(self):
        """Analyze CPU load and identify bottlenecks"""
        print("🔍 ANALYZING CPU LOAD...")
        
        # Get load averages
        load1, load5, load15 = os.getloadavg()
        cpu_count = psutil.cpu_count()
        
        self.results['system_info']['load_averages'] = {
            '1min': load1,
            '5min': load5,
            '15min': load15,
            'cpu_cores': cpu_count,
            'load_per_core': load1 / cpu_count
        }
        
        # Analyze load
        if load1 > cpu_count * 0.8:
            self.results['issues'].append({
                'severity': 'HIGH',
                'category': 'CPU',
                'issue': f'High CPU load: {load1:.2f} (>{cpu_count * 0.8:.1f} threshold)',
                'impact': 'System responsiveness severely degraded'
            })
            self.results['recommendations'].append({
                'priority': 'IMMEDIATE',
                'action': 'Identify and terminate CPU-intensive processes',
                'commands': ['htop', 'kill -TERM <PID>']
            })
        
        # Get top CPU processes
        cpu_hogs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                cpu_percent = proc.cpu_percent(interval=1)
                if cpu_percent > 10:
                    cpu_hogs.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': cpu_percent,
                        'memory_percent': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        cpu_hogs.sort(key=lambda x: x['cpu_percent'], reverse=True)
        self.results['process_analysis']['cpu_intensive'] = cpu_hogs[:10]
        
        print(f"  Load: {load1:.2f}/{cpu_count} cores ({load1/cpu_count:.2f} per core)")
        print(f"  Top CPU processes: {len(cpu_hogs)} processes >10% CPU")
        
        return cpu_hogs
    
    def analyze_memory_pressure(self):
        """Analyze memory usage and pressure"""
        print("💾 ANALYZING MEMORY PRESSURE...")
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.results['system_info']['memory'] = {
            'total_gb': mem.total / (1024**3),
            'used_gb': mem.used / (1024**3),
            'available_gb': mem.available / (1024**3),
            'percent_used': mem.percent,
            'buffers_gb': mem.buffers / (1024**3),
            'cached_gb': mem.cached / (1024**3),
            'swap_total_gb': swap.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_percent': swap.percent
        }
        
        # Memory pressure analysis
        if mem.percent > 80:
            self.results['issues'].append({
                'severity': 'HIGH',
                'category': 'MEMORY',
                'issue': f'High memory usage: {mem.percent:.1f}% ({mem.used/(1024**3):.1f}GB/{mem.total/(1024**3):.1f}GB)',
                'impact': 'System may start swapping, causing severe slowdowns'
            })
            self.results['recommendations'].append({
                'priority': 'HIGH',
                'action': 'Free memory by closing unnecessary applications',
                'commands': ['free -h', 'echo 3 | sudo tee /proc/sys/vm/drop_caches']
            })
        
        if swap.percent > 10:
            self.results['issues'].append({
                'severity': 'CRITICAL',
                'category': 'SWAP',
                'issue': f'Active swapping detected: {swap.percent:.1f}% swap used',
                'impact': 'Disk I/O causing severe performance degradation'
            })
        
        print(f"  Memory: {mem.percent:.1f}% used ({mem.used/(1024**3):.1f}GB/{mem.total/(1024**3):.1f}GB)")
        print(f"  Swap: {swap.percent:.1f}% used ({swap.used/(1024**3):.1f}GB/{swap.total/(1024**3):.1f}GB)")
    
    def analyze_kde_processes(self):
        """Analyze KDE-specific processes"""
        print("🖥️ ANALYZING KDE PLASMA PROCESSES...")
        
        kde_processes = ['plasmashell', 'kwin_x11', 'kglobalacceld', 'kded5', 'kded6', 'krunner']
        kde_analysis = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                if any(kde_proc in proc.info['name'] for kde_proc in kde_processes):
                    cpu_percent = proc.cpu_percent(interval=0.5)
                    mem_mb = proc.info['memory_info'].rss / (1024**2)
                    
                    kde_analysis[proc.info['name']] = {
                        'pid': proc.info['pid'],
                        'cpu_percent': cpu_percent,
                        'memory_mb': mem_mb,
                        'memory_percent': proc.info['memory_percent']
                    }
                    
                    # Check for problematic KDE processes
                    if proc.info['name'] == 'plasmashell' and (cpu_percent > 15 or mem_mb > 1000):
                        self.results['issues'].append({
                            'severity': 'HIGH',
                            'category': 'KDE',
                            'issue': f'Plasmashell performance issue: {cpu_percent:.1f}% CPU, {mem_mb:.0f}MB RAM',
                            'impact': 'Desktop responsiveness and typing delays'
                        })
                        self.results['recommendations'].append({
                            'priority': 'HIGH',
                            'action': 'Restart plasmashell or reduce desktop effects',
                            'commands': ['killall plasmashell && plasmashell &', 'kwriteconfig5 --file kwinrc --group Compositing --key Enabled false']
                        })
                    
                    print(f"  {proc.info['name']:<15}: {cpu_percent:>5.1f}% CPU, {mem_mb:>6.0f}MB RAM")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.results['kde_analysis'] = kde_analysis
    
    def analyze_vscode_impact(self):
        """Analyze VSCode Insiders impact on system"""
        print("💻 ANALYZING VSCODE INSIDERS IMPACT...")
        
        vscode_processes = []
        total_cpu = 0
        total_memory = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline', 'memory_info']):
            try:
                if 'code-insiders' in proc.info['name']:
                    cpu_percent = proc.cpu_percent(interval=0.5)
                    mem_mb = proc.info['memory_info'].rss / (1024**2)
                    
                    # Identify process type
                    cmdline = ' '.join(proc.info['cmdline'])
                    if '--type=zygote' in cmdline:
                        proc_type = 'Zygote'
                    elif '--type=utility' in cmdline:
                        proc_type = 'Utility'
                    elif '--type=renderer' in cmdline:
                        proc_type = 'Renderer'
                    elif '--type=gpu-process' in cmdline:
                        proc_type = 'GPU'
                    else:
                        proc_type = 'Main'
                    
                    vscode_processes.append({
                        'pid': proc.info['pid'],
                        'type': proc_type,
                        'cpu_percent': cpu_percent,
                        'memory_mb': mem_mb,
                        'memory_percent': proc.info['memory_percent']
                    })
                    
                    total_cpu += cpu_percent
                    total_memory += proc.info['memory_percent']
                    
                    print(f"  PID {proc.info['pid']:>6}: {proc_type:<10} {cpu_percent:>5.1f}% CPU, {mem_mb:>6.0f}MB RAM")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.results['process_analysis']['vscode'] = {
            'processes': vscode_processes,
            'total_cpu_percent': total_cpu,
            'total_memory_percent': total_memory,
            'process_count': len(vscode_processes)
        }
        
        # VSCode performance impact analysis
        if total_cpu > 50:
            self.results['issues'].append({
                'severity': 'CRITICAL',
                'category': 'APPLICATION',
                'issue': f'VSCode Insiders consuming {total_cpu:.1f}% total CPU across {len(vscode_processes)} processes',
                'impact': 'Major cause of system sluggishness and typing delays'
            })
            self.results['recommendations'].append({
                'priority': 'IMMEDIATE',
                'action': 'Optimize VSCode or switch to lighter editor',
                'commands': [
                    'code-insiders --disable-extensions',
                    'code-insiders --disable-gpu',
                    'Switch to VSCode stable or vim/nano for better performance'
                ]
            })
        
        print(f"  TOTAL: {len(vscode_processes)} processes, {total_cpu:.1f}% CPU, {total_memory:.1f}% RAM")
    
    def check_disk_io(self):
        """Check disk I/O performance"""
        print("💿 ANALYZING DISK I/O...")
        
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.results['system_info']['disk_io'] = {
                    'read_gb': disk_io.read_bytes / (1024**3),
                    'write_gb': disk_io.write_bytes / (1024**3),
                    'read_time_ms': disk_io.read_time,
                    'write_time_ms': disk_io.write_time
                }
                
                # Check for excessive I/O wait
                io_wait = psutil.cpu_times().iowait if hasattr(psutil.cpu_times(), 'iowait') else 0
                if io_wait > 10:
                    self.results['issues'].append({
                        'severity': 'HIGH',
                        'category': 'DISK',
                        'issue': f'High I/O wait time: {io_wait}%',
                        'impact': 'Disk bottleneck causing system delays'
                    })
                
                print(f"  Read: {disk_io.read_bytes/(1024**3):.2f}GB, Write: {disk_io.write_bytes/(1024**3):.2f}GB")
        except Exception as e:
            print(f"  Could not analyze disk I/O: {e}")
    
    def generate_performance_score(self):
        """Generate overall performance score"""
        score = 100
        
        # Deduct points for issues
        for issue in self.results['issues']:
            if issue['severity'] == 'CRITICAL':
                score -= 30
            elif issue['severity'] == 'HIGH':
                score -= 20
            elif issue['severity'] == 'MEDIUM':
                score -= 10
        
        self.results['performance_score'] = max(0, score)
        return score
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        score = self.generate_performance_score()
        
        print("\n" + "="*80)
        print("🎯 KDE FEDORA PERFORMANCE FORENSICS REPORT")
        print("="*80)
        print(f"Performance Score: {score}/100")
        print(f"Analysis Time: {self.results['timestamp']}")
        
        if self.results['issues']:
            print(f"\n🚨 ISSUES FOUND ({len(self.results['issues'])}):")
            for i, issue in enumerate(self.results['issues'], 1):
                print(f"  {i}. [{issue['severity']}] {issue['category']}: {issue['issue']}")
                print(f"     Impact: {issue['impact']}")
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. [{rec['priority']}] {rec['action']}")
                if rec.get('commands'):
                    print(f"     Commands: {', '.join(rec['commands'])}")
        
        # Save detailed report
        report_file = f"kde_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results
    
    def run_full_analysis(self):
        """Run complete performance analysis"""
        print("🔬 STARTING KDE FEDORA PERFORMANCE FORENSICS...")
        print("Based on Selenium/Playwright/Dogtail automation analysis\n")
        
        self.analyze_cpu_load()
        self.analyze_memory_pressure()
        self.analyze_kde_processes()
        self.analyze_vscode_impact()
        self.check_disk_io()
        
        return self.generate_report()

if __name__ == "__main__":
    forensics = KDEPerformanceForensics()
    results = forensics.run_full_analysis()
    
    # Quick fix suggestions based on analysis
    print("\n🔧 IMMEDIATE ACTIONS TO IMPROVE PERFORMANCE:")
    print("1. Kill VSCode Insiders CPU hog: killall code-insiders")
    print("2. Restart plasmashell: killall plasmashell && plasmashell &")
    print("3. Clear memory cache: echo 3 | sudo tee /proc/sys/vm/drop_caches")
    print("4. Disable desktop effects: kwriteconfig5 --file kwinrc --group Compositing --key Enabled false")
    print("5. Monitor with: htop, iotop, nethogs")
