# Project Architecture & Structure

## Directory Layout

```
parkrun_analysis/
│
├── 📄 main.py                  ← START HERE: CLI application entry point
├── 📄 config.py                ← Centralized configuration
├── 📄 requirements.txt          ← Python dependencies
│
├── 📁 Core Modules
│   ├── 📄 data_manager.py      ← CSV handling, data validation
│   ├── 📄 analysis_engine.py   ← Statistics, growth calculations
│   ├── 📄 visualization.py     ← Plotting (single & comparison)
│   └── 📄 web_scraper.py       ← Web scraping for parkrun results
│
├── 📁 Utilities & Testing
│   └── 📄 utils.py             ← Testing, sample data generation
│
├── 📁 Documentation
│   ├── 📄 README.md            ← Full documentation
│   ├── 📄 QUICKSTART.md        ← Quick start guide
│   └── 📄 .gitignore           ← Git ignore rules
│
├── 📁 parkrun_data/            ← CSV files (auto-created)
│   ├── windsor.csv
│   ├── battersea.csv
│   └── wimbledon.csv
│
└── 📁 plots/                   ← Output plots (auto-created)
    ├── windsor_analysis.png
    ├── windsor_seasonal.png
    ├── comparison_normalized.png
    └── ...
```

## Module Dependency Graph

```
                          main.py (CLI)
                             │
                ┌────────────┼────────────┐
                │            │            │
           config.py    data_manager    analysis_engine
                │            │            │
                │            │         ┌──┴──┐
                │            │         │     │
            web_scraper  pandas    scipy  numpy
                
                       visualization
                            │
                    ┌────────┴────────┐
                    │                 │
              matplotlib         analysis_engine
                    │                 │
                  numpy          pyplot, dates
```

## Component Descriptions

### 1. **main.py** - Application Entry Point
**Responsibility:** CLI interface and workflow orchestration

**Key Classes:**
- `ParkrunAnalyzer` - Main controller

**Key Methods:**
- `analyze_single_event()` - Single event analysis
- `analyze_multiple_events()` - Multi-event comparison
- `update_event_data()` - Fetch and update data
- `list_events()` - Show available events

**Dependencies:** All other modules

**Run with:** `python main.py [options]`

---

### 2. **data_manager.py** - Data Persistence
**Responsibility:** CSV file operations and data validation

**Key Classes:**
- `DataManager` - Handles CSV I/O

**Key Methods:**
- `load_csv()` - Load event data
- `save_csv()` - Save data to file
- `append_results()` - Add new results
- `needs_update()` - Check age of CSV
- `validate_data()` - Verify data integrity
- `csv_exists()` - Check if file exists

**Dependencies:** pandas, pathlib, datetime

**Data Flow:**
```
CSV File → load_csv() → DataFrame
DataFrame → append_results() → Updated DataFrame → save_csv() → CSV File
```

---

### 3. **analysis_engine.py** - Statistical Analysis
**Responsibility:** Calculations for growth, trends, and statistics

**Key Classes:**
- `AnalysisEngine` - Statistical computations

**Key Methods:**
- `add_season_column()` - Assign seasons to dates
- `calculate_trendline()` - Linear regression
- `calculate_rolling_mean()` - Moving average
- `get_growth_stats()` - Summary statistics
- `get_seasonal_stats()` - Season-grouped statistics
- `get_season()` - Determine season for date

**Dependencies:** pandas, numpy, scipy.stats

**Calculations:**
```
DataFrame → Trendline (linregress) + Rolling Mean + Growth Stats
```

---

### 4. **visualization.py** - Plotting
**Responsibility:** Create publication-quality plots

**Key Classes:**
- `Visualizer` - Plot generation

**Key Methods:**
- `plot_single_event()` - Main growth chart
- `plot_seasonal_boxplot()` - Seasonal distribution
- `plot_comparison()` - Multi-event comparison

**Plot Features:**
- Seasonal color coding
- Trendlines
- Rolling means
- Statistics boxes
- Interactive legends

**Dependencies:** matplotlib, pandas, numpy, analysis_engine

---

### 5. **web_scraper.py** - Data Collection
**Responsibility:** Fetch and parse parkrun webpages

**Key Classes:**
- `ParkrunScraper` - Web scraping
- `ParkrunURLBuilder` - URL construction

**Key Methods:**
- `scrape_event()` - Get results for one event
- `scrape_multiple_events()` - Batch scraping
- `parse_results_table()` - HTML parsing
- `fetch_page()` - HTTP requests

**Dependencies:** requests, BeautifulSoup, pandas

---

### 6. **config.py** - Configuration
**Responsibility:** Centralized settings

**Contains:**
- Season definitions
- Color schemes
- Window sizes
- Update thresholds
- URLs and timeouts

**Usage:**
```python
from config import config
color = config.get_season_color('Winter')
```

---

