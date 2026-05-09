"""
Utility Script
Helper functions for testing, sample data generation, and development
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from data_manager import DataManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Generate sample parkrun data for testing"""
    
    @staticmethod
    def generate_event_data(event_name: str, 
                           num_weeks: int = 104,
                           base_finishers: int = 100,
                           trend: float = 0.3,
                           noise: float = 15,
                           seasonal_variation: bool = True) -> pd.DataFrame:
        """
        Generate realistic sample data
        
        Args:
            event_name: Name of the event
            num_weeks: Number of weeks of data
            base_finishers: Starting number of finishers
            trend: Weekly growth rate (0.3 = 0.3% per week)
            noise: Standard deviation of random noise
            seasonal_variation: Add seasonal patterns
            
        Returns:
            DataFrame with sample data
        """
        # Create dates (weekly)
        start_date = datetime.now() - timedelta(weeks=num_weeks)
        dates = pd.date_range(start_date, periods=num_weeks, freq='W')
        
        # Generate finisher data with trend
        trend_component = base_finishers * (1 + trend/100) ** np.arange(num_weeks)
        
        # Add noise
        noise_component = np.random.normal(0, noise, num_weeks)
        
        # Add seasonal component (higher in summer, lower in winter)
        month_of_year = np.array([d.month for d in dates])
        seasonal_component = 20 * np.sin(2 * np.pi * month_of_year / 12)
        
        if seasonal_variation:
            finishers = trend_component + seasonal_component + noise_component
        else:
            finishers = trend_component + noise_component
        
        # Ensure finishers are positive
        finishers = np.maximum(finishers, 20).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'first_male': 'John Smith',
            'first_female': 'Jane Doe',
            'finishers': finishers,
            'helpers': np.random.randint(10, 25, num_weeks)
        })
        
        return df
    
    @staticmethod
    def generate_multiple_events(event_configs: Dict[str, Dict],
                                data_dir: str = './parkrun_data') -> None:
        """
        Generate multiple sample events
        
        Args:
            event_configs: Dict with event names as keys and config dicts as values
                          Config dict keys: num_weeks, base_finishers, trend, noise
            data_dir: Directory to save CSVs
        """
        dm = DataManager(data_dir)
        
        for event_name, config in event_configs.items():
            logger.info(f"Generating sample data for {event_name}...")
            
            df = TestDataGenerator.generate_event_data(
                event_name,
                num_weeks=config.get('num_weeks', 104),
                base_finishers=config.get('base_finishers', 100),
                trend=config.get('trend', 0.3),
                noise=config.get('noise', 15)
            )
            
            dm.save_csv(event_name, df)
            logger.info(f"  Created {len(df)} weeks of data")


