import pandas as pd
import os
import numpy as np

# load the combined residential listings and sold datasets
listing_df = pd.read_csv("../../csv/CRMLSListings_Combined_Residential.csv", encoding="latin-1")
sold_df = pd.read_csv("../../csv/CRMLSSold_combined_residential.csv", encoding="latin-1")

# variables for dtypes, and missing values
list_dtypes = listing_df.dtypes
sold_dtypes = sold_df.dtypes

L_missing_pct = listing_df.isnull().mean() * 100
listing_missing = L_missing_pct[L_missing_pct >90]

S_missing_pct = sold_df.isnull().mean() * 100
sold_missing = S_missing_pct[S_missing_pct >90]

# prints number of rows and columns, dtypes, and missing value percentages for both datasets
print(f"Listing shape: {listing_df.shape[0]} rows, {listing_df.shape[1]} columns")
print(f"Sold shape: {sold_df.shape[0]} rows, {sold_df.shape[1]} columns")

print(f"dtypes for listing_df:\n{list_dtypes}")
print(f"dtypes for sold_df:\n{sold_dtypes}")

print(f"Missing value %s for listing_df:\n{listing_missing}")
print(f"Missing value %s for sold_df:\n{sold_missing}")

# csvs for missing values greater than 90%
listing_missing.to_csv("listing_missing.csv", header=["missing_pct"])
sold_missing.to_csv("sold_missing.csv", header=["missing_pct"])