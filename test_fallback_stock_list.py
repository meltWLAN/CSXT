#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 _generate_fallback_stock_list 方法 (300股票版本)
专门测试应急股票列表生成功能
"""

import sys
import os
import time
import logging
import json
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestFallbackStockList')

# 定义行业股票信息
INDUSTRY_STOCKS = {
    "科技": {
        "prefix": ["688", "605", "300"],
        "description": "科技行业，包括计算机、软件、互联网等"
    },
    "金融": {
        "prefix": ["601", "600"],
        "description": "金融行业，包括银行、保险、证券等"
    },
    "医疗": {
        "prefix": ["300", "603"],
        "description": "医疗健康行业，包括医药、医疗器械等"
    },
    "能源": {
        "prefix": ["600", "601"],
        "description": "能源行业，包括石油、天然气、电力等"
    },
    "消费": {
        "prefix": ["603", "002"],
        "description": "消费行业，包括食品饮料、家电、服装等"
    },
    "工业": {
        "prefix": ["600", "601"],
        "description": "工业行业，包括机械、制造、建筑等"
    },
    "材料": {
        "prefix": ["600", "601"],
        "description": "材料行业，包括化工、钢铁、有色金属等"
    },
    "通信": {
        "prefix": ["600", "002"],
        "description": "通信行业，包括通信设备、运营商等"
    },
    "房地产": {
        "prefix": ["600", "001"],
        "description": "房地产行业，包括开发商、物业等"
    },
    "公用事业": {
        "prefix": ["600", "601"],
        "description": "公用事业，包括水务、燃气、环保等"
    }
}

def generate_fallback_stock_list(num_stocks, industry_stocks):
    """生成应急股票列表
    
    当其他所有获取股票数据的方法都失败时，生成随机的模拟股票列表
    
    Args:
        num_stocks: 需要生成的股票数量
        industry_stocks: 行业股票信息字典
        
    Returns:
        List[Dict]: 股票数据列表
    """
    logger.info(f"开始生成{num_stocks}只应急股票数据")
    
    fallback_stocks = []
    
    try:
        # 确保各个行业都有股票
        industries = list(industry_stocks.keys())
        stocks_per_industry = max(1, num_stocks // len(industries))
        remainder = num_stocks % len(industries)
        
        for i, industry in enumerate(industries):
            # 计算当前行业需要生成的股票数量
            current_count = stocks_per_industry + (1 if i < remainder else 0)
            if current_count <= 0:
                continue
                
            industry_data = industry_stocks[industry]
            prefixes = industry_data["prefix"]
            
            for j in range(current_count):
                # 选择前缀
                prefix = random.choice(prefixes)
                
                # 生成随机股票代码
                random_num = random.randint(1, 9999)
                code = f"{prefix}{random_num:04d}"
                
                # 生成股票名称
                name = f"{industry}股{random_num:04d}"
                
                # 创建股票数据
                stock = {
                    'code': code,
                    'name': name,
                    'industry': industry,
                    'market': 'SH' if prefix.startswith('6') else 'SZ',
                    'is_fallback': True  # 标记为应急数据
                }
                
                fallback_stocks.append(stock)
        
        logger.info(f"成功生成{len(fallback_stocks)}只应急股票数据")
        return fallback_stocks
        
    except Exception as e:
        logger.error(f"生成应急股票数据时出错: {str(e)}")
        import traceback
        logger.debug(f"错误详情: {traceback.format_exc()}")
        
        # 如果连应急生成都失败了，返回一个最小的硬编码列表
        minimal_stocks = []
        for i in range(min(10, num_stocks)):
            minimal_stocks.append({
                'code': f"SH60{i:04d}",
                'name': f"应急股票{i}",
                'industry': "未知",
                'market': 'SH',
                'is_fallback': True
            })
        
        return minimal_stocks

def run_test(num_stocks=300):
    """运行测试"""
    print(f"=== 开始测试，生成 {num_stocks} 只股票 ===")
    
    # 开始计时
    start_time = time.time()
    
    # 生成股票
    stocks = generate_fallback_stock_list(num_stocks, INDUSTRY_STOCKS)
    
    # 计算耗时
    elapsed_time = time.time() - start_time
    
    # 打印结果
    print(f"\n=== 生成完成，共 {len(stocks)} 只股票，耗时 {elapsed_time:.4f} 秒 ===")
    
    # 打印行业分布
    industry_counts = {}
    for stock in stocks:
        industry = stock.get('industry', '未知')
        if industry not in industry_counts:
            industry_counts[industry] = 0
        industry_counts[industry] += 1
    
    print("\n行业分布:")
    for industry, count in industry_counts.items():
        print(f"{industry}: {count} 只")
    
    # 打印前10只股票
    print("\n前10只股票示例:")
    for i, stock in enumerate(stocks[:10]):
        print(f"{i+1}. {stock['code']} - {stock['name']} - {stock['industry']} - {stock['market']}")
    
    # 保存到文件
    try:
        output_file = "fallback_stocks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print(f"\n股票数据已保存到 {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")

if __name__ == "__main__":
    # 测试参数
    num_stocks = 300
    
    # 运行测试
    run_test(num_stocks) 