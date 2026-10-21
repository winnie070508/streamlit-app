import streamlit as st
import polars as pl
import plotly.express as px
from clean_load import clean_load

st.set_page_config(page_title="Price Analysis", layout="wide")
st.title("💰 Price Analysis")

@st.cache_data
def get_data():
    return clean_load("Nike_CN.csv")

def compute_insight(filters: dict) -> dict:
    df = get_data()
    denominator = len(df)
    
    if filters.get("price_range"):
        lo, hi = filters["price_range"]
        df = df.filter(pl.col("price_cny").is_between(lo, hi))
        
    n = len(df)
    
    if n == 0:
        return {
            "metric": "Median Price", 
            "value": 0, 
            "n": 0, 
            "denominator": denominator, 
            "filters": filters, 
            "unit": "CNY", 
            "data": df
        }
        
    median_price = df["price_cny"].median()
    
    return {
        "metric": "Median Price",
        "value": median_price,
        "n": n,
        "denominator": denominator,
        "filters": filters,
        "unit": "CNY",
        "data": df
    }

df_all = get_data()
min_price = int(df_all["price_cny"].min())
max_price = int(df_all["price_cny"].max())

price_range = st.slider("Select Price Range (CNY)", min_price, max_price, (min_price, max_price))

filters = {"price_range": price_range}
insight = compute_insight(filters)

if insight["n"] == 0:
    st.warning("No products found in this price range.")
else:
    st.markdown(f"**Insight:** In the selected range, the median price is **{insight['value']:.0f} CNY** (n={insight['n']} out of {insight['denominator']} products).")
    
    fig1 = px.histogram(
        insight["data"].to_pandas(), 
        x="price_cny", 
        nbins=40,
        title="Distribution of Product Prices (CNY)",
        labels={"price_cny": "Price (CNY)", "count": "Number of Products"}
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"Figure 1: Price distribution. n={insight['n']}. Filter: {price_range[0]} - {price_range[1]} CNY.")
    
    category_median = insight["data"].group_by("category").agg(
        pl.col("price_cny").median().alias("median_price"),
        pl.len().alias("count")
    ).sort("median_price", descending=True)
    
    fig2 = px.bar(
        category_median.to_pandas(),
        x="category",
        y="median_price",
        title="Median Price by Category (CNY)",
        labels={"category": "Category", "median_price": "Median Price (CNY)"},
        text_auto='.0f'
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Figure 2: Median price by category. n={insight['n']}.")