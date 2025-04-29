#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
综合测试脚本 - 测试生成300只应急股票及其历史数据
用于测试 _generate_fallback_stock_list 和模拟历史数据生成功能
"""

import os
import sys
import time
import random
import logging
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ComprehensiveStockTest')

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

def create_mock_history(stock_code, history_days=60, pattern_type=None):
    """创建模拟历史数据
    
    Args:
        stock_code: 股票代码
        history_days: 历史数据天数
        pattern_type: 价格模式类型，可以是 "上升", "下降", "横盘", "震荡", "底部企稳", "大幅波动" 或 None (随机选择)
        
    Returns:
        list: 历史数据列表，包含OHLCV等信息
    """
    logger.info(f"为股票 {stock_code} 创建模拟历史数据")
    
    # 如果未指定模式，随机选择一种
    if pattern_type is None:
        pattern_type = random.choice(["上升", "下降", "横盘", "震荡", "底部企稳", "大幅波动"])
    
    logger.info(f"股票 {stock_code} 使用价格模式: {pattern_type}")
    
    # 生成过去N个交易日的数据
    end_date = datetime.now()
    dates = []
    current_date = end_date
    
    # 生成交易日日期（去除周末）
    while len(dates) < history_days:
        if current_date.weekday() < 5:  # 0-4表示周一至周五
            dates.append(current_date)
        current_date -= timedelta(days=1)
        
    dates.reverse()  # 按日期升序排序
    
    # 使用股票代码作为随机种子以保持一致性
    random.seed(int(stock_code[-6:]) % 10000)
    np.random.seed(int(stock_code[-6:]) % 10000)
    
    # 基础价格
    base_price = max(5, int(stock_code[-4:]) % 80 + 20)  # 生成20-100之间的价格
    
    # 随机生成成交量基数
    base_volume = random.uniform(50000, 5000000)
    
    # 创建价格和成交量数据
    historical_data = []
    
    for day in range(history_days):
        # 计算日期字符串
        date_str = dates[day].strftime("%Y-%m-%d")
        
        # 根据不同趋势生成价格
        if pattern_type == "上升":
            price_multiplier = 1 + 0.002 * day + random.uniform(-0.02, 0.03)
        elif pattern_type == "下降":
            price_multiplier = 1 - 0.002 * day + random.uniform(-0.02, 0.02)
        elif pattern_type == "横盘":
            price_multiplier = 1 + random.uniform(-0.015, 0.015)
        elif pattern_type == "震荡":
            price_multiplier = 1 + 0.05 * np.sin(day/10) + random.uniform(-0.02, 0.02)
        elif pattern_type == "底部企稳":
            if day < history_days * 0.7:
                price_multiplier = 1 - 0.001 * (history_days * 0.7 - day) + random.uniform(-0.01, 0.01)
            else:
                price_multiplier = 1 + 0.002 * (day - history_days * 0.7) + random.uniform(-0.005, 0.025)
        else:  # 大幅波动
            price_multiplier = 1 + 0.1 * np.sin(day/8) + random.uniform(-0.03, 0.03)
        
        # 是否为潜在爆发股
        is_potential_breakout = random.random() < 0.3  # 30%的股票有潜在突破
        
        # 为潜在暴涨股增加底部形态和放量特征
        if is_potential_breakout and day >= history_days * 0.7:
            # 在最近30%的时间里形成底部并开始突破
            if day > history_days * 0.9:  # 最近10%的时间
                price_multiplier += 0.01 + 0.01 * (day - history_days * 0.9) / (history_days * 0.1)
                # 放量
                volume_multiplier = 1.5 + 0.5 * (day - history_days * 0.9) / (history_days * 0.1)
            else:
                # 底部震荡整理
                price_multiplier = 1 + 0.01 * np.sin((day - history_days * 0.7) * 0.5) + random.uniform(-0.005, 0.005)
                volume_multiplier = 0.8 + 0.4 * random.random()
        else:
            volume_multiplier = 0.7 + 0.6 * random.random()
        
        # 计算当天价格
        day_price = base_price * price_multiplier
        
        # 确保价格合理
        day_price = max(1.0, day_price)  # 最低不低于1元
        
        # 计算当天高低价
        day_high = day_price * (1 + random.uniform(0.01, 0.03))
        day_low = day_price * (1 - random.uniform(0.01, 0.03))
        
        # 确保开盘价和收盘价在最高价和最低价之间
        day_open = day_low + (day_high - day_low) * random.random()
        day_close = day_low + (day_high - day_low) * random.random()
        
        # 计算成交量
        volume = base_volume * volume_multiplier * (0.8 + 0.4 * random.random())
        
        # 添加到历史数据
        data_point = {
            'date': date_str,
            'open': round(day_open, 2),
            'high': round(day_high, 2),
            'low': round(day_low, 2),
            'close': round(day_close, 2),
            'volume': int(volume),
            'amount': int(volume * day_close),  # 成交额=成交量*收盘价 (简化)
            'is_mock': True  # 标记为模拟数据
        }
        
        historical_data.append(data_point)
    
    # 确保历史数据按日期降序排列 (最新的在前)
    historical_data = sorted(historical_data, key=lambda x: x['date'], reverse=True)
    
    logger.info(f"成功为股票 {stock_code} 创建 {len(historical_data)} 天的模拟历史数据")
    return historical_data

def visualize_stock_history(stock_code, historical_data, output_dir="outputs"):
    """可视化股票历史数据
    
    Args:
        stock_code: 股票代码
        historical_data: 历史数据列表
        output_dir: 输出目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 将数据转换为DataFrame
    df = pd.DataFrame(historical_data)
    # 按日期升序排列
    df = df.sort_values('date')
    
    # 设置绘图
    plt.figure(figsize=(12, 8))
    
    # 1. 创建价格子图
    plt.subplot(2, 1, 1)
    plt.plot(df['date'], df['close'], label='收盘价', color='blue')
    plt.title(f"股票 {stock_code} 模拟价格走势")
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    
    # 2. 创建成交量子图
    plt.subplot(2, 1, 2)
    plt.bar(df['date'], df['volume'], color='green', alpha=0.6)
    plt.title(f"股票 {stock_code} 模拟成交量")
    plt.xlabel('日期')
    plt.ylabel('成交量')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = os.path.join(output_dir, f"{stock_code}_history.png")
    plt.savefig(output_file)
    plt.close()
    
    logger.info(f"已生成股票 {stock_code} 的历史数据可视化图表: {output_file}")
    return output_file

