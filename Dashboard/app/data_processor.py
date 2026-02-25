"""
Data Processing Module for Tunisia Used Car Market Dashboard
Handles merging, cleaning, and standardization of datasets A and B
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

class CarDataProcessor:
    """
    Processes and merges car market datasets from different sources
    """
    
    def __init__(self, dataset_a_path, dataset_b_path):
        """
        Initialize processor with dataset paths
        
        Args:
            dataset_a_path: Path to 2025 dataset (4900 rows)
            dataset_b_path: Path to 2007-2024 dataset (4492 rows)
        """
        self.dataset_a_path = dataset_a_path
        self.dataset_b_path = dataset_b_path
        self.merged_data = None
        
    def load_and_standardize(self):
        """
        Load both datasets and standardize column names and types
        """
        print("📥 Loading datasets...")
        
        # Load Dataset A (2025)
        df_a = pd.read_csv(self.dataset_a_path)
        
        # Load Dataset B (2007-2024)
        df_b = pd.read_csv(self.dataset_b_path)
        
        print(f"Dataset A shape: {df_a.shape}")
        print(f"Dataset B shape: {df_b.shape}")
        
        # Standardize Dataset B to match Dataset A schema
        # Keep only common columns
        common_columns = [
            'price', 'brand', 'model', 'mileage', 'circulation-date', 
            'fuel', 'fiscal-power', 'body-type', 'publish-date', 
            'location', 'car-age', 'year'
        ]
        
        # Select available columns from both datasets
        df_a_std = df_a[common_columns].copy()
        df_b_std = df_b[[col for col in common_columns if col in df_b.columns]].copy()
        
        # Add missing columns to Dataset B with NaN
        for col in common_columns:
            if col not in df_b_std.columns:
                df_b_std[col] = np.nan
        
        # Reorder columns to match
        df_b_std = df_b_std[common_columns]
        
        # Add source identifier
        df_a_std['source'] = '2025_scrape'
        df_b_std['source'] = '2007_2024_scrape'
        
        # Merge datasets
        self.merged_data = pd.concat([df_a_std, df_b_std], ignore_index=True)
        
        print(f"✅ Merged dataset shape: {self.merged_data.shape}")
        
        return self.merged_data
    
    def clean_and_transform(self):
        """
        Clean data, handle missing values, and create derived features
        """
        print("🧹 Cleaning and transforming data...")
        
        df = self.merged_data.copy()
        
        # 1. Clean price (remove outliers and invalid values)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df[df['price'] > 0]  # Remove zero/negative prices
        df = df[df['price'] < df['price'].quantile(0.99)]  # Remove top 1% outliers
        
        # 2. Clean brand and model (standardize text)
        df['brand'] = df['brand'].str.strip().str.title()
        df['model'] = df['model'].str.strip().str.title()
        df['brand_model'] = df['brand'] + ' ' + df['model']
        
        # 3. Handle year column
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df[(df['year'] >= 2007) & (df['year'] <= 2025)]  # Valid year range
        
        # 4. Clean mileage
        df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce')
        
        # 5. Clean car-age
        df['car-age'] = pd.to_numeric(df['car-age'], errors='coerce')
        
        # 6. Handle circulation-date
        df['circulation-date'] = pd.to_datetime(df['circulation-date'], errors='coerce')
        df['circulation_year'] = df['circulation-date'].dt.year
        
        # Use circulation_year as primary, fallback to 'year' column
        df['registration_year'] = df['circulation_year'].fillna(df['year'])
        
        # 7. Create price category for analysis
        df['price_category'] = pd.cut(
            df['price'], 
            bins=[0, 20000, 40000, 60000, 100000, np.inf],
            labels=['Budget (<20K)', 'Economy (20-40K)', 'Mid-range (40-60K)', 
                    'Premium (60-100K)', 'Luxury (>100K)']
        )
        
        # 8. Drop rows with missing critical data
        df = df.dropna(subset=['price', 'brand', 'model', 'year'])
        
        # 9. Reset index
        df = df.reset_index(drop=True)
        
        self.merged_data = df
        
        print(f"✅ Cleaned dataset shape: {df.shape}")
        print(f"Year range: {df['year'].min()} - {df['year'].max()}")
        print(f"Unique brands: {df['brand'].nunique()}")
        print(f"Unique models: {df['brand_model'].nunique()}")
        
        return df
    
    def aggregate_for_analysis(self):
        """
        Create aggregated datasets for visualization
        """
        print("📊 Creating aggregated datasets...")
        
        df = self.merged_data
        
        # 1. Overall market trend (average price per year)
        market_trend = df.groupby('year').agg({
            'price': ['mean', 'median', 'count', 'std']
        }).reset_index()
        market_trend.columns = ['year', 'avg_price', 'median_price', 'count', 'std_price']
        
        # 2. Brand-level trends
        brand_trend = df.groupby(['year', 'brand']).agg({
            'price': ['mean', 'count']
        }).reset_index()
        brand_trend.columns = ['year', 'brand', 'avg_price', 'count']
        
        # 3. Model-level trends
        model_trend = df.groupby(['year', 'brand', 'model']).agg({
            'price': ['mean', 'median', 'count']
        }).reset_index()
        model_trend.columns = ['year', 'brand', 'model', 'avg_price', 'median_price', 'count']
        model_trend['brand_model'] = model_trend['brand'] + ' ' + model_trend['model']
        
        # 4. Add data quality flags
        market_trend['data_quality'] = market_trend['count'].apply(
            lambda x: 'High' if x >= 50 else ('Medium' if x >= 20 else 'Low')
        )
        
        model_trend['data_quality'] = model_trend['count'].apply(
            lambda x: 'High' if x >= 10 else ('Medium' if x >= 5 else 'Low')
        )
        
        print("✅ Aggregation complete")
        
        return {
            'market_trend': market_trend,
            'brand_trend': brand_trend,
            'model_trend': model_trend,
            'raw_data': df
        }
    
    def save_processed_data(self, output_path=None):
        """
        Save processed data to CSV
        """
        if output_path is None:
            output_path = PROJECT_ROOT / 'data' / 'merged_data.csv'

        if self.merged_data is not None:
            self.merged_data.to_csv(output_path, index=False)
            print(f"💾 Processed data saved to {output_path}")
        else:
            print("❌ No data to save. Run load_and_standardize() first.")
    
    def get_summary_stats(self):
        """
        Generate summary statistics for dashboard context
        """
        df = self.merged_data
        
        stats = {
            'total_listings': len(df),
            'year_range': f"{int(df['year'].min())}-{int(df['year'].max())}",
            'avg_price_overall': df['price'].mean(),
            'price_change': self._calculate_price_change(df),
            'top_brands': df['brand'].value_counts().head(10).to_dict(),
            'avg_mileage': df['mileage'].mean(),
            'most_common_fuel': df['fuel'].mode()[0] if 'fuel' in df.columns else 'N/A'
        }
        
        return stats
    
    def _calculate_price_change(self, df):
        """
        Calculate percentage change in average price from earliest to latest year
        """
        early_years = df[df['year'] <= 2010]['price'].mean()
        recent_years = df[df['year'] >= 2023]['price'].mean()
        
        if pd.notna(early_years) and pd.notna(recent_years) and early_years > 0:
            change_pct = ((recent_years - early_years) / early_years) * 100
            return round(change_pct, 1)
        return None


# Main execution function
def process_car_data(dataset_a_path, dataset_b_path, save_output=True):
    """
    Complete data processing pipeline
    
    Args:
        dataset_a_path: Path to 2025 dataset
        dataset_b_path: Path to 2007-2024 dataset
        save_output: Whether to save processed data to CSV
    
    Returns:
        Dictionary containing processed dataframes and stats
    """
    processor = CarDataProcessor(dataset_a_path, dataset_b_path)
    
    # Step 1: Load and standardize
    processor.load_and_standardize()
    
    # Step 2: Clean and transform
    processor.clean_and_transform()
    
    # Step 3: Aggregate for analysis
    aggregated_data = processor.aggregate_for_analysis()
    
    # Step 4: Get summary statistics
    stats = processor.get_summary_stats()
    
    # Step 5: Save if requested
    if save_output:
        processor.save_processed_data()
    
    return {
        **aggregated_data,
        'stats': stats,
        'processor': processor
    }


if __name__ == "__main__":
    # Example usage
    result = process_car_data(
        dataset_a_path=WORKSPACE_ROOT / 'data_wrangling' / 'final_data' / '2025_data.csv',
        dataset_b_path=WORKSPACE_ROOT / 'data_wrangling' / 'final_data' / 'historical_data.csv',
        save_output=True
    )
    
    print("\n📈 Summary Statistics:")
    print(f"Total listings: {result['stats']['total_listings']:,}")
    print(f"Year range: {result['stats']['year_range']}")
    print(f"Average price: {result['stats']['avg_price_overall']:,.0f} TND")
    print(f"Price change: +{result['stats']['price_change']}%")