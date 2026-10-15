import pandas as pd

# run week2-3_mortgage.py first, it creates the with_rates files used here
# part 1: types, columns, missing values, invalid numeric values
# part 2 (next): date consistency flags and geographic checks

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]
num_cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "LotSizeAcres",
            "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
            "Latitude", "Longitude", "rate_30yr_fixed"]

# columns kept for weeks 6-12, everything else is dropped as metadata
# agent and office names stay because week 6 segments and the competitive workbook need them
keep_cols = date_cols + num_cols + [
    "ListingKey", "ListingId", "PropertyType", "PropertySubType", "MlsStatus", "StandardStatus",
    "UnparsedAddress", "City", "PostalCode", "CountyOrParish", "MLSAreaMajor", "StateOrProvince",
    "ListAgentFullName", "ListOfficeName", "BuyerAgentFullName", "BuyerOfficeName",
    "year_month"]

files = {"sold": "../../csv/CRMLS_sold_with_rates.csv",
         "listing": "../../csv/CRMLS_listing_with_rates.csv"}

for name, path in files.items():
    print(f"----- {name} -----")
    # these files were saved by pandas as utf-8, so no latin-1 here
    df = pd.read_csv(path, low_memory=False)
    print("rows at start:", len(df))
    print("columns at start:", df.shape[1])

    # 1. dates to datetime
    # errors="coerce" turns bad values into NaT, so count how many that happened to
    for c in date_cols:
        if c not in df.columns:
            print(c, "not in file, skipped")
            continue
        before = df[c].notnull().sum()
        df[c] = pd.to_datetime(df[c], errors="coerce")
        print(c, "values that failed to parse:", before - df[c].notnull().sum())

    # 2. numeric fields to numbers
    # same idea, a string like "1,200" would become NaN, so count those
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
    # nothing is filled in with guesses (no median prices, no made up dates)
    # rows are only dropped when the field that defines the record is missing:
    # a sale needs a close price and close date, a listing needs a listing date
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

    # 5. remove invalid numeric values (these are never valid, so they are removed, not flagged)
    # nulls are not removed here, a null compared with < 0 is just False
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

    df.to_csv(f"../../csv/CRMLS_{name}_cleaned_part1.csv", index=False)
