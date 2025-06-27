#!/usr/bin/env python3
"""
VSCode Typing Delay Forensics Tool
==================================

Based on analysis of VSCode Insiders logs after update and Augment Code extension pinning.
This script forensically determines why typing is still slow despite updates.

Key findings from log analysis:
- Excessive Augment extension secret requests (every ~2 seconds)
- Heavy Python extension file system watching
- Keyboard events with "No matching keybinding" overhead
- Continuous encryption/decryption operations

This script provides targeted diagnostics and solutions.
"""

import subprocess
import time
import os
import json
import re
from datetime import datetime
from pathlib import Path

class TypingDelayForensics:
    def __init__(self, log_file=None):
        self.log_file = log_file or "6854a1da-e23c-8008-a9fc-76b7fa3c1f92.2025-06-27_074931.txt"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'log_analysis': {},
            'extension_issues': [],
            'performance_issues': [],
            'recommendations': [],
            'typing_delay_score': 0
        }
    
    def analyze_log_file(self):
        """Analyze VSCode log file for typing delay causes"""
        print("📄 ANALYZING VSCODE LOG FILE...")
        
        if not os.path.exists(self.log_file):
            print(f"❌ Log file not found: {self.log_file}")
            return
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Count critical events
        augment_requests = content.count('augment.vscode-augment')
        secret_requests = content.count('Getting password for augment')
        decrypt_requests = content.count('decrypting gotten secret')
        watch_requests = content.count('MainThreadFileSystemEventService')
        python_watches = content.count('ms-python.python')
        keyboard_events = content.count('KeybindingService#dispatch')
        no_keybinding = content.count('No matching keybinding')
        
        self.results['log_analysis'] = {
            'total_lines': len(lines),
            'augment_requests': augment_requests,
            'secret_requests': secret_requests,
            'decrypt_requests': decrypt_requests,
            'watch_requests': watch_requests,
            'python_watches': python_watches,
            'keyboard_events': keyboard_events,
            'no_keybinding_events': no_keybinding
        }
        
        # Calculate frequency
        time_span_minutes = 5  # Approximate from log timestamps
        secret_frequency = secret_requests / time_span_minutes if time_span_minutes > 0 else 0
        
        print(f"  📊 Augment Extension Activity:")
        print(f"    Secret requests: {secret_requests} ({secret_frequency:.1f}/min)")
        print(f"    Decrypt operations: {decrypt_requests}")
        print(f"  📁 File System Activity:")
        print(f"    Watch requests: {watch_requests}")
        print(f"    Python watches: {python_watches}")
        print(f"  ⌨️ Keyboard Activity:")
        print(f"    Dispatch events: {keyboard_events}")
        print(f"    No keybinding matches: {no_keybinding}")
        
        # Identify issues
        if secret_requests > 50:
            self.results['extension_issues'].append({
                'severity': 'CRITICAL',
                'extension': 'Augment Code',
                'issue': f'Excessive secret requests: {secret_requests} operations',
                'impact': 'Continuous I/O operations blocking typing',
                'frequency': f'{secret_frequency:.1f} requests per minute'
            })
        
        if python_watches > 10:
            self.results['extension_issues'].append({
                'severity': 'HIGH',
                'extension': 'Python',
                'issue': f'Excessive file watching: {python_watches} watch requests',
                'impact': 'File system monitoring overhead',
                'paths': 'Multiple Python site-packages directories'
            })
        
        if no_keybinding > 20:
            self.results['performance_issues'].append({
                'severity': 'MEDIUM',
                'category': 'Keyboard Processing',
                'issue': f'Unmatched keybinding events: {no_keybinding}',
                'impact': 'Keyboard event processing overhead'
            })
    
    def analyze_extension_performance(self):
        """Analyze extension-specific performance issues"""
        print("\n🔌 ANALYZING EXTENSION PERFORMANCE...")
        
        # Check Augment extension status
        try:
            result = subprocess.run(['code-insiders', '--list-extensions'], 
                                  capture_output=True, text=True, timeout=10)
            extensions = result.stdout.split('\n')
            
            augment_installed = any('augment' in ext.lower() for ext in extensions)
            python_installed = any('python' in ext.lower() for ext in extensions)
            
            print(f"  Augment extension: {'✅ Installed' if augment_installed else '❌ Not found'}")
            print(f"  Python extension: {'✅ Installed' if python_installed else '❌ Not found'}")
            
            if augment_installed:
                self.results['extension_issues'].append({
                    'severity': 'HIGH',
                    'extension': 'Augment Code',
                    'issue': 'Extension causing frequent secret operations',
                    'impact': 'Typing delays due to encryption/decryption overhead'
                })
                
        except subprocess.TimeoutExpired:
            print("  ⚠️ Extension list timeout - VSCode may be unresponsive")
        except Exception as e:
            print(f"  ❌ Could not check extensions: {e}")
    
    def analyze_system_resources(self):
        """Analyze current system resource usage"""
        print("\n💻 ANALYZING SYSTEM RESOURCES...")
        
        try:
            # Check VSCode processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.split('\n')
            
            vscode_processes = [p for p in processes if 'code-insiders' in p]
            total_cpu = 0
            total_memory = 0
            
            for proc in vscode_processes:
                parts = proc.split()
                if len(parts) >= 11:
                    try:
                        cpu = float(parts[2])
                        mem = float(parts[3])
                        total_cpu += cpu
                        total_memory += mem
                    except ValueError:
                        pass
            
            print(f"  VSCode Processes: {len(vscode_processes)}")
            print(f"  Total CPU: {total_cpu:.1f}%")
            print(f"  Total Memory: {total_memory:.1f}%")
            
            if total_cpu > 30:
                self.results['performance_issues'].append({
                    'severity': 'HIGH',
                    'category': 'CPU Usage',
                    'issue': f'High VSCode CPU usage: {total_cpu:.1f}%',
                    'impact': 'System resources consumed, causing input lag'
                })
                
        except Exception as e:
            print(f"  ❌ Could not analyze system resources: {e}")
    
    def check_vscode_settings(self):
        """Check VSCode settings that might cause typing delays"""
        print("\n⚙️ CHECKING VSCODE SETTINGS...")
        
        settings_paths = [
            "~/.config/Code - Insiders/User/settings.json",
            "~/.vscode-insiders/settings.json"
        ]
        
        for path in settings_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                try:
                    with open(expanded_path, 'r') as f:
                        settings = json.load(f)
                    
                    # Check problematic settings
                    problematic_settings = []
                    
                    if settings.get('files.watcherExclude', {}) == {}:
                        problematic_settings.append('files.watcherExclude not configured')
                    
                    if settings.get('search.followSymlinks', True):
                        problematic_settings.append('search.followSymlinks enabled')
                    
                    if settings.get('python.defaultInterpreterPath'):
                        problematic_settings.append('Python interpreter path set')
                    
                    if problematic_settings:
                        print(f"  ⚠️ Problematic settings found:")
                        for setting in problematic_settings:
                            print(f"    - {setting}")
                    else:
                        print(f"  ✅ Settings appear optimized")
                        
                except Exception as e:
                    print(f"  ❌ Could not read settings: {e}")
                break
        else:
            print("  ❌ VSCode settings file not found")
    
    def generate_recommendations(self):
        """Generate specific recommendations to fix typing delays"""
        print("\n💡 GENERATING RECOMMENDATIONS...")
        
        # Critical fixes based on log analysis
        if any(issue['extension'] == 'Augment Code' for issue in self.results['extension_issues']):
            self.results['recommendations'].append({
                'priority': 'IMMEDIATE',
                'category': 'Extension',
                'action': 'Temporarily disable Augment Code extension',
                'commands': [
                    'code-insiders --disable-extension augment.vscode-augment',
                    'Or: Extensions panel -> Augment Code -> Disable'
                ],
                'reason': 'Excessive secret operations causing I/O delays'
            })
        
        if any(issue['extension'] == 'Python' for issue in self.results['extension_issues']):
            self.results['recommendations'].append({
                'priority': 'HIGH',
                'category': 'Extension',
                'action': 'Optimize Python extension file watching',
                'commands': [
                    'Add to settings.json:',
                    '"python.analysis.autoSearchPaths": false',
                    '"python.analysis.watchForLibraryChanges": false'
                ],
                'reason': 'Reduce file system monitoring overhead'
            })
        
        # System-level fixes
        self.results['recommendations'].append({
            'priority': 'HIGH',
            'category': 'VSCode',
            'action': 'Clear VSCode secrets and cache',
            'commands': [
                'rm -rf ~/.config/Code\\ -\\ Insiders/User/globalStorage/storageservice.sqlite*',
                'rm -rf ~/.config/Code\\ -\\ Insiders/CachedExtensions/',
                'code-insiders --reset-extensions'
            ],
            'reason': 'Clear corrupted secrets causing encryption overhead'
        })
        
        self.results['recommendations'].append({
            'priority': 'MEDIUM',
            'category': 'Settings',
            'action': 'Optimize file watching settings',
            'commands': [
                'Add to settings.json:',
                '"files.watcherExclude": {',
                '  "**/.git/objects/**": true,',
                '  "**/node_modules/**": true,',
                '  "**/.venv/**": true,',
                '  "**/venv/**": true',
                '}'
            ],
            'reason': 'Reduce file system monitoring load'
        })
    
    def calculate_typing_delay_score(self):
        """Calculate overall typing delay severity score"""
        score = 100  # Start with perfect score
        
        # Deduct points for issues
        for issue in self.results['extension_issues']:
            if issue['severity'] == 'CRITICAL':
                score -= 40
            elif issue['severity'] == 'HIGH':
                score -= 25
            elif issue['severity'] == 'MEDIUM':
                score -= 15
        
        for issue in self.results['performance_issues']:
            if issue['severity'] == 'HIGH':
                score -= 20
            elif issue['severity'] == 'MEDIUM':
                score -= 10
        
        self.results['typing_delay_score'] = max(0, score)
        return score
    
    def generate_report(self):
        """Generate comprehensive typing delay report"""
        score = self.calculate_typing_delay_score()
        
        print("\n" + "="*80)
        print("🎯 TYPING DELAY FORENSICS REPORT")
        print("="*80)
        print(f"Typing Responsiveness Score: {score}/100")
        print(f"Analysis Time: {self.results['timestamp']}")
        
        if self.results['extension_issues']:
            print(f"\n🔌 EXTENSION ISSUES ({len(self.results['extension_issues'])}):")
            for i, issue in enumerate(self.results['extension_issues'], 1):
                print(f"  {i}. [{issue['severity']}] {issue['extension']}: {issue['issue']}")
                print(f"     Impact: {issue['impact']}")
        
        if self.results['performance_issues']:
            print(f"\n⚡ PERFORMANCE ISSUES ({len(self.results['performance_issues'])}):")
            for i, issue in enumerate(self.results['performance_issues'], 1):
                print(f"  {i}. [{issue['severity']}] {issue['category']}: {issue['issue']}")
                print(f"     Impact: {issue['impact']}")
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. [{rec['priority']}] {rec['action']}")
                print(f"     Reason: {rec['reason']}")
                if rec.get('commands'):
                    print(f"     Commands: {rec['commands'][0]}")
        
        # Save detailed report
        report_file = f"typing_delay_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.results
    
    def run_full_analysis(self):
        """Run complete typing delay analysis"""
        print("🔬 STARTING TYPING DELAY FORENSICS...")
        print("Based on VSCode Insiders logs and system analysis\n")
        
        self.analyze_log_file()
        self.analyze_extension_performance()
        self.analyze_system_resources()
        self.check_vscode_settings()
        self.generate_recommendations()
        
        return self.generate_report()

if __name__ == "__main__":
    forensics = TypingDelayForensics()
    results = forensics.run_full_analysis()
    
    # Quick fix suggestions
    print("\n🔧 IMMEDIATE ACTIONS TO FIX TYPING DELAYS:")
    print("1. Disable Augment extension: code-insiders --disable-extension augment.vscode-augment")
    print("2. Clear secrets cache: rm -rf ~/.config/Code\\ -\\ Insiders/User/globalStorage/storageservice.sqlite*")
    print("3. Restart extension host: Ctrl+Shift+P -> 'Developer: Restart Extension Host'")
    print("4. Optimize Python settings: Add 'python.analysis.autoSearchPaths': false")
    print("5. Monitor with: htop, iotop, code-insiders --verbose")
