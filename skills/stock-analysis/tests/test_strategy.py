"""
Strategy 模組測試
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy import (
    analyze_technical_sentiment,
    analyze_macro_impact,
    analyze_news_sentiment,
    analyze_momentum,
    analyze_valuation,
    calculate_position_size,
    generate_investment_thesis,
    generate_professional_recommendation,
    calculate_overall_score,
    generate_entry_exit_points,
    analyze_risk_reward,
    generate_strategy_signal,
    generate_daily_strategy,
    generate_trading_recommendation,
    StopLossType,
    PositionSide,
    calculate_stop_loss,
    calculate_take_profit,
    calculate_trailing_stop,
    calculate_risk_management,
    calculate_kelly_criterion,
    calculate_position_size_kelly,
    rank_signals_by_weight,
    optimize_risk_reward,
)


class TestAnalyzeTechnicalSentiment:
    """技術面多空分析測試"""
    
    def test_analyze_technical_sentiment_basic(self):
        """基本功能"""
        results = {
            'indicators': {'rsi': 50, 'macd': 1, 'signal': 0.5, 'k': 60, 'd': 50}
        }
        result = analyze_technical_sentiment(results)
        assert 'sentiment' in result
        assert 'strength' in result
        assert 'signals' in result
    
    def test_analyze_technical_sentiment_oversold(self):
        """RSI 超賣"""
        results = {
            'indicators': {'rsi': 25, 'macd': -1, 'signal': 0, 'k': 20, 'd': 30}
        }
        result = analyze_technical_sentiment(results)
        assert result['strength'] > 0
    
    def test_analyze_technical_sentiment_overbought(self):
        """RSI 超買"""
        results = {
            'indicators': {'rsi': 85, 'macd': 2, 'signal': 1, 'k': 90, 'd': 80}
        }
        result = analyze_technical_sentiment(results)
        assert result['strength'] < 0


class TestAnalyzeMacroImpact:
    """總體經濟影響測試"""
    
    def test_analyze_macro_impact_basic(self):
        """基本功能"""
        results = {
            'macro': {
                'usd_twd': {'change_pct': 0.5},
                'crude_oil': {'change_pct': 1},
                'sp500': {'change_pct': 0.5},
                'nasdaq': {'change_pct': 0.5},
                'us_10y_bond': {'rate': 4.0}
            }
        }
        result = analyze_macro_impact(results)
        assert 'impact' in result
        assert 'score' in result
        assert 'factors' in result
    
    def test_analyze_macro_impact_no_macro(self):
        """無總經數據"""
        results = {}
        result = analyze_macro_impact(results)
        assert 'impact' in result
        assert 'score' in result


class TestAnalyzeNewsSentiment:
    """新聞情緒分析測試"""
    
    def test_analyze_news_sentiment_basic(self):
        """基本功能"""
        results = {
            'related_news': [
                {'title': '股價大漲 5%，突破新高'},
                {'title': '獲利創新高'}
            ]
        }
        result = analyze_news_sentiment(results)
        assert 'sentiment' in result
        assert 'score' in result
    
    def test_analyze_news_sentiment_empty(self):
        """無新聞"""
        results = {'related_news': []}
        result = analyze_news_sentiment(results)
        assert result['sentiment'] == '中立'


class TestAnalyzeMomentum:
    """動能分析測試"""
    
    def test_analyze_momentum_basic(self, sample_price_data):
        """基本功能"""
        results = {}
        result = analyze_momentum(sample_price_data, results)
        assert 'momentum' in result
        assert 'strength' in result
    
    def test_analyze_momentum_insufficient(self, insufficient_data):
        """數據不足"""
        results = {}
        result = analyze_momentum(insufficient_data, results)
        assert result['momentum'] == '不明'
    
    def test_analyze_momentum_none(self):
        """None 輸入"""
        result = analyze_momentum(None, {})
        assert result['momentum'] == '不明'


class TestAnalyzeValuation:
    """評價面分析測試"""
    
    def test_analyze_valuation_basic(self):
        """基本功能"""
        results = {
            'stock_info': {'pe_ratio': 15, 'dividend_yield': 0.03}
        }
        result = analyze_valuation(results)
        assert 'valuation' in result
        assert 'score' in result
    
    def test_analyze_valuation_undervalued(self):
        """低估"""
        results = {
            'stock_info': {'pe_ratio': 8, 'dividend_yield': 0.06}
        }
        result = analyze_valuation(results)
        assert result['valuation'] in ['偏低', '嚴重低估']
    
    def test_analyze_valuation_no_info(self):
        """無資料"""
        results = {}
        result = analyze_valuation(results)
        assert result['valuation'] == '合理'


class TestCalculatePositionSize:
    """部位大小計算測試"""
    
    def test_calculate_position_size_basic(self):
        """基本功能"""
        results = {
            'indicators': {'rsi': 50},
            'macro': {},
            'stock_info': {}
        }
        result = calculate_position_size(results)
        assert 'position_pct' in result
        assert 'risk_level' in result
    
    def test_calculate_position_size_aggressive(self):
        """積極型"""
        results = {
            'indicators': {'rsi': 20},
            'macro': {'usd_twd': {'change_pct': -2}},
            'stock_info': {'pe_ratio': 8}
        }
        result = calculate_position_size(results)
        assert result['position_pct'] >= 20


class TestCalculateOverallScore:
    """綜合評分測試"""
    
    def test_calculate_overall_score_basic(self):
        """基本功能"""
        results = {}
        result = calculate_overall_score(results)
        assert isinstance(result, int)
        assert 0 <= result <= 100
    
    def test_calculate_overall_score_bullish(self):
        """多頭"""
        results = {
            'moving_avg': {'alignment': {'alignment': 'bullish'}},
            'indicators': {'signals': [{'action': 'buy'}]}
        }
        result = calculate_overall_score(results)
        assert result >= 50


class TestGenerateEntryExitPoints:
    """進退場點位測試"""
    
    def test_generate_entry_exit_points_basic(self):
        """基本功能"""
        results = {
            'price_action': {
                'current_price': 100,
                'nearest_support': 90,
                'nearest_resistance': 120
            }
        }
        result = generate_entry_exit_points(results)
        assert 'recommended_buy' in result
        assert 'recommended_sell' in result
    
    def test_generate_entry_exit_points_empty(self):
        """無價格資料"""
        results = {}
        result = generate_entry_exit_points(results)
        assert result == {}


class TestAnalyzeRiskReward:
    """風險報酬比測試"""
    
    def test_analyze_risk_reward_basic(self):
        """基本功能"""
        results = {
            'price_action': {
                'current_price': 100,
                'nearest_support': 90,
                'nearest_resistance': 120
            }
        }
        result = analyze_risk_reward(results)
        assert 'risk_reward' in result
    
    def test_analyze_risk_reward_insufficient(self):
        """資料不足"""
        results = {}
        result = analyze_risk_reward(results)
        assert result == {}


class TestGenerateStrategySignal:
    """交易訊號測試"""
    
    def test_generate_strategy_signal_basic(self):
        """基本功能"""
        results = {
            'moving_avg': {'alignment': {'alignment': 'bullish'}}
        }
        result = generate_strategy_signal(results)
        assert 'signal' in result
        assert 'score' in result
    
    def test_generate_strategy_signal_strong_buy(self):
        """強烈買入"""
        results = {
            'moving_avg': {'alignment': {'alignment': 'bullish'}},
            'indicators': {'signals': [{'action': 'buy'}, {'action': 'buy'}]},
            'advanced_indicators': {'dmi': {'plus_di': 30, 'minus_di': 15, 'adx': 30}}
        }
        result = generate_strategy_signal(results)
        assert '買入' in result['signal']


class TestStopLossCalculation:
    """停損計算測試"""
    
    def test_calculate_stop_loss_long_percent(self):
        """多頭百分比停損"""
        result = calculate_stop_loss(100, PositionSide.LONG, StopLossType.PERCENT, percent=5)
        assert result == 95.0
    
    def test_calculate_stop_loss_long_atr(self):
        """多頭 ATR 停損"""
        result = calculate_stop_loss(100, PositionSide.LONG, StopLossType.ATR, atr=2, atr_multiplier=2)
        assert result == 96.0
    
    def test_calculate_stop_loss_short_percent(self):
        """空頭百分比停損"""
        result = calculate_stop_loss(100, PositionSide.SHORT, StopLossType.PERCENT, percent=5)
        assert result == 105.0


class TestTakeProfitCalculation:
    """停利計算測試"""
    
    def test_calculate_take_profit_long(self):
        """多頭停利"""
        result = calculate_take_profit(100, PositionSide.LONG, risk_reward_ratio=2.0)
        assert result == 104.0
    
    def test_calculate_take_profit_fixed(self):
        """固定百分比停利"""
        result = calculate_take_profit(100, PositionSide.LONG, fixed_percent=10)
        assert abs(result - 110.0) < 0.01


class TestTrailingStop:
    """移動停損測試"""
    
    def test_calculate_trailing_stop_long(self):
        """多頭移動停損"""
        result = calculate_trailing_stop(110, 100, 115, PositionSide.LONG, activation_percent=3)
        assert result >= 97.0
    
    def test_calculate_trailing_stop_long_atr(self):
        """多頭 ATR 移動停損"""
        result = calculate_trailing_stop(110, 100, 115, PositionSide.LONG, atr=2, atr_multiplier=2)
        assert result >= 97.0


class TestRiskManagement:
    """完整風控測試"""
    
    def test_calculate_risk_management_long(self):
        """多頭風控"""
        result = calculate_risk_management(100, 100, PositionSide.LONG)
        assert 'stop_loss' in result
        assert 'take_profit' in result
        assert 'risk_reward_ratio' in result
        assert result['risk_reward_ratio'] >= 2.0


class TestKellyCriterion:
    """Kelly Criterion 測試"""
    
    def test_calculate_kelly_positive_edge(self):
        """正期望値"""
        result = calculate_kelly_criterion(win_rate=0.5, avg_win=100, avg_loss=50)
        assert result['kelly_fraction'] > 0
        assert 'verdict' in result
    
    def test_calculate_kelly_negative_edge(self):
        """負期望値"""
        result = calculate_kelly_criterion(win_rate=0.3, avg_win=50, avg_loss=100)
        assert result['kelly_fraction'] == 0
        assert '無正期望値' in result['verdict']
    
    def test_calculate_position_size_kelly(self):
        """Kelly 部位計算"""
        result = calculate_position_size_kelly(1000000, 0.5, 100, 50)
        assert 'position_value' in result
        assert 'shares' in result
        assert 'kelly_info' in result


class TestSignalRanking:
    """訊號排序測試"""
    
    def test_rank_signals_by_weight(self):
        """訊號權重排序"""
        signals = [
            {'type': 'buy', 'text': '訊號1'},
            {'type': 'sell', 'text': '訊號2'},
            {'type': 'neutral', 'text': '訊號3'},
        ]
        weights = {'buy': 10, 'sell': -10, 'neutral': 0}
        result = rank_signals_by_weight(signals, weights)
        assert result[0]['type'] == 'buy'
        assert result[-1]['type'] == 'sell'


class TestRiskRewardOptimization:
    """風險報酬優化測試"""
    
    def test_optimize_risk_reward(self):
        """風險報酬優化"""
        result = optimize_risk_reward(100, [120, 130], [95, 90])
        assert 'best' in result
        assert 'all_options' in result
        assert len(result['all_options']) > 0
    
    def test_optimize_valid_options(self):
        """有效選項"""
        result = optimize_risk_reward(100, [120], [90])
        assert len(result['valid_options']) > 0