"""
共用 pytest fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def pytest_configure(config):
    """註冊自訂標記"""
    config.addinivalue_line("markers", "integration: 整合測試 (需要網路連線)")


@pytest.fixture
def sample_price_data():
    """標準價格數據 (足夠計算所有指標)"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    np.random.seed(42)
    
    # 產生波動的價格數據
    base_price = 100
    prices = [base_price]
    for i in range(99):
        change = np.random.randn() * 2
        prices.append(prices[-1] * (1 + change/100))
    
    return pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 100)
    })


@pytest.fixture
def flat_price_data():
    """完全持平的價格數據 (測試除零保護)"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Open': [100.0] * 30,
        'High': [100.0] * 30,
        'Low': [100.0] * 30,
        'Close': [100.0] * 30,
        'Volume': [1000000] * 30
    })


@pytest.fixture
def rising_price_data():
    """持續上漲的價格數據"""
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    prices = [100 + i for i in range(60)]
    return pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Close': prices,
        'Volume': [1000000] * 60
    })


@pytest.fixture
def falling_price_data():
    """持續下跌的價格數據"""
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    prices = [160 - i for i in range(60)]
    return pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Close': prices,
        'Volume': [1000000] * 60
    })


@pytest.fixture
def insufficient_data():
    """數據不足的情況"""
    dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'High': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'Low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'Volume': [1000000] * 10
    })