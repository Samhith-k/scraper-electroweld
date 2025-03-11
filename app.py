import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# Set page configuration
logo_image = Image.open("./logo-png.png")
st.set_page_config(
    page_title="Hardware Parts Price Comparison",
    page_icon=logo_image,
    layout="wide"
)

# Display logo and header
st.image(logo_image, width=150)
st.title("Hardware Parts Price Comparison")
st.markdown("### Compare Prices of Hardware Parts on EBay")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("combined.csv")
    df.columns = df.columns.str.strip()

    def parse_price(price):
        if pd.isna(price):
            return np.nan
        price_str = str(price)
        # Remove extra characters and text
        for char in ["AU", "$", ",", "each"]:
            price_str = price_str.replace(char, "")
        price_str = price_str.strip()
        try:
            return float(price_str)
        except Exception:
            return np.nan

    df["Price_Numeric"] = df["Price"].apply(parse_price)
    return df

# Load and pivot data
df = load_data()
df_pivot = df.pivot_table(
    index=["BRAND", "PRODUCT NAME"], 
    columns="Shop Name", 
    values="Price_Numeric", 
    aggfunc='first'
).reset_index()

# Sidebar filters
st.sidebar.header("Filters")
brand_options = df_pivot["BRAND"].dropna().unique().tolist()
selected_brand = st.sidebar.multiselect("Select Brand(s):", options=brand_options, default=[])

product_options = df_pivot["PRODUCT NAME"].dropna().unique().tolist()
selected_product = st.sidebar.multiselect("Select Product(s):", options=product_options, default=[])

# Apply filters
filtered_df = df_pivot.copy()

if selected_brand:
    filtered_df = filtered_df[filtered_df["BRAND"].isin(selected_brand)]

if selected_product:
    filtered_df = filtered_df[filtered_df["PRODUCT NAME"].isin(selected_product)]

# Define a function to highlight the cheapest price in each row (ignoring BRAND and PRODUCT NAME)
def highlight_min(row):
    # Identify competitor columns (all columns except BRAND and PRODUCT NAME)
    competitor_cols = [col for col in row.index if col not in ["BRAND", "PRODUCT NAME"]]
    # If there are no numeric values, return empty style for all columns
    if row[competitor_cols].dropna().empty:
        return [""] * len(row)
    # Find the minimum price among competitor columns (ignoring NaNs)
    min_val = row[competitor_cols].min()
    # Return a style list for the row: highlight the cell if it equals the min value.
    return [
        'background-color: lightgreen' if (col in competitor_cols and row[col] == min_val) else ''
        for col in row.index
    ]

# Apply styling to the DataFrame: format numeric columns to 2 decimal places and highlight minimums.
competitor_columns = [col for col in filtered_df.columns if col not in ["BRAND", "PRODUCT NAME"]]
styled_df = (
    filtered_df.style
    .apply(highlight_min, axis=1)
    .format("{:.2f}", subset=competitor_columns)
)

# Display filtered data with highlighted cheapest prices
st.subheader("Filtered Data")
st.dataframe(styled_df)

# Download option for filtered data
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(filtered_df)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name='filtered_data.csv',
    mime='text/csv'
)
