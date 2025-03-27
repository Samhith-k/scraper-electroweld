import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import glob
import os

# Set page configuration at the very top
logo_image = Image.open("./logo-electroweld.jpg")
st.set_page_config(
    page_title="Hardware Parts Price Comparison",
    page_icon=logo_image,
    layout="wide"
)

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Welders Comparison", "Helmet Comparison"])

if page == "Welders Comparison":
    st.image(logo_image, width=150)
    st.title("Hardware Parts Price Comparison")
    
    @st.cache_data
    def load_data():
        # Find all CSV files matching the pattern in the combined_csvs directory
        csv_files = glob.glob("combined_csvs/combined_*.csv")
        if not csv_files:
            st.error("No CSV files found in the combined_csvs directory!")
            return pd.DataFrame()
        # Sort files by modification time (oldest first)
        csv_files.sort(key=lambda x: os.path.getmtime(x))
        # Select the most recently modified file
        latest_csv = csv_files[-1]
        df = pd.read_csv(latest_csv)
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
    
    # Sidebar filters for brand and product (default empty = show everything)
    st.sidebar.header("Filters")
    brand_options = df_pivot["BRAND"].dropna().unique().tolist()
    selected_brand = st.sidebar.multiselect("Select Brand(s):", options=brand_options, default=[])
    product_options = df_pivot["PRODUCT NAME"].dropna().unique().tolist()
    selected_product = st.sidebar.multiselect("Select Product(s):", options=product_options, default=[])
    
    # For companies, default is empty and empty selection means "everything"
    competitor_columns = [col for col in df_pivot.columns if col not in ["BRAND", "PRODUCT NAME"]]
    selected_companies = st.sidebar.multiselect("Select Companies:", options=competitor_columns, default=[])
    if not selected_companies:
        selected_companies = competitor_columns
    
    # Additional view option
    view_option = st.sidebar.radio("Display Format", ["Styled Display", "Basic Table Display"])
    
    # Apply brand and product filters
    filtered_df = df_pivot.copy()
    if selected_brand:
        filtered_df = filtered_df[filtered_df["BRAND"].isin(selected_brand)]
    if selected_product:
        filtered_df = filtered_df[filtered_df["PRODUCT NAME"].isin(selected_product)]
    
    st.subheader("Individual Price Comparison Tables")
    
    # Function to highlight the minimum value among competitor columns
    def highlight_min_row(row):
        company_cols = [col for col in row.index if col not in ["Brand", "Product"]]
        if row[company_cols].dropna().empty:
            return ["" for _ in row.index]
        min_val = row[company_cols].min()
        return [
            'background-color: lightgreen' if col in company_cols and row[col] == min_val else ''
            for col in row.index
        ]
    
    if filtered_df.empty:
        st.write("No data available for the selected filters.")
    else:
        if view_option == "Styled Display":
            # For the styled display, process each row separately using sorted competitor data.
            counter = 1
            for idx, row in filtered_df.iterrows():
                companies_dict = {}
                # Add ELECTROWELD WEBSITE if available.
                if "ELECTROWELD WEBSITE" in df_pivot.columns:
                    companies_dict["ELECTROWELD WEBSITE"] = row.get("ELECTROWELD WEBSITE", np.nan)
                # Add other selected companies (if they have nonzero and non-NaN values)
                for comp in selected_companies:
                    if comp == "ELECTROWELD WEBSITE":
                        continue
                    value = row.get(comp)
                    if pd.notna(value) and value != 0:
                        companies_dict[comp] = value
                # Order companies: sort the competitors (excluding ELECTROWELD WEBSITE) by price, then put ELECTROWELD WEBSITE first.
                electroweld_value = companies_dict.pop("ELECTROWELD WEBSITE", np.nan)
                sorted_companies = sorted(companies_dict.items(), key=lambda x: x[1] if pd.notna(x[1]) else float('inf'))
                ordered_companies = [("ELECTROWELD WEBSITE", electroweld_value)] + sorted_companies
                # Build display data with Brand, Product, and the competitor data.
                display_data = {"Brand": row["BRAND"], "Product": row["PRODUCT NAME"]}
                for comp, price in ordered_companies:
                    display_data[comp] = price
                display_df = pd.DataFrame([display_data], index=[counter])
                counter += 1
                company_cols = [col for col in display_df.columns if col not in ["Brand", "Product"]]
                styled_row = display_df.style.apply(highlight_min_row, axis=1).format("{:.2f}", subset=company_cols)
                st.dataframe(styled_row, use_container_width=True)
        elif view_option == "Basic Table Display":
            st.subheader("Pivoted Price Comparison Data")
            
            # Reorder columns: first "BRAND" and "PRODUCT NAME", then "ELECTROWELD WEBSITE" and "ELECTROWELD EBAY" (if present), then the rest.
            primary_cols = [col for col in ["BRAND", "PRODUCT NAME"] if col in filtered_df.columns]
            preferred_cols = [col for col in ["ELECTROWELD WEBSITE", "ELECTROWELD EBAY"] if col in filtered_df.columns]
            remaining_cols = [col for col in filtered_df.columns if col not in primary_cols + preferred_cols]
            new_order = primary_cols + preferred_cols + remaining_cols
            df_reordered = filtered_df[new_order]
            
            # Define a function to highlight the cheapest price among competitor columns.
            # We exclude the non-numeric columns "BRAND" and "PRODUCT NAME".
            def highlight_min_row_basic(row):
                competitor_cols = [col for col in row.index if col not in ["BRAND", "PRODUCT NAME"]]
                if row[competitor_cols].dropna().empty:
                    return ["" for _ in row.index]
                min_val = row[competitor_cols].min()
                return [
                    'background-color: lightgreen' if col in competitor_cols and row[col] == min_val else ''
                    for col in row.index
                ]
            
            # Identify competitor columns for numeric formatting.
            competitor_columns = [col for col in new_order if col not in ["BRAND", "PRODUCT NAME"]]
            styled_df = df_reordered.style.apply(highlight_min_row_basic, axis=1) \
                                        .format("{:.2f}", subset=competitor_columns)
            
            st.dataframe(styled_df, use_container_width=True)


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
