#!/usr/bin/env python3
"""
GitHub Repo Auto-Clone Skill
自動檢測 GitHub URL 並克隆到 tmp 目錄
"""

import os
import re
import sys
import subprocess

def auto_clean_repo(path):
    """
    自動清理研究完的 tmp 目錄
    """
    if os.path.exists(path):
        try:
            subprocess.run(['rm', '-rf', path], check=True)
            print(f"🗑️  已自動清理：{path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 清理失敗：{e.stderr}")
            return False
    return False

def auto_detect_and_clone(url, cleanup_after=False):
    """
    自動檢測 GitHub URL 並執行克隆
    如果 cleanup_after=True，研究完後會自動清理 tmp 目錄
    """
    # 檢測是否為 GitHub URL
    if re.match(r'^https?://(?:www\.)?github\.com/.*', url):
        # 去除 cleanup 參數
        url_base = re.sub(r'\?.*$', '', url)
        
        # 提取 repo 名稱（格式：https://github.com/username/repo.git 或 https://github.com/user/repo）
        repo_match = re.search(r'github\.com/([^/]+/[^/]+?)(?:\.git)?$', url_base)
        if repo_match:
            parts = repo_match.group(1).split('/')
            owner = parts[0]
            repo = parts[1]
            
            # 轉換為 .git 格式
            # git clone https://github.com/owner/repo.git /path
            git_url = f"https://github.com/{owner}/{repo}.git"
            
            # 克隆到 tmp 目錄
            clone_path = f"/tmp/{repo}"
            
            # 執行 git clone
            try:
                result = subprocess.run(
                    ['git', 'clone', git_url, clone_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ 已自動克隆：{git_url}")
                print(f"📁 下載到：{clone_path}")
                
                # 如果設定為研究完後清理
                if cleanup_after:
                    auto_clean_repo(clone_path)
                
                return True, clone_path
            except subprocess.CalledProcessError as e:
                print(f"❌ 克隆失敗：{e.stderr}")
                return False, None
            except Exception as e:
                print(f"❌ 錯誤：{e}")
                return False, None
        else:
            print("❌ 無法解析 repo 名稱")
            return False, None
    else:
        print("ℹ️  未檢測到 GitHub URL，請手動輸入 /github-repo 命令")
        return False, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        # 如果 URL 以 ?cleanup=true 結束，則研究完後自動清理
        if '?' in url and url.endswith('?cleanup=true'):
            cleanup_after = True
        else:
            cleanup_after = False
        
        success, path = auto_detect_and_clone(url, cleanup_after)
        if success:
            print(f"\n使用命令查看：ls -la {path}")
    else:
        print("用法：python auto_clone.py <github-url>")
        print("\n或直接在 TUI 中輸入 GitHub URL 即可自動克隆")
        print("\n範例：")
        print("  https://github.com/repo?cleanup=true  (研究完後自動清理)")
