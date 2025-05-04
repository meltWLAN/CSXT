#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单面板结果展示修复工具
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
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("修复工具")

# 要添加的方法内容
DISPLAY_METHOD = '''
    def display_results(self, results=None):
        """显示分析结果"""
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger("面板")
        self.logger.info("显示分析结果")
        
        # 使用传入的结果或取类属性中的结果
        if results is None:
            if hasattr(self, 'results'):
                results = self.results
            else:
                self.logger.warning("没有可用的分析结果")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("没有可用的分析结果")
                return
        
        # 更新状态标签
        if hasattr(self, 'status_label'):
            self.status_label.setText("分析完成，显示结果")
        
        # 显示结果到表格
        if hasattr(self, 'result_table'):
            self._update_table(results)
        
        # 显示结果到文本区域
        if hasattr(self, 'result_text'):
            if isinstance(results, dict):
                text = str(results)
            elif isinstance(results, list):
                text = "\\n".join([str(item) for item in results])
            else:
                text = str(results)
            self.result_text.setText(text)
    
    def _update_table(self, results):
        """更新表格显示"""
        from PyQt5.QtWidgets import QTableWidgetItem
        
        # 清空表格
        self.result_table.setRowCount(0)
        
        if isinstance(results, list) and results:
            if isinstance(results[0], dict):
                # 处理字典列表
                headers = list(results[0].keys())
                self.result_table.setColumnCount(len(headers))
                self.result_table.setHorizontalHeaderLabels(headers)
                
                for i, item in enumerate(results):
                    self.result_table.insertRow(i)
                    for j, key in enumerate(headers):
                        value = item.get(key, "")
                        self.result_table.setItem(i, j, QTableWidgetItem(str(value)))
            else:
                # 处理普通列表
                self.result_table.setColumnCount(1)
                self.result_table.setHorizontalHeaderLabels(["值"])
                
                for i, item in enumerate(results):
                    self.result_table.insertRow(i)
                    self.result_table.setItem(i, 0, QTableWidgetItem(str(item)))
                    
        elif isinstance(results, dict):
            # 处理字典
            self.result_table.setColumnCount(2)
            self.result_table.setHorizontalHeaderLabels(["键", "值"])
            
            for i, (key, value) in enumerate(results.items()):
                if isinstance(value, (dict, list)):
                    # 跳过复杂类型
                    continue
                self.result_table.insertRow(i)
                self.result_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.result_table.setItem(i, 1, QTableWidgetItem(str(value)))
'''

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak_{int(time.time())}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"已备份 {file_path} 到 {backup_path}")
        return True
    return False

def fix_panel(file_path, class_name):
    """修复面板，添加结果展示方法"""
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查类是否存在
        class_pattern = f"class {class_name}("
        if class_pattern not in content:
            logger.error(f"类 {class_name} 在文件中未找到")
            return False
        
        # 检查是否已有展示方法
        if "def display_results" in content:
            logger.info(f"文件已包含 display_results 方法")
            return True
        
        # 查找类定义的结束位置（下一个类定义或文件结束）
        class_start = content.find(class_pattern)
        next_class = content.find("\nclass ", class_start + 1)
        
        # 如果没有下一个类，使用文件结束位置
        if next_class == -1:
            next_class = len(content)
        
        # 备份文件
        backup_file(file_path)
        
        # 插入结果显示方法
        new_content = content[:next_class] + DISPLAY_METHOD + content[next_class:]
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"成功添加 display_results 方法到 {class_name}")
        return True
    
    except Exception as e:
        logger.error(f"修复面板时出错: {str(e)}")
        return False

def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 3:
        print("用法: python fix_simple.py <文件路径> <类名>")
        print("例如: python fix_simple.py QTS/quantum_desktop/ui/panels/quantum_stock_finder_panel.py QuantumStockFinderPanel")
        return 1
    
    file_path = sys.argv[1]
    class_name = sys.argv[2]
    
    # 修复面板
    if fix_panel(file_path, class_name):
        logger.info(f"成功修复 {file_path}")
        return 0
    else:
        logger.error(f"修复 {file_path} 失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 