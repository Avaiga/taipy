import pandas as pd


dataset_fossil_fuels_gdp = pd.read_csv("./per-capita-fossil-energy-vs-gdp.csv")
country_codes = pd.read_csv("./country_codes.csv")

dataset_fossil_fuels_gdp = dataset_fossil_fuels_gdp.merge(
    country_codes[["alpha-3", "region"]], how="left", left_on="Code", right_on="alpha-3"
)

dataset_fossil_fuels_gdp = dataset_fossil_fuels_gdp[
    ~dataset_fossil_fuels_gdp["Fossil fuels per capita (kWh)"].isnull()
].reset_index()

dataset_fossil_fuels_gdp["Fossil fuels per capita (kWh)"] = (
    dataset_fossil_fuels_gdp["Fossil fuels per capita (kWh)"] * 1000
)