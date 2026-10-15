import pandas as pd
import os

here = os.path.dirname(os.path.abspath(__file__))
out_folder = os.path.join(here, "..", "..", "output")

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]
num_cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "LotSizeAcres",
            "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
            "Latitude", "Longitude", "rate_30yr_fixed"]

keep_cols = date_cols + num_cols + [
    "ListingKey", "ListingId", "PropertyType", "PropertySubType", "MlsStatus", "StandardStatus",
    "UnparsedAddress", "City", "PostalCode", "CountyOrParish", "MLSAreaMajor", "StateOrProvince",
    "ListAgentFullName", "ListOfficeName", "BuyerAgentFullName", "BuyerOfficeName",
    "year_month"]

files = {"sold": os.path.join(out_folder, "CRMLS_sold_with_rates.csv"),
         "listing": os.path.join(out_folder, "CRMLS_listing_with_rates.csv")}

for name, path in files.items():
    print(f"----- {name} -----")
    
    df = pd.read_csv(path, low_memory=False)
    print("rows at start:", len(df))
    print("columns at start:", df.shape[1])

    # 1. dates to datetime
    for c in date_cols:
        if c not in df.columns:
            print(c, "not in file, skipped")
            continue
        before = df[c].notnull().sum()
        df[c] = pd.to_datetime(df[c], errors="coerce")
        print(c, "values that failed to parse:", before - df[c].notnull().sum())

    # 2. numeric fields to numbers
    for c in num_cols:
        if c not in df.columns:
            print(c, "not in file, skipped")
            continue
        before = df[c].notnull().sum()
        df[c] = pd.to_numeric(df[c], errors="coerce")
        print(c, "values that failed to convert:", before - df[c].notnull().sum())

    # 3. drop unneeded columns
    # print what is dropped and which keep columns are missing so nothing disappears silently
    kept = [c for c in keep_cols if c in df.columns]
    print("keep columns not found in file:", [c for c in keep_cols if c not in df.columns])
    print("dropped columns:", [c for c in df.columns if c not in kept])
    df = df[kept]
    print("columns after drop:", df.shape[1])

    # 4. missing values
    if name == "sold":
        required = ["ClosePrice", "CloseDate"]
    else:
        required = ["ListingContractDate"]
    before = len(df)
    df = df.dropna(subset=required)
    print("rows dropped for missing", required, ":", before - len(df))

    # livingarea of 0 means "not entered", not a real house, so make it null instead of dropping the row
    print("LivingArea <= 0 set to null:", (df["LivingArea"] <= 0).sum())
    df.loc[df["LivingArea"] <= 0, "LivingArea"] = None

    # 5. remove invalid numeric values 
    invalid = (df["DaysOnMarket"] < 0) | (df["BedroomsTotal"] < 0) | (df["BathroomsTotalInteger"] < 0)
    if name == "sold":
        invalid = invalid | (df["ClosePrice"] <= 0)
    print("ClosePrice <= 0:", (df["ClosePrice"] <= 0).sum())
    print("DaysOnMarket < 0:", (df["DaysOnMarket"] < 0).sum())
    print("BedroomsTotal < 0:", (df["BedroomsTotal"] < 0).sum())
    print("BathroomsTotalInteger < 0:", (df["BathroomsTotalInteger"] < 0).sum())
    print("rows removed as invalid:", invalid.sum())
    df = df[~invalid]

    # confirm types and remaining nulls after cleaning
    print(df.dtypes)
    print(df.isnull().sum())
    print("rows at end of part 1:", len(df))

    df.to_csv(os.path.join(out_folder, f"CRMLS_{name}_cleaned_part1.csv"), index=False)
