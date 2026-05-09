"""
Configuration Module
Centralized settings for the parkrun analysis tool
"""

from typing import Dict, Tuple

# ==================== DATA MANAGEMENT ====================

# Number of days before CSV needs updating
UPDATE_THRESHOLD_DAYS = 7

# CSV column names (DO NOT CHANGE unless you restructure all CSVs)
CSV_COLUMNS = ['date', 'first_male', 'first_female', 'finishers', 'helpers']

# ==================== ANALYSIS ====================

# Rolling mean window size in weeks
ROLLING_WINDOW_WEEKS = 13

# ==================== SEASONS ====================

# Season definitions (meteorological)
SEASONS: Dict[str, Tuple[int, ...]] = {
    'Winter': (12, 1, 2),      # Dec, Jan, Feb
    'Spring': (3, 4, 5),        # Mar, Apr, May
    'Summer': (6, 7, 8),        # Jun, Jul, Aug
    'Autumn': (9, 10, 11)       # Sep, Oct, Nov
}

# Season colors (matplotlib compatible - hexadecimal)
SEASON_COLORS: Dict[str, str] = {
    'Winter': '#2E86AB',   # Blue
    'Spring': '#06A77D',   # Green
    'Summer': '#F18F01',   # Orange
    'Autumn': '#C73E1D'    # Red/Brown
}

# ==================== VISUALIZATION ====================

# Figure size (width, height) in inches
FIGURE_SIZE = (14, 8)

# DPI for saved plots
FIGURE_DPI = 100

# Matplotlib style
MATPLOTLIB_STYLE = 'seaborn-v0_8-darkgrid'

# Scatter plot marker size
SCATTER_SIZE = 80

# Line widths
ROLLING_MEAN_WIDTH = 2.5
TRENDLINE_WIDTH = 2.0
COMPARISON_WIDTH = 2.5

# ==================== WEB SCRAPING ====================

# Request timeout in seconds
SCRAPE_TIMEOUT = 10

# User agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Parkrun base URLs by country
PARKRUN_BASE_URLS: Dict[str, str] = {
    'uk': 'https://uk.parkrun.com/{event}/results',
    'us': 'https://parkrun.us/{event}/results',
    'au': 'https://parkrun.com.au/{event}/results',
    'ca': 'https://parkrun.ca/{event}/results',
    'de': 'https://parkrun.de/{event}/results',
    'at': 'https://www.parkrun.co.at/{event}}/results/eventhistory/',
}

# ==================== LOGGING ====================

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'INFO'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ==================== DIRECTORIES ====================

DEFAULT_DATA_DIR = './parkrun_data'
DEFAULT_OUTPUT_DIR = './plots'

# ==================== STATISTICS ====================

# Minimum data points required for analysis
MIN_DATA_POINTS = 2

# Display decimal places for statistics
STATS_DECIMAL_PLACES = 1


class Config:
    """Configuration manager - can be extended for file-based config"""
    
    def __init__(self):
        """Load configuration"""
        self.update_threshold_days = UPDATE_THRESHOLD_DAYS
        self.rolling_window_weeks = ROLLING_WINDOW_WEEKS
        self.seasons = SEASONS
        self.season_colors = SEASON_COLORS
        self.figure_size = FIGURE_SIZE
        self.figure_dpi = FIGURE_DPI
        self.scrape_timeout = SCRAPE_TIMEOUT
        self.parkrun_urls = PARKRUN_BASE_URLS
    
    def get_season_color(self, season: str) -> str:
        """Get color for a season"""
        return SEASON_COLORS.get(season, '#000000')
    
    def get_parkrun_url(self, event: str, country: str = 'uk') -> str:
        """Get full parkrun URL for an event"""
        base = PARKRUN_BASE_URLS.get(country, PARKRUN_BASE_URLS['uk'])
        return base.format(event=event)


# Global config instance
config = Config()


if __name__ == '__main__':
    # Test configuration
    print("Configuration loaded successfully!")
    print(f"Update threshold: {config.update_threshold_days} days")
    print(f"Rolling window: {config.rolling_window_weeks} weeks")
    print(f"Seasons: {list(config.seasons.keys())}")
    print(f"Season colors: {list(config.season_colors.keys())}")
