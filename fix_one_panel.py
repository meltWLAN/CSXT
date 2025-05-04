#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单个面板结果展示修复工具
为指定面板添加结果展示方法
"""

import os
import sys
import logging
import shutil
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("panel_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("面板修复工具")

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak_{int(time.time())}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"已备份 {file_path} 到 {backup_path}")
        return True
    return False

def find_class_end(content, class_name):
    """查找类定义的结束位置"""
    class_start = content.find(f"class {class_name}(")
    if class_start == -1:
        return -1
    
    # 查找类定义结束的位置（下一个同级类定义或文件结束）
    next_class = content.find("\nclass ", class_start + 10)
    if next_class == -1:
        return len(content)
    return next_class

def add_display_method(file_path, panel_name, class_name):
    """为面板添加结果展示方法"""
    try:
        logger.info(f"正在处理 {panel_name} ({file_path})")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查类是否存在
        class_pattern = f"class {class_name}("
        if class_pattern not in content:
            logger.warning(f"类 {class_name} 在文件中未找到")
            return False
        
        # 检查是否已有展示方法
        display_methods = ["display_results", "update_results", "show_results", "_update_display", "_display_data"]
        for method in display_methods:
            if f"def {method}" in content:
                logger.info(f"{panel_name} 已有结果展示方法 ({method})")
                return True
        
        # 查找类定义结束的位置
        class_end = find_class_end(content, class_name)
        if class_end == -1:
            logger.error(f"无法确定类 {class_name} 的结束位置")
            return False
        
        # 备份文件
        backup_file(file_path)
        
        # 准备要添加的方法
        display_method = f"""
    def display_results(self, results=None):
        \"\"\"显示分析结果\"\"\"
        logger = logging.getLogger(f"{panel_name}")
        logger.info("显示 {panel_name} 分析结果")
        
        # 使用传入的结果或取类属性中的结果
        if results is None:
            if hasattr(self, 'results'):
                results = self.results
            else:
                logger.warning("没有可用的分析结果")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("没有可用的分析结果")
                return
        
        try:
            # 更新状态标签
            if hasattr(self, 'status_label'):
                self.status_label.setText("分析完成，显示结果")
            
            # 检查是否有表格组件
            if hasattr(self, 'result_table'):
                self._update_result_table(results)
            
            # 检查是否有文本组件
            if hasattr(self, 'result_text'):
                self._update_result_text(results)
            
            logger.info("{panel_name} 结果显示完成")
        except Exception as e:
            logger.error(f"显示 {panel_name} 结果时出错: {{str(e)}}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"显示结果出错: {{str(e)}}")
    
    def _update_result_table(self, results):
        \"\"\"更新结果表格\"\"\"
        if not hasattr(self, 'result_table'):
            return
            
        from PyQt5.QtWidgets import QTableWidgetItem
            
        # 清空表格
        self.result_table.setRowCount(0)
        
        # 检查结果类型并更新表格
        if isinstance(results, list):
            # 列表类型结果（如股票列表）
            if not results:
                return
                
            # 动态确定表格列
            if isinstance(results[0], dict):
                # 列表中包含字典
                headers = list(results[0].keys())
                self.result_table.setColumnCount(len(headers))
                self.result_table.setHorizontalHeaderLabels(headers)
                
                # 添加行
                for i, item in enumerate(results):
                    self.result_table.insertRow(i)
                    for j, key in enumerate(headers):
                        item_value = item.get(key, "")
                        self.result_table.setItem(i, j, QTableWidgetItem(str(item_value)))
            else:
                # 简单列表
                self.result_table.setColumnCount(1)
                self.result_table.setHorizontalHeaderLabels(["值"])
                
                # 添加行
                for i, item in enumerate(results):
                    self.result_table.insertRow(i)
                    self.result_table.setItem(i, 0, QTableWidgetItem(str(item)))
        
        elif isinstance(results, dict):
            # 字典类型结果（如分析报告）
            # 设置表格为两列：键和值
            self.result_table.setColumnCount(2)
            self.result_table.setHorizontalHeaderLabels(["项目", "值"])
            
            # 添加行
            row = 0
            for key, val in results.items():
                # 跳过复杂类型
                if isinstance(val, (dict, list)) and len(val) > 0:
                    continue
                    
                self.result_table.insertRow(row)
                self.result_table.setItem(row, 0, QTableWidgetItem(str(key)))
                self.result_table.setItem(row, 1, QTableWidgetItem(str(val)))
                row += 1
        
        # 调整列宽
        self.result_table.resizeColumnsToContents()
    
    def _update_result_text(self, results):
        \"\"\"更新结果文本\"\"\"
        if not hasattr(self, 'result_text'):
            return
            
        # 格式化结果为文本
        if isinstance(results, dict):
            text = self._format_dict_as_text(results)
        elif isinstance(results, list):
            text = self._format_list_as_text(results)
        else:
            text = str(results)
        
        # 设置文本
        self.result_text.setText(text)
    
    def _format_dict_as_text(self, data, indent=0):
        \"\"\"将字典格式化为文本\"\"\"
        text = ""
        for key, val in data.items():
            if isinstance(val, dict):
                text += "  " * indent + f"{key}:\\n"
                text += self._format_dict_as_text(val, indent + 1)
            elif isinstance(val, list):
                text += "  " * indent + f"{key}:\\n"
                text += self._format_list_as_text(val, indent + 1)
            else:
                text += "  " * indent + f"{key}: {val}\\n"
        return text
    
    def _format_list_as_text(self, data, indent=0):
        \"\"\"将列表格式化为文本\"\"\"
        text = ""
        for i, item in enumerate(data):
            if isinstance(item, dict):
                text += "  " * indent + f"[{i+1}]\\n"
                text += self._format_dict_as_text(item, indent + 1)
            elif isinstance(item, list):
                text += "  " * indent + f"[{i+1}]\\n"
                text += self._format_list_as_text(item, indent + 1)
            else:
                text += "  " * indent + f"[{i+1}] {item}\\n"
        return text
"""
        
        # 将方法插入到类定义结束之前
        new_content = content[:class_end] + display_method + content[class_end:]
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        logger.info(f"已为 {panel_name} 添加结果展示方法")
        return True
        
    except Exception as e:
        logger.error(f"为 {panel_name} 添加结果展示方法时出错: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 4:
        print("用法: python fix_one_panel.py <面板文件> <面板名称> <类名>")
        print("例如: python fix_one_panel.py QTS/quantum_desktop/ui/panels/quantum_stock_finder_panel.py 量子选股面板 QuantumStockFinderPanel")
        return 1
    
    file_path = sys.argv[1]
    panel_name = sys.argv[2]
    class_name = sys.argv[3]
    
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return 1
    
    if add_display_method(file_path, panel_name, class_name):
        logger.info(f"成功修复 {panel_name}")
        return 0
    else:
        logger.error(f"修复 {panel_name} 失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 