"""
Main Application
CLI interface for parkrun analysis - single event or comparison mode
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import logging

from data_manager import DataManager
from analysis_engine import AnalysisEngine
from visualization import Visualizer
from web_scraper import ParkrunScraper, ParkrunURLBuilder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParkrunAnalyzer:
    """Main application class coordinating all components"""
    
    def __init__(self, data_dir: str = './parkrun_data', 
                 output_dir: str = './plots'):
        """
        Initialize ParkrunAnalyzer
        
        Args:
            data_dir: Directory for storing CSV files
            output_dir: Directory for saving plots
        """
        self.data_manager = DataManager(data_dir)
        self.engine = AnalysisEngine()
        self.visualizer = Visualizer()
        self.scraper = ParkrunScraper()
        self.output_dir = output_dir
    
    def update_event_data(self, event_name: str, 
                         url: str,
                         force: bool = False) -> bool:
        """
        Update event data if needed
        
        Args:
            event_name: Name of the event
            url: URL of the results page
            force: Force update even if recent
            
        Returns:
            True if update was successful
        """
        # Check if update is needed
        if not force and not self.data_manager.needs_update(event_name):
            logger.info(f"{event_name} data is current (< 6 days old)")
            return True
        
        logger.info(f"Updating {event_name} data...")
        
        # Scrape new results
        results = self.scraper.scrape_event(url, event_name)
        
        if not results:
            logger.warning(f"Failed to scrape {event_name}")
            return False
        
        # Append to CSV
        try:
            self.data_manager.append_results(event_name, results)
            logger.info(f"Successfully updated {event_name} with {len(results)} records")
            return True
        except Exception as e:
            logger.error(f"Failed to save results for {event_name}: {e}")
            return False
    
    def analyze_single_event(self, event_name: str,
                            url: Optional[str] = None,
                            force_update: bool = False,
                            show_plots: bool = True) -> bool:
        """
        Analyze a single parkrun event
        
        Args:
            event_name: Name of the event
            url: URL of results page (if provided, will update data)
            force_update: Force update even if recent
            show_plots: Display plots (vs save only)
            
        Returns:
            True if analysis successful
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"SINGLE EVENT ANALYSIS: {event_name}")
        logger.info(f"{'='*60}\n")
        
        # Update data if URL provided
        if url:
            if not self.update_event_data(event_name, url, force_update):
                logger.warning(f"Skipping analysis due to update failure")
                return False
        
        # Load data
        try:
            df = self.data_manager.load_csv(event_name)
            logger.info(f"Loaded {len(df)} records for {event_name}")
        except FileNotFoundError:
            logger.error(f"No data found for {event_name}")
            return False
        
        # Validate data
        is_valid, msg = self.data_manager.validate_data(df)
        if not is_valid:
            logger.error(f"Data validation failed: {msg}")
            return False
        
        # Calculate statistics
        logger.info("\nCalculating statistics...")
        stats = self.engine.get_growth_stats(df)
        seasonal_stats = self.engine.get_seasonal_stats(df)
        
        # Log statistics
        logger.info(f"\nGrowth Statistics:")
        logger.info(f"  Average: {stats['average']:.0f}")
        logger.info(f"  Range: {stats['min']:.0f} - {stats['max']:.0f}")
        logger.info(f"  Std Dev: {stats['std']:.1f}")
        
        logger.info(f"\nSeasonal Statistics:")
        for season, season_stats in seasonal_stats.items():
            logger.info(f"  {season}: {season_stats['average']:.0f} avg " 
                       f"({season_stats['count']} events)")
        
        # Create visualizations
        logger.info("\nGenerating visualizations...")
        try:
            # Main plot
            fig_path = self.visualizer.plot_single_event(
                df, event_name, 
                output_dir=self.output_dir if not show_plots else None
            )
            if fig_path:
                logger.info(f"Saved plot: {fig_path}")
            
            # Seasonal boxplot
            box_path = self.visualizer.plot_seasonal_boxplot(
                df, event_name,
                output_dir=self.output_dir if not show_plots else None
            )
            if box_path:
                logger.info(f"Saved seasonal plot: {box_path}")
        
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            return False
        
        logger.info("\nAnalysis complete!\n")
        return True
    
    def analyze_multiple_events(self, event_names: List[str],
                               urls: Optional[Dict[str, str]] = None,
                               force_update: bool = False,
                               normalized: bool = False,
                               show_plots: bool = True) -> bool:
        """
        Compare multiple parkrun events
        
        Args:
            event_names: List of event names to compare
            urls: Optional dictionary of event names to URLs for updating
            force_update: Force update even if recent
            normalized: Plot normalized growth (%) or absolute values (default)
            show_plots: Display plots (vs save only)
            
        Returns:
            True if analysis successful
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"MULTI-EVENT COMPARISON: {', '.join(event_names)}")
        logger.info(f"{'='*60}\n")
        
        # Update data if URLs provided
        if urls:
            for event_name, url in urls.items():
                self.update_event_data(event_name, url, force_update)
        
        # Load all event data
        events_data = {}
        for event_name in event_names:
            try:
                df = self.data_manager.load_csv(event_name)
                is_valid, msg = self.data_manager.validate_data(df)
                
                if is_valid:
                    events_data[event_name] = df
                    logger.info(f"Loaded {len(df)} records for {event_name}")
                else:
                    logger.warning(f"Data invalid for {event_name}: {msg}")
            
            except FileNotFoundError:
                logger.warning(f"No data found for {event_name}")
        
        if not events_data:
            logger.error("No valid data loaded for any events")
            return False
        
        # Calculate and display comparison statistics
        logger.info("\nComparison Statistics:")
        for event_name, df in events_data.items():
            stats = self.engine.get_growth_stats(df)
            logger.info(f"\n  {event_name}:")
            logger.info(f"    Records: {stats['count']}")
            logger.info(f"    Average: {stats['average']:.0f}")
        
        # Create comparison visualization
        logger.info("\nGenerating comparison visualization...")
        try:
            fig_path = self.visualizer.plot_comparison(
                events_data,
                normalized=normalized,
                output_dir=self.output_dir if not show_plots else None
            )
            if fig_path:
                logger.info(f"Saved comparison plot: {fig_path}")
        
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            return False
        
        logger.info("\nComparison complete!\n")
        return True
    
    def list_events(self) -> None:
        """List all available events"""
        events = self.data_manager.get_event_list()
        
        if not events:
            logger.info("No events available. Add data to get started.")
            return
        
        logger.info(f"\nAvailable Events ({len(events)}):")
        for event in sorted(events):
            try:
                df = self.data_manager.load_csv(event)
                logger.info(f"  - {event}: {len(df)} records "
                           f"({df['date'].min().date()} to {df['date'].max().date()})")
            except:
                logger.info(f"  - {event}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Parkrun Results Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Single event analysis
  python main.py --event Windsor --url https://uk.parkrun.com/windsor/results
  
  # Compare multiple events
  python main.py --compare Windsor Battersea --normalized
  
  # List all events
  python main.py --list
  
  # Force update and analyze
  python main.py --event Windsor --force
        '''
    )
    
    # Single event analysis
    parser.add_argument('--event', type=str,
                       help='Event name for single event analysis')
    parser.add_argument('--url', type=str,
                       help='URL of results page (for updating data)')
    
    # Multi-event comparison
    parser.add_argument('--compare', nargs='+',
                       help='List of events to compare')
    parser.add_argument('--normalized', action='store_true',
                       help='Show normalized growth (%%) instead of absolute values')
    
    # Data management
    parser.add_argument('--force', action='store_true',
                       help='Force update even if data is recent')
    parser.add_argument('--list', action='store_true',
                       help='List all available events')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='./plots',
                       help='Directory for saving plots (default: ./plots)')
    parser.add_argument('--data-dir', type=str, default='./parkrun_data',
                       help='Directory for storing CSVs (default: ./parkrun_data)')
    parser.add_argument('--show', action='store_true',
                       help='Display plots interactively (vs saving only)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ParkrunAnalyzer(data_dir=args.data_dir, output_dir=args.output_dir)
    
    try:
        # Handle different commands
        if args.list:
            analyzer.list_events()
        
        elif args.event:
            success = analyzer.analyze_single_event(
                args.event,
                url=args.url,
                force_update=args.force,
                show_plots=args.show
            )
            sys.exit(0 if success else 1)
        
        elif args.compare:
            success = analyzer.analyze_multiple_events(
                args.compare,
                normalized=args.normalized,
                force_update=args.force,
                show_plots=args.show
            )
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
