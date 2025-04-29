#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交易日历工具
用于处理中国股市交易日期和交易时间的相关功能
"""

import os
import json
import datetime
import logging
import pandas as pd
from typing import Dict, List, Union, Optional, Tuple

# 配置日志
logger = logging.getLogger("utils.trading_calendar")

class TradingCalendar:
    """中国股市交易日历
    
    用于判断是否是交易日、获取最近交易日等功能
    """
    
    def __init__(self, calendar_file: str = None):
        """初始化交易日历
        
        Args:
            calendar_file: 交易日历数据文件路径，默认自动生成
        """
        self.holidays = set()  # 法定节假日集合
        self.special_trading_days = set()  # 特殊交易日（如正常应该休市但实际交易的日期）
        
        # 交易日历文件
        self.calendar_file = calendar_file or os.path.join(
            os.path.expanduser("~"), ".supergod", "trading_calendar.json"
        )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.calendar_file), exist_ok=True)
        
        # 加载交易日历
        self._load_calendar()
    
    def _load_calendar(self):
        """加载交易日历数据"""
        try:
            if os.path.exists(self.calendar_file):
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 将日期字符串转换为datetime.date对象
                self.holidays = set([
                    self._parse_date(d) for d in data.get('holidays', [])
                ])
                self.special_trading_days = set([
                    self._parse_date(d) for d in data.get('special_trading_days', [])
                ])
                
                # 检查是否需要更新
                last_update = data.get('last_update')
                if last_update:
                    last_update_date = self._parse_date(last_update)
                    if (datetime.date.today() - last_update_date).days > 30:
                        self._generate_calendar()
                else:
                    self._generate_calendar()
            else:
                # 文件不存在，生成交易日历
                self._generate_calendar()
                
        except Exception as e:
            logger.error(f"加载交易日历出错: {str(e)}")
            # 出错则生成基本交易日历
            self._generate_calendar()
    
    def _save_calendar(self):
        """保存交易日历数据"""
        try:
            data = {
                'last_update': datetime.date.today().strftime('%Y-%m-%d'),
                'holidays': [d.strftime('%Y-%m-%d') for d in self.holidays],
                'special_trading_days': [d.strftime('%Y-%m-%d') for d in self.special_trading_days]
            }
            
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存交易日历出错: {str(e)}")
    
    def _generate_calendar(self):
        """生成基本交易日历
        
        生成未来一年的交易日历数据，基于常规规则:
        1. 周一至周五为交易日
        2. 法定节假日为非交易日
        
        Note:
            这是基础规则生成，可能不准确，建议从数据提供商获取准确数据
        """
        # 获取当前年份
        current_year = datetime.date.today().year
        
        # 常规法定节假日（不完全准确，最好从数据提供商获取）
        # 以下是基本框架，具体日期需要根据每年的实际情况调整
        yearly_holidays = {
            # 元旦
            f"{current_year}-01-01",
            
            # 春节（假设农历正月初一前后7天）
            # 注意：这里只是示例，实际日期需要根据农历计算
            f"{current_year}-01-21", f"{current_year}-01-22",
            f"{current_year}-01-23", f"{current_year}-01-24",
            f"{current_year}-01-25", f"{current_year}-01-26",
            f"{current_year}-01-27",
            
            # 清明节
            f"{current_year}-04-05",
            
            # 劳动节
            f"{current_year}-05-01", f"{current_year}-05-02",
            f"{current_year}-05-03",
            
            # 端午节
            f"{current_year}-06-22",
            
            # 中秋节
            f"{current_year}-09-29",
            
            # 国庆节
            f"{current_year}-10-01", f"{current_year}-10-02",
            f"{current_year}-10-03", f"{current_year}-10-04",
            f"{current_year}-10-05", f"{current_year}-10-06",
            f"{current_year}-10-07",
        }
        
        # 转换为date对象
        self.holidays = set()
        for date_str in yearly_holidays:
            try:
                self.holidays.add(self._parse_date(date_str))
            except:
                pass
        
        # 保存日历
        self._save_calendar()
        
        logger.info(f"已生成交易日历数据，包含 {len(self.holidays)} 个假日")
    
    def _parse_date(self, date_str: str) -> datetime.date:
        """解析日期字符串为date对象
        
        Args:
            date_str: 日期字符串，格式为'YYYY-MM-DD'
            
        Returns:
            datetime.date对象
        """
        if isinstance(date_str, datetime.date):
            return date_str
            
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            # 尝试其他格式
            try:
                return datetime.datetime.strptime(date_str, '%Y%m%d').date()
            except:
                raise ValueError(f"无法解析日期字符串: {date_str}")
    
    def is_trading_day(self, date: Union[str, datetime.date, datetime.datetime] = None) -> bool:
        """判断指定日期是否为交易日
        
        Args:
            date: 要判断的日期，默认为今天
            
        Returns:
            是否为交易日
        """
        if date is None:
            date = datetime.date.today()
        elif isinstance(date, str):
            date = self._parse_date(date)
        elif isinstance(date, datetime.datetime):
            date = date.date()
        
        # 特殊交易日直接返回True
        if date in self.special_trading_days:
            return True
        
        # 周末判断
        if date.weekday() >= 5:  # 5: 周六, 6: 周日
            return False
        
        # 法定节假日判断
        if date in self.holidays:
            return False
            
        # 工作日且非法定节假日
        return True
    
    def is_trading_time(self, dt: Union[str, datetime.datetime] = None) -> bool:
        """判断指定时间是否为交易时间
        
        中国A股交易时间为:
        - 上午: 9:30 - 11:30
        - 下午: 13:00 - 15:00
        
        Args:
            dt: 要判断的时间，默认为当前时间
            
        Returns:
            是否为交易时间
        """
        if dt is None:
            dt = datetime.datetime.now()
        elif isinstance(dt, str):
            dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        
        # 首先判断是否为交易日
        if not self.is_trading_day(dt.date()):
            return False
        
        # 获取当前小时和分钟
        hour, minute = dt.hour, dt.minute
        time_value = hour * 100 + minute  # 将时间转换为整数方便比较
        
        # 判断是否在交易时段
        return (930 <= time_value <= 1130) or (1300 <= time_value <= 1500)
    
    def get_previous_trading_day(self, date: Union[str, datetime.date, datetime.datetime] = None) -> datetime.date:
        """获取指定日期之前的最近交易日
        
        Args:
            date: 指定日期，默认为今天
            
        Returns:
            最近的交易日
        """
        if date is None:
            date = datetime.date.today()
        elif isinstance(date, str):
            date = self._parse_date(date)
        elif isinstance(date, datetime.datetime):
            date = date.date()
        
        # 向前查找最近的交易日
        day = date - datetime.timedelta(days=1)
        while not self.is_trading_day(day):
            day = day - datetime.timedelta(days=1)
            
        return day
    
    def get_next_trading_day(self, date: Union[str, datetime.date, datetime.datetime] = None) -> datetime.date:
        """获取指定日期之后的最近交易日
        
        Args:
            date: 指定日期，默认为今天
            
        Returns:
            最近的交易日
        """
        if date is None:
            date = datetime.date.today()
        elif isinstance(date, str):
            date = self._parse_date(date)
        elif isinstance(date, datetime.datetime):
            date = date.date()
        
        # 向后查找最近的交易日
        day = date + datetime.timedelta(days=1)
        while not self.is_trading_day(day):
            day = day + datetime.timedelta(days=1)
            
        return day
    
    def get_trading_days_between(self, start_date: Union[str, datetime.date], 
                               end_date: Union[str, datetime.date]) -> List[datetime.date]:
        """获取两个日期之间的所有交易日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日列表
        """
        if isinstance(start_date, str):
            start_date = self._parse_date(start_date)
        if isinstance(end_date, str):
            end_date = self._parse_date(end_date)
        
        # 确保开始日期不晚于结束日期
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        # 获取所有交易日
        trading_days = []
        current_date = start_date
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date = current_date + datetime.timedelta(days=1)
            
        return trading_days

# 全局单例实例
_trading_calendar_instance = None

def get_trading_calendar() -> TradingCalendar:
    """获取交易日历实例
    
    返回一个全局的TradingCalendar实例，确保整个应用程序
    中只使用同一个交易日历实例。
    
    Returns:
        TradingCalendar: 交易日历实例
    """
    global _trading_calendar_instance
    
    if _trading_calendar_instance is None:
        _trading_calendar_instance = TradingCalendar()
        
    return _trading_calendar_instance 