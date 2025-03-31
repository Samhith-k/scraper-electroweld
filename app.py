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
            cleaned_price = re.sub(r'[a-zA-Z,$<>=/"]', '', s).strip()
            if cleaned_price and cleaned_price not in cleaned:
                cleaned.append(cleaned_price)
    return ', '.join(cleaned)

def load_welding_data():
    try:
        data = pd.read_csv("combined_csvs/combined_20250327_121553.csv")
        return data
    except Exception as e:
        st.error(f"Error loading Welding CSV file: {e}")
        return None

def load_helmet_data():
    """Load the helmet CSV file."""
    try:
        # Update this path if your helmet CSV is located elsewhere
        data = pd.read_csv("combined_csv/helmet_combined_20250330_212159.csv")
        return data
    except Exception as e:
        st.error(f"Error loading Helmet CSV file: {e}")
        return None

def pivot_data(df):
    try:
        if "BRAND" in df.columns:
            df["BRAND"] = df["BRAND"].fillna("Unknown")
        # Pivot the DataFrame so each unique shop becomes a column.
        pivot_df = df.pivot_table(
            index=["BRAND", "PRODUCT NAME"],
            columns="Shop Name",
            values="Price",
            aggfunc=clean_prices  # Clean up price values during aggregation.
        ).reset_index()
        
        # Reorder columns so that ELECTROWELD WEBSITE and ELECTROWELD EBAY (if present)
        # appear right after BRAND and PRODUCT NAME
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
            # Attempt to convert cell (which may be comma-separated) to float.
            value_str = str(cell).split(",")[0].strip()
            numeric_values.append(float(value_str))
        except:
            numeric_values.append(float('inf'))
            
    min_value = min(numeric_values)
    is_min = [val == min_value for val in numeric_values]
    return ['background-color: yellow' if flag else '' for flag in is_min]

def display_comparison_page(df, page_title):
    """
    Reusable function to display a comparison page (for Welders or Helmets).
    df: Loaded DataFrame from CSV
    page_title: A string like "Welders" or "Helmets"
    """
    if df is None:
        return
    
    pivot_df = pivot_data(df)
    if pivot_df is None or pivot_df.empty:
        st.error("Pivot table is empty or could not be created.")
        return

    # -------------------
    # Add Filters
    # -------------------
    all_brands = sorted(pivot_df["BRAND"].unique())
    selected_brands = st.sidebar.multiselect(f"Filter {page_title} by Brand", all_brands, default=[])
    if not selected_brands:
        selected_brands = all_brands
        
    filtered_by_brand = pivot_df[pivot_df["BRAND"].isin(selected_brands)]
    all_products = sorted(filtered_by_brand["PRODUCT NAME"].unique())
    
    selected_products = st.sidebar.multiselect(f"Filter {page_title} by Product Name", all_products, default=[])
    if not selected_products:
        selected_products = all_products
    
    company_columns = list(pivot_df.columns[2:])  # everything after BRAND, PRODUCT NAME
    selected_companies = st.sidebar.multiselect(f"Filter {page_title} by Companies", company_columns, default=[])
    if not selected_companies:
        selected_companies = company_columns
    
    # Apply the filters
    pivot_df = pivot_df[
        (pivot_df["BRAND"].isin(selected_brands)) &
        (pivot_df["PRODUCT NAME"].isin(selected_products))
    ]
    
    # Only keep the columns we need
    columns_to_show = ["BRAND", "PRODUCT NAME"] + selected_companies
    columns_to_show = [col for col in columns_to_show if col in pivot_df.columns]  # guard against missing columns
    pivot_df = pivot_df[columns_to_show]
    
    st.write(f"### {page_title} Price Comparison by Shop")
    
    # Style Choice
    style_choice = st.sidebar.radio(f"{page_title} Table Style", ["Basic", "Styled"])
    
    if style_choice == "Basic":
        # Show the full pivot table with highlighting
        styled_df = pivot_df.style.apply(highlight_min, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:  # "Styled"
        # Create a mini-table per product row
        for _, row in pivot_df.iterrows():
            product_data = row.to_dict()
            filtered_data = {
                "BRAND": product_data.get("BRAND"),
                "PRODUCT NAME": product_data.get("PRODUCT NAME")
            }
            # Show only non-empty columns from the selected companies
            for col in selected_companies:
                val = product_data.get(col)
                if pd.notna(val) and val != "" and val != "nan":
                    filtered_data[col] = val
            
            product_df = pd.DataFrame([filtered_data])
            styled_df = product_df.style.apply(highlight_min, axis=1)
            st.dataframe(styled_df, use_container_width=True)

def main():
    # Set up the page with a logo and config.
    logo_image = Image.open("./app_data/logo-electroweld.jpg")
    st.set_page_config(
        page_title="Hardware Parts Price Comparison",
        page_icon=logo_image,
        layout="wide"
    )
    st.title("Product Price Comparison")
    
    # Navigation
    page = st.sidebar.radio("Navigation", ["Welders Comparison", "Helmet Comparison"])
    
    if page == "Welders Comparison":
        df_welders = load_welding_data()
        display_comparison_page(df_welders, "Welders")
    else:  # "Helmet Comparison"
        df_helmets = load_helmet_data()
        display_comparison_page(df_helmets, "Helmets")

if __name__ == '__main__':
    main()
