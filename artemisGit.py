#!/usr/bin/env python3
"""
Git Repository Downloader Script
Downloads three Git repositories automatically with GUI
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from pathlib import Path

# Configuration - Default Artemis Repositories for WNCKTC1TESTAUFGABEJAVA
DEFAULT_REPOSITORIES = [
    {
        "url": "https://nutzerf@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-exercise.git",
        "name": "exercise"
    },
    {
        "url": "https://nutzer@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-solution.git", 
        "name": "solution"
    },
    {
        "url": "https://nutzer@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-tests.git",
        "name": "tests"
    }
]

# Base directory for downloads (script directory)
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR

def run_command(command, cwd=None):
    """Executes a shell command and returns the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_git_installed():
    """Checks if Git is installed"""
    success, _ = run_command("git --version")
    return success

def clone_repository(repo_info):
    """Clones a single repository"""
    repo_url = repo_info["url"]
    repo_name = repo_info["name"]
    target_path = DOWNLOAD_DIR / repo_name
    
    print(f"\n📥 Downloading repository: {repo_name}")
    print(f"URL: {repo_url}")
    print(f"Target directory: {target_path}")
    
    # Check if directory already exists
    if target_path.exists():
        print(f"🗑️  Directory {target_path} already exists - deleting automatically...")
        import shutil
        import stat
        
        def force_remove_readonly(func, path, _):
            """Removes readonly attribute and deletes the file/folder"""
            try:
                if os.path.exists(path):
                    # Remove readonly attribute
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            except Exception:
                pass
        
        try:
            # Try normal deletion first
            if target_path.exists():
                shutil.rmtree(target_path, onerror=force_remove_readonly)
            
            # Check if directory still exists
            if target_path.exists():
                # Last chance: Delete with Windows-specific methods
                import time
                time.sleep(0.1)  # Wait briefly
                if target_path.exists():
                    # Try with rmdir for empty directories
                    for root, dirs, files in os.walk(target_path, topdown=False):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                os.chmod(file_path, stat.S_IWRITE)
                                os.remove(file_path)
                            except Exception:
                                pass
                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            try:
                                os.rmdir(dir_path)
                            except Exception:
                                pass
                    try:
                        os.rmdir(target_path)
                    except Exception:
                        pass
            
            if target_path.exists():
                print(f"⚠️  Warning: Directory could not be completely deleted")
                # Try PowerShell as last option
                ps_command = f'Remove-Item -Path "{target_path}" -Recurse -Force'
                success, _ = run_command(f'powershell -Command "{ps_command}"')
                if not success and target_path.exists():
                    print(f"❌ Directory could not be deleted")
                    return False
            
            print("✅ Old directory successfully deleted")
            
        except Exception as e:
            print(f"❌ Error during deletion: {e}")
            return False
    
    # Clone repository
    clone_command = f"git clone {repo_url} {target_path}"
    success, output = run_command(clone_command)
    
    if success:
        print(f"✅ Repository successfully cloned: {repo_name}")
        return True
    else:
        print(f"❌ Error cloning {repo_name}: {output}")
        return False

def check_repository_reachable(repo_url):
    """Checks if a repository is reachable"""
    try:
        # Try to do a git ls-remote to check if repository is accessible
        command = f"git ls-remote {repo_url}"
        success, output = run_command(command)
        return success, output if success else "Repository not reachable or invalid credentials"
    except Exception as e:
        return False, str(e)

class GitDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Repository Downloader")
        self.root.geometry("800x700")
        
        # Initialize repositories with default values
        self.repositories = DEFAULT_REPOSITORIES.copy()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Git Repository Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Repository input section
        self.create_repository_inputs(main_frame)
        
        # Buttons section
        self.create_buttons(main_frame)
        
        # Output section
        self.create_output_section(main_frame)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def create_repository_inputs(self, parent):
        # Repository inputs
        repo_frame = ttk.LabelFrame(parent, text="Repository Configuration", padding="10")
        repo_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        repo_frame.columnconfigure(1, weight=1)
        
        self.url_entries = []
        self.name_entries = []
        self.status_labels = []
        
        for i in range(3):
            # Repository label
            ttk.Label(repo_frame, text=f"Repository {i+1}:").grid(row=i*3, column=0, sticky=tk.W, pady=(10, 5))
            
            # URL input
            ttk.Label(repo_frame, text="URL:").grid(row=i*3+1, column=0, sticky=tk.W, padx=(20, 5))
            url_entry = ttk.Entry(repo_frame, width=60)
            url_entry.grid(row=i*3+1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
            url_entry.insert(0, self.repositories[i]["url"])
            self.url_entries.append(url_entry)
            
            # Test button
            test_btn = ttk.Button(repo_frame, text="Test", width=8,
                                command=lambda idx=i: self.test_repository(idx))
            test_btn.grid(row=i*3+1, column=2, padx=(5, 0))
            
            # Name input
            ttk.Label(repo_frame, text="Name:").grid(row=i*3+2, column=0, sticky=tk.W, padx=(20, 5))
            name_entry = ttk.Entry(repo_frame, width=30)
            name_entry.grid(row=i*3+2, column=1, sticky=tk.W, padx=(0, 5))
            name_entry.insert(0, self.repositories[i]["name"])
            self.name_entries.append(name_entry)
            
            # Status label
            status_label = ttk.Label(repo_frame, text="Not tested", foreground="gray")
            status_label.grid(row=i*3+2, column=2, padx=(5, 0))
            self.status_labels.append(status_label)
            
    def create_buttons(self, parent):
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Test all button
        self.test_all_btn = ttk.Button(button_frame, text="🔍 Test All Repositories", 
                                      command=self.test_all_repositories)
        self.test_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Download button
        self.download_btn = ttk.Button(button_frame, text="📥 Download All", 
                                      command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear logs button
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear Logs", 
                                   command=self.clear_output)
        self.clear_btn.pack(side=tk.LEFT)
        
    def create_output_section(self, parent):
        # Output section
        output_frame = ttk.LabelFrame(parent, text="Output Log", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def log_message(self, message):
        """Add message to output log"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_output(self):
        """Clear the output log"""
        self.output_text.delete(1.0, tk.END)
        
    def test_repository(self, index):
        """Test a single repository"""
        url = self.url_entries[index].get().strip()
        if not url:
            self.status_labels[index].config(text="No URL", foreground="red")
            return
            
        self.status_labels[index].config(text="Testing...", foreground="blue")
        self.root.update_idletasks()
        
        def test_thread():
            success, message = check_repository_reachable(url)
            if success:
                self.status_labels[index].config(text="✅ Reachable", foreground="green")
                self.log_message(f"Repository {index+1}: Reachable")
            else:
                self.status_labels[index].config(text="❌ Failed", foreground="red")
                self.log_message(f"Repository {index+1}: {message}")
        
        threading.Thread(target=test_thread, daemon=True).start()
        
    def test_all_repositories(self):
        """Test all repositories"""
        self.log_message("🔍 Testing all repositories...")
        for i in range(3):
            self.test_repository(i)
            
    def update_repositories_from_input(self):
        """Update repositories list from GUI inputs"""
        self.repositories = []
        for i in range(3):
            url = self.url_entries[i].get().strip()
            name = self.name_entries[i].get().strip()
            if url and name:
                self.repositories.append({"url": url, "name": name})
                
    def start_download(self):
        """Start the download process in a separate thread"""
        self.update_repositories_from_input()
        
        if not self.repositories:
            messagebox.showerror("Error", "Please enter at least one repository URL and name.")
            return
            
        # Disable buttons during download
        self.download_btn.config(state="disabled")
        self.test_all_btn.config(state="disabled")
        self.progress.start()
        
        threading.Thread(target=self.download_repositories, daemon=True).start()
        
    def download_repositories(self):
        """Download all repositories"""
        try:
            self.log_message("🚀 Starting Git Repository Download")
            self.log_message("=" * 50)
            
            # Check Git installation
            self.log_message("🔍 Checking system requirements...")
            if not check_git_installed():
                self.log_message("❌ Git is not installed or not available in PATH")
                self.log_message("Please install Git: https://git-scm.com/")
                return
            self.log_message("✅ Git found")
            
            # Show download directory
            self.log_message(f"📁 Download directory: {DOWNLOAD_DIR}")
            
            # Start downloading
            self.log_message(f"\n🔄 Starting download of {len(self.repositories)} repositories...")
            successful_downloads = []
            
            for repo_info in self.repositories:
                if self.clone_repository_gui(repo_info):
                    successful_downloads.append(DOWNLOAD_DIR / repo_info["name"])
            
            # Summary
            self.log_message(f"\n📊 Download completed!")
            self.log_message(f"✅ Successful: {len(successful_downloads)}/{len(self.repositories)} repositories")
            
            if successful_downloads:
                self.log_message("\nDownloaded repositories:")
                for path in successful_downloads:
                    self.log_message(f"  📁 {path}")
            
            self.log_message(f"\n🎉 All repositories successfully downloaded!")
            
        except Exception as e:
            self.log_message(f"\n❌ Unexpected error: {e}")
        finally:
            # Re-enable buttons
            self.progress.stop()
            self.download_btn.config(state="normal")
            self.test_all_btn.config(state="normal")
            
    def clone_repository_gui(self, repo_info):
        """Clone a repository with GUI logging"""
        repo_url = repo_info["url"]
        repo_name = repo_info["name"]
        target_path = DOWNLOAD_DIR / repo_name
        
        self.log_message(f"\n📥 Downloading repository: {repo_name}")
        self.log_message(f"URL: {repo_url}")
        self.log_message(f"Target directory: {target_path}")
        
        # Check if directory already exists and delete if necessary
        if target_path.exists():
            self.log_message(f"🗑️  Directory {target_path} already exists - deleting automatically...")
            if not self.delete_directory_gui(target_path):
                return False
        
        # Clone repository
        clone_command = f"git clone {repo_url} {target_path}"
        success, output = run_command(clone_command)
        
        if success:
            self.log_message(f"✅ Repository successfully cloned: {repo_name}")
            return True
        else:
            self.log_message(f"❌ Error cloning {repo_name}: {output}")
            return False
            
    def delete_directory_gui(self, target_path):
        """Delete directory with GUI logging"""
        import shutil
        import stat
        import time
        
        def force_remove_readonly(func, path, _):
            try:
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            except Exception:
                pass
        
        try:
            if target_path.exists():
                shutil.rmtree(target_path, onerror=force_remove_readonly)
            
            if target_path.exists():
                time.sleep(0.1)
                if target_path.exists():
                    for root, dirs, files in os.walk(target_path, topdown=False):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                os.chmod(file_path, stat.S_IWRITE)
                                os.remove(file_path)
                            except Exception:
                                pass
                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            try:
                                os.rmdir(dir_path)
                            except Exception:
                                pass
                    try:
                        os.rmdir(target_path)
                    except Exception:
                        pass
            
            if target_path.exists():
                self.log_message(f"⚠️  Warning: Directory could not be completely deleted")
                ps_command = f'Remove-Item -Path "{target_path}" -Recurse -Force'
                success, _ = run_command(f'powershell -Command "{ps_command}"')
                if not success and target_path.exists():
                    self.log_message(f"❌ Directory could not be deleted")
                    return False
            
            self.log_message("✅ Old directory successfully deleted")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error during deletion: {e}")
            return False

def main():
    """Main function - starts the GUI"""
    # Check if tkinter is available
    try:
        root = tk.Tk()
        app = GitDownloaderGUI(root)
        root.mainloop()
    except ImportError:
        print("❌ tkinter is not available. Please install tkinter or use the console version.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