class QuickTest:
    """Quick test routines"""
    
    @staticmethod
    def test_data_manager() -> None:
        """Test DataManager functionality"""
        logger.info("\n=== Testing DataManager ===")
        
        dm = DataManager('./test_data')
        
        # Generate test data
        dates = pd.date_range('2023-01-01', periods=52, freq='W')
        test_df = pd.DataFrame({
            'date': dates,
            'first_male': 'John',
            'first_female': 'Jane',
            'finishers': np.random.randint(80, 150, 52),
            'helpers': np.random.randint(10, 20, 52)
        })
        
        # Test save
        dm.save_csv('TestEvent', test_df)
        logger.info("✓ Save CSV successful")
        
        # Test load
        loaded = dm.load_csv('TestEvent')
        logger.info(f"✓ Load CSV successful ({len(loaded)} rows)")
        
        # Test validation
        valid, msg = dm.validate_data(loaded)
        logger.info(f"✓ Validation: {msg}")
        
        # Test exists
        exists = dm.csv_exists('TestEvent')
        logger.info(f"✓ CSV exists check: {exists}")
        
        # Cleanup
        import shutil
        shutil.rmtree('./test_data')
        logger.info("✓ Test data cleaned up")
    
    @staticmethod
    def test_analysis_engine() -> None:
        """Test AnalysisEngine functionality"""
        logger.info("\n=== Testing AnalysisEngine ===")
        
        from analysis_engine import AnalysisEngine
        
        engine = AnalysisEngine(rolling_window=4)
        
        # Create test data
        dates = pd.date_range('2023-01-01', periods=52, freq='W')
        finishers = 100 + np.cumsum(np.random.randn(52) * 2)
        df = pd.DataFrame({
            'date': dates,
            'finishers': finishers.astype(int)
        })
        
        # Test season detection
        df_with_season = engine.add_season_column(df)
        logger.info(f"✓ Season detection: {df_with_season['season'].unique()}")
        
        # Test statistics
        stats = engine.get_growth_stats(df)
        logger.info(f"✓ Growth stats: {stats['percent_change']:.1f}% change")
        
        # Test seasonal stats
        seasonal = engine.get_seasonal_stats(df)
        logger.info(f"✓ Seasonal stats: {list(seasonal.keys())}")
        
        # Test rolling mean
        rolling = engine.calculate_rolling_mean(df)
        logger.info(f"✓ Rolling mean calculated: {len(rolling)} values")
        
        # Test trendline
        x, y = engine.calculate_trendline(df)
        logger.info(f"✓ Trendline calculated: {len(x)} points")
    
    @staticmethod
    def test_visualizer() -> None:
        """Test Visualizer functionality"""
        logger.info("\n=== Testing Visualizer ===")
        
        from visualization import Visualizer
        
        visualizer = Visualizer()
        
        # Create test data
        dates = pd.date_range('2023-01-01', periods=52, freq='W')
        finishers = 100 + np.cumsum(np.random.randn(52) * 2)
        df = pd.DataFrame({
            'date': dates,
            'finishers': finishers.astype(int)
        })
        
        # Test plot creation (without saving)
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            visualizer.plot_single_event(df, 'TestEvent')
            logger.info("✓ Single event plot created successfully")
            
            visualizer.plot_seasonal_boxplot(df, 'TestEvent')
            logger.info("✓ Seasonal boxplot created successfully")
            
        except Exception as e:
            logger.error(f"✗ Visualization test failed: {e}")
    
    @staticmethod
    def run_all_tests() -> None:
        """Run all quick tests"""
        logger.info("\n" + "="*50)
        logger.info("RUNNING QUICK TESTS")
        logger.info("="*50)
        
        try:
            QuickTest.test_data_manager()
            QuickTest.test_analysis_engine()
            QuickTest.test_visualizer()
            
            logger.info("\n" + "="*50)
            logger.info("✓ ALL TESTS PASSED")
            logger.info("="*50)
        
        except Exception as e:
            logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)


def create_sample_project() -> None:
    """Create a sample project with test data"""
    logger.info("Creating sample project...")
    
    sample_events = {
        'Windsor': {
            'num_weeks': 104,
            'base_finishers': 120,
            'trend': 0.5,
            'noise': 12
        },
        'Battersea': {
            'num_weeks': 104,
            'base_finishers': 150,
            'trend': 0.2,
            'noise': 18
        },
        'Wimbledon': {
            'num_weeks': 52,
            'base_finishers': 200,
            'trend': -0.1,
            'noise': 25
        }
    }
    
    TestDataGenerator.generate_multiple_events(sample_events)
    logger.info("\nSample project created! Try:")
    logger.info("  python main.py --event Windsor --show")
    logger.info("  python main.py --compare Windsor Battersea Wimbledon --show")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            QuickTest.run_all_tests()
        elif command == 'sample':
            create_sample_project()
        else:
            print("Usage:")
            print("  python utils.py test     - Run quick tests")
            print("  python utils.py sample   - Create sample project")
    else:
        print("Usage:")
        print("  python utils.py test     - Run quick tests")
        print("  python utils.py sample   - Create sample project")
