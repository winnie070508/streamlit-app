import streamlit as st
import polars as pl
import plotly.express as px
from clean_load import clean_load

st.set_page_config(page_title="Discount Analysis", layout="wide")
st.title("🏷️ Discount Analysis")

@st.cache_data
def get_data():
    df = clean_load("Nike_CN.csv")
    df = df.with_columns(
        pl.when(pl.col("sale_price_cny").is_null() | (pl.col("sale_price_cny") == 0))
        .then(pl.col("price_cny"))
        .otherwise(pl.col("sale_price_cny"))
        .alias("original_price_cny")
    )
    df = df.with_columns(
        (
            (1 - (pl.col("price_cny") / pl.col("original_price_cny"))) * 100
        ).alias("discount_pct")
    )
    return df

def compute_insight(filters: dict) -> dict:
    df = get_data()
    denominator = len(df)
    
    if filters.get("categories"):
        df = df.filter(pl.col("category").is_in(filters["categories"]))
        
    if filters.get("min_discount"):
        df = df.filter(pl.col("discount_pct") >= filters["min_discount"])
        
    n = len(df)
    
    if n == 0:
        return {
            "metric": "Average Discount", 
            "value": 0, 
            "n": 0, 
            "denominator": denominator, 
            "filters": filters, 
            "unit": "%", 
            "data": df
        }
        
    avg_discount = df["discount_pct"].mean()
    
    return {
        "metric": "Average Discount",
        "value": avg_discount,
        "n": n,
        "denominator": denominator,
        "filters": filters,
        "unit": "%",
        "data": df
    }

df_all = get_data()
all_categories = df_all["category"].unique().drop_nulls().to_list()

selected_categories = st.multiselect("Select Categories", all_categories, default=all_categories)
min_discount = st.slider("Minimum Discount (%)", 0, 100, 0)

filters = {"categories": selected_categories, "min_discount": min_discount}
insight = compute_insight(filters)

if insight["n"] == 0:
    st.warning("No products found with these filters.")
else:
    st.markdown(f"**Insight:** For the selected products, the average discount is **{insight['value']:.1f}%** (n={insight['n']} out of {insight['denominator']} products).")
    
    fig1 = px.histogram(
        insight["data"].to_pandas(),
        x="discount_pct",
        nbins=30,
        title="Distribution of Discount Rates (%)",
        labels={"discount_pct": "Discount Rate (%)", "count": "Number of Products"}
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"Figure 1: Discount distribution. n={insight['n']}. Minimum discount filter applied: {min_discount}%.")
    
    gender_discount = insight["data"].group_by("gender_segment").agg(
        pl.col("discount_pct").mean().alias("avg_discount"),
        pl.len().alias("count")
    ).drop_nulls()
    
    fig2 = px.bar(
        gender_discount.to_pandas(),
        x="gender_segment",
        y="avg_discount",
        title="Average Discount Rate by Gender Segment (%)",
        labels={"gender_segment": "Gender Segment", "avg_discount": "Average Discount (%)"},
        text_auto='.1f'
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Figure 2: Average discount by gender. n={insight['n']}.")