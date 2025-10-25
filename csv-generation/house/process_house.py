import pandas as pd

# === 1. Load Zillow state-level home value data ===
print("📂 Loading Zillow data...")
df = pd.read_csv("states.csv")

# Convert state names to string and clean whitespace
df["StateName"] = df["StateName"].astype(str).str.strip()

# Identify date columns (e.g., "2000-01-31", "2025-09-30")
date_cols = [col for col in df.columns if col[:4].isdigit()]

# Melt wide date columns into long format
print("📊 Reshaping Zillow data...")
long_df = df.melt(
    id_vars=["RegionID", "SizeRank", "RegionName", "RegionType", "StateName"],
    value_vars=date_cols,
    var_name="Date",
    value_name="Avg_Home_Value"
)

# Convert date column to datetime
long_df["Date"] = pd.to_datetime(long_df["Date"], errors="coerce")

# Filter only rows that represent state-level data
long_df = long_df[long_df["RegionType"] == "state"].copy()

# === 2. Load Hyperscale Announcement data ===
print("⚙️ Loading hyperscale data...")
hype = pd.read_csv("hyperscales.csv")
hype["State"] = hype["State"].astype(str).str.strip()
hype["AnnouncementDate"] = pd.to_datetime(hype["AnnouncementDate"], errors="coerce")

# === 3. Merge on state ===
print("🔗 Merging Zillow and Hyperscale data...")
merged = long_df.merge(hype, left_on="StateName", right_on="State", how="left")

# === 4. Create flags and calculate percent change ===
merged["Is_Post_Announcement"] = (
    merged["AnnouncementDate"].notna() & (merged["Date"] > merged["AnnouncementDate"])
).astype(int)

merged["is_hub"] = (merged["AnnouncementDate"].notna()).astype(int)
merged["Year"] = merged["Date"].dt.year

# Percent change in home value per year by state
merged["HomeValue_Pct_Change"] = (
    merged.groupby("StateName")["Avg_Home_Value"].pct_change() * 100
)

# === 5. Save to new file ===
output_file = "merged_hyperscale_zillow.csv"
merged.to_csv(output_file, index=False)

# === 6. Provide clear feedback ===
num_states = merged["StateName"].nunique()
num_hype_states = merged[merged["is_hub"] == 1]["StateName"].nunique()
print(f"✅ Merge complete! Saved as {output_file}")
print(f"📈 Total states in dataset: {num_states}")
print(f"🏗️ States with hyperscale announcements: {num_hype_states}")
print("📁 You can now open merged_hyperscale_zillow.csv to inspect the results.")
