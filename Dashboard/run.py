"""
Tunisia Used Car Market Dashboard
Main entry point for the application
"""

from app.dashboard import TunisiaCarDashboard
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

def main():
    # Load the pre-merged data
    print("📊 Loading merged dataset...")
    
    # Support both local and deployed paths (private data should stay untracked)
    default_data_path = Path(__file__).resolve().parent / 'data' / 'merged_data.csv'
    data_path = Path(os.environ.get('DASHBOARD_DATA_PATH', str(default_data_path)))

    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Set DASHBOARD_DATA_PATH or place a private dataset at Dashboard/data/merged_data.csv."
        )

    merged_data = pd.read_csv(data_path)
    print(f"✅ Loaded {len(merged_data):,} records")
    
    # Standardize column names
    print("\n🔄 Standardizing column names...")
    merged_data.columns = merged_data.columns.str.replace('-', '_')
    print("✅ Column names standardized")
    
    # Ensure car_age exists
    if 'car_age' not in merged_data.columns:
        print("\n⚠️ 'car_age' column missing, calculating...")
        current_year = datetime.now().year
        
        if 'year' in merged_data.columns:
            merged_data['car_age'] = current_year - merged_data['year']
            print("✅ 'car_age' calculated from 'year' column")
        else:
            print("⚠️ Cannot calculate car_age: 'year' column missing")
            merged_data['car_age'] = 0
    
    # Clean data
    print("\n🧹 Cleaning data...")
    original_count = len(merged_data)
    
    # Remove rows with missing critical columns
    required_cols = ['brand', 'model', 'year', 'price']
    merged_data = merged_data.dropna(subset=required_cols)
    
    # Convert year to integer
    print("🔢 Converting year to integer values...")
    merged_data['year'] = pd.to_numeric(merged_data['year'], errors='coerce')
    merged_data['year'] = merged_data['year'].round(0).astype('Int64')
    
    # Ensure proper data types for other columns
    merged_data['price'] = pd.to_numeric(merged_data['price'], errors='coerce')
    
    if 'mileage' in merged_data.columns:
        merged_data['mileage'] = pd.to_numeric(merged_data['mileage'], errors='coerce')
    
    if 'car_age' in merged_data.columns:
        merged_data['car_age'] = pd.to_numeric(merged_data['car_age'], errors='coerce')
    
    # Remove invalid data
    merged_data = merged_data.dropna(subset=['year', 'price'])
    merged_data = merged_data[
        (merged_data['year'] >= 2000) & 
        (merged_data['year'] <= 2025) &
        (merged_data['price'] > 0)
    ]
    
    # Convert year back to regular int
    merged_data['year'] = merged_data['year'].astype(int)
    
    cleaned_count = len(merged_data)
    print(f"✅ Cleaned: {original_count:,} → {cleaned_count:,} records "
          f"({original_count - cleaned_count:,} removed)")
    
    # Verify year values
    print(f"\n📅 Year range: {merged_data['year'].min()} - {merged_data['year'].max()}")
    unique_years = sorted(merged_data['year'].unique())
    print(f"📅 Unique years ({len(unique_years)}): {unique_years}")
    
    # Create dashboard instance with pre-loaded data
    print("\n🚀 Initializing dashboard...")
    dashboard = TunisiaCarDashboard(merged_data=merged_data)
    
    # Return the server for deployment
    return dashboard.app.server

# For local development
if __name__ == '__main__':
    app_server = main()
    
    # Determine environment
    is_production = os.environ.get('RENDER') or os.environ.get('DYNO')
    
    if not is_production:
        # Local development mode
        print("\n" + "="*60)
        print("🚗 Tunisia Car Market Dashboard Ready!")
        print("="*60)
        print("📊 Dashboard URL: http://127.0.0.1:8050")
        print("🔄 Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        # Get the Dash app from server
        from werkzeug.serving import run_simple
        run_simple('127.0.0.1', 8050, app_server, use_reloader=True, use_debugger=True)
    else:
        print("🌐 Running in production mode")

# For deployment (Render, Heroku, etc.)
server = main()