### 7. **utils.py** - Testing & Utilities
**Responsibility:** Development tools and testing

**Key Classes:**
- `TestDataGenerator` - Create sample data
- `QuickTest` - Test all components

**Key Methods:**
- `generate_event_data()` - Realistic sample data
- `create_sample_project()` - Setup demo
- `run_all_tests()` - Verify installation

---

## Data Flow Diagrams

### Single Event Analysis Flow
```
Input: Event Name + Optional URL
    │
    ├─→ Check if update needed (>7 days old?)
    │
    ├─→ If URL provided: Scrape website
    │       └─→ parse_results_table()
    │       └─→ append_results()
    │
    ├─→ Load CSV from disk
    │
    ├─→ Validate data
    │
    ├─→ Calculate statistics
    │       ├─→ add_season_column()
    │       ├─→ get_growth_stats()
    │       ├─→ get_seasonal_stats()
    │       ├─→ calculate_trendline()
    │       └─→ calculate_rolling_mean()
    │
    ├─→ Create visualizations
    │       ├─→ plot_single_event()
    │       └─→ plot_seasonal_boxplot()
    │
    └─→ Output: Plots + Statistics
```

### Multi-Event Comparison Flow
```
Input: List of Event Names + Normalized Flag
    │
    ├─→ For each event:
    │       ├─→ Load CSV
    │       ├─→ Validate
    │       └─→ Calculate stats
    │
    ├─→ If normalized:
    │       └─→ calculate_event_comparison_normalized()
    │           (Convert to % growth from start)
    │
    ├─→ Create comparison plot
    │       └─→ plot_comparison()
    │
    └─→ Output: Comparison chart + Statistics
```

## Class Hierarchies

### DataManager
```
DataManager
├── get_csv_path()
├── csv_exists()
├── needs_update()
├── load_csv()
├── save_csv()
├── append_results()
├── get_event_list()
└── validate_data()
```

### AnalysisEngine
```
AnalysisEngine
├── SEASONS (constant)
├── SEASON_COLORS (constant)
├── get_season()
├── add_season_column()
├── calculate_trendline()
├── calculate_rolling_mean()
├── get_growth_stats()
├── get_seasonal_stats()
└── calculate_event_comparison_normalized()
```

### Visualizer
```
Visualizer
├── __init__()
├── plot_single_event()
├── plot_comparison()
└── plot_seasonal_boxplot()
```

## Configuration Hierarchy

```
config.py (Global Constants)
    │
    ├── UPDATE_THRESHOLD_DAYS = 7
    ├── ROLLING_WINDOW_WEEKS = 13
    ├── SEASONS = {...}
    ├── SEASON_COLORS = {...}
    ├── FIGURE_SIZE = (14, 8)
    ├── SCRAPE_TIMEOUT = 10
    └── PARKRUN_BASE_URLS = {...}
    
    Config Class (Wrapper for access)
        └── Methods for getting values
```

## Error Handling Flow

```
Input
    │
    ├─→ FileNotFoundError
    │       └─→ Log error, return False
    │
    ├─→ ValidationError
    │       └─→ Log error, return False
    │
    ├─→ ScrapingError
    │       └─→ Log warning, use existing data
    │
    ├─→ PlottingError
    │       └─→ Log error, return False
    │
    └─→ KeyboardInterrupt
            └─→ Graceful exit with message
```

## Data Structures

### CSV Format
```
date (datetime) | first_male (str) | first_female (str) | finishers (int) | helpers (int)
2023-01-01      | John Smith       | Jane Doe            | 127              | 15
```

### DataFrame Columns
```
date (datetime64)
first_male (object)
first_female (object)
finishers (int64)
helpers (int64)
season (object) - Added by analysis_engine
```

### Statistics Dictionary
```
{
    'start_value': float,
    'end_value': float,
    'absolute_change': float,
    'percent_change': float,
    'average': float,
    'max': float,
    'min': float,
    'std': float,
    'count': int
}
```

## Extensibility Points

### Add New Metrics
Edit `analysis_engine.py`:
```python
def calculate_custom_metric(self, df, ...):
    # Your calculation here
    return results
```

### Add New Plot Types
Edit `visualization.py`:
```python
def plot_custom_visualization(self, df, ...):
    # Your plotting code here
    return filepath
```

### Change Scraping Logic
Edit `web_scraper.py`:
```python
def parse_results_table(self, soup):
    # Adjust CSS selectors for new site structure
```

### Add New Data Sources
Create new module following DataManager pattern:
```python
class NewDataSource:
    def load_data(self, ...):
        # Load from your source
```

---

This architecture is designed for:
- ✅ **Modularity** - Each component has single responsibility
- ✅ **Testability** - Components can be tested independently
- ✅ **Extensibility** - Easy to add features
- ✅ **Maintainability** - Clear separation of concerns
- ✅ **Reusability** - Components can be used programmatically
