"""
Analysis Module
Calculates growth metrics, trendlines, rolling means, and seasonal data
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, List
from scipy import stats
from config import SEASONS

class AnalysisEngine:
    """Analyzes parkrun results data"""
    
    def __init__(self, rolling_window: int = 13):
        """
        Initialize AnalysisEngine
        
        Args:
            rolling_window: Number of weeks for rolling mean calculation
        """
        self.rolling_window = rolling_window
    
    def get_season(self, date: datetime) -> str:
        """
        Determine the season for a given date
        
        Args:
            date: datetime object
            
        Returns:
            Season name
        """
        month = date.month
        for season, months in SEASONS.items():
            if month in months:
                return season
        return 'Winter'
    
    def add_season_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add season column to DataFrame
        
        Args:
            df: DataFrame with 'date' column
            
        Returns:
            DataFrame with added 'season' column
        """
        df = df.copy()
        df['season'] = df['date'].apply(self.get_season)
        return df
    
    def calculate_trendline(self, df: pd.DataFrame, 
                           x_col: str = 'date', 
                           y_col: str = 'finishers') -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Calculate linear trendline using least squares regression
        
        Args:
            df: DataFrame with data
            x_col: Column name for x-axis (should be date)
            y_col: Column name for y-axis values
            
        Returns:
            Tuple of (x_values, y_values, slope) for trendline
        """
        # Convert dates to numeric values (days since start)
        dates = df[x_col]
        x_numeric = (dates - dates.min()).dt.days.values

        y = df[y_col].values.astype(float)
        
        # Remove NaN values
        mask = ~np.isnan(y)
        x_numeric = x_numeric[mask]
        y = y[mask]
        
        if len(x_numeric) < 2:
            return None, None
        
        # Calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, y)
        
        # Generate trendline
        y_trend = slope * x_numeric + intercept
        
        return np.arange(len(df)), y_trend, slope
    
    def calculate_rolling_mean(self, df: pd.DataFrame, 
                              window: int = None,
                              y_col: str = 'finishers') -> pd.Series:
        """
        Calculate rolling mean (moving average)
        
        Args:
            df: DataFrame with data
            window: Window size in rows (if None, uses self.rolling_window)
            y_col: Column name for y-axis values
            
        Returns:
            Series with rolling mean
        """
        if window is None:
            window = self.rolling_window
        
        return df[y_col].rolling(window=window, center=True, min_periods=1).mean()
    
    def get_growth_stats(self, df: pd.DataFrame, 
                        y_col: str = 'finishers') -> Dict[str, float]:
        """
        Calculate growth statistics
        
        Args:
            df: DataFrame with data
            y_col: Column name for y-axis values
            
        Returns:
            Dictionary with growth metrics
        """
        values = df[y_col].dropna()
        
        if len(values) < 2:
            return {
                'average': 0,
                'max': 0,
                'min': 0,
                'std': 0
            }
        
        _,_,slope = self.calculate_trendline(df)

        growth = slope * 365
        
        return {
            'average': float(values.mean()),
            'max': float(values.max()),
            'min': float(values.min()),
            'std': float(values.std()),
            'growth': growth,
            'count': len(values)
        }
    
    def get_seasonal_stats(self, df: pd.DataFrame, 
                          y_col: str = 'finishers') -> Dict[str, Dict]:
        """
        Calculate statistics grouped by season
        
        Args:
            df: DataFrame with data (should have 'season' column)
            y_col: Column name for y-axis values
            
        Returns:
            Dictionary with stats for each season
        """
        df = self.add_season_column(df)
        stats_dict = {}
        
        for season in SEASONS.keys():
            season_data = df[df['season'] == season][y_col].dropna()
            
            if len(season_data) > 0:
                stats_dict[season] = {
                    'average': float(season_data.mean()),
                    'max': float(season_data.max()),
                    'min': float(season_data.min()),
                    'std': float(season_data.std()),
                    'count': len(season_data)
                }
        
        return stats_dict
    
    def calculate_event_comparison_normalized(self, 
                                             events_data: Dict[str, pd.DataFrame]) -> Dict[str, np.ndarray]:
        """
        Normalize multiple events for comparison (percentage growth from start)
        
        Args:
            events_data: Dictionary with event names as keys and DataFrames as values
            
        Returns:
            Dictionary with normalized values
        """
        normalized = {}
        
        for event_name, df in events_data.items():
            values = df['finishers'].values.astype(float)
            start_value = values[0]
            
            if start_value > 0:
                normalized[event_name] = ((values / start_value - 1) * 100)
            else:
                normalized[event_name] = np.zeros_like(values)
        
        return normalized


if __name__ == "__main__":
    # Example usage
    engine = AnalysisEngine(rolling_window=4)
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=52, freq='W')
    finishers = np.random.randint(50, 200, 52)
    df = pd.DataFrame({'date': dates, 'finishers': finishers})
    
    # Add seasons
    df = engine.add_season_column(df)
    
    # Calculate stats
    stats = engine.get_growth_stats(df)
    print(f"Growth stats: {stats}")
    
    # Get seasonal stats
    seasonal = engine.get_seasonal_stats(df)
    print(f"Seasonal stats: {seasonal}")
