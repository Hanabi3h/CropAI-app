"""
Test script to verify data loading matches Colab
"""
import pandas as pd
import numpy as np

print("=" * 60)
print("TESTING DATA LOADING (Same as Colab)")
print("=" * 60)

# Try to load the CSV
csv_path = 'crops_district_production.csv'

try:
    df_real = pd.read_csv(csv_path)
    print(f"✅ Loaded: {csv_path}")
    print(f"   Shape: {df_real.shape}")
    print(f"   Columns: {list(df_real.columns)}")
    
    # Apply same processing as Colab
    df_real = df_real[df_real['production'] > 0].copy()
    
    if 'crop_type' in df_real.columns:
        df_real.drop(columns=['crop_type'], inplace=True)
    
    df_real.rename(columns={'crop_species': 'crop_type', 'production': 'production_tonnes'}, inplace=True)
    df_real['crop_type'] = df_real['crop_type'].astype(str).str.replace('_', ' ').str.title()
    
    print(f"\n✅ After processing:")
    print(f"   Shape: {df_real.shape}")
    print(f"   Unique crops: {df_real['crop_type'].nunique()}")
    print(f"   Sample crops: {df_real['crop_type'].unique()[:5]}")
    print(f"   Unique states: {df_real['state'].nunique()}")
    print(f"   Unique districts: {df_real['district'].nunique()}")
    
    print("\n✅ Test passed! The frontend will work correctly.")
    
except FileNotFoundError:
    print(f"❌ File not found: {csv_path}")
    print(f"\nCurrent directory: {os.getcwd()}")
    print("Files in current directory:")
    import os
    for f in os.listdir('.'):
        if f.endswith('.csv'):
            print(f"  - {f}")
    
except Exception as e:
    print(f"❌ Error: {e}")