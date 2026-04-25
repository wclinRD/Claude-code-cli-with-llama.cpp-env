"""
Wave Theory 模組測試
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wave_theory import (
    find_wave_peaks,
    detect_wave_pattern,
    identify_elliott_wave,
    calculate_fibonacci_retracements,
    analyze_wave_structure,
    detect_elliott_waves,
    golden_ratio_analysis,
    predict_wave_progression
)


class TestFindWavePeaks:
    """波浪峰值偵測測試"""
    
    def test_find_wave_peaks_basic(self, sample_price_data):
        """基本功能"""
        result = find_wave_peaks(sample_price_data)
        assert 'peaks' in result
        assert 'troughs' in result
    
    def test_find_wave_peaks_insufficient(self, insufficient_data):
        """數據不足"""
        result = find_wave_peaks(insufficient_data)
        assert result['peaks'] == []
        assert result['troughs'] == []
    
    def test_find_wave_peaks_none(self):
        """None 輸入"""
        result = find_wave_peaks(None)
        assert result['peaks'] == []
        assert result['troughs'] == []


class TestDetectWavePattern:
    """波浪模式偵測測試"""
    
    def test_detect_wave_pattern_basic(self, sample_price_data):
        """基本功能"""
        peaks_troughs = find_wave_peaks(sample_price_data)
        result = detect_wave_pattern(sample_price_data, peaks_troughs['peaks'], peaks_troughs['troughs'])
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_detect_wave_pattern_insufficient(self, sample_price_data):
        """數據不足"""
        result = detect_wave_pattern(sample_price_data, [], [])
        assert result == ('unclear', 'unknown')


class TestIdentifyElliottWave:
    """艾略特波浪識別測試"""
    
    def test_identify_elliott_wave_basic(self, sample_price_data):
        """基本功能"""
        peaks_troughs = find_wave_peaks(sample_price_data)
        result = identify_elliott_wave(sample_price_data, peaks_troughs['peaks'], peaks_troughs['troughs'])
        assert isinstance(result, str)
    
    def test_identify_elliott_wave_insufficient(self, sample_price_data):
        """數據不足"""
        result = identify_elliott_wave(sample_price_data, [], [])
        assert result == 'wave_1'


class TestCalculateFibonacciRetracements:
    """斐波那契回調位測試"""
    
    def test_calculate_fibonacci_basic(self):
        """基本功能"""
        result = calculate_fibonacci_retracements(100, 200)
        assert 'fib_0' in result
        assert 'fib_38' in result  # 0.382
        assert 'fib_61' in result  # 0.618
        assert 'fib_78' in result  # 0.786
        assert 'fib_100' in result
    
    def test_calculate_fibonacci_order(self):
        """順序正確"""
        result = calculate_fibonacci_retracements(100, 200)
        assert result['fib_0'] < result['fib_61'] < result['fib_100']


class TestAnalyzeWaveStructure:
    """波浪結構分析測試"""
    
    def test_analyze_wave_structure_basic(self, sample_price_data):
        """基本功能"""
        result = analyze_wave_structure(sample_price_data)
        assert 'wave_type' in result
        assert 'wave_stage' in result
        assert 'elliott_position' in result
    
    def test_analyze_wave_structure_insufficient(self, insufficient_data):
        """數據不足"""
        result = analyze_wave_structure(insufficient_data)
        assert 'error' in result
    
    def test_analyze_wave_structure_none(self):
        """None 輸入"""
        result = analyze_wave_structure(None)
        assert 'error' in result


class TestDetectElliottWaves:
    """艾略特波浪偵測測試"""
    
    def test_detect_elliott_waves_basic(self, sample_price_data):
        """基本功能"""
        result = detect_elliott_waves(sample_price_data)
        assert 'pattern' in result
        assert 'wave' in result
    
    def test_detect_elliott_waves_insufficient(self, insufficient_data):
        """數據不足"""
        result = detect_elliott_waves(insufficient_data)
        assert result['pattern'] is None


class TestGoldenRatioAnalysis:
    """黃金分割率分析測試"""
    
    def test_golden_ratio_analysis_basic(self, sample_price_data):
        """基本功能"""
        result = golden_ratio_analysis(sample_price_data)
        assert 'current' in result
        assert 'high' in result
        assert 'low' in result
        assert 'targets' in result
    
    def test_golden_ratio_analysis_insufficient(self, insufficient_data):
        """數據不足"""
        result = golden_ratio_analysis(insufficient_data)
        assert result['targets'] == []
    
    def test_golden_ratio_analysis_none(self):
        """None 輸入"""
        result = golden_ratio_analysis(None)
        assert result['targets'] == []


class TestPredictWaveProgression:
    """波浪後續走勢預測測試"""
    
    def test_predict_wave_progression_basic(self, sample_price_data):
        """基本功能"""
        result = predict_wave_progression(sample_price_data, '推動浪', 'wave_3')
        assert 'forecasts' in result
        assert 'time_estimate' in result
    
    def test_predict_wave_progression_insufficient(self, insufficient_data):
        """數據不足"""
        result = predict_wave_progression(insufficient_data, '推動浪', 'wave_3')
        assert result['forecast'] == '數據不足'
    
    def test_predict_wave_progression_none(self):
        """None 輸入"""
        result = predict_wave_progression(None, '推動浪', 'wave_3')
        # 返回 '數據不足' 或 'forecasts'
        assert 'forecast' in result or 'forecasts' in result