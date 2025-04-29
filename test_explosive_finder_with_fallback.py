#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模拟爆发式股票查找器的应急股票列表机制测试脚本
演示当数据检索失败时如何使用应急股票列表
"""

import os
import sys
import time
import random
import logging
import json
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FallbackMechanismTest')

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

class MockAPIHelper:
    """模拟API助手，有时会失败"""
    
    def __init__(self, failure_rate=0.8):
        """
        初始化模拟API助手
        
        Args:
            failure_rate: API调用失败的概率 (0-1)
        """
        self.failure_rate = failure_rate
        logger.info(f"初始化MockAPIHelper，失败率: {failure_rate*100:.0f}%")
        
    def get_stock_list(self):
        """获取股票列表 (可能失败)"""
        if random.random() < self.failure_rate:
            logger.warning("API调用失败: get_stock_list()")
            return None
        
        # 成功时返回少量股票
        stocks = []
        for i in range(10):
            stocks.append({
                'code': f"600{i:03d}",
                'name': f"模拟股票{i}",
                'industry': random.choice(list(INDUSTRY_STOCKS.keys())),
                'market': 'SH'
            })
        
        logger.info(f"API调用成功: get_stock_list(), 返回 {len(stocks)} 只股票")
        return stocks
    
    def get_stock_daily(self, code):
        """获取股票日线数据 (可能失败)"""
        if random.random() < self.failure_rate:
            logger.warning(f"API调用失败: get_stock_daily({code})")
            return None
        
        # 成功时返回模拟历史数据
        data = []
        base_price = random.uniform(10, 100)
        
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            price_change = random.uniform(-0.05, 0.05)
            price = base_price * (1 + price_change)
            base_price = price  # 更新价格
            
            data.append({
                'date': date,
                'open': price * (1 - random.uniform(0, 0.01)),
                'high': price * (1 + random.uniform(0, 0.02)),
                'low': price * (1 - random.uniform(0, 0.02)),
                'close': price,
                'volume': random.randint(100000, 1000000)
            })
        
        logger.info(f"API调用成功: get_stock_daily({code}), 返回 {len(data)} 天数据")
        return data

class MockExplosiveStockFinder:
    """模拟ExplosiveStockFinder类，专注于测试应急股票列表机制"""
    
    def __init__(self, api_helper):
        """初始化爆发式股票查找器"""
        self.api_helper = api_helper
        self.market_data = None
        self.results = []
        self.status = "初始化"
        self.progress = 0.0
        logger.info("初始化MockExplosiveStockFinder")
    
    def generate_fallback_stock_list(self, num_stocks, industry_stocks):
        """生成应急股票列表
        
        当其他所有获取股票数据的方法都失败时，生成随机的模拟股票列表
        
        Args:
            num_stocks: 需要生成的股票数量
            industry_stocks: 行业股票信息字典
            
        Returns:
            List[Dict]: 股票数据列表
        """
        logger.info(f"生成应急股票列表: {num_stocks} 只")
        
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
    
    def create_mock_history(self, stock_code, days=30):
        """为股票创建模拟历史数据"""
        logger.info(f"为股票 {stock_code} 创建模拟历史数据")
        
        # 使用股票代码作为随机种子以保持一致性
        random.seed(int(stock_code[-6:]) % 10000)
        
        # 基础价格
        base_price = max(5, int(stock_code[-4:]) % 80 + 20)  # 生成20-100之间的价格
        current_price = base_price
        
        # 随机生成成交量基数
        base_volume = random.uniform(50000, 5000000)
        
        # 创建价格和成交量数据
        historical_data = []
        
        for i in range(days):
            # 计算日期字符串
            date = (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
            
            # 生成价格变动
            price_change = random.uniform(-0.03, 0.03)
            current_price = current_price * (1 + price_change)
            
            # 确保价格合理
            current_price = max(1.0, current_price)  # 最低不低于1元
            
            # 高低价
            high_price = current_price * (1 + random.uniform(0.01, 0.03))
            low_price = current_price * (1 - random.uniform(0.01, 0.03))
            open_price = low_price + (high_price - low_price) * random.random()
            
            # 成交量
            volume = int(base_volume * (0.7 + 0.6 * random.random()))
            
            # 添加数据点
            data_point = {
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(current_price, 2),
                'volume': volume,
                'amount': int(volume * current_price)
            }
            
            historical_data.append(data_point)
        
        # 确保历史数据按日期降序排列 (最新的在前)
        historical_data = sorted(historical_data, key=lambda x: x['date'], reverse=True)
        
        logger.info(f"完成：已为股票 {stock_code} 创建 {len(historical_data)} 天的历史数据")
        return historical_data
    
    def generate_test_data(self, num_stocks=300):
        """
        生成测试数据用于模拟分析
        
        调用顺序：
        1. 尝试使用API获取股票列表
        2. 如果失败，使用fallback机制创建股票列表
        3. 为股票添加历史数据
        
        Args:
            num_stocks: 生成的股票数量
            
        Returns:
            list: 股票数据列表
        """
        logger.info(f"开始生成测试数据: 目标 {num_stocks} 只股票")
        
        try:
            # 首先尝试从API获取股票列表
            logger.info("尝试从API获取股票列表...")
            stock_list = self.api_helper.get_stock_list()
            
            # 判断是否成功获取股票列表
            if stock_list is None or len(stock_list) == 0:
                logger.warning("从API获取股票列表失败，启用应急股票列表机制")
                stock_list = self.generate_fallback_stock_list(num_stocks, INDUSTRY_STOCKS)
                data_source = "fallback"
            else:
                logger.info(f"从API成功获取 {len(stock_list)} 只股票")
                data_source = "api"
                
                # 如果API返回的股票数量不足，使用应急股票填充
                if len(stock_list) < num_stocks:
                    missing_count = num_stocks - len(stock_list)
                    logger.info(f"API返回的股票数量不足，使用应急股票填充剩余 {missing_count} 只")
                    
                    fallback_stocks = self.generate_fallback_stock_list(missing_count, INDUSTRY_STOCKS)
                    for stock in fallback_stocks:
                        stock['data_source'] = 'fallback'
                    
                    stock_list.extend(fallback_stocks)
                    data_source = "mixed"
            
            # 为每只股票获取或生成历史数据
            enriched_stocks = []
            
            for i, stock in enumerate(stock_list):
                if i % 10 == 0:
                    logger.info(f"处理股票 {i+1}/{len(stock_list)}")
                    
                code = stock['code']
                
                # 对于API获取的股票，尝试获取实际历史数据
                if data_source in ['api', 'mixed'] and not stock.get('is_fallback', False):
                    historical_data = self.api_helper.get_stock_daily(code)
                    
                    # 如果API获取历史数据失败，创建模拟数据
                    if historical_data is None:
                        logger.warning(f"无法从API获取股票 {code} 的历史数据，生成模拟数据")
                        historical_data = self.create_mock_history(code)
                        stock['history_source'] = 'simulated'
                    else:
                        stock['history_source'] = 'api'
                else:
                    # 对于应急股票，直接创建模拟数据
                    historical_data = self.create_mock_history(code)
                    stock['history_source'] = 'simulated'
                
                # 添加历史数据
                stock['historical_data'] = historical_data
                
                # 添加当前价格
                if historical_data:
                    stock['current_price'] = historical_data[0]['close']
                
                enriched_stocks.append(stock)
            
            logger.info(f"数据生成完成，共 {len(enriched_stocks)} 只股票")
            
            # 分析生成数据来源
            api_count = len([s for s in enriched_stocks if s.get('data_source') == 'api'])
            fallback_count = len([s for s in enriched_stocks if s.get('is_fallback', False)])
            api_history_count = len([s for s in enriched_stocks if s.get('history_source') == 'api'])
            simulated_history_count = len([s for s in enriched_stocks if s.get('history_source') == 'simulated'])
            
            logger.info(f"数据源分析: API股票: {api_count}, 应急股票: {fallback_count}")
            logger.info(f"历史数据分析: API历史: {api_history_count}, 模拟历史: {simulated_history_count}")
            
            return enriched_stocks
            
        except Exception as e:
            logger.error(f"生成测试数据时出错: {str(e)}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 如果所有方法都失败，返回一个最小的硬编码列表
            minimal_stocks = []
            for i in range(min(10, num_stocks)):
                code = f"600{i:03d}"
                minimal_stocks.append({
                    'code': code,
                    'name': f"最小应急股票{i}",
                    'industry': "未知",
                    'market': 'SH',
                    'is_fallback': True,
                    'historical_data': self.create_mock_history(code, days=10),
                    'data_source': 'emergency',
                    'history_source': 'simulated'
                })
            
            return minimal_stocks
    
    def start_analysis(self):
        """启动分析过程，生成测试数据并模拟分析"""
        logger.info("开始启动分析流程...")
        
        # 生成测试数据
        self.market_data = self.generate_test_data(num_stocks=300)
        
        # 模拟分析过程
        logger.info("开始模拟分析过程...")
        total_stocks = len(self.market_data)
        
        for i in range(10):
            # 更新进度
            self.progress = (i + 1) / 10
            self.status = f"正在分析... {self.progress*100:.0f}%"
            logger.info(self.status)
            time.sleep(0.5)
        
        # 模拟分析结果：从数据中选择10%的股票作为结果
        self.results = random.sample(self.market_data, max(1, total_stocks // 10))
        
        # 为结果添加一些模拟评分
        for stock in self.results:
            stock['explosion_energy'] = round(random.uniform(0.1, 1.0), 2)
            stock['expected_increase'] = round(random.uniform(0.01, 0.2), 2)
            stock['buying_timing_score'] = round(random.uniform(0.3, 0.9), 2)
        
        # 按爆发能量降序排序
        self.results.sort(key=lambda x: x.get('explosion_energy', 0), reverse=True)
        
        self.status = "分析完成"
        logger.info(f"分析完成，找到 {len(self.results)} 只潜在爆发股")
        
        return self.results
    
    def get_status(self):
        """获取当前状态"""
        return self.status
    
    def get_progress(self):
        """获取进度"""
        return self.progress
    
    def get_results(self):
        """获取分析结果"""
        return self.results

def run_test(failure_rate=0.8):
    """运行测试
    
    Args:
        failure_rate: API调用失败率 (0-1)
    """
    print(f"=== 开始测试爆发式股票查找器的应急股票列表机制 ===")
    print(f"API调用失败率设置为: {failure_rate*100:.0f}%")
    
    # 创建模拟API助手和爆发式股票查找器
    api_helper = MockAPIHelper(failure_rate=failure_rate)
    finder = MockExplosiveStockFinder(api_helper=api_helper)
    
    # 启动分析
    print("\n1. 启动分析流程")
    start_time = time.time()
    results = finder.start_analysis()
    elapsed_time = time.time() - start_time
    
    # 打印分析结果
    print(f"\n2. 分析完成，耗时: {elapsed_time:.2f} 秒")
    print(f"找到 {len(results)} 只潜在爆发股")
    
    # 打印前5只股票详情
    print("\n3. 前5只潜在爆发股:")
    for i, stock in enumerate(results[:5]):
        code = stock['code']
        name = stock['name']
        industry = stock['industry']
        price = stock.get('current_price', 0)
        energy = stock.get('explosion_energy', 0)
        increase = stock.get('expected_increase', 0) * 100
        
        # 判断是否为应急数据
        is_fallback = stock.get('is_fallback', False)
        history_source = stock.get('history_source', 'unknown')
        
        print(f"  {i+1}. {code} - {name} - {industry} - 当前价: {price:.2f}")
        print(f"     爆发能量: {energy:.2f}, 预期涨幅: {increase:.1f}%")
        print(f"     数据来源: {'应急生成' if is_fallback else 'API获取'}, 历史数据: {history_source}")
    
    # 保存结果
    try:
        output_file = "explosive_finder_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果时出错: {str(e)}")
    
    print("\n=== 测试完成 ===")

def run_with_real_data(use_cache=True):
    """
    运行爆发式股票查找器，使用真实历史数据
    
    Args:
        use_cache: 是否使用缓存数据
    """
    logger.info("启动爆发式股票查找器 (真实数据模式)")
    
    try:
        # 创建一个真实数据连接器
        from QTS.quantum_core.real_data_connector import RealDataConnector
        real_data_connector = RealDataConnector()
        real_data_connector.start()
        
        # 创建一个API助手，但禁用模拟数据
        api_helper = MockAPIHelper(failure_rate=0.0)  # 设置失败率为0以避免使用模拟数据
        
        # 创建配置，强制使用真实数据
        config = {
            'use_real_data': True,
            'max_cache_age': 7*24*60*60,  # 缓存7天
            'use_cache': use_cache,
            'auto_download_market_data': True,
            'data_sources': ['tushare', 'akshare', 'eastmoney']
        }
        
        # 创建一个增强数据提供器
        from QTS.quantum_core.enhanced_data_provider import get_enhanced_data_provider
        data_provider = get_enhanced_data_provider(config)
        
        # 创建一个股票查找器，使用API助手和数据提供器
        from QTS.quantum_core.explosive_stock_finder import ExplosiveStockFinder
        finder = ExplosiveStockFinder(api_helper=api_helper)
        
        # 启动分析
        finder.start(market_scope="全市场", min_increase_percent=8, time_range="3-7天", quantum_weight=0.5)
        
        # 等待分析完成
        import time
        start_time = time.time()
        timeout = 600  # 10分钟超时
        
        while not finder.is_finished() and time.time() - start_time < timeout:
            progress = finder.get_progress()
            status = finder.get_status()
            logger.info(f"进度: {progress*100:.1f}%, 状态: {status}")
            time.sleep(5)
        
        # 获取结果
        results = finder.get_results()
        
        # 显示结果
        logger.info(f"分析完成，找到 {len(results)} 只潜在爆发股")
        
        # 保存结果到文件
        result_file = "explosive_finder_real_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到 {result_file}")
        
        # 停止服务
        finder.stop()
        real_data_connector.stop()
        
        # 返回前10个结果
        return results[:10] if results else []
        
    except Exception as e:
        logger.error(f"使用真实数据运行时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def compare_real_vs_simulated():
    """比较真实数据和模拟数据的分析结果"""
    logger.info("开始比较真实数据和模拟数据的分析结果")
    
    # 运行真实数据测试
    logger.info("=== 使用真实数据进行分析 ===")
    real_results = run_with_real_data(use_cache=True)
    
    # 运行模拟数据测试
    logger.info("=== 使用模拟数据进行分析 ===")
    simulated_results = run_test(failure_rate=1.0)  # 强制使用模拟数据
    
    # 比较结果
    if not real_results or not simulated_results:
        logger.warning("无法进行比较，因为至少有一组结果为空")
        return
    
    # 打印真实数据结果
    logger.info("真实数据分析结果 (前10只):")
    for i, stock in enumerate(real_results):
        logger.info(f"{i+1}. {stock['code']} {stock['name']} - 得分: {stock['score']:.2f}, 预期涨幅: {stock['expected_increase']:.2f}%")
    
    # 打印模拟数据结果
    logger.info("模拟数据分析结果 (前10只):")
    for i, stock in enumerate(simulated_results[:10]):
        logger.info(f"{i+1}. {stock['code']} {stock['name']} - 得分: {stock['score']:.2f}, 预期涨幅: {stock['expected_increase']:.2f}%")
    
    # 简单统计分析
    real_avg_score = sum(stock['score'] for stock in real_results) / len(real_results)
    sim_avg_score = sum(stock['score'] for stock in simulated_results[:10]) / min(10, len(simulated_results))
    
    real_avg_increase = sum(stock['expected_increase'] for stock in real_results) / len(real_results)
    sim_avg_increase = sum(stock['expected_increase'] for stock in simulated_results[:10]) / min(10, len(simulated_results))
    
    logger.info(f"真实数据平均得分: {real_avg_score:.2f}, 平均预期涨幅: {real_avg_increase:.2f}%")
    logger.info(f"模拟数据平均得分: {sim_avg_score:.2f}, 平均预期涨幅: {sim_avg_increase:.2f}%")
    
    # 保存比较结果
    comparison = {
        "real_data": real_results,
        "simulated_data": simulated_results[:10],
        "statistics": {
            "real_avg_score": real_avg_score,
            "sim_avg_score": sim_avg_score,
            "real_avg_increase": real_avg_increase,
            "sim_avg_increase": sim_avg_increase
        }
    }
    
    with open("data_comparison_results.json", 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    
    logger.info("比较结果已保存到 data_comparison_results.json")

def test_data_provider_only():
    """
    测试增强数据提供器的真实数据获取能力
    这个简化的测试避免了复杂的依赖，只专注于验证数据获取功能
    """
    logger.info("开始测试增强数据提供器的真实数据获取能力")
    
    try:
        import sys
        # 添加必要的路径
        sys.path.append('/Users/mac/CSXT')
        
        # 导入增强数据提供器
        from QTS.quantum_core.enhanced_data_provider import EnhancedDataProvider
        
        # 创建配置
        config = {
            'use_real_data': True,
            'max_cache_age': 7*24*60*60,  # 缓存7天
            'use_cache': True,
            'auto_download_market_data': False,  # 测试时不启动自动下载
            'data_sources': ['eastmoney', 'akshare', 'tushare']  # 优先尝试东方财富
        }
        
        # 创建数据提供器
        logger.info("创建增强数据提供器实例")
        data_provider = EnhancedDataProvider(config)
        
        # 测试从东方财富网直接获取数据
        logger.info("尝试直接从东方财富网获取沪深股票列表")
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url = 'http://80.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=50&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14,f2,f3,f8'
            
            logger.info(f"请求URL: {url}")
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                
                if data['data'] and data['data']['diff']:
                    stock_list = []
                    for item in data['data']['diff']:
                        code = item['f12']
                        name = item['f14']
                        price = item.get('f2', 0)
                        change_pct = item.get('f3', 0)
                        
                        stock = {
                            'code': code,
                            'name': name,
                            'price': price,
                            'change_pct': change_pct
                        }
                        stock_list.append(stock)
                    
                    logger.info(f"成功从东方财富网获取 {len(stock_list)} 只股票")
                    
                    # 打印前5只股票信息
                    logger.info("从东方财富网获取的前5只股票信息:")
                    for i, stock in enumerate(stock_list[:5]):
                        logger.info(f"{i+1}. {stock['code']} - {stock['name']} - 价格: {stock['price']} 涨跌幅: {stock['change_pct']}%")
                    
                    # 保存实时数据结果
                    with open("eastmoney_realtime_data.json", 'w', encoding='utf-8') as f:
                        import json
                        json.dump(stock_list[:20], f, ensure_ascii=False, indent=2)
                    
                    logger.info("东方财富实时数据已保存到 eastmoney_realtime_data.json")
                    
                    # 为第一只股票获取历史数据
                    if stock_list:
                        test_stock = stock_list[0]
                        test_code = test_stock['code']
                        # 转换为tushare格式
                        if test_code.startswith('6'):
                            test_code = f"{test_code}.SH"
                        else:
                            test_code = f"{test_code}.SZ"
                            
                        logger.info(f"尝试获取股票 {test_code} 的历史数据")
                        history_data = data_provider.get_stock_history(test_code, days=30, force_refresh=True)
                else:
                    logger.error("东方财富网API无返回数据")
            else:
                logger.error(f"东方财富网API请求失败，状态码: {r.status_code}")
        except Exception as e:
            logger.error(f"从东方财富网获取数据失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # 获取股票列表
        logger.info("尝试获取股票列表")
        stock_list = data_provider._get_stock_list()
        
        if stock_list and len(stock_list) > 0:
            logger.info(f"成功获取股票列表，共 {len(stock_list)} 只股票")
            
            # 打印前5只股票信息
            logger.info("前5只股票信息:")
            for i, stock in enumerate(stock_list[:5]):
                logger.info(f"{i+1}. {stock.get('code', '未知')} - {stock.get('name', '未知')} - {stock.get('industry', '未知')}")
            
            # 测试获取单只股票历史数据
            test_stock = stock_list[0]
            stock_code = test_stock.get('code', '')
            
            logger.info(f"尝试获取股票 {stock_code} 的历史数据")
            # 将min_history_days暂时设为较小的值以测试
            data_provider.min_history_days = 20
            history_data = data_provider.get_stock_history(stock_code, days=30, force_refresh=True)
            
            if history_data:
                logger.info(f"成功获取股票 {stock_code} 的历史数据")
                
                # 检查是否是模拟数据
                is_simulated = history_data.get('is_simulated', False)
                logger.info(f"数据类型: {'模拟数据' if is_simulated else '真实数据'}")
                
                # 显示最近3天数据
                if 'date' in history_data and len(history_data['date']) > 0:
                    logger.info("最近3天数据:")
                    for i in range(min(3, len(history_data['date']))):
                        date = history_data['date'][i]
                        close = history_data['close'][i] if 'close' in history_data else 0
                        volume = history_data['volume'][i] if 'volume' in history_data else 0
                        logger.info(f"  {date}: 收盘价 {close}, 成交量 {volume}")
                
                # 保存结果到文件
                result = {
                    "code": stock_code,
                    "name": test_stock.get('name', ''),
                    "is_simulated": is_simulated,
                    "data_sample": {
                        "dates": history_data.get('date', [])[:5],
                        "closes": history_data.get('close', [])[:5],
                        "volumes": history_data.get('volume', [])[:5]
                    }
                }
                
                with open("data_provider_test_result.json", 'w', encoding='utf-8') as f:
                    import json
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                logger.info("测试结果已保存到 data_provider_test_result.json")
                return True
            else:
                logger.error(f"无法获取股票 {stock_code} 的历史数据")
        else:
            logger.error("无法获取股票列表")
        
        return False
        
    except Exception as e:
        logger.error(f"测试数据提供器时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # 根据命令行参数选择运行模式
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        # 使用真实数据运行
        run_with_real_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "--compare":
        # 比较真实数据和模拟数据
        compare_real_vs_simulated()
    elif len(sys.argv) > 1 and sys.argv[1] == "--provider-test":
        # 只测试数据提供器
        test_data_provider_only()
    else:
        # 默认运行测试
        run_test() 