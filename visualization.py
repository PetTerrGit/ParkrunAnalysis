"""
Visualization Module
Creates plots with seasonal colors, trendlines, and rolling means
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
from analysis_engine import AnalysisEngine
from config import SEASON_COLORS, SEASONS


class Visualizer:
    """Creates visualizations for parkrun data"""
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid', 
                 fig_size: Tuple = (14, 8),
                 dpi: int = 100):
        """
        Initialize Visualizer
        
        Args:
            style: Matplotlib style
            fig_size: Figure size (width, height) in inches
            dpi: DPI for figure
        """
        try:
            plt.style.use(style)
        except OSError:
            # Fallback if specific style not available
            plt.style.use('default')
        
        self.fig_size = fig_size
        self.dpi = dpi
        self.engine = AnalysisEngine()
    
    def plot_single_event(self, df: pd.DataFrame, 
                         event_name: str,
                         output_dir: Optional[str] = None) -> Optional[str]:
        """
        Plot single event with finishers, trendline, and rolling mean
        
        Args:
            df: DataFrame with event data
            event_name: Name of the event
            output_dir: Directory to save plot (if None, displays plot)
            
        Returns:
            Path to saved figure, or None if displayed
        """
        # Prepare data
        df = self.engine.add_season_column(df)
        rolling_mean = self.engine.calculate_rolling_mean(df)
        x_trend, y_trend, _ = self.engine.calculate_trendline(df)
        stats = self.engine.get_growth_stats(df)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Plot finishers by season (color coded)
        for season in SEASONS.keys():
            season_mask = df['season'] == season
            season_data = df[season_mask]
            
            ax.scatter(season_data['date'], 
                      season_data['finishers'],
                      color=SEASON_COLORS[season],
                      label=season,
                      s=80,
                      alpha=0.7,
                      edgecolors='black',
                      linewidth=0.5)
        
        # Plot rolling mean
        ax.plot(df['date'], rolling_mean,
               color='#2F4F4F',
               linewidth=2.5,
               label=f'Rolling Mean ({self.engine.rolling_window}w)',
               alpha=0.8)
        
        # Plot trendline
        if x_trend is not None:
            trendline_dates = df['date'].iloc[x_trend]
            ax.plot(trendline_dates, y_trend,
                   color='red',
                   linestyle='--',
                   linewidth=2,
                   label='Trendline',
                   alpha=0.7)
        
        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylim(bottom=0)
        ax.set_ylabel('Number of Finishers', fontsize=12, fontweight='bold')
        ax.set_title(f'{event_name} - Growth Analysis',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Rotate x-axis labels
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Legend
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        
        # Add statistics box
        stats_text = (f"Avg Finishers: {stats['average']:.0f}\n"
                     f"Max: {stats['max']:.0f}\n"
                     f"Min: {stats['min']:.0f}\n"
                     f"Std Dev: {stats['std']:.1f}\n"
                     f"Growth per year: {stats['growth']:.0f} people")
        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
               fontsize=9)
        
        plt.tight_layout()
        
        # Save or display
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            safe_name = event_name.lower().replace(' ', '_').replace('/', '_')
            filepath = output_path / f"{safe_name}_analysis.png"
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.show()
            return None
    
    def plot_comparison(self, events_data: Dict[str, pd.DataFrame],
                       normalized: bool = False,
                       output_dir: Optional[str] = None) -> Optional[str]:
        """
        Plot comparison of multiple events (trendlines)
        
        Args:
            events_data: Dictionary with event names as keys and DataFrames as values
            normalized: If True, plot normalized growth; if False, absolute values (default)
            output_dir: Directory to save plot
            
        Returns:
            Path to saved figure, or None if displayed
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        
        # Color palette for events
        colors = plt.cm.tab10(np.linspace(0, 1, len(events_data)))
        
        if normalized:
            # Plot normalized trendlines
            normalized_data = self.engine.calculate_event_comparison_normalized(events_data)
            
            for (event_name, values), color in zip(normalized_data.items(), colors):
                x_numeric = np.arange(len(values))
                
                # Calculate trendline on normalized data
                from scipy import stats as sp_stats
                slope, intercept, _, _, _ = sp_stats.linregress(x_numeric, values)
                y_trend = slope * x_numeric + intercept
                
                ax.plot(x_numeric, y_trend,
                       color=color,
                       linewidth=2.5,
                       label=event_name,
                       marker='o',
                       markersize=4,
                       alpha=0.8)
            
            ax.set_ylabel('Growth from Start (%)', fontsize=12, fontweight='bold')
            title = 'Event Comparison - Normalized Growth'
        else:
            # Plot absolute values (same scale)
            for (event_name, df), color in zip(events_data.items(), colors):
                x_numeric = np.arange(len(df))
                y = df['finishers'].values.astype(float)
                
                # Calculate trendline on absolute data
                from scipy import stats as sp_stats
                slope, intercept, _, _, _ = sp_stats.linregress(x_numeric, y)
                y_trend = slope * x_numeric + intercept
                
                ax.plot(x_numeric, y_trend,
                       color=color,
                       linewidth=2.5,
                       label=event_name,
                       marker='o',
                       markersize=4,
                       alpha=0.8)
            
            ax.set_ylabel('Number of Finishers', fontsize=12, fontweight='bold')
            title = 'Event Comparison - Absolute Values (Same Scale)'
        
        # Formatting
        ax.set_xlabel('Events (chronological)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11, framealpha=0.95)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save or display
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            norm_suffix = "_normalized" if normalized else "_absolute"
            filepath = output_path / f"comparison{norm_suffix}.png"
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.show()
            return None
    
    def plot_seasonal_boxplot(self, df: pd.DataFrame,
                             event_name: str,
                             output_dir: Optional[str] = None) -> Optional[str]:
        """
        Create boxplot showing seasonal variation
        
        Args:
            df: DataFrame with event data
            event_name: Name of the event
            output_dir: Directory to save plot
            
        Returns:
            Path to saved figure, or None if displayed
        """
        df = self.engine.add_season_column(df)
        
        # Prepare data for boxplot
        season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
        season_data = [df[df['season'] == s]['finishers'].dropna() for s in season_order]
        colors = [SEASON_COLORS[s] for s in season_order]
        
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)
        
        bp = ax.boxplot(season_data,
                       labels=season_order,
                       patch_artist=True,
                       showmeans=True)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Number of Finishers', fontsize=12, fontweight='bold')
        ax.set_xlabel('Season', fontsize=12, fontweight='bold')
        ax.set_title(f'{event_name} - Seasonal Distribution', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            safe_name = event_name.lower().replace(' ', '_').replace('/', '_')
            filepath = output_path / f"{safe_name}_seasonal.png"
            plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.show()
            return None


if __name__ == "__main__":
    # Example usage
    from typing import Tuple
    
    visualizer = Visualizer()
    
    # Create sample data
    dates = pd.date_range('2022-01-01', periods=104, freq='W')
    finishers = 100 + np.cumsum(np.random.randn(104) * 3)
    df = pd.DataFrame({'date': dates, 'finishers': finishers})
    
    # Plot
    visualizer.plot_single_event(df, "Example Event", output_dir="./plots")
