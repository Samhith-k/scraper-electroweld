import streamlit as st
import pandas as pd
from PIL import Image
import re

def clean_prices(prices):
    cleaned = []
    for price in prices:
        if pd.notna(price):
            s = str(price)
            # Remove letters (a-z, A-Z), commas, and $ symbols.
            cleaned_price = re.sub(r'[a-zA-Z,$]', '', s).strip()
            if cleaned_price and cleaned_price not in cleaned:
                cleaned.append(cleaned_price)
    return ', '.join(cleaned)

def load_welding_data():
    try:
        data = pd.read_csv("combined_csvs/combined_20250327_121553.csv")
        return data
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None

def pivot_data(df):
    try:
        # Pivot the DataFrame so that each unique shop becomes a column.
        pivot_df = df.pivot_table(
            index=["BRAND", "PRODUCT NAME"],
            columns="Shop Name",
            values="Price",
            aggfunc=clean_prices  # Clean up the price values during aggregation.
        ).reset_index()
        
        # Reorder columns so that electroweld website and electroweld ebay come immediately
        # after BRAND and PRODUCT NAME (if they exist in the columns).
        all_columns = list(pivot_df.columns)
        
        # Start with the mandatory columns
        new_order = ["BRAND", "PRODUCT NAME"]
        
        # Append the two Electroweld columns if they exist
        electroweld_columns = ["ELECTROWELD WEBSITE", "ELECTROWELD EBAY"]
        for col in electroweld_columns:
            if col in all_columns:
                new_order.append(col)
        
        # Append the rest of the columns that are not already in new_order
        for col in all_columns:
            if col not in new_order:
                new_order.append(col)
        
        # Reindex pivot_df with the new column order
        pivot_df = pivot_df[new_order]
        return pivot_df
    except Exception as e:
        st.error(f"Error pivoting data: {e}")
        return None

def highlight_min(row):
    """Highlight the minimum (cheapest) price in a row."""
    numeric_values = []
    for cell in row:
        try:
            # Attempt to convert cell (which can be comma-separated) to float.
            value_str = str(cell).split(",")[0].strip()
            numeric_values.append(float(value_str))
        except:
            numeric_values.append(float('inf'))
            
    min_value = min(numeric_values)
    is_min = [val == min_value for val in numeric_values]
    return ['background-color: yellow' if cell else '' for cell in is_min]

def main():
    # Set up the page with a logo and configuration.
    logo_image = Image.open("./app_data/logo-electroweld.jpg")
    st.set_page_config(
        page_title="Hardware Parts Price Comparison",
        page_icon=logo_image,
        layout="wide"
    )
    st.title("Product Price Comparison")
    
    # Navigation and style selectors.
    page = st.sidebar.radio("Navigation", ["Welders Comparison", "Helmet Comparison"])
    style = st.sidebar.radio("Style", ["Basic", "Styled"])

    if page == "Welders Comparison":
        df = load_welding_data()
        if df is None:
            return
        
        pivot_df = pivot_data(df)
        if pivot_df is None or pivot_df.empty:
            st.error("Pivot table is empty or could not be created.")
            return

        # -------------------
        # Add Filters (defaults are empty)
        # -------------------
        
        # All possible brands
        all_brands = sorted(pivot_df["BRAND"].unique())
        # Brand multiselect filter
        selected_brands = st.sidebar.multiselect("Filter by Brand", all_brands, default=[])
        # If no brands are selected, we use all brands
        if not selected_brands:
            selected_brands = all_brands
        
        # Filtered pivot_df to retrieve only product names relevant to selected brands
        filtered_by_brand = pivot_df[pivot_df["BRAND"].isin(selected_brands)]
        all_products = sorted(filtered_by_brand["PRODUCT NAME"].unique())
        
        # Product Name multiselect filter
        selected_products = st.sidebar.multiselect("Filter by Product Name", all_products, default=[])
        # If no product names are selected, we use all product names
        if not selected_products:
            selected_products = all_products
        
        # Company (Shop) columns (everything after BRAND and PRODUCT NAME)
        company_columns = list(pivot_df.columns[2:])
        # Company multiselect filter
        selected_companies = st.sidebar.multiselect("Filter by Companies", company_columns, default=[])
        # If no companies are selected, we use all company columns
        if not selected_companies:
            selected_companies = company_columns
        
        # -------------------
        # Apply filters
        # -------------------
        # Filter by selected brands and products
        pivot_df = pivot_df[
            (pivot_df["BRAND"].isin(selected_brands)) &
            (pivot_df["PRODUCT NAME"].isin(selected_products))
        ]
        
        # Now select only the columns for companies that were chosen, plus the mandatory first two.
        columns_to_show = ["BRAND", "PRODUCT NAME"] + selected_companies
        # Make sure we only select columns that exist in pivot_df
        columns_to_show = [col for col in columns_to_show if col in pivot_df.columns]
        pivot_df = pivot_df[columns_to_show]
        
        st.write("### Price Comparison by Shop")
        
        # -------------------
        # Display the table
        # -------------------
        if style == "Basic":
            # Show the full pivot table with selected columns, highlighting cheapest price.
            styled_df = pivot_df.style.apply(highlight_min, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        
        elif style == "Styled":
            # For each product row, create and display a one-row table with only the
            # selected columns that have non-missing values.
            for _, row in pivot_df.iterrows():
                product_data = row.to_dict()
                filtered_data = {
                    "BRAND": product_data.get("BRAND"),
                    "PRODUCT NAME": product_data.get("PRODUCT NAME")
                }
                for col in selected_companies:
                    val = product_data.get(col)
                    # Only show the column if there's a non-missing value
                    if pd.notna(val) and val != "nan" and val != "":
                        filtered_data[col] = val
                product_df = pd.DataFrame([filtered_data])
                styled_df = product_df.style.apply(highlight_min, axis=1)
                st.dataframe(styled_df, use_container_width=True)

if __name__ == '__main__':
    main()
