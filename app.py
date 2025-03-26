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

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Welders Comparison","Helmet Comparison"])

if page == "Price Comparison":
    st.image(logo_image, width=150)
    st.title("Hardware Parts Price Comparison")
    
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
    
    # Sidebar filters for brand, product, and companies
    st.sidebar.header("Filters")
    brand_options = df_pivot["BRAND"].dropna().unique().tolist()
    selected_brand = st.sidebar.multiselect("Select Brand(s):", options=brand_options, default=[])
    product_options = df_pivot["PRODUCT NAME"].dropna().unique().tolist()
    selected_product = st.sidebar.multiselect("Select Product(s):", options=product_options, default=[])
    
    # Get competitor columns (all columns except BRAND and PRODUCT NAME)
    competitor_columns = [col for col in df_pivot.columns if col not in ["BRAND", "PRODUCT NAME"]]
    # Force "ELECTROWELD WEBSITE" to be included in the sidebar filters.
    selected_companies = st.sidebar.multiselect("Select Companies:", options=competitor_columns, default=competitor_columns)
    if "ELECTROWELD WEBSITE" not in selected_companies and "ELECTROWELD WEBSITE" in competitor_columns:
        selected_companies.insert(0, "ELECTROWELD WEBSITE")
    
    # Apply brand and product filters
    filtered_df = df_pivot.copy()
    if selected_brand:
        filtered_df = filtered_df[filtered_df["BRAND"].isin(selected_brand)]
    if selected_product:
        filtered_df = filtered_df[filtered_df["PRODUCT NAME"].isin(selected_product)]
    
    st.subheader("Individual Price Comparison Tables")
    
    # Define a function to highlight the minimum price among the company columns.
    def highlight_min_row(row):
        company_cols = [col for col in row.index if col not in ["Brand", "Product"]]
        if row[company_cols].dropna().empty:
            return ["" for _ in row.index]
        min_val = row[company_cols].min()
        return [
            'background-color: lightgreen'
            if col in company_cols and row[col] == min_val else ''
            for col in row.index
        ]
    
    if filtered_df.empty:
        st.write("No data available for the selected filters.")
    else:
        # Process each row from the filtered data.
        for idx, row in filtered_df.iterrows():
            companies_dict = {}
            # Always include "ELECTROWELD WEBSITE" first, even if its value is NaN.
            if "ELECTROWELD WEBSITE" in df_pivot.columns:
                companies_dict["ELECTROWELD WEBSITE"] = row.get("ELECTROWELD WEBSITE", np.nan)
            
            # For other companies, include only if they have a nonzero and non-NaN value.
            for comp in selected_companies:
                if comp == "ELECTROWELD WEBSITE":
                    continue
                value = row.get(comp)
                if pd.notna(value) and value != 0:
                    companies_dict[comp] = value
            
            # Order companies: "ELECTROWELD WEBSITE" first, then others sorted by price (NaN values go last).
            electroweld_value = companies_dict.pop("ELECTROWELD WEBSITE", np.nan)
            sorted_companies = sorted(companies_dict.items(), key=lambda x: x[1] if pd.notna(x[1]) else float('inf'))
            ordered_companies = [("ELECTROWELD WEBSITE", electroweld_value)] + sorted_companies
            
            # Create a display dictionary that includes Brand, Product, and the company prices.
            display_data = {"Brand": row["BRAND"], "Product": row["PRODUCT NAME"]}
            for comp, price in ordered_companies:
                display_data[comp] = price  # Keep as numeric so formatting works properly.
            
            display_df = pd.DataFrame([display_data])
            # Determine which columns are company columns for formatting.
            company_cols = [col for col in display_df.columns if col not in ["Brand", "Product"]]
            
            # Style the DataFrame: highlight the minimum value and format numbers to 2 decimal places.
            styled_row = (
                display_df.style
                .apply(highlight_min_row, axis=1)
                .format("{:.2f}", subset=company_cols)
            )
            st.dataframe(styled_row, use_container_width=True)
    
    # CSV download option for filtered data
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
