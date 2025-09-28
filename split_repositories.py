#!/usr/bin/env python3
"""
Repository Split Script untuk Shrimpwatch
Script untuk memisahkan file berdasarkan jenis repository (public/private)
"""

import os
import shutil
from pathlib import Path

class RepositorySplitter:
    def __init__(self):
        """Initialize repository splitter"""
        self.public_dir = Path("shrimpwatch-public")
        self.private_dir = Path("shrimpwatch-private")
        
        # File yang aman untuk public repository
        self.public_files = [
            'app.py',
            'config.py',
            'database.py',
            'requirements.txt',
            'setup.py',
            'run.py',
            'database_setup.py',
            'check_secrets.py',
            'split_repositories.py',
            '.gitignore',
            'README.md',
            'INSTALL.md',
            'QUICK_START.md',
            'SECURITY.md',
            'REPOSITORY_STRATEGY.md',
            'MODEL_SETUP.md',
            'github_setup.md',
            'LICENSE',
            'env.example',
            'asset/',
            'docs/',
            'tests/',
            'scripts/',
            '.github/',
        ]
        
        # File yang hanya untuk private repository
        self.private_only_files = [
            '.env',
            '.env.local',
            '.env.production',
            '.env.staging',
            'config.ini',
            'secrets.json',
            'credentials.json',
            'best.pt',
            '*.pth',
            '*.h5',
            '*.pkl',
            'data/',
            'datasets/',
            'uploads/',
            'temp/',
            'tmp/',
            'logs/',
            'log/',
            'backup/',
            'backups/',
            '*.bak',
            '*.backup',
            '*.old',
            'local_config.py',
            'dev_config.py',
            'sensitive/',
            'private/',
            '__pycache__/',
            '*.pyc',
            '.streamlit/',
            '.pytest_cache/',
            'venv/',
            'env/',
            'ENV/',
            '.venv/',
            '.env/',
        ]
    
    def create_directories(self):
        """Create public and private directories"""
        self.public_dir.mkdir(exist_ok=True)
        self.private_dir.mkdir(exist_ok=True)
        
        print(f"✅ Created directories:")
        print(f"  - Public: {self.public_dir}")
        print(f"  - Private: {self.private_dir}")
    
    def copy_public_files(self):
        """Copy files safe for public repository"""
        copied_files = []
        
        for file_pattern in self.public_files:
            if '*' in file_pattern:
                # Handle wildcard patterns
                for file_path in Path('.').rglob(file_pattern):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        dest_path = self.public_dir / file_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        copied_files.append(str(file_path))
            else:
                # Handle exact file/directory names
                if Path(file_pattern).exists():
                    source_path = Path(file_pattern)
                    dest_path = self.public_dir / file_pattern
                    
                    if source_path.is_file():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        copied_files.append(file_pattern)
                    elif source_path.is_dir():
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        copied_files.append(file_pattern)
        
        print(f"✅ Copied {len(copied_files)} files to public repository")
        return copied_files
    
    def copy_private_files(self):
        """Copy all files to private repository"""
        copied_files = []
        
        # Copy all files from current directory
        for item in Path('.').iterdir():
            if item.name.startswith('.') and item.name not in ['.git', '.gitignore']:
                continue  # Skip hidden files except .gitignore
            
            dest_path = self.private_dir / item.name
            
            if item.is_file():
                shutil.copy2(item, dest_path)
                copied_files.append(item.name)
            elif item.is_dir():
                shutil.copytree(item, dest_path, dirs_exist_ok=True)
                copied_files.append(item.name)
        
        print(f"✅ Copied {len(copied_files)} files to private repository")
        return copied_files
    
    def create_gitignore_public(self):
        """Create .gitignore for public repository"""
        gitignore_content = """# Environment variables
.env
.env.local
.env.production
.env.staging

# Model files (if proprietary)
*.pt
*.pth
*.h5
*.pkl

# Log files
*.log
logs/
log/

# Cache and temporary files
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.cache/
.pytest_cache/

# Virtual environment
venv/
env/
ENV/
.venv/
.env/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Streamlit cache
.streamlit/

# Data files
data/
datasets/
uploads/
temp/
tmp/

# Backup files
*.bak
*.backup
*.old

# Jupyter notebook checkpoints
.ipynb_checkpoints/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation build
docs/_build/

# Local development
local_config.py
dev_config.py
"""
        
        gitignore_path = self.public_dir / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        print(f"✅ Created .gitignore for public repository")
    
    def create_gitignore_private(self):
        """Create .gitignore for private repository"""
        gitignore_content = """# Cache and temporary files
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.cache/
.pytest_cache/

# Virtual environment
venv/
env/
ENV/
.venv/
.env/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Streamlit cache
.streamlit/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation build
docs/_build/
"""
        
        gitignore_path = self.private_dir / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        print(f"✅ Created .gitignore for private repository")
    
    def create_setup_scripts(self):
        """Create setup scripts for each repository"""
        
        # Public repository setup script
        public_setup = """#!/usr/bin/env python3
\"\"\"
Public Repository Setup Script
\"\"\"

import subprocess
import sys

def setup_public_repository():
    \"\"\"Setup public repository\"\"\"
    print("🌐 Setting up public repository...")
    
    # Initialize git
    subprocess.run(["git", "init"], check=True)
    
    # Add remote
    remote_url = input("Enter public repository URL: ").strip()
    if remote_url:
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    
    # Add files
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit
    subprocess.run(["git", "commit", "-m", "Initial public release"], check=True)
    
    # Push
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    
    print("✅ Public repository setup complete!")

if __name__ == "__main__":
    setup_public_repository()
"""
        
        with open(self.public_dir / 'setup_public.py', 'w') as f:
            f.write(public_setup)
        
        # Private repository setup script
        private_setup = """#!/usr/bin/env python3
\"\"\"
Private Repository Setup Script
\"\"\"

import subprocess
import sys

def setup_private_repository():
    \"\"\"Setup private repository\"\"\"
    print("🔒 Setting up private repository...")
    
    # Initialize git
    subprocess.run(["git", "init"], check=True)
    
    # Add remote
    remote_url = input("Enter private repository URL: ").strip()
    if remote_url:
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    
    # Add files
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit
    subprocess.run(["git", "commit", "-m", "Initial private repository"], check=True)
    
    # Push
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    
    print("✅ Private repository setup complete!")

if __name__ == "__main__":
    setup_private_repository()
"""
        
        with open(self.private_dir / 'setup_private.py', 'w') as f:
            f.write(private_setup)
        
        print("✅ Created setup scripts for both repositories")
    
    def split_repositories(self):
        """Split repositories into public and private"""
        print("🔄 Splitting repositories...")
        
        # Create directories
        self.create_directories()
        
        # Copy files
        public_files = self.copy_public_files()
        private_files = self.copy_private_files()
        
        # Create .gitignore files
        self.create_gitignore_public()
        self.create_gitignore_private()
        
        # Create setup scripts
        self.create_setup_scripts()
        
        print(f"\n✅ Repository split complete!")
        print(f"📁 Public repository: {self.public_dir}")
        print(f"📁 Private repository: {self.private_dir}")
        
        return {
            'public_files': public_files,
            'private_files': private_files
        }

def main():
    """Main function for repository splitting"""
    print("🔄 Shrimpwatch Repository Splitter")
    print("=" * 40)
    
    splitter = RepositorySplitter()
    
    # Split repositories
    results = splitter.split_repositories()
    
    print(f"\n📋 Summary:")
    print(f"  - Public files: {len(results['public_files'])}")
    print(f"  - Private files: {len(results['private_files'])}")
    
    print(f"\n📝 Next steps:")
    print(f"1. Review files in {splitter.public_dir}")
    print(f"2. Review files in {splitter.private_dir}")
    print(f"3. Setup public repository: cd {splitter.public_dir} && python setup_public.py")
    print(f"4. Setup private repository: cd {splitter.private_dir} && python setup_private.py")

if __name__ == "__main__":
    main()
