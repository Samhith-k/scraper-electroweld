#!/usr/bin/env python3
import pandas as pd
import argparse

def extract_links(input_csv, output_csv):
    # Read CSV and strip header spaces
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    # Forward-fill the product info columns so every row in a product block has them
    product_cols = ["BRAND", "PRODUCT SKU", "PRODUCT NAME"]
    df[product_cols] = df[product_cols].fillna(method="ffill")

    # Standardize the shop names to lowercase (strip spaces as well)
    df["Shop Name"] = df["Shop Name"].astype(str).str.strip().str.lower()

    # Define the set of shop names we care about
    shops_of_interest = {"electroweld ebay", "hampdon", "hampdon ebay"}

    # Filter rows where Shop Name is one of our shops
    df_filtered = df[df["Shop Name"].isin(shops_of_interest)]

    # Pivot the filtered DataFrame so that each product becomes one row and
    # each distinct shop becomes its own column with its PRODUCT LINK
    pivot_df = df_filtered.pivot_table(
        index=["BRAND", "PRODUCT SKU", "PRODUCT NAME"],
        columns="Shop Name",
        values="PRODUCT LINK",
        aggfunc="first"
    ).reset_index()
    pivot_df.columns.name = None  # remove pivot column grouping

    # Create our output columns:
    # - For electroworld, use the link from "electroweld ebay" (if present)
    pivot_df["electroworld"] = pivot_df.get("electroweld ebay", "")

    # - For hampdon, if "hampdon ebay" exists use it; otherwise use "hampdon" (if present)
    pivot_df["hampdon"] = pivot_df.get("hampdon ebay", pivot_df.get("hampdon", ""))

    # Select final columns in the desired order:
    final_cols = ["BRAND", "PRODUCT SKU", "PRODUCT NAME", "electroworld", "hampdon"]
    final_df = pivot_df[final_cols]

    # Write the final DataFrame to CSV
    final_df.to_csv(output_csv, index=False)
    print(f"Wrote {len(final_df)} products to '{output_csv}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Extract electroweld ebay (as electroworld) and Hampdon/Hampdon ebay links for each product."
    )
    parser.add_argument("input_csv", help="Path to the input CSV file.")
    parser.add_argument("output_csv", help="Path for the output CSV file.")
    args = parser.parse_args()
    extract_links(args.input_csv, args.output_csv)

if __name__ == "__main__":
    main()
