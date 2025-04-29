#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_manager.py - 股票数据管理模块

负责下载、缓存和管理股票数据，提供稳定的数据源给分析模块使用。
支持定期更新、离线使用和数据完整性检查。
"""

import os
import json
import time
import logging
import datetime
import requests
import pandas as pd
import numpy as np
import threading
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

# 导入交易日历
from utils.trading_calendar import get_trading_calendar

# 设置日志
logger = logging.getLogger("quantum_core.data_manager")

class StockDataManager:
    """股票数据管理器
    
    用于下载、缓存和管理A股市场全部股票的数据，
    提供稳定的数据源给分析模块使用。
    """
    
    def __init__(self, data_dir: str = None):
        """初始化数据管理器
        
        Args:
            data_dir: 数据存储目录，默认为用户目录下的.supergod/market_data
        """
        # 设置数据存储目录
        if data_dir is None:
            self.data_dir = os.path.join(os.path.expanduser("~"), ".supergod", "market_data")
        else:
            self.data_dir = data_dir
            
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 基础数据文件路径
        self.stock_list_file = os.path.join(self.data_dir, "stock_list.json")
        self.stock_data_dir = os.path.join(self.data_dir, "stock_data")
        self.index_data_dir = os.path.join(self.data_dir, "index_data")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        
        # 确保子目录存在
        os.makedirs(self.stock_data_dir, exist_ok=True)
        os.makedirs(self.index_data_dir, exist_ok=True)
        
        # 初始化元数据
        self.metadata = self._load_metadata()
        
        # 初始化股票列表缓存
        self.stock_list_cache = None
        
        # 获取交易日历
        self.trading_calendar = get_trading_calendar()
        
        # 初始化API配置
        self.api_config = {
            # 东方财富股票列表API
            'stock_list_api': 'https://push2.eastmoney.com/api/qt/clist/get',
            'stock_list_params': {
                'pn': 1,
                'pz': 6000,  # 获取足够多的股票
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股市场
                'fields': 'f12,f14,f17,f100,f107,f152',  # 股票代码,名称,市值,行业等
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fltt': 2,
                'invt': 2,
                'cb': 'jQuery'
            },
            
            # 东方财富历史行情API
            'stock_history_api': 'https://push2his.eastmoney.com/api/qt/stock/kline/get',
            'stock_history_params': {
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 101,  # 日线
                'fqt': 1,    # 前复权
                'beg': '',   # 开始日期，格式YYYYMMDD，空表示最早
                'end': '',   # 结束日期，格式YYYYMMDD，空表示最新
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'cb': 'jQuery'
            }
        }
        
        # 状态变量
        self.is_updating = False
        self.update_progress = 0.0
        self.update_status = "初始化"
        
        # 日志初始化完成
        logger.info("股票数据管理器初始化完成")

    def get_stock_history(self, stock_code: str) -> Optional[pd.DataFrame]:
        """获取股票历史行情数据
        
        Args:
            stock_code: 股票代码，如'000001'或'000001.SZ'
            
        Returns:
            股票历史行情DataFrame，包含日期、开盘价、收盘价、最高价、最低价、成交量等
        """
        try:
            # 标准化股票代码
            stock_code = self._normalize_stock_code(stock_code)
            
            # 检查是否为交易日
            today = datetime.date.today()
            if not self.trading_calendar.is_trading_day(today):
                logger.info(f"今天 {today} 不是交易日，使用上一个交易日的数据")
                # 使用最近的交易日
                latest_trading_day = self.trading_calendar.get_previous_trading_day(today)
                logger.info(f"最近的交易日是 {latest_trading_day}")
            
            # 构建文件路径
            file_path = os.path.join(self.stock_data_dir, f"{stock_code}.csv")
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 读取本地文件
                df = pd.read_csv(file_path)
                
                # 检查数据是否是最新的（假设最后一天的数据是最新交易日的）
                if len(df) > 0:
                    # 将日期列转换为日期类型
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                    elif 'trade_date' in df.columns:
                        df['date'] = pd.to_datetime(df['trade_date'])
                        
                    # 检查最后一个交易日是否是最新的
                    last_date = df['date'].max().date()
                    latest_trading_day = self.trading_calendar.get_previous_trading_day()
                    
                    if last_date >= latest_trading_day:
                        # 数据是最新的，直接返回
                        return df
                    else:
                        # 数据不是最新的，尝试更新
                        logger.info(f"股票 {stock_code} 数据不是最新的，尝试更新")
            else:
                logger.warning(f"股票 {stock_code} 历史数据文件不存在")
            
            # 尝试从各个数据源获取数据
            df = None
            # 尝试从东方财富获取
            if df is None:
                df = self._fetch_stock_history_from_eastmoney(stock_code)
            
            # 如果所有来源都失败，生成模拟数据
            if df is None:
                logger.error(f"获取股票 {stock_code} 历史数据全部尝试失败，返回模拟数据")
                df = self._generate_mock_data(stock_code)
                
            # 保存数据到本地
            if df is not None and len(df) > 0:
                df.to_csv(file_path, index=False)
                
            return df
                
        except Exception as e:
            logger.error(f"获取股票历史数据出错: {str(e)}")
            return None

    def get_market_data(self, market_scope: str = "全市场") -> List[Dict]:
        """获取特定市场范围的股票数据
        
        Args:
            market_scope: 市场范围，可以是'全市场'、'沪深300'、'中证500'等
            
        Returns:
            股票数据列表
        """
        try:
            # 检查是否为交易日或交易时间，如果不是则使用上一个交易日的数据
            today = datetime.date.today()
            now = datetime.datetime.now()
            
            if not self.trading_calendar.is_trading_day(today):
                logger.warning(f"今天 {today} 不是交易日，使用最近交易日的数据")
            elif not self.trading_calendar.is_trading_time(now):
                logger.warning(f"当前时间 {now.strftime('%H:%M:%S')} 不是交易时间，使用最近交易日的数据")
            
            # 获取股票列表
            stock_list = self.get_stock_list()
            if not stock_list:
                return []
                
            # 根据市场范围过滤
            filtered_stocks = []
            if market_scope == "全市场":
                filtered_stocks = stock_list
            elif market_scope == "沪深300":
                # 假设股票信息中有'is_hs300'字段
                filtered_stocks = [s for s in stock_list if s.get('is_hs300', False)]
            elif market_scope == "中证500":
                # 假设股票信息中有'is_zz500'字段
                filtered_stocks = [s for s in stock_list if s.get('is_zz500', False)]
            elif market_scope == "创业板":
                # 创业板股票代码以'300'开头
                filtered_stocks = [s for s in stock_list if s.get('code', '').startswith('300')]
            elif market_scope == "科创板":
                # 科创板股票代码以'688'开头
                filtered_stocks = [s for s in stock_list if s.get('code', '').startswith('688')]
            else:
                logger.warning(f"未知的市场范围: {market_scope}，使用全市场")
                filtered_stocks = stock_list
                
            return filtered_stocks
                
        except Exception as e:
            logger.error(f"获取市场数据出错: {str(e)}")
            return [] 