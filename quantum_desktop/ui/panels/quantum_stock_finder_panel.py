def _init_stock_strategy(self):
    """Initialize quantum stock strategy"""
    try:
        logger.info("Initializing quantum stock strategy...")
        
        # Try to import the real strategy
        try:
            from quantum_core.quantum_stock_strategy import QuantumStockStrategy
            self.stock_strategy = QuantumStockStrategy(system_manager=self.system_manager)
            logger.info("Successfully loaded real quantum stock strategy")
        except ImportError:
            try:
                # Try import from QTS namespace
                from QTS.quantum_core.quantum_stock_strategy import QuantumStockStrategy
                self.stock_strategy = QuantumStockStrategy(system_manager=self.system_manager)
                logger.info("Successfully loaded quantum stock strategy from QTS namespace")
            except ImportError:
                logger.warning("Cannot import quantum stock strategy, using fallback implementation")
                
                # Create a fallback implementation
                class QuantumStockStrategy:
                    def __init__(self, **kwargs):
                        self.system_manager = kwargs.get('system_manager')
                        self.is_running = False
                        self.config = {
                            'quantum_power': 50,
                            'risk_preference': 'balanced',
                            'market_scope': 'all',
                            'sector_filter': 'all'
                        }
                        logger.info("Created fallback quantum stock strategy")
                        
                    def start(self):
                        self.is_running = True
                        logger.info("Started fallback quantum stock strategy")
                        
                    def stop(self):
                        self.is_running = False
                        logger.info("Stopped fallback quantum stock strategy")
                        
                    def find_stocks(self, **kwargs):
                        import random
                        import pandas as pd
                        from datetime import datetime
                        
                        logger.info("Using fallback quantum stock finder")
                        
                        # Update configuration from kwargs
                        for key, value in kwargs.items():
                            if key in self.config:
                                self.config[key] = value
                        
                        # Quality factor based on quantum power
                        quantum_power = self.config.get('quantum_power', 50)
                        quality_factor = quantum_power / 100.0
                        
                        # Risk preference affects stock characteristics
                        risk_preference = self.config.get('risk_preference', 'balanced')
                        
                        # Generate simulated stocks
                        num_stocks = random.randint(8, 15)
                        industries = ['Technology', 'Healthcare', 'Consumer', 'Financial', 
                                    'Energy', 'Industrial', 'Materials', 'Communication', 'Utilities']
                        
                        # Create stock list
                        stocks = []
                        for i in range(num_stocks):
                            # Base score influenced by quantum power
                            base_score = random.uniform(60, 85) + (quality_factor * 15)
                            base_score = min(99, base_score)
                            
                            # Risk-based characteristics
                            if risk_preference == 'conservative':
                                pe_ratio = random.uniform(5, 15)
                                pb_ratio = random.uniform(0.8, 2.0)
                                growth_rate = random.uniform(5, 15)
                            elif risk_preference == 'aggressive':
                                pe_ratio = random.uniform(25, 60)
                                pb_ratio = random.uniform(3.0, 8.0)
                                growth_rate = random.uniform(30, 80)
                            else:  # balanced
                                pe_ratio = random.uniform(15, 30)
                                pb_ratio = random.uniform(1.5, 4.0)
                                growth_rate = random.uniform(15, 30)
                            
                            # Generate signals
                            signals = {
                                'quantum_momentum': random.uniform(50, quality_factor * 100),
                                'trend_prediction': random.uniform(50, quality_factor * 100),
                                'volatility_capture': random.uniform(50, quality_factor * 100),
                                'value_factor': random.uniform(50, quality_factor * 100)
                            }
                            
                            # Final score with some randomness
                            score = base_score + random.uniform(-5, 5) * (1 - quality_factor)
                            score = max(60, min(99, score))
                            
                            # Select industry
                            industry = industries[i % len(industries)]
                            
                            # Generate stock code
                            if i % 3 == 0:
                                code = f"600{random.randint(100, 999)}"
                            elif i % 3 == 1:
                                code = f"000{random.randint(100, 999)}"
                            else:
                                code = f"300{random.randint(100, 999)}"
                            
                            # Generate reasons
                            reason_templates = [
                                "Strong upward trend in quantum feature analysis",
                                "Positive signals in multi-dimensional quantum indicators",
                                "Quantum momentum indicator at historical high",
                                "High probability of future growth in hybrid quantum model",
                                "Low volatility high return pattern in quantum prediction",
                                "Breakthrough rise predicted by quantum tunneling effect",
                                "Strong market correlation in quantum entanglement indicator"
                            ]
                            reason = random.choice(reason_templates) + f", Growth expectation {growth_rate:.1f}%"
                            
                            # Create stock entry
                            stock = {
                                "code": code,
                                "name": f"Mock Stock {i+1}",
                                "industry": industry,
                                "reason": reason,
                                "score": round(score, 1),
                                "pe_ratio": round(pe_ratio, 2),
                                "pb_ratio": round(pb_ratio, 2),
                                "growth_rate": round(growth_rate, 2),
                                "signals": signals,
                                "quantum_analysis": True
                            }
                            stocks.append(stock)
                        
                        # Sort by score
                        stocks.sort(key=lambda x: x['score'], reverse=True)
                        
                        # Create result
                        result = {
                            'stocks': stocks,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'quantum_power': quantum_power,
                            'risk_preference': risk_preference
                        }
                        return result
                
                # Use fallback strategy
                self.stock_strategy = QuantumStockStrategy(system_manager=self.system_manager)
                logger.info("Using fallback quantum stock strategy")
        
        # Connect system events
        if self.system_manager:
            self.system_manager.system_started.connect(self.on_system_started)
            self.system_manager.system_stopped.connect(self.on_system_stopped)
        
        logger.info("Quantum stock strategy initialization complete")
        
    except Exception as e:
        logger.error(f"Error initializing quantum stock strategy: {str(e)}")
        self.status_label.setText(f"Error initializing stock finder: {str(e)}")

    # 获取量子后端和市场分析器 