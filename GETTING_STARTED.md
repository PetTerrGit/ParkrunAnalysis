# 🚀 Getting Started - Copy & Paste Commands

## 1️⃣ Installation (2 minutes)

```bash
# Enter the project directory
cd parkrun_analysis

# Install dependencies
pip install -r requirements.txt
```

✅ Done! You now have all required packages.

---

## 2️⃣ Create Sample Data (30 seconds)

```bash
python utils.py sample
```

This creates three sample events with realistic parkrun data:
- Windsor
- Battersea  
- Wimbledon

You can now analyze without needing to scrape.

---

## 3️⃣ Run Your First Analysis (10 seconds)

### Option A: Display the plot
```bash
python main.py --event Windsor --show
```

### Option B: Save the plot to file
```bash
python main.py --event Windsor
# Plots saved to ./plots/
```

You should see:
- Finisher counts colored by season
- Rolling 13-week average line
- Linear trendline
- Seasonal statistics
- Boxplot showing seasonal distribution

---

## 4️⃣ Compare Multiple Events (10 seconds)

```bash
python main.py --compare Windsor Battersea Wimbledon --show
```

Shows how all three events' finisher numbers are trending on the same scale (absolute values).

To see normalized growth (%) instead:
```bash
python main.py --compare Windsor Battersea Wimbledon --normalized --show
```

---

## 5️⃣ List Your Events

```bash
python main.py --list
```

Shows all events you have data for.

---

## 6️⃣ Add Your Real Parkrun Event

### Method 1: Automatic from Website
```bash
python main.py --event YourEventName \
    --url https://uk.parkrun.com/your-event-name/results
```

The tool will:
1. Scrape the website
2. Create a CSV with historical data
3. Generate analysis plots

### Method 2: Manual CSV
Create `parkrun_data/your_event_name.csv`:
```csv
date,first_male,first_female,finishers,helpers
2023-01-01,John Smith,Jane Doe,127,15
2023-01-08,John Smith,Jane Doe,142,16
```

Then analyze:
```bash
python main.py --event your_event_name --show
```

See `example_data.csv` for full format.

---

## 7️⃣ Update Event Data Weekly

```bash
# Automatic (only updates if >7 days old)
python main.py --event Windsor --show

# Force update
python main.py --event Windsor \
    --url https://uk.parkrun.com/windsor/results \
    --force --show
```

---

## 8️⃣ All Commands Reference

```bash
# Single event
python main.py --event Windsor --show

# With web scraping
python main.py --event Windsor --url https://uk.parkrun.com/windsor/results

# Force update
python main.py --event Windsor --force

# Multiple events
python main.py --compare Windsor Battersea Wimbledon

# Normalized (%) comparison
python main.py --compare Windsor Battersea Wimbledon --normalized

# List all events
python main.py --list

# Custom output directory
python main.py --event Windsor --output-dir ./my_reports

# Custom data directory
python main.py --event Windsor --data-dir ./my_data

# Save instead of display
python main.py --event Windsor
# (plots saved to ./plots/)
```

---

## 9️⃣ Verify Everything Works

```bash
# Run test suite
python utils.py test
```

Output should show ✓ checks for all components.

---

## 🔧 Customization Cheat Sheet

### Change Rolling Mean Window
Edit `config.py`:
```python
ROLLING_WINDOW_WEEKS = 4  # was 13
```

### Use Different Seasons (Q1-Q4)
Edit `config.py`:
```python
SEASONS = {
    'Q1': (1, 2, 3),
    'Q2': (4, 5, 6),
    'Q3': (7, 8, 9),
    'Q4': (10, 11, 12)
}

SEASON_COLORS = {
    'Q1': '#1f77b4',
    'Q2': '#2ca02c',
    'Q3': '#ff7f0e',
    'Q4': '#d62728'
}
```

### Larger/Higher Quality Plots
Edit `visualization.py`:
```python
visualizer = Visualizer(fig_size=(16, 10), dpi=300)
```

---

## 📊 What You'll See

