# CSXT Quantum Trading System

一个基于量子计算和机器学习的智能化股票交易系统。

## 系统特点

- 量子增强的预测模型
- 自适应特征工程
- 多维度分析
- 实时市场情绪分析
- 智能风险控制
- 自动化交易执行

## 主要组件

1. **量子核心系统**
   - 量子特征提取
   - 量子态预测
   - 量子优化算法

2. **预测模型**
   - 深度学习模型
   - 集成学习
   - 自适应优化

3. **特征工程**
   - 技术指标
   - 市场情绪
   - 多维度分析
   - 量子特征

4. **风险控制**
   - 实时风险监控
   - 自适应止损
   - 仓位管理

5. **回测系统**
   - 历史数据模拟
   - 性能评估
   - 策略优化

## 安装要求

- Python 3.8+
- PyTorch 1.8+
- pandas
- numpy
- scikit-learn
- TA-Lib
- qiskit (用于量子计算)

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/CSXT.git
cd CSXT
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行系统：
```bash
cd QTS
python launch_quantum_core.py --mode desktop
```

## 配置说明

系统配置文件位于 `QTS/config/` 目录下：
- `config.json`: 主配置文件
- `quantum_config.json`: 量子模块配置
- `model_config.json`: 模型配置
- `trading_config.json`: 交易配置

## 使用说明

1. **数据获取**
```python
from quantum_core.data_manager import get_stock_data_manager

# 初始化数据管理器
data_manager = get_stock_data_manager()

# 获取股票数据
data = data_manager.get_stock_data("600000.SH")
```

2. **预测模型**
```python
from quantum_core.models import EnhancedPredictor

# 创建预测模型
predictor = EnhancedPredictor()

# 训练模型
predictor.fit(X_train, y_train)

# 预测
predictions = predictor.predict(X_test)
```

3. **回测分析**
```python
from quantum_core.backtest import BacktestFramework

# 创建回测框架
backtest = BacktestFramework()

# 运行回测
results = backtest.run(strategy, data)
```

## 开发计划

- [ ] 增强量子特征工程
- [ ] 优化预测模型性能
- [ ] 添加更多技术指标
- [ ] 改进风险控制系统
- [ ] 优化回测框架

## 贡献指南

欢迎提交 Pull Request 或创建 Issue。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。 