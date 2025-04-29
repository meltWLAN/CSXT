#!/usr/bin/env python3
"""
直接测试Tushare API的连接和数据获取
"""

import os
import sys
import pandas as pd
import datetime

# Tushare token
TUSHARE_TOKEN = "0e65a5c636112dc9d9af5ccc93ef06c55987805b9467db0866185a10"

def test_tushare_connection():
    """测试Tushare API连接"""
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        # 测试获取股票列表
        stocks = pro.stock_basic(exchange='', list_status='L')
        if stocks is None or len(stocks) == 0:
            print("获取股票列表失败")
            return False
            
        print(f"成功获取 {len(stocks)} 只股票的基本信息")
        print("\n股票列表前5行:")
        print(stocks.head())
        
        # 测试获取历史数据 - 平安银行
        ts_code = stocks.iloc[0]['ts_code']
        print(f"\n获取股票 {ts_code} 的历史数据:")
        
        end_date = datetime.datetime.now().strftime('%Y%m%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d')
        
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or len(df) == 0:
            print(f"获取股票 {ts_code} 历史数据失败")
            return False
            
        print(f"成功获取 {len(df)} 条历史数据")
        print("\n历史数据前5行:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"测试Tushare API失败: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"开始测试Tushare API...")
    success = test_tushare_connection()
    print(f"\nTushare API测试: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1) 