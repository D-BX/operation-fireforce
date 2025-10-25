import pandas as pd

def process_iso_file(file_path, iso_name, price_column_name, filter_by_market):
    """
    Loads data for a single ISO, standardizes it, and calculates summary statistics.
    
    Args:
        file_path (str): The path to the ISO's CSV file.
        iso_name (str): The name of the ISO (e.g., 'CAISO').
        price_column_name (str): The name of the price column ('lmp' or 'spp').
        filter_by_market (bool): If True, filters for 'REAL_TIME' market data.
        
    Returns:
        pandas.DataFrame: A DataFrame with standardized summary statistics.
    """
    try:
        print(f"--- Processing {iso_name} data from '{file_path}' ---")
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"⚠️  WARNING: File not found: '{file_path}'. Skipping this ISO.")
        return None

    # --- 1. Standardize Column Names ---
    if price_column_name not in df.columns:
        print(f"⚠️  WARNING: Price column '{price_column_name}' not found in '{file_path}'. Skipping.")
        return None
    df.rename(columns={price_column_name: 'price'}, inplace=True)

    # --- 2. Pre-processing ---
    df['timestamp'] = pd.to_datetime(df['interval_start_utc'], errors='coerce')
    df.dropna(subset=['timestamp', 'price'], inplace=True)
    df['year'] = df['timestamp'].dt.year

    # --- 3. FLEXIBLE FILTERING (THIS IS THE KEY CHANGE) ---
    df_filtered = None
    if filter_by_market:
        print("Filtering for 'REAL_TIME' market...")
        if 'market' not in df.columns:
            print(f"⚠️  WARNING: 'market' column not found in '{file_path}'. Cannot filter. Skipping.")
            return None
        
        df['market'] = df['market'].astype(str)
        df_filtered = df[df['market'].str.contains('REAL_TIME', case=False)].copy()
        
        if df_filtered.empty:
            print(f"⚠️  WARNING: No 'REAL_TIME' market data found after filtering. Skipping.")
            return None
    else:
        # If not filtering, we use the entire cleaned dataframe.
        print("ℹ️  Skipping market-based filtering for this ISO as configured.")
        df_filtered = df.copy()

    # --- 4. Grouping and Aggregation ---
    grouped = df_filtered.groupby(['location', 'year'])
    
    summary_df = grouped.agg(
        Avg_Price=('price', 'mean'),
        Price_Std_Dev=('price', 'std')
    ).reset_index()
    
    summary_df['ISO'] = iso_name
    
    print(f"✅ Finished processing {iso_name}. Found {len(summary_df)} summary rows.")
    return summary_df


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # --- UPDATED CONFIGURATION ---
    # We've added a 'filter_market' flag.
    ISO_CONFIG = {
        "CAISO": {"file": "real_location_pricing/casio.csv", "price_col": "lmp", "filter_market": True},
        "ERCOT": {"file": "real_location_pricing/ercot.csv", "price_col": "spp", "filter_market": True},
        "ISONE": {"file": "real_location_pricing/isone.csv", "price_col": "lmp", "filter_market": False}, # SET TO FALSE
        "MISO":  {"file": "real_location_pricing/miso.csv",  "price_col": "lmp", "filter_market": True},
        "PJM":   {"file": "real_location_pricing/pjm.csv",   "price_col": "lmp", "filter_market": True}
    }
    
    all_summaries = []

    # Loop through the configuration and process each file
    for iso, config in ISO_CONFIG.items():
        summary = process_iso_file(
            file_path=config["file"], 
            iso_name=iso, 
            price_column_name=config["price_col"],
            filter_by_market=config["filter_market"] # Pass the new flag to the function
        )
        if summary is not None:
            all_summaries.append(summary)

    if all_summaries:
        final_df = pd.concat(all_summaries, ignore_index=True)
        final_df = final_df[['ISO', 'location', 'year', 'Avg_Price', 'Price_Std_Dev']]
        output_filename = 'all_isos_summary_statistics.csv'
        
        print("\n" + "="*60)
        print("✅ Combined Summary for All ISOs")
        print("="*60)
        
        final_df.to_csv(output_filename, index=False)
        print(f"\n✅ Master summary successfully saved to '{output_filename}'")
    else:
        print("\nNo data was processed. Please check your file paths and configurations.")
