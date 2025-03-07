import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Hardware Parts Price Comparison",
    page_icon=":hammer:",
    layout="wide"
)

# Display a logo and header
logo_url = "https://via.placeholder.com/150"  # Replace with your actual logo URL
st.image(logo_url, width=150)
st.title("Hardware Parts Price Comparison")
st.markdown("### Compare Prices of Hardware Parts on EBay")

# Function to load and preprocess the CSV data
@st.cache_data
def load_data():
    # Read the CSV file (ensure it's in the same folder as app.py)
    df = pd.read_csv("Pricing_Ebay_append.csv")
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    # For debugging (optional), you can display the column names:
    #st.write("CSV Columns:", df.columns.tolist())
    
    # Define a function to parse price strings into floats
    def parse_price(price):
        if pd.isna(price):
            return np.nan
        price_str = str(price)
        # Remove common currency symbols and unwanted text
        for char in ["AU", "$", ",", "each"]:
            price_str = price_str.replace(char, "")
        price_str = price_str.strip()
        try:
            return float(price_str)
        except Exception:
            return np.nan

    # Convert price columns to numeric values for filtering (though not displayed)
    df["Price_EBay_Numeric"] = df["Price_EBay"].apply(parse_price)
    df["Price_Bundle_EBay_Numeric"] = df["Price_Bundle_EBay"].apply(parse_price)
    return df

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Filter by BRAND using the "BRAND" column
if "BRAND" in df.columns:
    brand_options = df["BRAND"].dropna().unique().tolist()
    selected_brand = st.sidebar.multiselect("Select Brand(s):", options=brand_options, default=brand_options)
else:
    st.error("Column 'BRAND' not found in CSV!")
    selected_brand = []

# Price range filter based on the numeric EBay price
if "Price_EBay_Numeric" in df.columns and df["Price_EBay_Numeric"].notna().any():
    min_price = float(df["Price_EBay_Numeric"].min())
    max_price = float(df["Price_EBay_Numeric"].max())
else:
    min_price = 0.0
    max_price = 1000.0

selected_price = st.sidebar.slider(
    "Select EBay Price Range:",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# Apply filters on the data
filtered_df = df.copy()
if selected_brand:
    filtered_df = filtered_df[filtered_df["BRAND"].isin(selected_brand)]
filtered_df = filtered_df[
    (filtered_df["Price_EBay_Numeric"] >= selected_price[0]) &
    (filtered_df["Price_EBay_Numeric"] <= selected_price[1])
]

# Select only the desired columns for display
display_columns = ["BRAND", "PRODUCT NAME", "Shop Name", "Price_EBay"]
if all(col in filtered_df.columns for col in display_columns):
    display_df = filtered_df[display_columns]
else:
    st.error("One or more required columns are missing in the data.")
    display_df = filtered_df

# Display the filtered data with only the selected columns
st.subheader("Filtered Data")
st.dataframe(display_df)

# Option to download the filtered data (with selected columns) as CSV
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(display_df)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name='filtered_data.csv',
    mime='text/csv'
)
