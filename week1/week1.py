import pandas as pd
import os

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(here, "..", "..", "csv")
out_folder = os.path.join(here, "..", "..", "output")
os.makedirs(out_folder, exist_ok=True)

# May-Aug 2026 - len(df) counts data rows only, the header is not counted
check_months = ["202605", "202606", "202607", "202608"]


# the listing export asks for some fields twice, so pandas reads the second copy
# as CloseDate.1, LivingArea.1 and so on. the copies are the same, drop them.
def drop_dupe_cols(df):
    dupes = [c for c in df.columns if "." in c and c.rsplit(".", 1)[1].isdigit()
             and c.rsplit(".", 1)[0] in df.columns]
    return df.drop(columns=dupes)


listing_files = sorted([f for f in os.listdir(folder) if f.startswith("CRMLSListing") and f.endswith(".csv")])

listing_dfs = []
for f in listing_files:
    df = pd.read_csv(os.path.join(folder, f), encoding="latin-1", low_memory=False)
    df = drop_dupe_cols(df)
    if any(m in f for m in check_months):
        print(f"{f}: {len(df)} rows")
    listing_dfs.append(df)

listings = pd.concat(listing_dfs, ignore_index=True)
print(f"Listing - rows after concat, before filter: {len(listings)}")

listings_residential = listings[listings['PropertyType'] == 'Residential']
print(f"Listing - rows after filter: {len(listings_residential)}")

listings_residential.to_csv(os.path.join(out_folder, "CRMLS_listing_combined_residential.csv"), index=False)

sold_files = sorted([f for f in os.listdir(folder) if f.startswith("CRMLSSold") and f.endswith(".csv")])

sold_dfs = []
for f in sold_files:
    df = pd.read_csv(os.path.join(folder, f), encoding="latin-1", low_memory=False)
    df = drop_dupe_cols(df)
    if any(m in f for m in check_months):
        print(f"{f}: {len(df)} rows")
    sold_dfs.append(df)

sold = pd.concat(sold_dfs, ignore_index=True)
print(f"Sold - rows after concat, before filter: {len(sold)}")

sold_residential = sold[sold["PropertyType"] == "Residential"]
print(f"Sold - rows after Residential filter: {len(sold_residential)}")

sold_residential.to_csv(os.path.join(out_folder, "CRMLS_sold_combined_residential.csv"), index=False)
