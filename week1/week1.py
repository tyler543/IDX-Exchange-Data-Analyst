import pandas as pd
import os

folder = "../csv"

listing_files = sorted([f for f in os.listdir(folder) if f.startswith("CRMLSListing")])

listing_dfs = []
for f in listing_files:
    df = pd.read_csv(os.path.join(folder, f), encoding="latin-1") 
    listing_dfs.append(df)
    
listings = pd.concat(listing_dfs, ignore_index=True)
print(f"Listing - rows after concat, before filter: {len(listings)}")

listings_residential = listings[listings['PropertyType'] == 'Residential']
print(f"Listing - rows after filter: {len(listings_residential)}")

listings_residential.to_csv(os.path.join(folder, "CRMLSListings_Combined_Residential.csv"), index=False)

sold_files = sorted([f for f in os.listdir(folder) if f.startswith("CRMLSSold") and f.endswith(".csv")])

sold_dfs = []
for f in sold_files:
    df = pd.read_csv(os.path.join(folder, f), encoding="latin-1")
    sold_dfs.append(df)

sold = pd.concat(sold_dfs, ignore_index=True)
print(f"Sold - rows after concat, before filter: {len(sold)}")

sold_residential = sold[sold["PropertyType"] == "Residential"]
print(f"Sold - rows after Residential filter: {len(sold_residential)}")

sold_residential.to_csv(os.path.join(folder, "CRMLSSold_combined_residential.csv"), index=False)