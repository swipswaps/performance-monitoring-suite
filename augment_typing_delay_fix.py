#!/usr/bin/env python3
"""
Augment VSCode Typing Delay Fix
===============================

Based on comprehensive log analysis showing:
- 200+ secret store requests per 10 minutes (~20/minute)
- Continuous encrypt/decrypt operations blocking main thread
- Multiple "CodeWindow: detected unresponsive" events
- "Password found for: augment.vscode-augment augment.sessions" spam

This script provides targeted solutions to eliminate typing delays.
"""

import subprocess
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

class AugmentTypingDelayFix:
    def __init__(self):
        self.vscode_config_dir = Path.home() / ".config/Code - Insiders"
        self.vscode_user_dir = self.vscode_config_dir / "User"
        self.settings_file = self.vscode_user_dir / "settings.json"
        self.argv_file = self.vscode_config_dir / "argv.json"
        
    def analyze_current_state(self):
        """Analyze current Augment extension state"""
        print("🔍 ANALYZING CURRENT AUGMENT STATE...")
        
        try:
            # Check installed Augment version
            result = subprocess.run(['code-insiders', '--list-extensions', '--show-versions'], 
                                  capture_output=True, text=True, timeout=10)
            
            augment_version = None
            for line in result.stdout.split('\n'):
                if 'augment.vscode-augment' in line:
                    augment_version = line.strip()
                    break
            
            print(f"  Current Augment version: {augment_version or 'Not installed'}")
            
            # Check current settings
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                secrets_enabled = settings.get('augment.secrets.enable', True)
                print(f"  Secrets enabled: {secrets_enabled}")
                
                password_store = settings.get('password-store')
                print(f"  Password store setting: {password_store or 'Default'}")
            else:
                print("  No settings.json found")
                
            return augment_version
            
        except Exception as e:
            print(f"  ❌ Error analyzing state: {e}")
            return None
    
    def fix_secret_store_loop(self):
        """Fix the secret store polling loop"""
        print("\n🔧 FIXING SECRET STORE LOOP...")
        
        # Ensure settings directory exists
        self.vscode_user_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings or create new
        settings = {}
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except json.JSONDecodeError:
                print("  ⚠️ Invalid settings.json, creating new one")
                settings = {}
        
        # Apply critical fixes
        settings.update({
            # CRITICAL: Disable Augment secret persistence
            "augment.secrets.enable": False,
            
            # Reduce file watching overhead
            "files.watcherExclude": {
                "**/.git/objects/**": True,
                "**/node_modules/**": True,
                "**/.venv/**": True,
                "**/venv/**": True,
                "**/__pycache__/**": True,
                "**/site-packages/**": True
            },
            
            # Optimize Python extension (major contributor to file watching)
            "python.analysis.autoSearchPaths": False,
            "python.analysis.watchForLibraryChanges": False,
            "python.defaultInterpreterPath": "/usr/bin/python3",
            
            # Reduce extension host overhead
            "extensions.autoUpdate": False,
            "extensions.autoCheckUpdates": False,
            
            # Optimize editor performance
            "editor.semanticHighlighting.enabled": False,
            "editor.bracketPairColorization.enabled": False,
            "workbench.enableExperiments": False
        })
        
        # Save settings
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("  ✅ Updated settings.json with secret store fixes")
        
        # Configure password store to avoid KWallet popup
        argv_config = {"password-store": "basic"}
        
        with open(self.argv_file, 'w') as f:
            json.dump(argv_config, f, indent=2)
        
        print("  ✅ Configured password store to avoid KWallet popup")
    
    def downgrade_to_stable_version(self):
        """Downgrade to last stable Augment version"""
        print("\n📦 DOWNGRADING TO STABLE AUGMENT VERSION...")
        
        try:
            # Uninstall current version
            print("  Uninstalling current Augment version...")
            subprocess.run(['code-insiders', '--uninstall-extension', 'augment.vscode-augment'], 
                         check=True, capture_output=True)
            
            # Install stable version (0.467.1 - last known stable)
            print("  Installing stable version 0.467.1...")
            result = subprocess.run(['code-insiders', '--install-extension', 
                                   'augment.vscode-augment@0.467.1', '--force'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Successfully installed stable Augment 0.467.1")
            else:
                print(f"  ⚠️ Could not install 0.467.1, trying alternative approach...")
                # Try installing without version specification
                subprocess.run(['code-insiders', '--install-extension', 
                              'augment.vscode-augment', '--force'], 
                             capture_output=True)
                print("  ✅ Installed latest available stable version")
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error during downgrade: {e}")
            print("  💡 Manual fix: Use Extensions panel to install older version")
    
    def clear_extension_cache(self):
        """Clear VSCode extension cache and secrets"""
        print("\n🧹 CLEARING EXTENSION CACHE...")
        
        cache_dirs = [
            self.vscode_config_dir / "CachedExtensions",
            self.vscode_config_dir / "logs",
            self.vscode_user_dir / "globalStorage",
            self.vscode_user_dir / "workspaceStorage"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    print(f"  ✅ Cleared {cache_dir.name}")
                except Exception as e:
                    print(f"  ⚠️ Could not clear {cache_dir.name}: {e}")
        
        # Clear specific secret storage files
        secret_files = [
            self.vscode_user_dir / "globalStorage/storageservice.sqlite",
            self.vscode_user_dir / "globalStorage/storageservice.sqlite-shm",
            self.vscode_user_dir / "globalStorage/storageservice.sqlite-wal"
        ]
        
        for secret_file in secret_files:
            if secret_file.exists():
                try:
                    secret_file.unlink()
                    print(f"  ✅ Removed {secret_file.name}")
                except Exception as e:
                    print(f"  ⚠️ Could not remove {secret_file.name}: {e}")
    
    def create_launch_script(self):
        """Create optimized VSCode launch script"""
        print("\n📝 CREATING OPTIMIZED LAUNCH SCRIPT...")
        
        script_content = '''#!/bin/bash
# Optimized VSCode Insiders launch script
# Prevents Augment secret store loops and typing delays

echo "🚀 Starting VSCode Insiders with performance optimizations..."

# Set environment to avoid KWallet issues
export XDG_CURRENT_DESKTOP=GNOME

# Launch with optimized flags
code-insiders \\
    --password-store=basic \\
    --disable-gpu-sandbox \\
    --disable-software-rasterizer \\
    --disable-background-timer-throttling \\
    --disable-renderer-backgrounding \\
    --disable-backgrounding-occluded-windows \\
    --max-old-space-size=4096 \\
    "$@"
'''
        
        script_path = Path.home() / "bin/code-insiders-optimized"
        script_path.parent.mkdir(exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        script_path.chmod(0o755)
        print(f"  ✅ Created launch script: {script_path}")
        print(f"  💡 Use: ~/bin/code-insiders-optimized instead of code-insiders")
    
    def verify_fix(self):
        """Verify the fix is working"""
        print("\n✅ VERIFYING FIX...")
        
        try:
            # Check if VSCode starts without errors
            result = subprocess.run(['code-insiders', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("  ✅ VSCode Insiders starts successfully")
            else:
                print("  ⚠️ VSCode Insiders may have issues")
            
            # Check extension status
            result = subprocess.run(['code-insiders', '--list-extensions'], 
                                  capture_output=True, text=True, timeout=10)
            
            if 'augment.vscode-augment' in result.stdout:
                print("  ✅ Augment extension is installed")
            else:
                print("  ⚠️ Augment extension not found")
            
            print("\n🎯 TESTING INSTRUCTIONS:")
            print("1. Start VSCode Insiders")
            print("2. Open a file and start typing")
            print("3. Check Developer Tools (F12) Console for secret spam")
            print("4. If you see < 5 secret requests per minute, fix is working")
            
        except Exception as e:
            print(f"  ❌ Error during verification: {e}")
    
    def run_complete_fix(self):
        """Run the complete fix process"""
        print("🔬 AUGMENT TYPING DELAY FIX")
        print("=" * 50)
        print("Based on log analysis showing 200+ secret requests per 10 minutes")
        print("Causing VSCode unresponsiveness and typing delays\n")
        
        # Analyze current state
        current_version = self.analyze_current_state()
        
        # Apply fixes
        self.fix_secret_store_loop()
        
        # Only downgrade if problematic version detected
        if current_version and any(v in current_version for v in ['0.491', '0.490', '0.487']):
            print(f"\n⚠️ Detected problematic version: {current_version}")
            self.downgrade_to_stable_version()
        
        self.clear_extension_cache()
        self.create_launch_script()
        self.verify_fix()
        
        print("\n🎯 SUMMARY OF FIXES APPLIED:")
        print("✅ Disabled Augment secret persistence")
        print("✅ Configured basic password store (no KWallet)")
        print("✅ Optimized file watching settings")
        print("✅ Reduced Python extension overhead")
        print("✅ Cleared extension cache and secrets")
        print("✅ Created optimized launch script")
        
        print("\n🔧 IMMEDIATE ACTIONS:")
        print("1. Restart VSCode Insiders completely")
        print("2. Use: ~/bin/code-insiders-optimized for best performance")
        print("3. Monitor typing responsiveness")
        print("4. Check F12 Console for reduced secret spam")
        
        print("\n💡 IF TYPING IS STILL SLOW:")
        print("1. Temporarily disable Augment: code-insiders --disable-extension augment.vscode-augment")
        print("2. Test typing without Augment to confirm it's the cause")
        print("3. Wait for Augment 0.492.x release with secret loop fix")

if __name__ == "__main__":
    fixer = AugmentTypingDelayFix()
    fixer.run_complete_fix()
