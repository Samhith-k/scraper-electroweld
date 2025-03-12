import streamlit as st
import pandas as pd
import numpy as np
import time
from PIL import Image

# Set page configuration
logo_image = Image.open("./logo-png.png")
st.set_page_config(
    page_title="Hardware Parts Price Comparison",
    page_icon=logo_image,
    layout="wide"
)

# Sidebar navigation to switch between the price comparator and scraping configuration
page = st.sidebar.radio("Navigation", ["Price Comparison", "Scraping Configurations"])

if page == "Scraping Configurations":
    st.title("Scraping Configurations")
    st.markdown("Configure scraping settings below.")

    # User Input Widgets
    url = st.text_input("Enter the URL to scrape", placeholder="https://example.com")
    source = st.selectbox("Select Company", ['HAMPDON EBAY' ,'NATIONAL WELDING EBAY', 'METRO WELDER SERVICE',
 'WELDCONNECT', 'WELD.COM.AU', 'GENTRONICS', 'BILBA', 'SUPERCHEAP AUTO',
 'ELECTROWELD WEBSITE', 'BILBA EBAY', 'WA INDUSTRIAL SUPPLIES EBAY',
 'ELECTROWELD EBAY', 'TOOLS WAREHOUSE', "KENNEDY'S WELDING SUPPLIES",
 'WA INDUSTRIAL SUPPLIES WEBSITE', 'TKD'])
    frequency = st.number_input("Scraping frequency (hours)", min_value=1, max_value=24, value=1)
    
    # File uploader for CSV/JSON files
    uploaded_file = st.file_uploader("Upload CSV/JSON file for scraped data", type=["csv", "json"])
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/csv":
                df_uploaded = pd.read_csv(uploaded_file)
            else:
                df_uploaded = pd.read_json(uploaded_file)
            st.write("Uploaded file preview:")
            st.dataframe(df_uploaded.head())
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Buttons & Actions
    auto_scrape = st.toggle("Enable Auto-Scraping Mode", value=False)
    if auto_scrape:
        st.info("Auto-scraping is enabled. The app will automatically run scraping tasks based on your frequency setting.")
    if st.button("Trigger Manual Scraping"):
        with st.spinner("Scraping in progress..."):
            # Here you would call your scraping function
            time.sleep(2)  # Simulated delay
            st.success("Scraping completed!")
    
    # Example of a progress indicator (useful for longer tasks)
    if st.button("Show Progress Example"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)  # Simulated work
            progress_bar.progress(i + 1)

elif page == "Price Comparison":
    st.image(logo_image, width=150)
    st.title("Hardware Parts Price Comparison")
    st.markdown("### Compare Prices of Hardware Parts on EBay")
    
    # Data loading and caching function
    @st.cache_data
    def load_data():
        df = pd.read_csv("combined.csv")
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

        df["Price_Numeric"] = df["Price"].apply(parse_price)
        return df

    df = load_data()
    df_pivot = df.pivot_table(
        index=["BRAND", "PRODUCT NAME"], 
        columns="Shop Name", 
        values="Price_Numeric", 
        aggfunc='first'
    ).reset_index()

    # Sidebar filters for Price Comparison page
    st.sidebar.header("Filters")
    brand_options = df_pivot["BRAND"].dropna().unique().tolist()
    selected_brand = st.sidebar.multiselect("Select Brand(s):", options=brand_options, default=[])
    product_options = df_pivot["PRODUCT NAME"].dropna().unique().tolist()
    selected_product = st.sidebar.multiselect("Select Product(s):", options=product_options, default=[])

    filtered_df = df_pivot.copy()
    if selected_brand:
        filtered_df = filtered_df[filtered_df["BRAND"].isin(selected_brand)]
    if selected_product:
        filtered_df = filtered_df[filtered_df["PRODUCT NAME"].isin(selected_product)]

    # Highlight the cheapest price in each row
    def highlight_min(row):
        competitor_cols = [col for col in row.index if col not in ["BRAND", "PRODUCT NAME"]]
        if row[competitor_cols].dropna().empty:
            return [""] * len(row)
        min_val = row[competitor_cols].min()
        return ['background-color: lightgreen' if (col in competitor_cols and row[col] == min_val) else '' for col in row.index]

    competitor_columns = [col for col in filtered_df.columns if col not in ["BRAND", "PRODUCT NAME"]]
    styled_df = (
        filtered_df.style
        .apply(highlight_min, axis=1)
        .format("{:.2f}", subset=competitor_columns)
    )

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
