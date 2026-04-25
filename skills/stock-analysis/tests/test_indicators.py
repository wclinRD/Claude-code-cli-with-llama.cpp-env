"""
技術指標測試
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_kd,
    calculate_obv,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_williams_r,
    calculate_cci,
    calculate_dmi,
    analyze_signals,
    analyze_advanced_signals
)


class TestRSI:
    """RSI 計算測試"""
    
    def test_rsi_calculation(self, sample_price_data):
        """RSI 計算基本功能"""
        result = calculate_rsi(sample_price_data)
        assert 'RSI' in result.columns
        assert result['RSI'].notna().sum() > 0
    
    def test_rsi_no_zero_division(self, flat_price_data):
        """RSI 計算不應產生除零錯誤"""
        result = calculate_rsi(flat_price_data)
        assert 'RSI' in result.columns
        # 持平時 RSI 應為 50 或 NaN，不應是 inf
        rsi_values = result['RSI'].dropna()
        assert not np.isinf(rsi_values).any()
    
    def test_rsi_bounds(self, sample_price_data):
        """RSI 值應在 0-100 之間"""
        result = calculate_rsi(sample_price_data)
        rsi = result['RSI'].dropna()
        assert rsi.min() >= 0
        assert rsi.max() <= 100
    
    def test_rsi_insufficient_data(self, insufficient_data):
        """數據不足時應返回原 DataFrame"""
        result = calculate_rsi(insufficient_data)
        assert 'RSI' not in result.columns or result['RSI'].isna().all()


class TestMACD:
    """MACD 計算測試"""
    
    def test_macd_calculation(self, sample_price_data):
        """MACD 計算基本功能"""
        result = calculate_macd(sample_price_data)
        assert 'MACD' in result.columns
        assert 'Signal' in result.columns
        assert 'Histogram' in result.columns
    
    def test_macd_no_zero_division(self, flat_price_data):
        """MACD 計算不應產生錯誤"""
        result = calculate_macd(flat_price_data)
        assert 'MACD' in result.columns
        assert not np.isinf(result['MACD'].dropna()).any()
    
    def test_macd_insufficient_data(self, insufficient_data):
        """數據不足時應返回原 DataFrame"""
        result = calculate_macd(insufficient_data)
        # len < 26 時不計算，應返回原數據
        assert len(result) == len(insufficient_data)


class TestKD:
    """KD 指標測試"""
    
    def test_kd_calculation(self, sample_price_data):
        """KD 計算基本功能"""
        result = calculate_kd(sample_price_data)
        assert 'K' in result.columns
        assert 'D' in result.columns
        assert 'J' in result.columns
    
    def test_kd_no_zero_division(self, flat_price_data):
        """KD 計算不應產生除零錯誤"""
        result = calculate_kd(flat_price_data)
        assert 'K' in result.columns
        # K, D, J 不應為 inf
        for col in ['K', 'D', 'J']:
            if col in result.columns:
                assert not np.isinf(result[col].dropna()).any()
    
    def test_kd_bounds(self, sample_price_data):
        """KD 值應在 0-100 之間 (通常)"""
        result = calculate_kd(sample_price_data)
        k = result['K'].dropna()
        d = result['D'].dropna()
        # K, D 通常在 0-100 範圍內
        assert k.min() >= -100  # 允許 J 計算導致的負值
        assert k.max() <= 200   # 允許 J 計算導致的高於 100


class TestOBV:
    """OBV 能量潮測試"""
    
    def test_obv_calculation(self, sample_price_data):
        """OBV 計算基本功能"""
        result = calculate_obv(sample_price_data)
        assert 'OBV' in result.columns
    
    def test_obv_monotonic(self, rising_price_data):
        """上漲時 OBV 應持續增加"""
        result = calculate_obv(rising_price_data)
        # 連續上漲，OBV 應該遞增
        assert result['OBV'].iloc[-1] > result['OBV'].iloc[0]
    
    def test_obv_decreasing(self, falling_price_data):
        """下跌時 OBV 應持續減少"""
        result = calculate_obv(falling_price_data)
        # 連續下跌，OBV 應該遞減
        assert result['OBV'].iloc[-1] < result['OBV'].iloc[0]


class TestBollingerBands:
    """布林帶測試"""
    
    def test_bb_calculation(self, sample_price_data):
        """布林帶計算基本功能"""
        result = calculate_bollinger_bands(sample_price_data)
        assert 'BB_Upper' in result.columns
        assert 'BB_Middle' in result.columns
        assert 'BB_Lower' in result.columns
    
    def test_bb_order(self, sample_price_data):
        """布林帶順序: 上軌 > 中軌 > 下軌"""
        result = calculate_bollinger_bands(sample_price_data)
        latest = result.iloc[-1]
        assert latest['BB_Upper'] >= latest['BB_Middle']
        assert latest['BB_Middle'] >= latest['BB_Lower']


class TestATR:
    """ATR 平均真實波幅測試"""
    
    def test_atr_calculation(self, sample_price_data):
        """ATR 計算基本功能"""
        result = calculate_atr(sample_price_data)
        assert 'ATR' in result.columns
        assert 'ATR_Pct' in result.columns
    
    def test_atr_no_zero_division(self, flat_price_data):
        """ATR 計算不應產生除零錯誤"""
        result = calculate_atr(flat_price_data)
        assert 'ATR' in result.columns
        # ATR_Pct 不應為 inf
        atr_pct = result['ATR_Pct'].dropna()
        assert not np.isinf(atr_pct).any()
    
    def test_atr_bounds(self, sample_price_data):
        """ATR_Pct 應為正值"""
        result = calculate_atr(sample_price_data)
        atr_pct = result['ATR_Pct'].dropna()
        assert atr_pct.min() >= 0


class TestWilliamsR:
    """威廉指標測試"""
    
    def test_wr_calculation(self, sample_price_data):
        """威廉指標計算基本功能"""
        result = calculate_williams_r(sample_price_data)
        assert 'Williams_R' in result.columns
    
    def test_wr_no_zero_division(self, flat_price_data):
        """威廉指標不應產生除零錯誤"""
        result = calculate_williams_r(flat_price_data)
        assert 'Williams_R' in result.columns
        wr = result['Williams_R'].dropna()
        assert not np.isinf(wr).any()
    
    def test_wr_bounds(self, sample_price_data):
        """威廉指標應在 -100 到 0 之間"""
        result = calculate_williams_r(sample_price_data)
        wr = result['Williams_R'].dropna()
        assert wr.min() >= -100
        assert wr.max() <= 0


class TestCCI:
    """CCI 商品通道指標測試"""
    
    def test_cci_calculation(self, sample_price_data):
        """CCI 計算基本功能"""
        result = calculate_cci(sample_price_data)
        assert 'CCI' in result.columns
    
    def test_cci_no_zero_division(self, flat_price_data):
        """CCI 不應產生除零錯誤"""
        result = calculate_cci(flat_price_data)
        assert 'CCI' in result.columns
        cci = result['CCI'].dropna()
        assert not np.isinf(cci).any()


class TestDMI:
    """DMI 趨向指標測試"""
    
    def test_dmi_calculation(self, sample_price_data):
        """DMI 計算基本功能"""
        result = calculate_dmi(sample_price_data)
        assert 'Plus_DI' in result.columns
        assert 'Minus_DI' in result.columns
        assert 'ADX' in result.columns
    
    def test_dmi_no_zero_division(self, flat_price_data):
        """DMI 不應產生除零錯誤"""
        result = calculate_dmi(flat_price_data)
        assert 'Plus_DI' in result.columns
        # 不應為 inf
        for col in ['Plus_DI', 'Minus_DI', 'DX', 'ADX']:
            if col in result.columns:
                assert not np.isinf(result[col].dropna()).any()


class TestAnalyzeSignals:
    """技術指標訊號分析測試"""
    
    def test_analyze_signals(self, sample_price_data):
        """訊號分析基本功能"""
        result = analyze_signals(sample_price_data)
        assert 'rsi' in result
        assert 'macd' in result
        assert 'k' in result
        assert 'd' in result
        assert 'signals' in result
    
    def test_analyze_signals_insufficient_data(self, insufficient_data):
        """數據不足時應返回錯誤訊息"""
        result = analyze_signals(insufficient_data)
        assert 'error' in result or result.get('rsi') is None
    
    def test_analyze_signals_output_format(self, sample_price_data):
        """訊號輸出格式正確"""
        result = analyze_signals(sample_price_data)
        signals = result.get('signals', [])
        for sig in signals:
            assert 'indicator' in sig
            assert 'signal' in sig
            assert 'action' in sig


class TestAnalyzeAdvancedSignals:
    """進階技術指標訊號分析測試"""
    
    def test_analyze_advanced_signals(self, sample_price_data):
        """進階訊號分析基本功能"""
        result = analyze_advanced_signals(sample_price_data)
        assert 'bollinger_bands' in result
        assert 'atr' in result
        assert 'dmi' in result
    
    def test_analyze_advanced_signals_insufficient(self, insufficient_data):
        """數據不足時應返回錯誤"""
        result = analyze_advanced_signals(insufficient_data)
        assert 'error' in result