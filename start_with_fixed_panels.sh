#!/bin/bash

# 启动带修复面板的量子交易系统
echo "====== 超神量子交易系统 - 面板修复启动器 ======"
echo "正在启动系统..."

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查QTS目录是否存在
if [ ! -d "QTS" ]; then
    echo "错误: 未找到QTS目录"
    exit 1
fi

# 切换到QTS目录
cd QTS

# 运行Python脚本
python3 start_with_fixed_panels.py

# 退出状态
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "系统启动失败，退出代码: $exit_code"
else
    echo "系统已成功启动"
fi 