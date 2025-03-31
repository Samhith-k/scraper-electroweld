import streamlit as st
import pandas as pd
from PIL import Image
import re

def clean_prices(prices):
    """
    Cleans a group of price strings by:
      1. Removing HTML tags.
      2. Stripping out all non-numeric, comma, dot, or minus chars.
      3. Returning a comma-separated string of unique cleaned values.
    """
    cleaned = []
    for price in prices:
        if pd.notna(price):
            s = str(price)
            # 1) Remove any HTML tags entirely
            s = re.sub(r"<[^>]*>", "", s)

            # 2) Keep only digits, ., ,, -, (and strip leftover spaces)
            s = re.sub(r"[^0-9.,\-]+", "", s).strip()
            
            # Now s should be mostly numeric with . or , or - 
            # If it's not empty and not already in our list, add it
            if s and s not in cleaned:
                cleaned.append(s)
    return ', '.join(cleaned)

def load_welding_data():
    """Load the welding CSV file."""
    try:
        data = pd.read_csv("combined_csvs/combined_20250327_121553.csv")
        return data
    except Exception as e:
        st.error(f"Error loading Welding CSV file: {e}")
        return None

def load_helmet_data():
    """Load the helmet CSV file."""
    try:
        # Update path if your helmet CSV is located elsewhere
        data = pd.read_csv("combined_csv/helmet_combined_20250330_212159.csv")
        return data
    except Exception as e:
        st.error(f"Error loading Helmet CSV file: {e}")
        return None

def pivot_data(df):
    """
    Pivot the DataFrame so each unique Shop Name becomes a column,
    using BRAND and PRODUCT NAME as the index.
    """
    try:
        # Ensure BRAND is not all NaN; otherwise pivoting will be empty.
        if "BRAND" in df.columns:
            df["BRAND"] = df["BRAND"].fillna("Unknown")

        # Ensure PRODUCT NAME is not all NaN in case that column is empty too.
        if "PRODUCT NAME" in df.columns:
            df["PRODUCT NAME"] = df["PRODUCT NAME"].fillna("NoProductName")

        # Pivot
        pivot_df = df.pivot_table(
            index=["BRAND", "PRODUCT NAME"],
            columns="Shop Name",
            values="Price",
            aggfunc=clean_prices  # Clean up price values during aggregation.
        ).reset_index()
        
        # Convert all column labels to string (avoid multi-index or unexpected dtypes).
        pivot_df.columns = [str(c) for c in pivot_df.columns]

        # Check for duplicate columns
        cols = pivot_df.columns.tolist()
        if len(cols) != len(set(cols)):
            st.warning("Duplicate columns found in pivot DataFrame!")
            st.write("Columns:", cols)

        # Reorder columns so that ELECTROWELD WEBSITE and ELECTROWELD EBAY appear after BRAND, PRODUCT NAME
        all_columns = list(pivot_df.columns)
        new_order = ["BRAND", "PRODUCT NAME"]
        electroweld_columns = ["ELECTROWELD WEBSITE", "ELECTROWELD EBAY"]
        for col in electroweld_columns:
            if col in all_columns:
                new_order.append(col)
        
        # Append everything else not already in new_order
        for col in all_columns:
            if col not in new_order:
                new_order.append(col)
        
        pivot_df = pivot_df[new_order]
        return pivot_df
    except Exception as e:
        st.error(f"Error pivoting data: {e}")
        return None

def highlight_min(row):
    """
    Highlight the minimum (cheapest) price in a row.
    If a cell has multiple prices (comma-separated), only the first is used for numeric comparison.
    """
    numeric_values = []
    for cell in row:
        try:
            # Attempt to convert cell to float (grab the first chunk if multiple comma-separated).
            value_str = str(cell).split(",")[0].strip()
            numeric_values.append(float(value_str))
        except:
            numeric_values.append(float('inf'))
            
    min_value = min(numeric_values)
    is_min = [val == min_value for val in numeric_values]
    # Make sure we return exactly the same number of styles as columns in row
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
        #st.warning(f"{page_title} pivot table is empty or could not be created. Check your CSV data.")
        return

    # Debug info about pivot_df
    #st.write(f"DEBUG: {page_title} pivot_df shape:", pivot_df.shape)
    #st.write(f"DEBUG: {page_title} pivot_df columns:", pivot_df.columns.tolist())

    # Attempt a plain display first (comment this out if not needed)
    try:
        st.write(f"DEBUG: Preview of unstyled {page_title} pivot_df:")
        st.dataframe(pivot_df, use_container_width=True)
    except:
        st.error("Plain pivot_df display crashed. Likely due to structure issues.")
        return

    # -------------------
    # Build filters
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
    
    # All columns except BRAND, PRODUCT NAME are potential "shop" columns
    company_columns = list(pivot_df.columns[2:])  
    selected_companies = st.sidebar.multiselect(f"Filter {page_title} by Companies", company_columns, default=[])
    if not selected_companies:
        selected_companies = company_columns
    
    # -------------------
    # Apply filters
    # -------------------
    pivot_df = pivot_df[
        (pivot_df["BRAND"].isin(selected_brands)) &
        (pivot_df["PRODUCT NAME"].isin(selected_products))
    ]
    
    # Only keep the columns we need
    columns_to_show = ["BRAND", "PRODUCT NAME"] + selected_companies
    columns_to_show = [col for col in columns_to_show if col in pivot_df.columns]
    pivot_df = pivot_df[columns_to_show]

    # If there's no data left, warn and return
    if pivot_df.empty or pivot_df.shape[1] < 3:
        st.warning(f"No {page_title} data to display after filtering. Check your selections or CSV content.")
        return
    
    st.write(f"### {page_title} Price Comparison by Shop")
    
    # Style Choice
    style_choice = st.sidebar.radio(f"{page_title} Table Style", ["Basic", "Styled"])
    
    # If it's not empty, let's show a quick shape:
    #st.write(f"DEBUG: Final {page_title} pivot_df shape (post-filter):", pivot_df.shape)

    if style_choice == "Basic":
        # Show the full pivot table with highlighting
        try:
            styled_df = pivot_df.style.apply(highlight_min, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error during styling the {page_title} DataFrame in Basic mode: {e}")
    else:  # "Styled"
        # Display each product row individually
        for i, (_, row) in enumerate(pivot_df.iterrows()):
            product_data = row.to_dict()
            filtered_data = {
                "BRAND": product_data.get("BRAND"),
                "PRODUCT NAME": product_data.get("PRODUCT NAME")
            }
            # Only include columns with non-empty values
            for col in selected_companies:
                val = product_data.get(col)
                if pd.notna(val) and val != "" and val != "nan":
                    filtered_data[col] = val
            
            # If there’s no actual shop data here, skip
            if len(filtered_data) <= 2:  # only BRAND & PRODUCT NAME
                continue

            product_df = pd.DataFrame([filtered_data])

            # Debug: show the mini DataFrame before styling
            st.write(f"DEBUG: Mini DataFrame for {page_title} row {i}: shape={product_df.shape}")
            st.dataframe(product_df)  # unstyled, to ensure it renders

            try:
                styled_df = product_df.style.apply(highlight_min, axis=1)
                st.dataframe(styled_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error styling mini DataFrame for row {i} ({page_title}): {e}")

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
