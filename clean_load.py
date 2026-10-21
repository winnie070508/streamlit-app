import polars as pl

def clean_load(file_path: str = "Nike_CN.csv") -> pl.DataFrame:
    df = pl.read_csv(file_path, infer_schema_length=0)

    df = df.with_columns([
        pl.col("price_local")
          .str.replace_all(r"[¥￥,CNY\s]", "") 
          .cast(pl.Float64, strict=False)
          .alias("price_cny"),
          
        pl.col("sale_price_local")
          .str.replace_all(r"[¥￥,CNY\s]", "") 
          .cast(pl.Float64, strict=False)
          .alias("sale_price_cny"),

        pl.col("snapshot_date")
          .str.to_datetime("%Y-%m-%d", strict=False)
          .alias("date_clean")
    ])
    
    return df