#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复东方财富API访问问题的辅助脚本
"""

import os
import json
import time
import logging
import requests
import random
import sys
import pandas as pd

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fix_eastmoney_api")

def parse_jsonp(jsonp_str):
    """解析JSONP字符串，提取JSON数据"""
    try:
        if not jsonp_str or len(jsonp_str) < 10:
            logger.error("JSONP字符串为空或太短")
            return None
            
        # 检查是否是有效的JSONP格式
        if 'jQuery' not in jsonp_str:
            # 可能是纯JSON
            try:
                return json.loads(jsonp_str)
            except:
                logger.error(f"非标准JSONP格式且不是有效JSON: {jsonp_str[:100]}...")
                return None
        
        # 处理标准jQuery回调格式
        # 格式可能是: jQuery123456({"data":...}) 或 jQuery123456_123456789({"data":...})
        start_idx = jsonp_str.find('(')
        if start_idx == -1:
            logger.error(f"找不到JSONP左括号: {jsonp_str[:100]}...")
            return None
            
        end_idx = jsonp_str.rfind(')')
        if end_idx == -1 or end_idx <= start_idx:
            logger.error(f"找不到JSONP右括号或格式错误: {jsonp_str[:100]}...")
            return None
        
        # 提取JSON部分
        json_str = jsonp_str[start_idx + 1:end_idx].strip()
        
        # 解析JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON失败: {str(e)}, JSON内容: {json_str[:100]}...")
            return None
            
    except Exception as e:
        logger.error(f"解析JSONP时发生未知错误: {str(e)}, 内容: {jsonp_str[:100]}...")
        return None

def test_multiple_stocks():
    """测试多个股票代码"""
    # 测试不同市场的股票
    test_codes = [
        # 深圳主板
        '000001', '000002', '000063',
        # 上海主板
        '600000', '600030', '601398',
        # 创业板
        '300059', '300033', '300014',
        # 科创板
        '688001', '688005', '688008'
    ]
    
    success_count = 0
    for code in test_codes:
        logger.info(f"=============== 测试股票: {code} ===============")
        if test_eastmoney_api(code):
            success_count += 1
    
    print(f"测试结果: {success_count}/{len(test_codes)} 成功")
    return success_count > 0

def test_eastmoney_api(stock_code):
    """测试东方财富API"""
    # 构造会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://quote.eastmoney.com/',
        'Origin': 'http://quote.eastmoney.com',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    # 确定市场
    market = "sh" if stock_code.startswith(('6', '9')) else "sz"
    market_id = "1" if market.lower() == "sh" else "0"
    
    # 构造API请求参数
    api_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    
    # 随机回调名
    random_id = random.randint(1000000, 9999999)
    timestamp = int(time.time() * 1000)
    
    # 构建参数
    params = {
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': 101,  # 日线
        'fqt': 1,    # 前复权
        'secid': f"{market_id}.{stock_code}",
        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
        'cb': f"jQuery{random_id}_{timestamp}"
    }
    
    logger.info(f"请求股票 {stock_code} 的历史数据，secid={params['secid']}")
    
    # 发送请求
    try:
        response = session.get(api_url, params=params, timeout=15)
        
        # 检查响应
        if response.status_code != 200:
            logger.error(f"API请求失败，状态码: {response.status_code}")
            return False
        
        # 检查响应内容类型
        content_type = response.headers.get('Content-Type', '')
        logger.info(f"响应Content-Type: {content_type}")
        
        # 打印响应头
        logger.info(f"响应头: {dict(response.headers)}")
        
        # 打印原始响应的前100个字符以检查
        response_preview = response.text[:100].replace('\n', ' ')
        logger.info(f"原始响应开始: {response_preview}...")
            
        # 解析JSON
        json_data = parse_jsonp(response.text)
        if not json_data:
            logger.error("解析JSONP失败")
            return False
            
        # 检查API返回状态
        if json_data.get('rc', 0) != 0:
            logger.error(f"API返回错误: {json_data}")
            
            # 判断是否是股票代码或市场识别问题
            if json_data.get('rc') == 102:
                logger.warning(f"股票 {stock_code} 可能不存在或市场标识错误")
            
            return False
            
        # 提取数据
        data = json_data.get('data')
        if not data or 'klines' not in data:
            logger.error("未找到K线数据")
            return False
            
        klines = data['klines']
        logger.info(f"成功获取 {len(klines)} 条K线数据")
        
        # 显示部分数据
        if klines:
            logger.info(f"最近一条数据: {klines[-1]}")
            
        return True
    
    except Exception as e:
        logger.error(f"API请求异常: {str(e)}")
        return False

def test_index_api():
    """测试指数API"""
    # 构造会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://quote.eastmoney.com/'
    })
    
    # 构造API请求参数 - 上证指数
    api_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    
    # 随机回调名
    random_id = random.randint(1000000, 9999999)
    timestamp = int(time.time() * 1000)
    
    # 构建参数 - 上证指数
    params = {
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': 101,  # 日线
        'fqt': 1,    # 前复权
        'secid': '1.000001',  # 上证指数
        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
        'cb': f"jQuery{random_id}_{timestamp}"
    }
    
    logger.info("请求上证指数历史数据")
    
    # 发送请求
    try:
        response = session.get(api_url, params=params, timeout=15)
        
        # 检查响应
        if response.status_code != 200:
            logger.error(f"API请求失败，状态码: {response.status_code}")
            return False
        
        # 打印原始响应的前100个字符以检查
        response_preview = response.text[:100].replace('\n', ' ')
        logger.info(f"原始响应开始: {response_preview}...")
            
        # 解析JSON
        json_data = parse_jsonp(response.text)
        if not json_data:
            logger.error("解析JSONP失败")
            return False
            
        # 检查API返回状态
        if json_data.get('rc', 0) != 0:
            logger.error(f"API返回错误: {json_data}")
            return False
            
        # 提取数据
        data = json_data.get('data')
        if not data or 'klines' not in data:
            logger.error("未找到K线数据")
            return False
            
        klines = data['klines']
        logger.info(f"成功获取 {len(klines)} 条K线数据")
        
        # 显示部分数据
        if klines:
            logger.info(f"最近一条数据: {klines[-1]}")
            
        return True
    
    except Exception as e:
        logger.error(f"API请求异常: {str(e)}")
        return False

def main():
    # 检查参数
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
        
        # 验证股票代码
        if not stock_code.isdigit() or len(stock_code) != 6:
            print(f"错误: 无效的股票代码 {stock_code}")
            return 1
        
        # 测试单个股票API
        success = test_eastmoney_api(stock_code)
        
        if success:
            print(f"股票 {stock_code} 的API访问成功！")
            return 0
        else:
            print(f"股票 {stock_code} 的API访问失败！")
            
            # 尝试测试指数API
            print("尝试测试指数API...")
            if test_index_api():
                print("指数API访问成功！")
                return 0
            else:
                print("指数API访问也失败！")
                return 1
    else:
        # 如果没有提供参数，测试多个股票
        print("测试多个股票代码...")
        return 0 if test_multiple_stocks() else 1

if __name__ == "__main__":
    sys.exit(main()) 