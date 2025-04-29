#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试爆发式股票查找器 (300股票版本)
基于中证500成分股进行爆发股测试，指定获取300只股票
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ExplosiveFinderTest300')

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入相关模块
try:
    import pandas as pd
    import numpy as np
    import tushare as ts
    
    # 导入量子系统
    from QTS.quantum_core.explosive_stock_finder import ExplosiveStockFinder
    from QTS.quantum_core.optimized_stock_finder import OptimizedStockFinder
    
except ImportError as e:
    logger.error(f"导入依赖库失败: {str(e)}")
    logger.error("请确保已安装必要的依赖: pip install tushare pandas numpy")
    
    # 尝试直接从当前目录导入
    try:
        logger.info("尝试直接从QTS目录导入...")
        from quantum_core.explosive_stock_finder import ExplosiveStockFinder
        from quantum_core.optimized_stock_finder import OptimizedStockFinder
        logger.info("从当前目录成功导入模块")
    except ImportError as e2:
        logger.error(f"第二次导入尝试也失败: {str(e2)}")
        sys.exit(1)

class TushareApiHelper:
    """Tushare API接口助手"""
    
    def __init__(self, token=None, cache_dir=None):
        """
        初始化Tushare API助手
        
        Args:
            token: Tushare API令牌，如果为None则尝试从环境变量获取
            cache_dir: 缓存目录，用于缓存API结果
        """
        try:
            # 如果未提供token，尝试从环境变量获取
            if token is None:
                token = os.environ.get('TUSHARE_TOKEN')
                
            # 如果仍然没有token，使用默认token
            if token is None:
                token = '0e65a5c636112dc9d9af5ccc93ef06c55987805b9467db0866185a10'
                logger.warning("使用默认Token，建议设置自己的Token")
                
            # 初始化Tushare API
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
                logger.info("Tushare API 初始化完成")
            except Exception as e:
                logger.error(f"Tushare API 初始化失败: {str(e)}")
                raise
                
            # 设置缓存目录
            self.cache_dir = cache_dir
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                
        except Exception as e:
            logger.error(f"初始化Tushare API助手失败: {str(e)}")
            raise
    
    def get_stock_daily(self, code, days=60):
        """
        获取股票日线数据
        
        Args:
            code: 股票代码，如 "000001.SZ"
            days: 获取的历史数据天数
            
        Returns:
            list: 包含历史数据的列表，按时间倒序排列
        """
        try:
            # 计算开始日期和结束日期
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            
            logger.info(f"获取股票 {code} 的日线数据，时间范围: {start_date} 至 {end_date}")
            
            # 尝试从Tushare API获取数据
            df = self.pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
            
            if df is None or df.empty:
                logger.warning(f"无法获取股票 {code} 的日线数据")
                return []
                
            # 按时间倒序排列
            df = df.sort_values('trade_date', ascending=False)
            
            # 限制返回天数
            if len(df) > days:
                df = df.head(days)
                
            # 添加日期列
            df['date'] = df['trade_date'].apply(lambda x: f"{x[:4]}-{x[4:6]}-{x[6:]}")
            
            # 转换为字典列表
            result = []
            for _, row in df.iterrows():
                day_data = {
                    'ts_code': row['ts_code'],
                    'trade_date': row['trade_date'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'pre_close': float(row['pre_close']),
                    'change': float(row['change']),
                    'pct_chg': float(row['pct_chg']),
                    'volume': float(row['vol']),
                    'amount': float(row['amount']),
                    'date': row['date']
                }
                result.append(day_data)
                
            logger.info(f"成功获取股票 {code} 的日线数据，共 {len(result)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"获取股票 {code} 的日线数据失败: {str(e)}")
            return []
    
    def get_csi500_stocks(self, limit=300):
        """
        直接从Tushare API获取中证500成分股
        
        Args:
            limit: 返回的最大股票数量，默认为300只
            
        Returns:
            List[Dict]: 中证500成分股列表
        """
        logger.info(f"开始直接获取中证500成分股 (限制: {limit}只)")
        
        try:
            # 从Tushare获取中证500成分股
            index_stocks = self.pro.index_weight(
                index_code='000905.SH',  # 中证500指数代码
                fields='con_code,weight'
            )
            
            if index_stocks is None or index_stocks.empty:
                logger.warning("获取中证500成分股失败")
                return []
                
            # 限制股票数量
            if limit < len(index_stocks):
                index_stocks = index_stocks.head(limit)
                
            logger.info(f"获取到 {len(index_stocks)} 只中证500成分股")
            
            # 获取股票的基本信息
            stock_codes = list(index_stocks['con_code'])
            stock_basic = self.pro.stock_basic(
                ts_code=','.join(stock_codes[:min(50, len(stock_codes))]),  # 避免请求过大
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            if stock_basic is None or stock_basic.empty:
                logger.warning("获取中证500成分股基本信息失败")
                return []
                
            # 合并权重和基本信息
            result = []
            for _, row in stock_basic.iterrows():
                ts_code = row['ts_code']
                # 查找对应的权重
                weight_row = index_stocks[index_stocks['con_code'] == ts_code]
                weight = float(weight_row['weight'].iloc[0]) if not weight_row.empty else 0
                
                # 构建标准化的股票数据
                stock = {
                    'code': ts_code,
                    'ts_code': ts_code,
                    'symbol': row['symbol'] if 'symbol' in row else ts_code.split('.')[0],
                    'name': row['name'],
                    'area': row.get('area', '未知'),
                    'industry': row.get('industry', '未知'),
                    'market': row.get('market', 'UNKNOWN'),
                    'list_date': row.get('list_date', ''),
                    'weight': weight,
                    'index': 'CSI500'
                }
                result.append(stock)
            
            logger.info(f"成功获取中证500成分股的基本信息，共 {len(result)} 只")
            return result
            
        except Exception as e:
            logger.error(f"获取中证500成分股时出错: {str(e)}")
            return []
    
    def fetch_csi500_market_data(self, limit=300):
        """
        获取中证500成分股的市场数据
        
        Args:
            limit: 限制返回的股票数量
            
        Returns:
            list: 包含股票完整数据的列表
        """
        try:
            logger.info(f"开始获取中证500成分股数据，限制: {limit} 只股票")
            
            # 使用自己的方法直接获取中证500成分股列表
            stock_list = self.get_csi500_stocks(limit=limit)
            
            if not stock_list:
                logger.error("无法获取中证500成分股列表")
                return []
                
            # 获取每只股票的历史数据
            result = []
            for i, stock in enumerate(stock_list):
                code = stock['ts_code']
                name = stock['name']
                    
                logger.info(f"获取股票数据 [{i+1}/{len(stock_list)}]: {code} {name}")
                    
                # 获取历史数据
                historical_data = self.get_stock_daily(code)
                    
                if not historical_data:
                    continue
                    
                # 复制股票信息，避免修改原始数据
                stock_data = stock.copy()
                
                # 添加历史数据
                stock_data['historical_data'] = historical_data
                
                # 添加当前价格
                if historical_data:
                    stock_data['current_price'] = historical_data[0]['close']
                else:
                    stock_data['current_price'] = 0
                    
                result.append(stock_data)
                
                # 每10只股票休息1秒，避免API限流
                if (i+1) % 5 == 0:
                    time.sleep(1)
            
            logger.info(f"成功获取中证500成分股市场数据，共 {len(result)} 只股票")
            return result
            
        except Exception as e:
            logger.error(f"获取中证500成分股市场数据失败: {str(e)}")
            return []

def run_explosive_stock_finder(limit=300, min_increase=0.1, time_range="3-5天", quantum_weight=0.5):
    """运行爆发式股票查找器测试"""
    try:
        print(f"=== 启动爆发式股票查找器 (测试 {limit} 只股票) ===")
        logger.info(f"启动参数: 股票数量={limit}, 最小涨幅={min_increase}%")
        
        # 创建Tushare API Helper
        api_helper = TushareApiHelper(cache_dir="/tmp/qts_cache")
        
        # 创建实例
        finder = ExplosiveStockFinder(api_helper=api_helper)
        
        # 准备市场数据
        market_data = []
        print("正在准备中证500成分股数据...")
        market_data = api_helper.fetch_csi500_market_data(limit=limit)
        
        if not market_data:
            print("警告：无法获取中证500成分股数据，将使用生成的测试数据")
            print("这将使分析结果仅供演示，不能用于实际交易决策")
            market_data = None
        else:
            print(f"成功获取 {len(market_data)} 只中证500成分股的真实市场数据")
            
            # 打印第一只股票的数据结构，用于调试
            if len(market_data) > 0:
                first_stock = market_data[0]
                print(f"第一只股票代码: {first_stock.get('code', 'unknown')}")
                print(f"第一只股票名称: {first_stock.get('name', 'unknown')}")
                print(f"所属行业: {first_stock.get('industry', 'unknown')}")
                print(f"第一只股票数据结构: 包含关键字 {list(first_stock.keys())}")
                if 'historical_data' in first_stock:
                    hist_data = first_stock['historical_data']
                    print(f"获取历史数据 {len(hist_data)} 天")
                    if len(hist_data) > 0:
                        print(f"第一条历史数据: {hist_data[0]['date']} 收盘价: {hist_data[0]['close']}")
                        if len(hist_data) > 1:
                            print(f"第二条历史数据: {hist_data[1]['date']} 收盘价: {hist_data[1]['close']}")
            
            # 手动设置市场数据
            finder.market_data = market_data
        
        # 启动分析
        print(f"正在启动中证500成分股分析，共 {limit} 只股票，预期涨幅: {min_increase}%...")
        finder.start(
            market_scope="中证500", 
            min_increase_percent=min_increase, 
            time_range=time_range,
            quantum_weight=quantum_weight,  # 使用传入的量子权重
            test_data_count=300  # 确保测试数据数量也是300
        )
        
        # 等待处理完成
        progress_spinner = ['-', '\\', '|', '/']
        spinner_idx = 0
        timeout_seconds = 300  # 5分钟超时
        start_time = time.time()
        
        while not finder.is_finished() and finder.get_progress() < 0.99:
            status = finder.get_status()
            progress = finder.get_progress() * 100
            
            # 显示进度和旋转加载指示
            spinner = progress_spinner[spinner_idx]
            spinner_idx = (spinner_idx + 1) % len(progress_spinner)
            
            sys.stdout.write(f"\r{spinner} 状态: {status}, 进度: {progress:.1f}%")
            sys.stdout.flush()
            
            time.sleep(1)
            
            # 检查是否超时
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                print("\n处理超时，强制结束分析")
                finder.stop()
                break
        
        print("\n处理完成")
        
        # 获取结果
        results = finder.get_results()
        
        # 打印结果
        if results and len(results) > 0:
            print(f"\n=== 找到 {len(results)} 只中证500潜在暴涨股票 ===")
            
            # 打印表头
            print(f"{'代码':<10} {'名称':<10} {'行业':<12} {'当前价':<8} {'爆发能量':<8} {'预期涨幅':<8} {'推荐':<8}")
            print("-" * 80)
            
            # 打印股票信息
            for stock in results:
                code = stock.get('code', '')
                name = stock.get('name', '')
                industry = stock.get('industry', '')[:12]  # 限制行业名称长度
                price = stock.get('current_price', 0)
                energy = stock.get('explosion_energy', 0)
                increase = stock.get('expected_increase', 0) * 100
                
                # 生成推荐级别
                if energy >= 0.7:
                    recommendation = "强烈推荐"
                elif energy >= 0.4:
                    recommendation = "推荐"
                elif energy >= 0.2:
                    recommendation = "观望"
                else:
                    recommendation = "弱信号"
                
                print(f"{code:<10} {name:<10} {industry:<12} {price:<8.2f} {energy:<8.2f} {increase:<8.1f}% {recommendation:<8}")
            
            # 打印第一只股票的详细信息
            if len(results) > 0:
                print("\n=== 首选爆发股详情 ===")
                first_stock = results[0]
                print(f"代码: {first_stock.get('code', '')}")
                print(f"名称: {first_stock.get('name', '')}")
                print(f"行业: {first_stock.get('industry', '')}")
                print(f"当前价格: {first_stock.get('current_price', 0):.2f}")
                print(f"爆发能量: {first_stock.get('explosion_energy', 0):.2f}")
                print(f"预期涨幅: {first_stock.get('expected_increase', 0) * 100:.1f}%")
                print(f"买入时机评分: {first_stock.get('buying_timing_score', 0):.2f}")
                
                # 打印爆发因素
                factors = first_stock.get('explosion_factors', {})
                if factors:
                    print("\n爆发因素:")
                    for factor, value in factors.items():
                        print(f"- {factor}: {value:.2f}")
        else:
            print("\n未找到符合条件的爆发股票")
        
        print("\n=== 分析完成 ===")
        
    except Exception as e:
        print(f"运行爆发式股票查找器时出错: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    # 默认参数
    stock_limit = 300  # 分析的股票数量
    min_increase = 0.1  # 最小预期涨幅百分比
    time_range = "3-5天"  # 预期时间范围
    quantum_weight = 0.5  # 量子分析权重 (0-1之间)
    
    # 运行爆发式股票查找器
    run_explosive_stock_finder(
        limit=stock_limit,
        min_increase=min_increase,
        time_range=time_range,
        quantum_weight=quantum_weight
    ) 