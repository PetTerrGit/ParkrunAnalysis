# Quick Start Guide

## 5-Minute Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Create Sample Data (Optional)
```bash
python utils.py sample
```

This creates three sample parkrun events with realistic data.

### 3. Run Your First Analysis
```bash
# Single event
python main.py --event Windsor --show

# Compare events
python main.py --compare Windsor Battersea Wimbledon --show
```

## Common Workflows

### Workflow 1: Track a Single Event Over Time

```bash
# First time: Add event and scrape data
python main.py --event Windsor \
    --url https://uk.parkrun.com/windsor/results \
    --show

# Weekly: Re-analyze (updates automatically if >7 days)
python main.py --event Windsor --show

# Force update regardless of age
python main.py --event Windsor \
    --url https://uk.parkrun.com/windsor/results \
    --force --show
```

**Output:**
- Growth chart with seasonal colors
- Rolling mean trend
- Linear trendline
- Seasonal distribution boxplot
- Statistics summary

### Workflow 2: Compare Multiple Events

```bash
# Add initial data for events
python main.py --event Windsor --url https://uk.parkrun.com/windsor/results
python main.py --event Battersea --url https://uk.parkrun.com/battersea-park/results
python main.py --event Wimbledon --url https://uk.parkrun.com/wimbledon/results

# Compare all events (absolute scale - same numbers)
python main.py --compare Windsor Battersea Wimbledon --show

# Or use normalized (%) growth
python main.py --compare Windsor Battersea Wimbledon --normalized --show
```

**Output:**
- **Default:** Comparison chart with trendlines on absolute scale (number of finishers)
- **Normalized:** Chart showing % growth from each event's starting point

### Workflow 3: Monthly Report Generation

```bash
#!/bin/bash
# save as generate_report.sh

echo "Updating all events..."
python main.py --event Windsor --url https://uk.parkrun.com/windsor/results
python main.py --event Battersea --url https://uk.parkrun.com/battersea-park/results
python main.py --event Wimbledon --url https://uk.parkrun.com/wimbledon/results

echo "Generating individual analyses..."
python main.py --event Windsor
python main.py --event Battersea
python main.py --event Wimbledon

echo "Creating comparison..."
python main.py --compare Windsor Battersea Wimbledon --normalized

echo "Report saved to ./plots/"
```

Run with: `bash generate_report.sh`

## Adding Your Own Events

### Method 1: Automatic from Website

```bash
python main.py --event YourEventName \
    --url https://uk.parkrun.com/your-event-name/results
```

The scraper will automatically find the results table.

### Method 2: Manual CSV

Create `parkrun_data/your_event_name.csv`:

```csv
date,first_male,first_female,finishers,helpers
2023-01-01,John Smith,Jane Doe,127,15
2023-01-08,John Smith,Jane Doe,142,16
2023-01-15,John Smith,Jane Doe,138,16
```

Then analyze:
```bash
python main.py --event your_event_name --show
```

### Method 3: Programmatic

```python
from data_manager import DataManager
import pandas as pd

dm = DataManager()

# Create your data
df = pd.DataFrame({
    'date': ['2023-01-01', '2023-01-08'],
    'first_male': ['John', 'John'],
    'first_female': ['Jane', 'Jane'],
    'finishers': [127, 142],
    'helpers': [15, 16]
})

# Save
dm.save_csv('YourEvent', df)

# Analyze
# python main.py --event YourEvent --show
```

## Customization Examples

### Change Rolling Mean Window

Edit `analysis_engine.py`:
```python
# In ParkrunAnalyzer.__init__:
self.engine = AnalysisEngine(rolling_window=4)  # 4 weeks instead of 13
```

### Use Custom Season Definitions

Edit `config.py`:
```python
SEASONS = {
    'Q1': (1, 2, 3),
    'Q2': (4, 5, 6),
    'Q3': (7, 8, 9),
    'Q4': (10, 11, 12)
}
```

### Change Plot Colors

Edit `config.py`:
```python
SEASON_COLORS = {
    'Winter': '#1f77b4',    # Dark blue
    'Spring': '#2ca02c',    # Dark green
    'Summer': '#ff7f0e',    # Orange
    'Autumn': '#d62728'     # Red
}
```

### Larger/Higher Quality Plots