def run_comprehensive_test(num_stocks=300, history_samples=5):
    """运行综合测试"""
    print(f"=== 开始综合测试，生成 {num_stocks} 只股票 ===")
    
    # 测试开始时间
    start_time = time.time()
    
    # 第一步：生成股票列表
    print("\n1. 生成模拟股票列表...")
    stocks = generate_fallback_stock_list(num_stocks, INDUSTRY_STOCKS)
    
    # 第二步：为部分股票生成历史数据
    print(f"\n2. 为 {history_samples} 只样本股票生成历史数据...")
    
    # 随机选择几只股票来生成历史数据
    sampled_stocks = random.sample(stocks, min(history_samples, len(stocks)))
    
    # 为每只样本股票生成历史数据
    for i, stock in enumerate(sampled_stocks):
        code = stock['code']
        name = stock['name']
        
        print(f"   处理 [{i+1}/{len(sampled_stocks)}]: {code} - {name}")
        
        # 分配一种价格模式
        pattern = random.choice(["上升", "下降", "横盘", "震荡", "底部企稳", "大幅波动"])
        
        # 生成历史数据
        historical_data = create_mock_history(code, history_days=60, pattern_type=pattern)
        
        # 添加到股票数据中
        stock['historical_data'] = historical_data
        
        # 添加当前价格
        if historical_data:
            stock['current_price'] = historical_data[0]['close']
        
        # 生成可视化
        visualize_stock_history(code, historical_data)
    
    # 第三步：分析行业分布
    print("\n3. 分析行业分布...")
    industry_counts = {}
    for stock in stocks:
        industry = stock.get('industry', '未知')
        if industry not in industry_counts:
            industry_counts[industry] = 0
        industry_counts[industry] += 1
    
    for industry, count in industry_counts.items():
        print(f"   {industry}: {count} 只 ({count/len(stocks)*100:.1f}%)")
    
    # 第四步：保存数据到文件
    try:
        # 保存完整数据
        full_output_file = "comprehensive_fallback_stocks.json"
        with open(full_output_file, 'w', encoding='utf-8') as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print(f"\n4. 完整股票数据已保存到 {full_output_file}")
        
        # 保存样本股票数据
        sample_output_file = "sampled_fallback_stocks.json"
        with open(sample_output_file, 'w', encoding='utf-8') as f:
            json.dump(sampled_stocks, f, ensure_ascii=False, indent=2)
        print(f"   样本股票数据已保存到 {sample_output_file}")
    except Exception as e:
        print(f"   保存文件时出错: {str(e)}")
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    print(f"\n=== 综合测试完成，共生成 {len(stocks)} 只股票，耗时 {elapsed_time:.2f} 秒 ===")

if __name__ == "__main__":
    # 测试参数
    num_stocks = 300  # 生成的股票数量
    history_samples = 10  # 生成历史数据的样本数量
    
    # 运行综合测试
    run_comprehensive_test(num_stocks, history_samples) 