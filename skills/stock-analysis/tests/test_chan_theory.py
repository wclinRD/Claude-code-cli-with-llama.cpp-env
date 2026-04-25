"""
Chan Theory 模組測試
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chan_theory import (
    identify笔,
    identify线段,
    identify中枢,
    classify趋势,
    analyze_chan
)


class TestIdentify笔:
    """筆識別測試"""
    
    def test_identify笔_basic(self, sample_price_data):
        """基本功能"""
        result = identify笔(sample_price_data)
        assert isinstance(result, list)
    
    def test_identify笔_insufficient(self, insufficient_data):
        """數據不足 - 使用更少的數據"""
        # insufficient_data 有 10 筆，可能足夠形成筆
        # 測試 3 筆數據肯定不足
        dates = pd.date_range(end=pd.Timestamp.now(), periods=3, freq='D')
        tiny_df = pd.DataFrame({
            'Date': dates,
            'Open': [100, 101, 102],
            'High': [102, 103, 104],
            'Low': [98, 99, 100],
            'Close': [100, 101, 102],
            'Volume': [1000000] * 3
        })
        result = identify笔(tiny_df)
        assert result == []
    
    def test_identify笔_none(self):
        """None 輸入"""
        result = identify笔(None)
        assert result == []
    
    def test_identify笔_structure(self, sample_price_data):
        """筆結構正確"""
        result = identify笔(sample_price_data)
        if result:
            pen = result[0]
            assert 'start' in pen
            assert 'end' in pen
            assert 'type' in pen
            assert pen['type'] in ['up', 'down']


class TestIdentify线段:
    """線段識別測試"""
    
    def test_identify线段_basic(self, sample_price_data):
        """基本功能"""
        result = identify线段(sample_price_data)
        assert isinstance(result, list)
    
    def test_identify线段_insufficient(self, insufficient_data):
        """數據不足 - 需要 10 筆以上"""
        # 使用 5 筆數據肯定不足
        dates = pd.date_range(end=pd.Timestamp.now(), periods=5, freq='D')
        tiny_df = pd.DataFrame({
            'Date': dates,
            'Open': [100, 101, 102, 103, 104],
            'High': [102, 103, 104, 105, 106],
            'Low': [98, 99, 100, 101, 102],
            'Close': [100, 101, 102, 103, 104],
            'Volume': [1000000] * 5
        })
        result = identify线段(tiny_df)
        assert result == []
    
    def test_identify线段_none(self):
        """None 輸入"""
        result = identify线段(None)
        assert result == []
    
    def test_identify线段_structure(self, sample_price_data):
        """線段結構正確"""
        result = identify线段(sample_price_data)
        if result:
            seg = result[0]
            assert 'start' in seg
            assert 'end' in seg
            assert 'type' in seg


class TestIdentify中枢:
    """中樞識別測試"""
    
    def test_identify中枢_basic(self, sample_price_data):
        """基本功能"""
        result = identify中枢(sample_price_data)
        assert isinstance(result, list)
    
    def test_identify中枢_insufficient(self, insufficient_data):
        """數據不足"""
        result = identify中枢(insufficient_data)
        assert result == []
    
    def test_identify中枢_none(self):
        """None 輸入"""
        result = identify中枢(None)
        assert result == []
    
    def test_identify中枢_structure(self, sample_price_data):
        """中樞結構正確"""
        result = identify中枢(sample_price_data)
        if result:
            z = result[0]
            assert 'zone_high' in z
            assert 'zone_low' in z
            assert z['zone_high'] >= z['zone_low']


class TestClassify趋势:
    """趨勢分類測試"""
    
    def test_classify趋势_basic(self, sample_price_data):
        """基本功能"""
        result = classify趋势(sample_price_data)
        assert 'trend' in result
    
    def test_classify趋势_insufficient(self, insufficient_data):
        """數據不足"""
        result = classify趋势(insufficient_data)
        assert result['trend'] == 'unknown'
    
    def test_classify趋势_none(self):
        """None 輸入"""
        result = classify趋势(None)
        assert result['trend'] == 'unknown'
    
    def test_classify趋势_uptrend(self, rising_price_data):
        """上漲趨勢"""
        result = classify趋势(rising_price_data)
        assert result['trend'] in ['上升趨勢', '盤整']
    
    def test_classify趋势_downtrend(self, falling_price_data):
        """下跌趨勢"""
        result = classify趋势(falling_price_data)
        assert result['trend'] in ['下降趨勢', '盤整']


class TestAnalyzeChan:
    """綜合纏論分析測試"""
    
    def test_analyze_chan_basic(self, sample_price_data):
        """基本功能"""
        result = analyze_chan(sample_price_data)
        assert 'pens' in result
        assert 'segments' in result
        assert 'zhongshus' in result
        assert 'trend' in result
    
    def test_analyze_chan_none(self):
        """None 輸入"""
        result = analyze_chan(None)
        assert 'error' in result
    
    def test_analyze_chan_empty(self):
        """空 DataFrame"""
        result = analyze_chan(pd.DataFrame())
        assert 'error' in result