Edit `visualization.py`:
```python
# In Visualizer.__init__:
visualizer = Visualizer(
    fig_size=(16, 10),      # Larger
    dpi=300                 # Higher quality (slower)
)
```

## Troubleshooting

### Plot won't show
- Use `--show` flag explicitly
- Check you have display capability
- Try saving to file instead: remove `--show`

### Web scraping fails
- Check URL is correct
- Try visiting the URL in browser
- Website structure may have changed
- Check network/firewall

### "No such file or directory"
- Make sure you're in the project directory
- Run `python main.py --list` to check data

### Data looks wrong
- Check CSV format in `parkrun_data/` folder
- Run `python utils.py test` to verify setup

## Example Output

### Single Event Analysis
```
============================================================
SINGLE EVENT ANALYSIS: Windsor
============================================================

Loaded 104 records for Windsor

Calculating statistics...

Growth Statistics:
  Start Value: 127
  End Value: 142
  Change: +15 (+11.8%)
  Average: 134
  Range: 95 - 165
  Std Dev: 18.3

Seasonal Statistics:
  Winter: 128 avg (26 events)
  Spring: 142 avg (27 events)
  Summer: 138 avg (26 events)
  Autumn: 126 avg (25 events)

Generating visualizations...
Saved plot: ./plots/windsor_analysis.png
Saved seasonal plot: ./plots/windsor_seasonal.png

Analysis complete!
```

### Multi-Event Comparison
```
============================================================
MULTI-EVENT COMPARISON: Windsor, Battersea, Wimbledon
============================================================

Loaded 104 records for Windsor
Loaded 104 records for Battersea
Loaded 52 records for Wimbledon

Comparison Statistics:

  Windsor:
    Records: 104
    Average: 134
    Growth: +11.8%

  Battersea:
    Records: 104
    Average: 168
    Growth: +5.2%

  Wimbledon:
    Records: 52
    Average: 195
    Growth: -8.3%

Generating comparison visualization...
Saved comparison plot: ./plots/comparison_normalized.png

Comparison complete!
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Create sample data (or add your own)
3. ✅ Run first analysis
4. ✅ Explore customization options
5. ✅ Set up regular update schedule

## Advanced Usage

### Batch Processing Script

```python
# batch_analyze.py
from main import ParkrunAnalyzer

analyzer = ParkrunAnalyzer()

# Events to track
events = {
    'Windsor': 'https://uk.parkrun.com/windsor/results',
    'Battersea': 'https://uk.parkrun.com/battersea-park/results',
    'Wimbledon': 'https://uk.parkrun.com/wimbledon/results',
}

# Update and analyze each
for event_name, url in events.items():
    analyzer.analyze_single_event(event_name, url=url)

# Create comparison
analyzer.analyze_multiple_events(list(events.keys()))

print("All analyses complete!")
```

Run with: `python batch_analyze.py`

### Generate Reports

```python
# generate_report.py
from main import ParkrunAnalyzer
from datetime import datetime

analyzer = ParkrunAnalyzer(output_dir='./reports/latest')

events = ['Windsor', 'Battersea', 'Wimbledon']

for event in events:
    analyzer.analyze_single_event(event, show_plots=False)

analyzer.analyze_multiple_events(events, show_plots=False)

# Rename with timestamp
import shutil
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.move('./reports/latest', f'./reports/report_{timestamp}')

print(f"Report generated: ./reports/report_{timestamp}/")
```

## Tips & Tricks

- **Performance**: Store CSVs locally to avoid repeated scraping
- **Updates**: Data auto-updates if >7 days old (use `--force` to override)
- **Storage**: Each event takes minimal disk space (~1KB per month)
- **Plotting**: Use `--show` for interactive, omit for batch processing
- **Comparison**: Normalized view shows % growth (better for comparing different-sized events)
- **Testing**: Run `python utils.py test` to verify all components work

## Support Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point - run this with flags |
| `config.py` | All settings in one place |
| `data_manager.py` | CSV handling |
| `analysis_engine.py` | Statistics and trends |
| `visualization.py` | Plotting functions |
| `web_scraper.py` | Website data collection |
| `utils.py` | Testing and utilities |

---

**Happy analyzing! Questions? Check README.md for detailed documentation.**
