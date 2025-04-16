#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
量子交易模拟器快速启动脚本
"""

import os
import sys
import argparse
import json
import logging
from datetime import datetime
import pandas as pd

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 直接导入模拟器模块
from QTS.models.quantum_simulator import QuantumSimulator
from QTS.utils.logger import setup_logging

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         量子交易系统模拟器 - Quantum Trading Simulator         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """设置参数并启动模拟器"""
    print_banner()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="量子交易系统模拟器")
    parser.add_argument("--stocks", type=str, default="000001.SZ,600000.SH,300001.SZ", 
                      help="要回测的股票代码列表，以逗号分隔")
    parser.add_argument("--start-date", type=str, 
                      default=(datetime.now().replace(year=datetime.now().year - 1)).strftime('%Y-%m-%d'),
                      help="回测开始日期，格式：YYYY-MM-DD")
    parser.add_argument("--end-date", type=str, 
                      default=datetime.now().strftime('%Y-%m-%d'),
                      help="回测结束日期，格式：YYYY-MM-DD")
    parser.add_argument("--rebalance", type=str, default="weekly", 
                      choices=["daily", "weekly", "monthly"],
                      help="投资组合再平衡频率")
    parser.add_argument("--config", type=str, default=None, 
                      help="配置文件路径")
    parser.add_argument("--plot", action="store_true", default=True,
                      help="是否绘制性能图表")
    parser.add_argument("--output", type=str, default="output",
                      help="输出目录")
    parser.add_argument("--log-level", type=str, default="INFO",
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    logs_dir = os.path.join(args.output, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    setup_logging(args.log_level, logs_dir)
    
    # 解析股票代码列表
    stock_symbols = [symbol.strip() for symbol in args.stocks.split(',')]
    
    print(f"股票池: {', '.join(stock_symbols)}")
    print(f"回测区间: {args.start_date} 至 {args.end_date}")
    print(f"再平衡频率: {args.rebalance}")
    print(f"--------------------------------------")
    
    # 创建模拟器实例
    simulator = QuantumSimulator(config_path=args.config)
    
    # 运行回测
    print("开始回测...")
    report = simulator.run_backtest(
        symbols=stock_symbols,
        start_date=args.start_date,
        end_date=args.end_date,
        rebalance_frequency=args.rebalance
    )
    
    # 打印回测结果摘要
    if "error" in report:
        print(f"\n错误: {report['error']}")
        return 1
    
    print("\n回测结果摘要:")
    print(f"--------------------------------------")
    print(f"初始资金: {report['initial_capital']:,.2f}")
    print(f"最终资产: {report['final_portfolio_value']:,.2f}")
    print(f"总收益率: {report['total_return']:.2%}")
    
    # 打印性能指标
    if 'performance_metrics' in report and report['performance_metrics']:
        metrics = report['performance_metrics']
        print(f"\n性能指标:")
        print(f"--------------------------------------")
        print(f"夏普比率: {metrics.get('sharpe_ratio', 0):.4f}")
        print(f"索提诺比率: {metrics.get('sortino_ratio', 0):.4f}")
        print(f"最大回撤: {metrics.get('max_drawdown', 0):.2%}")
        print(f"年化收益率: {metrics.get('annual_return', 0):.2%}")
        print(f"年化波动率: {metrics.get('annual_volatility', 0):.2%}")
    
    # 打印交易分析
    if 'trades_analysis' in report and report['trades_analysis']:
        trades = report['trades_analysis']
        print(f"\n交易分析:")
        print(f"--------------------------------------")
        print(f"总交易次数: {trades.get('total_trades', 0)}")
        print(f"买入交易: {trades.get('buy_trades', 0)}")
        print(f"卖出交易: {trades.get('sell_trades', 0)}")
        print(f"盈利交易: {trades.get('profitable_trades', 0)}")
        print(f"亏损交易: {trades.get('losing_trades', 0)}")
        print(f"胜率: {trades.get('win_rate', 0):.2%}")
        print(f"盈亏比: {trades.get('profit_loss_ratio', 0):.2f}")
        print(f"总利润: {trades.get('total_profit', 0):,.2f}")
        print(f"总亏损: {trades.get('total_loss', 0):,.2f}")
        print(f"净利润: {trades.get('net_profit', 0):,.2f}")
        print(f"总佣金: {trades.get('total_commission', 0):,.2f}")
    
    # 保存回测报告
    os.makedirs(args.output, exist_ok=True)
    report_path = os.path.join(args.output, f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print(f"\n保存回测报告到: {report_path}")
    simulator.save_report(report, report_path)
    
    # 绘制性能图表
    if args.plot:
        chart_path = os.path.join(args.output, f"performance_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        print("\n绘制性能图表...")
        simulator.plot_performance(output_path=chart_path)
    
    print("\n量子交易系统模拟回测完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 