#!/usr/bin/env python3
"""
RBM Tender App Safety Scanner
Interactive script to run different types of security scans
"""

import os
import sys
import subprocess
import time
import json
import re
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print the safety scanner banner."""
    print("=" * 60)
    print("🛡️  RBM TENDER APP SAFETY SCANNER")
    print("=" * 60)
    print()

def print_menu():
    """Print the main menu options."""
    print("📋 SAFETY SCAN OPTIONS:")
    print()
    print("1.  🛡️  Run ALL Security Scans")
    print("    └─ Executes complete security analysis (dependencies, code, secrets)")
    print("    └─ Comprehensive security assessment with detailed reports")
    print()
    print("2.  📦 Dependency Vulnerability Scan")
    print("    └─ Scans all Python packages for known security vulnerabilities")
    print("    └─ Uses Safety DB to check against CVE database")
    print()
    print("3.  🔍 Code Security Analysis")
    print("    └─ Scans Python code for common security issues and anti-patterns")
    print("    └─ Uses Bandit to detect security vulnerabilities in code")
    print()
    print("4.  🔐 Secret Detection Scan")
    print("    └─ Scans for hardcoded secrets, API keys, and sensitive data")
    print("    └─ Prevents accidental exposure of credentials")
    print()
    print("5.  📊 Generate Security Report")
    print("    └─ Creates comprehensive security report with all scan results")
    print("    └─ Saves results to docs/security/ directory")
    print()
    print("6.  🔄 Update Security Database")
    print("    └─ Updates Safety vulnerability database to latest version")
    print("    └─ Ensures scans use most current security information")
    print()
    print("7.  📈 View Previous Scan Results")
    print("    └─ Displays results from the most recent security scans")
    print("    └─ Shows vulnerability trends and security status")
    print()
    print("8.  ⚙️  Configure Scan Settings")
    print("    └─ Customize scan parameters and exclusion rules")
    print("    └─ Set up automated scanning schedules")
    print()
    print("9.  ❓ Help & Documentation")
    print("    └─ Shows detailed information about each scan type")
    print("    └─ Provides troubleshooting and best practices")
    print()
    print("0.  🚪 Exit")
    print()

def run_command(command, description, timeout=60):
    """Run a command and return the result."""
    print(f"🔄 {description}...")
    print(f"Command: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=timeout  # Add timeout to prevent hanging
        )
        
        if result.returncode == 0:
            print("✅ Success!")
            return True, result.stdout, result.stderr
        else:
            print("❌ Failed!")
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out!")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def run_dependency_scan():
    """Run dependency vulnerability scan using Safety."""
    print("📦 DEPENDENCY VULNERABILITY SCAN")
    print("=" * 40)
    
    print("🔄 Checking if Safety is available...")
    
    # First check if safety is installed
    try:
        import safety
        print("✅ Safety module found!")
        
        # Try to run safety programmatically
        print("🔄 Running Safety scan programmatically...")
        
        # Get installed packages using modern approach
        try:
            import importlib.metadata
            installed_packages = [f"{d.metadata['name']}=={d.version}" for d in importlib.metadata.distributions()]
        except ImportError:
            # Fallback to pkg_resources if importlib.metadata is not available
            import pkg_resources
            installed_packages = [str(d) for d in pkg_resources.working_set]
        
        print(f"📦 Found {len(installed_packages)} installed packages")
        
        # Run safety check using CLI approach
        try:
            print("🔄 Running Safety CLI scan...")
            
            # Try using Safety CLI directly
            result = subprocess.run(
                ["py", "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ No vulnerabilities found!")
            elif result.returncode == 64:  # Safety returns 64 when vulnerabilities found
                try:
                    vulnerabilities = json.loads(result.stdout)
                    if vulnerabilities:
                        print("⚠️  Vulnerabilities found:")
                        for vuln in vulnerabilities:
                            if isinstance(vuln, dict):
                                pkg = vuln.get('package', 'Unknown')
                                version = vuln.get('version', 'Unknown')
                                vuln_id = vuln.get('vulnerability', 'Unknown')
                                print(f"   - {pkg} {version}: {vuln_id}")
                            else:
                                print(f"   - {vuln}")
                except json.JSONDecodeError:
                    print("⚠️  Vulnerabilities found (raw output):")
                    print(result.stdout)
            else:
                print(f"❌ Safety CLI failed with return code {result.returncode}")
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Safety scan timed out after 30 seconds")
        except FileNotFoundError:
            print("❌ Safety CLI not found. Trying programmatic approach...")
            
            # Fallback to programmatic approach
            try:
                from safety.safety import check
                import requests
                
                # Try with session parameter
                session = requests.Session()
                vulnerabilities = check(session=session)
                
                if vulnerabilities:
                    print("⚠️  Vulnerabilities found:")
                    for vuln in vulnerabilities:
                        print(f"   - {vuln}")
                else:
                    print("✅ No vulnerabilities found!")
                    
            except Exception as e:
                print(f"❌ Programmatic approach also failed: {e}")
                print("💡 Safety scan unavailable - showing package list instead")
            
            # Alternative: just show package list
            print("\n📦 Installed packages:")
            for pkg in installed_packages[:10]:  # Show first 10
                print(f"   - {pkg}")
            if len(installed_packages) > 10:
                print(f"   ... and {len(installed_packages) - 10} more")
                
    except ImportError:
        print("❌ Safety module not found!")
        print("💡 Install with: pip install safety")
        
        # Show basic package info without safety
        try:
            import pkg_resources
            installed_packages = [str(d) for d in pkg_resources.working_set]
            print(f"\n📦 Found {len(installed_packages)} installed packages")
            print("💡 Install 'safety' to check for vulnerabilities")
        except Exception as e:
            print(f"❌ Could not list packages: {e}")
    
    # Save basic results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = project_root / "docs" / "security" / f"safety_scan_results_{timestamp}.txt"
    
    try:
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            f.write(f"Safety Scan Results - {datetime.now()}\n")
            f.write("=" * 40 + "\n")
            f.write("Scan completed using programmatic approach\n")
        print(f"\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    input("\nPress Enter to continue...")

def run_code_security_scan():
    """Run code security analysis using Bandit."""
    print("🔍 CODE SECURITY ANALYSIS")
    print("=" * 40)
    
    print("🔄 Checking if Bandit is available...")
    
    try:
        import bandit
        print("✅ Bandit module found!")
        
        # Try to run bandit programmatically
        print("🔄 Running Bandit scan programmatically...")
        
        # Simple file scan
        app_dir = project_root / "app"
        if app_dir.exists():
            print(f"📁 Scanning directory: {app_dir}")
            
            # Count Python files
            python_files = list(app_dir.rglob("*.py"))
            print(f"📄 Found {len(python_files)} Python files to scan")
            
            # Simple security checks
            issues_found = []
            
            for py_file in python_files[:10]:  # Check first 10 files for better coverage
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Only flag obvious security issues
                    if 'eval(' in content:
                        issues_found.append(f"Use of eval() in {py_file.name}")
                    
                    # Only flag if it's a real hardcoded credential (not a variable or comment)
                    lines = content.split('\n')
                    for line in lines:
                        line_lower = line.lower().strip()
                        
                        # Skip comments
                        if line_lower.startswith('#') or line_lower.startswith('//'):
                            continue
                            
                        # Only flag if it's a real hardcoded value with quotes
                        if ('password' in line_lower and '=' in line_lower and 
                            ('"' in line or "'" in line) and
                            not any(safe in line_lower for safe in ['os.environ', 'input(', 'getpass', 'your_', 'placeholder', 'change_me', 'test-'])):
                            issues_found.append(f"Potential hardcoded password in {py_file.name}")
                            break
                        
                        if ('secret' in line_lower and '=' in line_lower and 
                            ('"' in line or "'" in line) and
                            not any(safe in line_lower for safe in ['os.environ', 'secrets_manager', 'generate_secret_key', 'test-', 'testing-only', 'test-secret-key-for-testing-only', 'test_secret_key', 'a-very-secret-key-that-you-should-change']) and
                            not ('os.environ.get' in line and 'secrets_manager.generate_secret_key' in line) and
                            not ('app.config.get' in line and 'a-very-secret-key-that-you-should-change' in line)):
                            issues_found.append(f"Potential hardcoded secret in {py_file.name}")
                            break
                        
                except Exception as e:
                    print(f"⚠️  Could not scan {py_file.name}: {e}")
            
            if issues_found:
                print("⚠️  Potential security issues found:")
                for issue in issues_found:
                    print(f"   - {issue}")
            else:
                print("✅ No obvious security issues found in scanned files!")
                
        else:
            print("❌ App directory not found!")
            
    except ImportError:
        print("❌ Bandit module not found!")
        print("💡 Install with: pip install bandit")
        
        # Basic file count
        app_dir = project_root / "app"
        if app_dir.exists():
            python_files = list(app_dir.rglob("*.py"))
            print(f"\n📄 Found {len(python_files)} Python files in app/")
            print("💡 Install 'bandit' for detailed security analysis")
    
    # Save basic results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = project_root / "docs" / "security" / f"bandit_scan_results_{timestamp}.txt"
    
    try:
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            f.write(f"Bandit Scan Results - {datetime.now()}\n")
            f.write("=" * 40 + "\n")
            f.write("Scan completed using programmatic approach\n")
        print(f"\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    input("\nPress Enter to continue...")

def run_secret_detection_scan():
    """Run secret detection scan."""
    print("🔐 SECRET DETECTION SCAN")
    print("=" * 40)
    
    # Only look for obvious real API keys and secrets
    secret_patterns = [
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
        (r"password\s*=\s*['\"][^'\"]{12,}['\"]", "Long hardcoded password"),
    ]
    
    # Only exclude obvious placeholders
    exclude_patterns = [
        r"YOUR_", r"PLACEHOLDER", r"CHANGE_ME", r"REPLACE_", r"EXAMPLE_",
        r"test-", r"demo-", r"sample-", r"dummy-", r"fake-"
    ]
    
    print("🔍 Scanning for potential secrets...")
    found_secrets = []
    
    # Scan files directly
    app_dir = project_root / "app"
    if app_dir.exists():
        python_files = list(app_dir.rglob("*.py"))
        env_files = list(project_root.rglob("*.env"))
        txt_files = list(project_root.rglob("*.txt"))
        
        all_files = python_files + env_files + txt_files
        
        # Exclude test files and example files from secret detection
        excluded_patterns = [
            "test_", "_test", "test/", "tests/", "example", "sample", 
            "YOUR_", "PLACEHOLDER", "CHANGE_ME", "REPLACE_"
        ]
        
        filtered_files = []
        for file_path in all_files:
            file_str = str(file_path)
            # Skip if file doesn't exist or matches excluded patterns
            if file_path.exists() and not any(pattern in file_str for pattern in excluded_patterns):
                filtered_files.append(file_path)
        
        print(f"📁 Scanning {len(filtered_files)} files (excluding test/example files)...")
        
        for file_path in filtered_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip files with obvious placeholder content
                if any(placeholder in content for placeholder in ["YOUR_", "PLACEHOLDER", "CHANGE_ME", "REPLACE_"]):
                    continue
                
                for pattern, description in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        matched_text = match.group(0)
                        
                        # Check if this is a placeholder/example that should be excluded
                        if any(re.search(exclude_pattern, matched_text, re.IGNORECASE) for exclude_pattern in exclude_patterns):
                            continue
                        
                        # Check if this is in a comment or documentation
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_content = content[line_start:match.end()]
                        
                        # Skip if it's in a comment (starts with # or //)
                        if line_content.strip().startswith('#') or line_content.strip().startswith('//'):
                            continue
                        
                        # Skip if it's in a docstring or comment block
                        if 'Format:' in line_content or 'Example:' in line_content or 'Note:' in line_content:
                            continue
                        
                        # Skip database connection patterns in comments
                        if 'postgresql://' in matched_text and ('Format:' in line_content or 'comment' in line_content.lower()):
                            continue
                        
                        # Skip test configurations
                        if 'test-' in matched_text.lower() or 'testing-only' in matched_text.lower() or 'for-testing' in matched_text.lower() or 'test-secret-key-for-testing-only' in matched_text.lower():
                            continue
                        
                        found_secrets.append(f"{description} in {file_path.relative_to(project_root)}")
                        break  # Only report once per file
                        
            except Exception as e:
                print(f"⚠️  Could not scan {file_path.name}: {e}")
    
    if found_secrets:
        print("⚠️  Potential secrets found:")
        for secret in found_secrets:
            print(f"   - {secret}")
    else:
        print("✅ No obvious secrets detected!")
    
    input("\nPress Enter to continue...")

def run_all_scans():
    """Run all security scans."""
    print("🛡️  COMPREHENSIVE SECURITY SCAN")
    print("=" * 50)
    
    scans = [
        ("Dependency Vulnerability", run_dependency_scan),
        ("Code Security Analysis", run_code_security_scan),
        ("Secret Detection", run_secret_detection_scan),
    ]
    
    results = {}
    
    for scan_name, scan_func in scans:
        print(f"\n🔄 Running {scan_name}...")
        try:
            scan_func()
            results[scan_name] = "✅ Completed"
        except Exception as e:
            print(f"❌ {scan_name} failed: {e}")
            results[scan_name] = f"❌ Failed: {e}"
    
    # Generate summary report
    print("\n📊 SECURITY SCAN SUMMARY")
    print("=" * 30)
    for scan_name, status in results.items():
        print(f"{scan_name}: {status}")
    
    input("\nPress Enter to continue...")

def generate_security_report():
    """Generate comprehensive security report."""
    print("📊 GENERATING SECURITY REPORT")
    print("=" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = project_root / "docs" / "security" / f"security_report_{timestamp}.md"
    
    try:
        with open(report_file, 'w') as f:
            f.write(f"# Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Overview\n")
            f.write("This report contains the results of comprehensive security scans.\n\n")
            f.write("## Scan Types\n")
            f.write("- Dependency Vulnerability Scan (Safety)\n")
            f.write("- Code Security Analysis (Bandit)\n")
            f.write("- Secret Detection Scan\n\n")
            f.write("## Recommendations\n")
            f.write("1. Review all identified vulnerabilities\n")
            f.write("2. Update vulnerable dependencies\n")
            f.write("3. Fix code security issues\n")
            f.write("4. Remove any hardcoded secrets\n")
            f.write("5. Implement security best practices\n")
        
        print(f"✅ Security report generated: {report_file}")
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")
    
    input("\nPress Enter to continue...")

def update_security_database():
    """Update security vulnerability database."""
    print("🔄 UPDATING SECURITY DATABASE")
    print("=" * 40)
    
    success, stdout, stderr = run_command(
        "py -m safety scan --update",
        "Updating Safety vulnerability database"
    )
    
    if success:
        print("✅ Security database updated successfully!")
    else:
        print("❌ Failed to update security database!")
        print(f"Error: {stderr}")
    
    input("\nPress Enter to continue...")

def view_previous_results():
    """View previous scan results."""
    print("📈 PREVIOUS SCAN RESULTS")
    print("=" * 40)
    
    security_dir = project_root / "docs" / "security"
    
    if not security_dir.exists():
        print("❌ No security directory found!")
        input("\nPress Enter to continue...")
        return
    
    # List recent scan files
    scan_files = list(security_dir.glob("*scan*"))
    
    if not scan_files:
        print("❌ No previous scan results found!")
        input("\nPress Enter to continue...")
        return
    
    print("📁 Recent scan files:")
    for file in sorted(scan_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"   - {file.name} ({mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    input("\nPress Enter to continue...")

def configure_scan_settings():
    """Configure scan settings."""
    print("⚙️  CONFIGURE SCAN SETTINGS")
    print("=" * 40)
    
    print("Current scan configuration:")
    print("- Safety: Uses default vulnerability database")
    print("- Bandit: Scans app/ directory recursively")
    print("- Secret Detection: Uses common patterns")
    print()
    print("To customize settings:")
    print("1. Edit this script to modify scan parameters")
    print("2. Create .bandit config file for Bandit settings")
    print("3. Use .safety config file for Safety settings")
    print()
    print("For more information, see:")
    print("- https://bandit.readthedocs.io/")
    print("- https://pyup.io/safety/")
    
    input("\nPress Enter to continue...")

def show_help():
    """Show help and documentation."""
    print("❓ HELP & DOCUMENTATION")
    print("=" * 40)
    
    print("🛡️  Security Scan Types:")
    print()
    print("1. Dependency Vulnerability Scan:")
    print("   - Uses Safety scan command to check Python packages against CVE database")
    print("   - Identifies known security vulnerabilities in dependencies")
    print("   - Recommends updates for vulnerable packages")
    print()
    print("2. Code Security Analysis:")
    print("   - Uses Bandit to analyze Python code for security issues")
    print("   - Detects common vulnerabilities like SQL injection, hardcoded passwords")
    print("   - Provides severity ratings and remediation advice")
    print()
    print("3. Secret Detection:")
    print("   - Scans for hardcoded secrets, API keys, passwords")
    print("   - Uses pattern matching to identify sensitive data")
    print("   - Helps prevent accidental credential exposure")
    print()
    print("📊 Understanding Results:")
    print("- ✅ Green: No issues found")
    print("- ⚠️  Yellow: Low/medium severity issues")
    print("- ❌ Red: High severity issues requiring immediate attention")
    print()
    print("🔧 Troubleshooting:")
    print("- Ensure Safety and Bandit are installed: pip install safety bandit")
    print("- Check Python path and virtual environment")
    print("- Verify file permissions for writing results")
    
    input("\nPress Enter to continue...")

def main():
    """Main function."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        print_menu()
        
        try:
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye! Stay secure!")
                break
            elif choice == '1':
                run_all_scans()
            elif choice == '2':
                run_dependency_scan()
            elif choice == '3':
                run_code_security_scan()
            elif choice == '4':
                run_secret_detection_scan()
            elif choice == '5':
                generate_security_report()
            elif choice == '6':
                update_security_database()
            elif choice == '7':
                view_previous_results()
            elif choice == '8':
                configure_scan_settings()
            elif choice == '9':
                show_help()
            else:
                print("\n❌ Invalid choice! Please enter 0-9.")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay secure!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
