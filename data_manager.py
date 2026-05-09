"""
Data Management Module
Handles CSV operations, update checks, and data validation
"""

import os
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


class DataManager:
    """Manages parkrun historical data in CSV format"""
    
    # CSV column names
    COLUMNS = ['date', 'first_male', 'first_female', 'finishers', 'helpers', 'last_updated']
    
    def __init__(self, data_dir: str = './parkrun_data'):
        """
        Initialize DataManager
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def get_csv_path(self, event_name: str) -> Path:
        """Get the CSV file path for an event"""
        # Sanitize event name for filename
        safe_name = event_name.lower().replace(' ', '_').replace('/', '_')
        return self.data_dir / f"{safe_name}.csv"
    
    def csv_exists(self, event_name: str) -> bool:
        """Check if CSV file exists for an event"""
        return self.get_csv_path(event_name).exists()
    
    def needs_update(self, event_name: str, days_old: int = 7) -> bool:
        """
        Check if CSV needs updating based on timestamp in the CSV itself
        
        Args:
            event_name: Name of the parkrun event
            days_old: Number of days before update is needed
            
        Returns:
            True if file doesn't exist or last_updated is older than specified days
        """
        csv_path = self.get_csv_path(event_name)
        
        if not csv_path.exists():
            return True
        
        try:
            # Try to read the CSV
            df = pd.read_csv(csv_path)
            
            # Check if it has a last_updated column
            if 'last_updated' in df.columns:
                # Get the most recent timestamp from the last_updated column
                try:
                    last_updated = pd.to_datetime(df['last_updated']).max()
                    age = datetime.now() - last_updated.to_pydatetime()
                    return age > timedelta(days=days_old)
                except (ValueError, TypeError):
                    # If timestamp is invalid, check file modification time
                    mod_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
                    age = datetime.now() - mod_time
                    return age >= timedelta(days=days_old)
            else:
                # No timestamp column, fall back to file modification time
                mod_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
                age = datetime.now() - mod_time
                return age > timedelta(days=days_old)
        
        except Exception as e:
            # If we can't read the file, check modification time
            print(f"Could not check timestamp in CSV for {event_name}: {e}")
            mod_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
            age = datetime.now() - mod_time
            return age > timedelta(days=days_old)
    
    def load_csv(self, event_name: str) -> pd.DataFrame:
        """
        Load CSV data for an event
        
        Args:
            event_name: Name of the parkrun event
            
        Returns:
            DataFrame with columns: date, first_male, first_female, finishers, helpers
            
        Raises:
            FileNotFoundError: If CSV doesn't exist
        """
        csv_path = self.get_csv_path(event_name)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"No CSV found for event: {event_name}")
        
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def save_csv(self, event_name: str, df: pd.DataFrame) -> None:
        """
        Save DataFrame to CSV
        
        Args:
            event_name: Name of the parkrun event
            df: DataFrame with results data
        """
        csv_path = self.get_csv_path(event_name)
        
        # Ensure date column is in correct format
        if 'date' in df.columns:
            df = df.copy()
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        df.to_csv(csv_path, index=False)
    
    def append_results(self, event_name: str, new_results: List[Dict]) -> None:
        """
        Append new results to existing CSV
        
        Args:
            event_name: Name of the parkrun event
            new_results: List of result dictionaries
        """
        if not new_results:
            return
        
        # Load existing data if available
        if self.csv_exists(event_name):
            df = self.load_csv(event_name)
        else:
            df = pd.DataFrame(columns=self.COLUMNS)
        
        # Create DataFrame from new results
        new_df = pd.DataFrame(new_results)
        
        # Add last_updated timestamp to new results
        now = datetime.now()
        new_df['last_updated'] = now
        
        # Ensure columns match
        for col in self.COLUMNS:
            if col not in new_df.columns:
                new_df[col] = None
        
        # Append and remove duplicates based on date
        df = pd.concat([df, new_df[self.COLUMNS]], ignore_index=True)
        df['date'] = pd.to_datetime(df['date'])
        df = df.drop_duplicates(subset=['date'], keep='last')
        df = df.sort_values('date').reset_index(drop=True)
        
        # Save back to CSV
        self.save_csv(event_name, df)
    
    def get_event_list(self) -> List[str]:
        """Get list of all available events"""
        csv_files = list(self.data_dir.glob('*.csv'))
        # Convert filename back to event name
        return [f.stem.replace('_', ' ') for f in csv_files]
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate data integrity
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        required_cols = ['date', 'finishers']
        
        for col in required_cols:
            if col not in df.columns:
                return False, f"Missing required column: {col}"
        
        # Check for data type issues
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            return False, "Date column must be datetime type"
        
        if df['finishers'].dtype not in [int, float]:
            return False, "Finishers column must be numeric"
        
        if df.empty:
            return False, "DataFrame is empty"
        
        return True, "Data is valid"


if __name__ == "__main__":
    # Example usage
    dm = DataManager()
    
    # Check if event needs updating
    if dm.needs_update("Windsor"):
        print("Windsor needs updating")
    
    # Load existing data
    try:
        df = dm.load_csv("Windsor")
        print(f"Loaded {len(df)} records for Windsor")
    except FileNotFoundError:
        print("No data for Windsor yet")
