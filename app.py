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

# Display a logo and header
st.image(logo_image, width=150)
st.title("Hardware Parts Price Comparison")
st.markdown("### Compare Prices of Hardware Parts on EBay")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Pricing_Ebay_append.csv")
    df.columns = df.columns.str.strip()

    def parse_price(price):
        if pd.isna(price):
            return np.nan
        price_str = str(price)
        for char in ["AU", "$", ",", "each"]:
            price_str = price_str.replace(char, "")
        price_str = price_str.strip()
        try:
            return float(price_str)
        except Exception:
            return np.nan

    df["Price_EBay_Numeric"] = df["Price_EBay"].apply(parse_price)
    return df

# Load and pivot data
df = load_data()
df_pivot = df.pivot_table(index=["BRAND", "PRODUCT NAME"], columns="Shop Name", values="Price_EBay_Numeric", aggfunc='first').reset_index()

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

# Display filtered data
st.subheader("Filtered Data")
st.dataframe(filtered_df)

# Download option
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
