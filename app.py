# Author: Your Name
import streamlit as st
import polars as pl
from clean_load import clean_load

st.set_page_config(page_title="Nike China Catalogue", layout="wide")

@st.cache_data
def get_data():
    return clean_load("Nike_CN.csv")

st.title("👟 Nike China Catalogue - Schema & Overview")

st.markdown("""
### 1. Data Source & Grain
- **Source URL**: https://www.kaggle.com/datasets/bsthere/nike-global-catalogue-2026?select=Nike_CN.csv
- **Grain**: One row is a product variant (SKU) in the catalog on a specific snapshot date.
""")

st.markdown("### 2. Data Dictionary, Units & Missingness")

df = get_data()
st.write(f"Total rows: **{df.height}**, Total columns: **{df.width}**")

units_dict = {
    "date_clean": "Date (YYYY-MM-DD)",
    "price_cny": "Price (CNY)",
    "sale_price_cny": "Sale Price (CNY)",
    "country_code": "Country Code",
    "gender_segment": "Gender"
}

schema_data = {
    "Column Name": df.columns,
    "Polars Data Type": [str(dtype) for dtype in df.dtypes],
    "Unit/Description": [units_dict.get(col, "") for col in df.columns],
    "Missing (Nulls)": df.null_count().row(0)
}

st.dataframe(pl.DataFrame(schema_data))

st.markdown("### 3. Data Preview")
st.dataframe(df.head(5).to_pandas())