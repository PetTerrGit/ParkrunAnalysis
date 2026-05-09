# Parkrun Analysis Tool

A comprehensive Python tool for analyzing parkrun event results over time, tracking growth trends, and comparing multiple events.

## Features

- 📊 **Single Event Analysis**: Track growth over time with trendlines and rolling means
- 🌍 **Multi-Event Comparison**: Compare growth patterns across different events
- 🎨 **Seasonal Color Coding**: Visualize results with meteorological season colors
- 📈 **Statistical Analysis**: Calculate growth metrics, rolling averages, and trendlines
- 🔄 **Automatic Data Management**: Tracks when CSVs need updating (7+ days old)
- 🌐 **Web Scraping**: Automatically fetch latest results from parkrun webpages
- 💾 **CSV Storage**: Store historical data locally for trend analysis

## Installation

### 1. Clone/Setup Project
```bash
cd parkrun_analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas numpy matplotlib scipy requests beautifulsoup4
```

## Project Structure

```
parkrun_analysis/
├── main.py                 # CLI application entry point
├── data_manager.py         # CSV file handling and data validation
├── analysis_engine.py      # Growth calculations and statistics
├── visualization.py        # Plotting functions
├── web_scraper.py         # Web scraping for parkrun results
├── requirements.txt        # Python dependencies
└── parkrun_data/          # (Created automatically) CSV data files
└── plots/                 # (Created automatically) Output plots
```

## Quick Start

### 1. Analyze a Single Event

**With automatic data scraping:**
```bash
python main.py --event Windsor --url https://uk.parkrun.com/windsor/results
```

**Without scraping (use existing data):**
```bash
python main.py --event Windsor
```

**Display plots interactively:**
```bash
python main.py --event Windsor --show
```

### 2. Compare Multiple Events

```bash
python main.py --compare Windsor Battersea Wimbledon
```

**Show normalized growth (%):**
```bash
python main.py --compare Windsor Battersea Wimbledon --normalized
```

### 3. List Available Events

```bash
python main.py --list
```

## Usage Examples

### Example 1: Single Event with Web Scraping
```bash
python main.py --event Windsor \
    --url https://uk.parkrun.com/windsor/results \
    --output-dir ./plots
```

This will:
1. Check if Windsor CSV is older than 7 days
2. If outdated, scrape the website for latest results
3. Append new results to CSV
4. Generate growth analysis plot with:
   - Finisher counts colored by season
   - Rolling 13-week mean
   - Linear trendline
   - Seasonal distribution boxplot

### Example 2: Force Update and Compare
```bash
python main.py --compare Windsor Battersea Wimbledon \
    --force \
    --normalized \
    --show
```

This will:
1. Force update all three events from parkrun website
2. Create normalized growth comparison (showing % growth from start)
3. Display plot interactively

### Example 3: Batch Processing
```bash
# Create a script to analyze multiple events
python main.py --event Windsor
python main.py --event Battersea
python main.py --event Wimbledon
python main.py --compare Windsor Battersea Wimbledon
```

## Data Format

CSV files are stored in `parkrun_data/` with the following structure:

```csv
date,first_male,first_female,finishers,helpers,last_updated
2023-01-01,John Smith,Jane Doe,127,15,2024-03-29 12:00:00
2023-01-08,John Smith,Jane Doe,142,16,2024-03-29 12:00:00
2023-01-15,John Smith,Jane Doe,138,16,2024-03-29 12:00:00
```

- **date**: Event date (YYYY-MM-DD)
- **first_male**: Time of first male finisher (optional)
- **first_female**: Time of first female finisher (optional)
- **finishers**: Total number of finishers
- **helpers**: Number of volunteers (optional)
- **last_updated**: Timestamp of when data was last updated (auto-added on scrape)

## Visualization Details

### Single Event Plot
Shows:
- 🟠 Finisher points colored by season (Winter/Spring/Summer/Autumn)
- 📈 Rolling mean (default: 13-week window)
- 📊 Linear trendline
- 📋 Growth statistics box with key metrics

### Seasonal Distribution Plot
Boxplot showing:
- Median finishers per season
- Seasonal variation
- Outliers and quartiles

### Comparison Plot
When comparing multiple events:
- **Default (Absolute):** Trendlines for each event on the same scale (absolute finisher numbers)
- **Normalized:** Shows % growth from starting point (use `--normalized` flag)
- Event names in legend
- Easy visual comparison of growth patterns

## Configuration

### Customize Rolling Mean Window
Edit `analysis_engine.py`:
```python
# In __init__ method, change default:
def __init__(self, rolling_window: int = 4):  # Change from 13 to 4
```

