#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
界面展示完整性验证工具
检查所有修复后的界面模块是否能够完整展示分析结果
"""

import os
import sys
import logging
import json
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("界面验证工具")

# 要验证的面板列表
PANELS_TO_VERIFY = [
    {"name": "量子选股面板", "file": "quantum_stock_finder_panel.py", "class": "QuantumStockFinderPanel", "method": "display_results"},
    {"name": "市场分析面板", "file": "market_analysis_panel.py", "class": "MarketAnalysisPanel", "method": "display_results"},
    {"name": "量子电路面板", "file": "quantum_circuit_panel.py", "class": "QuantumCircuitPanel", "method": "display_results"},
    {"name": "策略回测面板", "file": "strategy_backtest_panel.py", "class": "StrategyBacktestPanel", "method": "display_results"},
    {"name": "指数研究面板", "file": "index_research_panel.py", "class": "IndexResearchPanel", "method": "display_results"},
    {"name": "新闻分析面板", "file": "news_analysis_panel.py", "class": "NewsAnalysisPanel", "method": "display_results"},
    {"name": "打板涨停面板", "file": "limit_board_panel.py", "class": "LimitBoardPanel", "method": "display_results"},
    {"name": "爆发式股票面板", "file": "explosive_stocks_panel.py", "class": "ExplosiveStocksPanel", "method": "display_results"}
]

def find_panels_directory():
    """查找面板目录"""
    possible_paths = [
        "QTS/quantum_desktop/ui/panels",
        "quantum_desktop/ui/panels",
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            logger.info(f"找到面板目录: {path}")
            return path
    
    logger.error("未找到面板目录")
    return None

def verify_method_exists(file_path, class_name, method_name):
    """验证方法是否存在"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找类定义
        class_pattern = f"class {class_name}("
        if class_pattern not in content:
            logger.error(f"类 {class_name} 在文件中未找到")
            return False
        
        # 查找方法定义
        method_pattern = f"def {method_name}"
        if method_pattern in content:
            return True
        else:
            logger.warning(f"方法 {method_name} 在类 {class_name} 中未找到")
            return False
    
    except Exception as e:
        logger.error(f"验证方法时出错: {str(e)}")
        return False

def verify_method_handles_results(file_path, class_name, method_name):
    """验证方法是否能够处理分析结果"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找方法定义
        class_start = content.find(f"class {class_name}(")
        if class_start == -1:
            return False
        
        method_start = content.find(f"def {method_name}", class_start)
        if method_start == -1:
            return False
        
        # 查找方法结束位置
        next_method = content.find("\n    def ", method_start + 10)
        if next_method == -1:
            method_content = content[method_start:]
        else:
            method_content = content[method_start:next_method]
        
        # 检查方法内容是否包含结果处理
        checks = [
            "result_table" in method_content,  # 表格显示
            "setText" in method_content,      # 文本显示
            "update_" in method_content,      # 更新方法
            "dict" in method_content,         # 字典处理
            "list" in method_content          # 列表处理
        ]
        
        # 至少满足3个条件
        if sum(checks) >= 3:
            return True
        else:
            logger.warning(f"方法 {method_name} 可能无法完整处理结果 (满足 {sum(checks)}/5 条件)")
            return False
    
    except Exception as e:
        logger.error(f"验证方法处理能力时出错: {str(e)}")
        return False

def verify_panel(panel, panels_dir):
    """验证单个面板"""
    file_path = os.path.join(panels_dir, panel["file"])
    if not os.path.exists(file_path):
        logger.error(f"面板文件不存在: {file_path}")
        return {
            "name": panel["name"],
            "file": panel["file"],
            "exists": False,
            "method_exists": False,
            "handles_results": False,
            "status": "文件不存在"
        }
    
    # 验证方法是否存在
    method_exists = verify_method_exists(file_path, panel["class"], panel["method"])
    
    # 验证方法是否能够处理结果
    handles_results = False
    if method_exists:
        handles_results = verify_method_handles_results(file_path, panel["class"], panel["method"])
    
    # 确定状态
    if method_exists and handles_results:
        status = "完全支持"
    elif method_exists:
        status = "方法存在但可能无法完整处理结果"
    else:
        status = "方法不存在"
    
    return {
        "name": panel["name"],
        "file": panel["file"],
        "exists": True,
        "method_exists": method_exists,
        "handles_results": handles_results,
        "status": status
    }

def generate_report(results):
    """生成验证报告"""
    report = {
        "验证时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "验证结果摘要": {
            "总面板数": len(results),
            "方法存在数": sum(1 for r in results if r["method_exists"]),
            "完全支持数": sum(1 for r in results if r["method_exists"] and r["handles_results"])
        },
        "详细结果": results
    }
    
    # 保存报告
    report_file = "panel_verification_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"验证报告已保存到 {report_file}")
    
    # 生成文本报告
    text_report = f"""
界面展示完整性验证报告
验证时间: {report['验证时间']}

验证结果摘要:
- 总面板数: {report['验证结果摘要']['总面板数']}
- 方法存在数: {report['验证结果摘要']['方法存在数']}
- 完全支持数: {report['验证结果摘要']['完全支持数']}

详细结果:
"""
    
    for panel in results:
        text_report += f"""
- {panel['name']} ({panel['file']})
  状态: {panel['status']}
  方法存在: {'是' if panel['method_exists'] else '否'}
  完整处理结果: {'是' if panel['handles_results'] else '否'}
"""
    
    report_txt_file = "panel_verification_report.txt"
    with open(report_txt_file, "w", encoding="utf-8") as f:
        f.write(text_report)
    
    logger.info(f"文本验证报告已保存到 {report_txt_file}")
    
    return report

def main():
    """主函数"""
    logger.info("开始验证界面模块的结果显示完整性...")
    
    # 查找面板目录
    panels_dir = find_panels_directory()
    if not panels_dir:
        return 1
    
    # 验证每个面板
    results = []
    for panel in PANELS_TO_VERIFY:
        logger.info(f"验证面板: {panel['name']}")
        result = verify_panel(panel, panels_dir)
        results.append(result)
        logger.info(f"面板 {panel['name']} 验证结果: {result['status']}")
    
    # 生成报告
    report = generate_report(results)
    
    # 打印摘要
    print("\n验证摘要:")
    print(f"总面板数: {report['验证结果摘要']['总面板数']}")
    print(f"方法存在数: {report['验证结果摘要']['方法存在数']}")
    print(f"完全支持数: {report['验证结果摘要']['完全支持数']}")
    
    # 验证成功条件：所有面板都至少有方法存在
    if all(r["method_exists"] for r in results):
        logger.info("所有界面模块都已实现结果显示方法")
        return 0
    else:
        logger.warning("有界面模块缺少结果显示方法")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 