import streamlit as st
import polars as pl
import plotly.express as px
from clean_load import clean_load

st.set_page_config(page_title="Gender & Price Analysis", layout="wide")
st.title("👟 Gender & Price Analysis")

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
    
    if filters.get("gender") and filters["gender"] != "All":
        df = df.filter(pl.col("gender_segment") == filters["gender"])
        
    if filters.get("category") and filters["category"] != "All":
        df = df.filter(pl.col("category") == filters["category"])
        
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
all_categories = ["All"] + df_all["category"].unique().drop_nulls().to_list()
all_genders = ["All"] + df_all["gender_segment"].unique().drop_nulls().to_list()

category_filter = st.selectbox("Select Category", all_categories)
gender_filter = st.radio("Select Gender Segment", all_genders, horizontal=True)

filters = {"category": category_filter, "gender": gender_filter}
insight = compute_insight(filters)

if insight["n"] == 0:
    st.warning("No products found with these filters.")
else:
    st.markdown(f"**Insight:** Under current filters (Gender: {gender_filter}, Category: {category_filter}), the median price is **{insight['value']:.0f} CNY** (n={insight['n']} out of {insight['denominator']} products).")
    
    fig1 = px.scatter(
        insight["data"].to_pandas(),
        x="original_price_cny",
        y="discount_pct",
        color="gender_segment",
        title="Original Price vs Discount Rate",
        labels={"original_price_cny": "Original Price (CNY)", "discount_pct": "Discount Rate (%)"}
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"Figure 1: Price vs Discount scatter plot. n={insight['n']}.")
    
    fig2 = px.box(
        insight["data"].to_pandas(),
        x="gender_segment",
        y="price_cny",
        color="gender_segment",
        title="Price Distribution by Gender",
        labels={"gender_segment": "Gender", "price_cny": "Price (CNY)"}
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"Figure 2: Price distribution boxplot. n={insight['n']}.")