### Customize Seasons
Edit `analysis_engine.py`:
```python
SEASONS = {
    'Winter': (12, 1, 2),
    'Spring': (3, 4, 5),
    'Summer': (6, 7, 8),
    'Autumn': (9, 10, 11)
}
```

### Change Season Colors
Edit `analysis_engine.py`:
```python
SEASON_COLORS = {
    'Winter': '#2E86AB',   # Blue
    'Spring': '#06A77D',   # Green
    'Summer': '#F18F01',   # Orange
    'Autumn': '#C73E1D'    # Red
}
```

## Data Management

### Automatic Update Check
- CSVs are checked every time you run analysis
- If a `last_updated` timestamp in the CSV is older than 7 days AND a URL is provided, it updates automatically
- The tool automatically adds/updates the `last_updated` timestamp when results are scraped
- Use `--force` flag to always update regardless of age
- Falls back to file modification time if timestamp column is missing

### Manual Data Entry
To manually create/edit a CSV:

1. Create `parkrun_data/event_name.csv`
2. Add header and data:
```csv
date,first_male,first_female,finishers,helpers
2023-01-01,John Smith,Jane Doe,127,15
```

### Web Scraping Notes

The scraper is designed for standard parkrun website structures but may need adjustment for:
- Non-UK parkrun sites (different URL pattern)
- Custom event pages
- Website structure changes

To customize scraping, edit `web_scraper.py`:
```python
def parse_results_table(self, soup: BeautifulSoup):
    # Adjust CSS selectors here if parkrun changes layout
    table = soup.find('table', {'class': ['sortable', 'results', 'table']})
```

## Command Line Options

```
--event NAME              Event name for analysis
--url URL                 URL of results page (triggers web scraping)
--compare E1 E2 E3        Compare multiple events
--normalized              Show normalized growth (%) instead of absolute
--force                   Force update even if recent
--list                    List all available events
--output-dir PATH         Directory for saving plots (default: ./plots)
--data-dir PATH           Directory for CSVs (default: ./parkrun_data)
--show                    Display plots interactively
```

## Statistics Calculated

### Growth Statistics
- **Start Value**: Finishers at first event
- **End Value**: Finishers at latest event
- **Absolute Change**: Difference in finishers
- **Percent Change**: % growth from start
- **Average**: Mean finishers across all events
- **Max/Min**: Highest and lowest attendance
- **Std Dev**: Standard deviation (stability measure)

### Seasonal Statistics
For each season:
- Average finishers
- Max/min values
- Event count
- Standard deviation

## Troubleshooting

### "No CSV found for event"
- Ensure event data has been loaded
- Check that `parkrun_data/` directory contains CSV
- Try with `--url` to scrape fresh data

### "Could not find results table"
- Website structure may have changed
- Check if URL is correct
- Review `web_scraper.py` selectors

### Empty plots
- Check data has finisher values (not NaN)
- Ensure at least 2 data points exist
- Run `--list` to verify data loaded

### Matplotlib style errors
- Visualizer falls back to default style automatically
- If issues persist, remove style specification

## Example Data Generation

To test with sample data:

```python
import pandas as pd
from pathlib import Path
import numpy as np

# Create sample data
dates = pd.date_range('2022-01-01', periods=52, freq='W')
finishers = 100 + np.cumsum(np.random.randn(52) * 3)

df = pd.DataFrame({
    'date': dates,
    'first_male': 'John Smith',
    'first_female': 'Jane Doe',
    'finishers': finishers.astype(int),
    'helpers': np.random.randint(10, 20, 52)
})

# Save
Path('parkrun_data').mkdir(exist_ok=True)
df.to_csv('parkrun_data/test_event.csv', index=False)

# Analyze
# python main.py --event test_event --show
```

## Performance Notes

- Typical analysis: < 1 second
- Web scraping: 5-10 seconds depending on internet
- Plotting: 1-2 seconds
- Memory: ~50MB for 100+ events with years of data

## Future Enhancements

Possible improvements:
- [ ] Weather data integration
- [ ] Holiday/event detection
- [ ] Predictive forecasting
- [ ] Interactive web dashboard
- [ ] Export to PDF reports
- [ ] Email notifications for outliers
- [ ] Multi-country parkrun support
- [ ] Time series decomposition (trend, seasonal, residual)

## Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Data handling and CSV operations |
| `numpy` | Numerical calculations |
| `matplotlib` | Plot generation |
| `scipy` | Statistical functions (linregress) |
| `requests` | Web requests for scraping |
| `beautifulsoup4` | HTML parsing |

## License

This project is provided as-is for personal use.

## Support

For issues or improvements:
1. Check the Troubleshooting section
2. Review the example commands
3. Check your data format matches the CSV structure

---

**Happy analyzing! 🏃‍♂️📊**
