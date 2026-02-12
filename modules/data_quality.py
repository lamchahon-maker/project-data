
import pandas as pd
import numpy as np

class DataQualityAudit:
    """
    Performs data quality checks across 4 dimensions:
    - Completeness
    - Accuracy
    - Consistency
    - Timeliness
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def check_completeness(self) -> pd.DataFrame:
        """Calculates percentage of missing values per column."""
        missing = self.df.isnull().sum()
        total = len(self.df)
        completeness = pd.DataFrame({
            'Missing Values': missing,
            'Percentage': (missing / total) * 100
        })
        return completeness[completeness['Missing Values'] > 0].sort_values('Percentage', ascending=False)
    
    def check_accuracy(self) -> dict:
        """
        Checks for value accuracy.
        - Latitude/Longitude bounds (approximate for Montgomery County/MD region for example purposes).
        - Vehicle Year validity.
        """
        results = {}
        
        # Latitude/Longitude Check (Rough bounds for Maryland/DC area)
        # Lat: ~37 to ~40, Long: ~-79 to ~-75
        invalid_geo = self.df[
            ((self.df['Latitude'] < 37) | (self.df['Latitude'] > 40)) |
            ((self.df['Longitude'] < -79) | (self.df['Longitude'] > -75))
        ]
        results['Invalid Geo Coordinates'] = len(invalid_geo)
        
        # Vehicle Year Check
        current_year = pd.Timestamp.now().year
        invalid_year = self.df[
            (self.df['Vehicle Year'] < 1900) | (self.df['Vehicle Year'] > current_year + 1)
        ]
        results['Invalid Vehicle Year'] = len(invalid_year)
        
        return results
        
    def check_consistency(self) -> dict:
        """
        Checks for logical consistency between columns.
        """
        results = {}
        
        # Example: Parked Vehicle vs Vehicle Movement
        # If Parked Vehicle is 'Yes', Movement should likely involve parking or be static/unknown
        if 'Parked Vehicle' in self.df.columns and 'Vehicle Movement' in self.df.columns:
            inconsistent_parking = self.df[
                (self.df['Parked Vehicle'] == 'Yes') & 
                (~self.df['Vehicle Movement'].isin(['PARKED', 'PARKING', 'STOPPED', 'STANDING']))
            ]
            results['Inconsistent Parking Data'] = len(inconsistent_parking)
            
        return results
        
    def check_timeliness(self) -> dict:
        """
        Checks for date validity and range.
        Assuming dataset should be roughly within last 20 years.
        """
        results = {}
        
        if 'Crash Date/Time' in self.df.columns:
            # Future dates
            future_dates = self.df[self.df['Crash Date/Time'] > pd.Timestamp.now()]
            results['Future Dates'] = len(future_dates)
            
            # Too old dates (e.g., before 2000 for this dataset context)
            old_dates = self.df[self.df['Crash Date/Time'] < pd.Timestamp('2000-01-01')]
            results['Dates Before 2000'] = len(old_dates)
            
        return results

    def run_full_audit(self):
        return {
            "completeness": self.check_completeness(),
            "accuracy": self.check_accuracy(),
            "consistency": self.check_consistency(),
            "timeliness": self.check_timeliness()
        }
