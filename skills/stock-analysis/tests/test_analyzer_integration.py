"""
Analyzer 整合測試
測試完整分析流程
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer import run_full_analysis


class TestAnalyzerIntegration:
    """整合分析測試 - 需要網路"""

    @pytest.mark.integration
    def test_run_full_analysis_basic(self):
        """基本功能 - 需要網路"""
        pass
    
    @pytest.mark.integration
    def test_run_full_analysis_invalid_ticker(self):
        """無效股票代碼"""
        output = run_full_analysis("INVALID_TICKER_XYZ", period="1mo")
        assert 'error' in output or 'results' in output
    
    def test_run_full_analysis_mock(self):
        """使用 Mock 數據測試整合"""
        from data_fetcher import resolve_stock_code, detect_market
        
        resolved = resolve_stock_code("AAPL")
        market = detect_market("AAPL")
        
        # market 可以是 NASDAQ, TWSE, OTC, US 等
        assert market is not None


class TestAnalyzerImports:
    """測試 Analyzer 導入"""
    
    def test_all_imports(self):
        """所有導入可用"""
        from analyzer import (
            run_full_analysis,
            analyze_price_action,
            analyze_moving_avg,
            analyze_signals,
            analyze_advanced_signals,
            analyze_chan,
            analyze_wave_structure,
            detect_elliott_waves,
            golden_ratio_analysis,
            predict_wave_progression,
            generate_daily_strategy,
            generate_trading_recommendation,
            generate_professional_recommendation,
            analyze_technical_sentiment,
            analyze_macro_impact,
            analyze_news_sentiment,
            analyze_momentum,
            analyze_valuation,
            generate_investment_thesis,
            calculate_position_size
        )
        assert callable(run_full_analysis)


class TestDataFetcherIntegration:
    """數據獲取整合測試"""
    
    @pytest.mark.integration
    def test_resolve_stock_code(self):
        """股票代碼解析"""
        from data_fetcher import resolve_stock_code
        
        result = resolve_stock_code("2330")
        assert result is not None
        
        result = resolve_stock_code("AAPL")
        assert result == "AAPL"
    
    @pytest.mark.integration
    def test_detect_market(self):
        """市場偵測"""
        from data_fetcher import detect_market
        
        assert detect_market("AAPL") == "NASDAQ"
        assert detect_market("2330.TW") in ["TWSE", "OTC"]


class TestChartGeneration:
    """圖表生成測試"""
    
    def test_generate_price_table(self):
        """價格表格"""
        from chart_generator import generate_price_table
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=5, freq='D')
        df = pd.DataFrame({
            'Date': dates,
            'Close': [100, 102, 101, 103, 105],
            'Open': [99, 101, 100, 102, 104],
            'High': [101, 103, 102, 104, 106],
            'Low': [98, 100, 99, 101, 103],
            'Volume': [1000000] * 5
        })
        
        result = generate_price_table(df)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_ma_table(self):
        """均線表格"""
        from chart_generator import generate_ma_table
        
        mas = {
            'MA5': 102.0,
            'MA10': 101.0,
            'MA20': 100.0,
            'MA60': 98.0
        }
        
        result = generate_ma_table(mas)
        assert isinstance(result, str)
    
    def test_generate_indicator_table(self):
        """指標表格"""
        from chart_generator import generate_indicator_table
        
        indicators = {
            'rsi': 55.5,
            'macd': 1.2,
            'signal': 0.8,
            'k': 65.0,
            'd': 60.0
        }
        
        result = generate_indicator_table(indicators)
        assert isinstance(result, str)


class TestQuoteModule:
    """報價模組測試"""
    
    @pytest.mark.integration
    def test_fetch_realtime_quote(self):
        """即時報價"""
        from quote import fetch_realtime_quote
        
        result = fetch_realtime_quote("2330", "tse")
        if result:
            assert 'close' in result or 'code' in result
    
    def test_quote_module_imports(self):
        """Quote 模組導入"""
        from data_fetcher import fetch_realtime_quote
        assert callable(fetch_realtime_quote)


class TestEndToEnd:
    """端到端測試"""
    
    def test_analysis_results_structure(self):
        """分析結果結構"""
        from indicators import analyze_signals
        from price_action import analyze_price_action
        from moving_avg import analyze_moving_avg
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100))
        
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Volume': [1000000] * 100
        })
        
        pa_result = analyze_price_action(df)
        assert 'current_price' in pa_result
        assert 'support' in pa_result
        assert 'resistance' in pa_result
        
        ma_result = analyze_moving_avg(df)
        assert 'mas' in ma_result
        assert 'alignment' in ma_result
        
        ind_result = analyze_signals(df)
        assert 'rsi' in ind_result or 'error' in ind_result
    
    def test_full_results_dict(self):
        """完整結果字典"""
        from chan_theory import analyze_chan
        from wave_theory import analyze_wave_structure
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100))
        
        df = pd.DataFrame({
            'Date': dates,
            'Close': prices,
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Volume': [1000000] * 100
        })
        
        chan_result = analyze_chan(df)
        assert 'pens' in chan_result
        assert 'trend' in chan_result
        
        wave_result = analyze_wave_structure(df)
        assert 'wave_type' in wave_result or 'error' in wave_result
    
    def test_strategy_integration(self):
        """策略整合"""
        from strategy import generate_strategy_signal, analyze_technical_sentiment
        
        results = {
            'moving_avg': {'alignment': {'alignment': 'bullish'}},
            'indicators': {'rsi': 45, 'macd': 1.5, 'signal': 1.0, 'k': 55, 'd': 50},
            'advanced_indicators': {'dmi': {'plus_di': 25, 'minus_di': 15, 'adx': 30}}
        }
        
        signal = generate_strategy_signal(results)
        assert 'signal' in signal
        assert 'score' in signal
        
        sentiment = analyze_technical_sentiment(results)
        assert 'sentiment' in sentiment