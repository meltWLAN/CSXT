#!/bin/bash
# 此脚本启动量子交易系统并显示所有增强模块

# 进入项目目录
cd /Users/mac/CSXT/QTS

# 设置环境变量以启用完整界面
export QTS_SHOW_ALL_MODULES=1
export QTS_ENHANCED_UI=1

# 启动系统
python launch_quantum_core.py --mode desktop
