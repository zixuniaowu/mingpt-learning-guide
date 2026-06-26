"""
Setup script for minGPT package installation.
minGPT包安装的设置脚本。
minGPTパッケージのインストール用セットアップスクリプト。
"""

from setuptools import setup

setup(name='minGPT',
      version='0.0.1',
      author='Andrej Karpathy',
      packages=['mingpt'],
      description='A PyTorch re-implementation of GPT',
      license='MIT',
      install_requires=[
            'torch',
      ],
)
