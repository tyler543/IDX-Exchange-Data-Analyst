import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

here = os.path.dirname(os.path.abspath(__file__))
out_folder = os.path.join(here, "..", "..", "output")

listing_df = pd.read_csv(os.path.join(out_folder, "CRMLS_listing_combined_residential.csv"), low_memory=False)
sold_df = pd.read_csv(os.path.join(out_folder, "CRMLS_sold_combined_residential.csv"), low_memory=False)

# fields used for market analysis, everything else is treated as metadata
num_cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "LotSizeAcres",
            "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"]
other_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "PropertyType",
              "PropertySubType", "CountyOrParish", "MLSAreaMajor", "City", "PostalCode",
              "Latitude", "Longitude"]
market_cols = num_cols + other_cols

for name, df in [("listing", listing_df), ("sold", sold_df)]:
    print(f"----- {name} -----")

    # rows, columns, dtypes
    print(df.shape)
    print(df.dtypes)

    # metadata fields (everything that is not a market field)
    print("metadata fields:", [c for c in df.columns if c not in market_cols])

    # property types and the residential filter
    # (already filtered to residential in week 1, so this should remove 0 rows)
    print(df["PropertyType"].value_counts(dropna=False))
    df = df[df["PropertyType"] == "Residential"]
    print("rows after residential filter:", len(df))

    # one stray text value makes the whole column text, so force the numbers first
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # null count and null percent for every column
    missing = pd.DataFrame({"null_count": df.isnull().sum(), "null_pct": df.isnull().mean() * 100})
    missing.to_csv(os.path.join(out_folder, f"{name}_null_summary.csv"))
    print(missing)

    # columns over 90% null
    over_90 = missing[missing["null_pct"] > 90]
    print(over_90)
    over_90.to_csv(os.path.join(out_folder, f"{name}_missing.csv"))

    # drop them unless they are core market fields
    df = df.drop(columns=[c for c in over_90.index if c not in market_cols])

    # numeric summary with percentiles
    print(df[num_cols].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T)

    # extreme outliers (3 x iqr), counted only, nothing is removed
    for c in num_cols:
        q1 = df[c].quantile(0.25)
        q3 = df[c].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[c] < q1 - 3 * iqr) | (df[c] > q3 + 3 * iqr)]
        print(c, "extreme outliers:", len(outliers))

    # histograms and boxplots, closed after saving so the sold pass starts clean
    df[num_cols].hist(bins=50, figsize=(14, 10))
    plt.savefig(os.path.join(here, f"{name}_hist.png"))
    plt.close("all")
    df[num_cols].plot(kind="box", subplots=True, layout=(3, 3), figsize=(14, 10))
    plt.savefig(os.path.join(here, f"{name}_box.png"))
    plt.close("all")

    # suggested questions (sold only)
    if name == "sold":
        print("median close price:", df["ClosePrice"].median())
        print("mean close price:", df["ClosePrice"].mean())
        print("sold above list %:", (df["ClosePrice"] > df["ListPrice"]).mean() * 100)
        print("sold below list %:", (df["ClosePrice"] < df["ListPrice"]).mean() * 100)
        listing_date = pd.to_datetime(df["ListingContractDate"], errors="coerce")
        close_date = pd.to_datetime(df["CloseDate"], errors="coerce")
        print("listing date after close date:", (listing_date > close_date).sum())
        counties = df.groupby("CountyOrParish")["ClosePrice"].agg(["median", "count"])
        print(counties[counties["count"] >= 100].sort_values("median", ascending=False).head(10))

    # save the filtered dataset
    df.to_csv(os.path.join(out_folder, f"CRMLS_{name}_filtered_residential.csv"), index=False)