### Single Event Plot
```
┌─────────────────────────────────────────┐
│     Windsor - Growth Analysis           │
│     Change: +15 (+11.8%)                │
├─────────────────────────────────────────┤
│  ●  Winter (Blue)                       │
│  ●  Spring (Green)      [Rolling Mean]  │
│  ●  Summer (Orange)   [Trendline]       │
│  ●  Autumn (Red)                        │
│                                         │
│  250 ├─────────────────────────────     │
│      │    ● ● ● ● ●       ╱             │
│  200 │  ●  ●  ●   ● ●   ╱               │
│      │ ● ● ●    ● ●   ╱                 │
│  150 │●   ●    ●   ╱                    │
│      │       ●   ╱                      │
│  100 └─────────────────────────────     │
│      2023-01   2023-06   2023-12        │
│                                         │
│  Stats: Avg=134, Max=165, Min=95       │
└─────────────────────────────────────────┘
```

### Comparison Plot
```
┌─────────────────────────────────────────┐
│  Event Comparison - Normalized Growth   │
├─────────────────────────────────────────┤
│  +30% ├─────────────────────────────    │
│       │        ╱ Windsor                │
│  +20% │      ╱╱ Battersea               │
│       │    ╱╱     ╱╱╱ Wimbledon         │
│  +10% │  ╱╱      ╱╱                     │
│       │╱╱      ╱╱                       │
│    0% └─────────────────────────────    │
│      0   25    50    75    100          │
│              Events (time)              │
└─────────────────────────────────────────┘
```

---

## 🎯 Common Workflows

### Workflow 1: Track One Event Forever
```bash
# Week 1: Add event
python main.py --event Windsor \
    --url https://uk.parkrun.com/windsor/results

# Every week after: Just run this (auto-updates if needed)
python main.py --event Windsor --show
```

### Workflow 2: Monthly Reports
```bash
#!/bin/bash
# save as monthly_report.sh

python main.py --event Windsor
python main.py --event Battersea
python main.py --event Wimbledon
python main.py --compare Windsor Battersea Wimbledon

echo "✓ Reports saved to ./plots/"
```

Run with: `bash monthly_report.sh`

### Workflow 3: Quick Check
```bash
python main.py --event Windsor --show
```

Just see the plot, no prompts.

---

## ✅ Troubleshooting

### "No module named pandas"
```bash
pip install -r requirements.txt
```

### "Connection refused" (scraping fails)
- Check internet connection
- Check URL is correct
- Try visiting URL in browser first

### "No such file" error
```bash
# Make sure you're in the project directory
cd parkrun_analysis

# Try listing available events
python main.py --list
```

### Plot not showing
- Add `--show` flag: `python main.py --event Windsor --show`
- Or check `./plots/` directory for saved file

---

## 📚 Documentation

- **README.md** - Complete reference
- **QUICKSTART.md** - Common workflows
- **ARCHITECTURE.md** - System design
- **PROJECT_SUMMARY.md** - Overview
- **config.py** - All settings

---

## 🎓 Learning Progression

**Beginner:**
1. `pip install -r requirements.txt`
2. `python utils.py sample`
3. `python main.py --event Windsor --show`

**Intermediate:**
1. Add your own parkrun event
2. `python main.py --compare E1 E2 E3`
3. Edit config.py to customize

**Advanced:**
1. Schedule weekly updates
2. Generate monthly reports
3. Integrate with other tools
4. Modify analysis_engine.py for custom metrics

---

## 🚀 Next Steps

1. ✅ Run the installation commands above
2. ✅ Create sample data
3. ✅ View first plot
4. ✅ Read README.md for details
5. ✅ Add your real parkrun event
6. ✅ Customize settings (optional)

**You're ready to go!** 🏃‍♂️📊

---

## 💡 Pro Tips

- Data auto-updates if CSV is >7 days old
- Use `--normalized` to compare events of different sizes
- Check `./plots/` folder for all saved images
- Run `python utils.py test` to verify installation
- Edit `config.py` to customize everything
- See `example_data.csv` for data format

---

**Questions? Check the docs. Ready to analyze? Start with step 3! 🎉**
