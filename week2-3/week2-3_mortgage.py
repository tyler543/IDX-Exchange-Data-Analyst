import pandas as pd

# run week2-3.py first, it creates the filtered files used here
sold = pd.read_csv("../../csv/CRMLS_sold_filtered_residential.csv", encoding="latin-1")
listings = pd.read_csv("../../csv/CRMLS_listing_filtered_residential.csv", encoding="latin-1")

# fetch weekly rates from fred
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]

# weekly to monthly average
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()

# year_month keys (sold uses closedate, listings use listingcontractdate)
sold["year_month"] = pd.to_datetime(sold["CloseDate"]).dt.to_period("M")
listings["year_month"] = pd.to_datetime(listings["ListingContractDate"]).dt.to_period("M")

# merge
sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")
listings_with_rates = listings.merge(mortgage_monthly, on="year_month", how="left")

# validate: null rates should be 0
print("sold rows before and after:", len(sold), len(sold_with_rates))
print("listings rows before and after:", len(listings), len(listings_with_rates))
print("sold null rates:", sold_with_rates["rate_30yr_fixed"].isnull().sum())
print("listings null rates:", listings_with_rates["rate_30yr_fixed"].isnull().sum())
print("sold rows with no close date:", sold["CloseDate"].isnull().sum())
print("listings rows with no listing date:", listings["ListingContractDate"].isnull().sum())
print(sold_with_rates[["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]].head())

# save both enriched datasets
sold_with_rates.to_csv("../../csv/CRMLS_sold_with_rates.csv", index=False)
listings_with_rates.to_csv("../../csv/CRMLS_listing_with_rates.csv", index=False)