#!/usr/bin/env python
"""
启动 Jupyter Notebook 服务器的脚本
Jupyter Notebook サーバーを起動するスクリプト
"""

import os
import webbrowser
import subprocess
import sys
import time

def main():
    # 获取笔记本路径
    notebook_path = os.path.join(os.path.dirname(__file__), 'learning_guide.ipynb')
    
    print("=" * 60)
    print("🚀 启动 Jupyter Notebook 服务器...")
    print("🚀 Jupyter Notebook サーバーを起動します...")
    print("=" * 60)
    print()
    print(f"笔记本文件: {notebook_path}")
    print(f"Notebook file: {notebook_path}")
    print()
    print("服务器启动中...")
    print("Starting server...")
    print()
    
    # 启动 Jupyter
    cmd = [sys.executable, '-m', 'notebook', notebook_path]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n服务器已停止 (Server stopped)")
        sys.exit(0)

if __name__ == '__main__':
    main()
