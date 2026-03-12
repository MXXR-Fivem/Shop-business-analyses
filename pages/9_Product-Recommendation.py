import pandas as pd
import streamlit as st

from data_loader import aisles, departments, order_product, products

st.header('Product Recommendation')

# DATA PREPARATION

# Merge products with aisles using the 'aisle_id' key
products_with_aisles = pd.merge(products, aisles, on='aisle_id')

# Then add departments by merging using 'department_id'
products_with_aisles_and_departments = products_with_aisles.merge(departments, on='department_id')

# Finally merge order products with all product information
# This allows us to have in a single DataFrame:
# - the order
# - the product
# - the aisle
# - the department
orders_products_with_full_product_information = order_product.merge(
    products_with_aisles_and_departments, on='product_id'
)

def get_best_sellers() -> object:
    """
    Returns the best-selling products of the store.

    ## Parameters
        None

    ## Returns
        DataFrame containing:
        - the number of orders
        - the product name
    """

    # Count how many times each product appears in orders
    counts_df = order_product['product_id'].value_counts().reset_index()

    # Rename columns for better readability
    counts_df.columns = ['product_id', 'count']

    # Retrieve product names by merging with the products table
    counts_df = counts_df.merge(products, on='product_id').loc[:, ['count', 'product_name']]

    # Return the final DataFrame
    return counts_df


def get_reco_product(
    product_name: str, n: int = 3, percent: int | float | None = None
) -> list[str]:
    """
    Returns the products most frequently purchased in the same order
    as the selected product.

    ## Parameters
        product_name : Product name (case insensitive)
        n : Maximum number of recommendations
        percent : Minimum appearance rate in recommendations

    ## Returns
        List of recommended product names
    """

    # Check parameter types
    if not isinstance(product_name, str) or not isinstance(n, int):
        raise TypeError

    # Ensure the product name is not empty
    elif not product_name:
        raise ValueError

    # List that will contain recommendations
    reco = []

    # RETRIEVE ORDERS

    # Get the IDs of orders that contain the selected product
    product_orders = orders_products_with_full_product_information[
        orders_products_with_full_product_information['product_name'] == product_name
    ]['order_id']

    # SEARCH FOR ASSOCIATED PRODUCTS

    # Retrieve other products present in the same orders
    reco_global = orders_products_with_full_product_information[
        (orders_products_with_full_product_information['product_name'] != product_name)
        & (orders_products_with_full_product_information['order_id'].isin(product_orders))
    ]

    # CALCULATE THE MOST FREQUENT PRODUCTS

    # Count how many times each product appears
    reco_global = (
        reco_global.groupby('product_name')
        .size()
        .sort_values(ascending=False)
        .reset_index(name='count')
    )

    # Keep only the top n products
    reco_global_head = reco_global.head(n)

    # OPTIONAL PERCENTAGE FILTER

    if percent is not None:
        # Calculate the appearance rate of each product
        reco_global_head['rate'] = (
            reco_global_head['count'] / reco_global_head['count'].sum()
        ) * 100

        # Keep only products with a rate above the threshold
        reco_global_head = reco_global_head[reco_global_head['rate'] >= percent]

        # Add products to the recommendation list
        reco.extend(reco_global_head['product_name'].to_list())

    else:
        # If no percentage filter is applied: directly add products
        reco.extend(reco_global_head['product_name'].to_list())

    return reco


# STREAMLIT INTERFACE

# Create two tabs in the application
tab1, tab2 = st.tabs(['Global recommendation', 'Product page recommendation'])

# TAB 1 : BEST SELLERS
with tab1:
    # Slider allowing the user to choose the number of products to display
    n_products = st.slider('Number of products to recommend', 1, 20, 5)

    # Retrieve the best-selling products
    best_sellers = get_best_sellers().head(n_products)

    # Shift index so it starts at 1 instead of 0
    best_sellers.index = best_sellers.index + 1

    # Display the results in an interactive table
    st.dataframe(best_sellers)

# TAB 2 : PRODUCT RECOMMENDATION
with tab2:
    # Unique list of product names
    product_list = products['product_name'].unique()

    # Dropdown menu allowing the user to select a product
    selected_product = st.selectbox('Select a product', product_list)

    # Choose the number of recommendations
    n_products = st.slider('Number of products', 1, 10, 3)

    # Slider to define a minimum appearance percentage
    percent = st.slider('Minimum purchase rate (%)', 0.0, 100.0, 0.0, 1.0)

    # Button to trigger the recommendation process
    if st.button('Get recommendations'):
        # Call the recommendation function
        reco = get_reco_product(
            product_name=selected_product, n=n_products, percent=percent if percent > 0 else None
        )

        # Display the results
        if reco:
            st.write(reco)
        else:
            st.write('No recommendation found')
