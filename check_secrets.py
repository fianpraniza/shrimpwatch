#!/usr/bin/env python3
"""
Security Check Script untuk Shrimpwatch
Script untuk memeriksa file sensitif sebelum commit ke repository
"""

import os
import re
from pathlib import Path

class SecurityChecker:
    def __init__(self):
        """Initialize security checker"""
        self.sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'database_password\s*=\s*["\'][^"\']+["\']',
            r'db_password\s*=\s*["\'][^"\']+["\']',
        ]
        
        self.sensitive_files = [
            '.env',
            '.env.local',
            '.env.production',
            '.env.staging',
            'config.ini',
            'secrets.json',
            'credentials.json',
            '*.log',
            'logs/',
            'data/',
            'datasets/',
            'uploads/',
            'temp/',
            'tmp/',
            'backup/',
            'backups/',
            '*.bak',
            '*.backup',
            '*.old',
            'local_config.py',
            'dev_config.py',
            'sensitive/',
            'private/',
        ]
        
        self.sensitive_extensions = [
            '.pt',
            '.pth',
            '.h5',
            '.pkl',
            '.pem',
            '.key',
            '.crt',
            '.p12',
            '.pfx',
        ]
    
    def check_sensitive_files(self) -> list:
        """Check for sensitive files in repository"""
        sensitive_found = []
        
        for pattern in self.sensitive_files:
            if '*' in pattern:
                # Handle wildcard patterns
                for file_path in Path('.').rglob(pattern):
                    if file_path.is_file():
                        sensitive_found.append(str(file_path))
            else:
                # Handle exact file/directory names
                if Path(pattern).exists():
                    sensitive_found.append(pattern)
        
        return sensitive_found
    
    def check_sensitive_extensions(self) -> list:
        """Check for files with sensitive extensions"""
        sensitive_found = []
        
        for ext in self.sensitive_extensions:
            for file_path in Path('.').rglob(f'*{ext}'):
                if file_path.is_file():
                    sensitive_found.append(str(file_path))
        
        return sensitive_found
    
    def check_sensitive_content(self, file_path: str) -> list:
        """Check file content for sensitive patterns"""
        sensitive_content = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in self.sensitive_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            sensitive_content.append({
                                'file': file_path,
                                'line': line_num,
                                'content': line.strip(),
                                'pattern': pattern
                            })
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
        
        return sensitive_content
    
    def check_all_files(self) -> dict:
        """Check all files for sensitive content"""
        results = {
            'sensitive_files': [],
            'sensitive_extensions': [],
            'sensitive_content': []
        }
        
        # Check sensitive files
        results['sensitive_files'] = self.check_sensitive_files()
        
        # Check sensitive extensions
        results['sensitive_extensions'] = self.check_sensitive_extensions()
        
        # Check content in Python files
        for py_file in Path('.').rglob('*.py'):
            if py_file.is_file():
                content_results = self.check_sensitive_content(str(py_file))
                results['sensitive_content'].extend(content_results)
        
        return results
    
    def generate_report(self, results: dict) -> str:
        """Generate security report"""
        report = []
        report.append("🔒 Security Check Report")
        report.append("=" * 50)
        
        # Sensitive files
        if results['sensitive_files']:
            report.append("\n❌ Sensitive Files Found:")
            for file in results['sensitive_files']:
                report.append(f"  - {file}")
        else:
            report.append("\n✅ No sensitive files found")
        
        # Sensitive extensions
        if results['sensitive_extensions']:
            report.append("\n❌ Files with Sensitive Extensions:")
            for file in results['sensitive_extensions']:
                report.append(f"  - {file}")
        else:
            report.append("\n✅ No files with sensitive extensions found")
        
        # Sensitive content
        if results['sensitive_content']:
            report.append("\n❌ Sensitive Content Found:")
            for item in results['sensitive_content']:
                report.append(f"  - {item['file']}:{item['line']}")
                report.append(f"    Pattern: {item['pattern']}")
                report.append(f"    Content: {item['content']}")
        else:
            report.append("\n✅ No sensitive content found")
        
        return '\n'.join(report)
    
    def check_repository_safety(self) -> bool:
        """Check if repository is safe for public upload"""
        results = self.check_all_files()
        
        # Check if any sensitive items found
        has_sensitive_files = len(results['sensitive_files']) > 0
        has_sensitive_extensions = len(results['sensitive_extensions']) > 0
        has_sensitive_content = len(results['sensitive_content']) > 0
        
        if has_sensitive_files or has_sensitive_extensions or has_sensitive_content:
            print("❌ Repository is NOT safe for public upload!")
            print(self.generate_report(results))
            return False
        else:
            print("✅ Repository is safe for public upload!")
            return True

def main():
    """Main function for security checking"""
    print("🔒 Shrimpwatch Security Checker")
    print("=" * 40)
    
    checker = SecurityChecker()
    
    # Check repository safety
    if checker.check_repository_safety():
        print("\n🎉 Repository is ready for public upload!")
    else:
        print("\n⚠️  Please remove sensitive files before uploading to public repository")
        print("\n📋 Recommended actions:")
        print("1. Move sensitive files to .gitignore")
        print("2. Use environment variables for credentials")
        print("3. Encrypt sensitive data")
        print("4. Use private repository for sensitive files")

if __name__ == "__main__":
    main()
