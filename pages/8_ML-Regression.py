import joblib
import pandas as pd
import streamlit as st

from data_loader import order_product, orders, products

st.header('ML Regression - Predict days before next reorder')


def load_model(model_name: str = './models/model_regression.joblib'):
    """
    Load the trained ML model saved with joblib.
    The file contains a bundle where the model is stored under the key 'model'.

    # Parameters
        **model_name** : The model name

    # Returns
        The model instance
    """

    bundle = joblib.load(model_name)

    return bundle['model']


model = load_model()


def build_features_for_user_product(
    user_id: int,
    product_id: int,
    orders: pd.DataFrame,
    order_product: pd.DataFrame,
    products: pd.DataFrame,
):
    """
    Predict whether a user will reorder a product in their next order.

    # Parameters
        **user_id** : User identifier
        **product_id** : Product identifier
        **orders** : pd.DataFrame, must contain at least: ['order_id', 'user_id', 'order_number', 'order_hour_of_day', 'days_since_prior_order']
        **order_product** : pd.DataFrame, must contain at least: ['order_id', 'product_id', 'add_to_cart_order']
        **products** : pd.DataFrame, must contain at least: ['product_id', 'aisle_id', 'department_id']

    #Returns
        dict of prediction payload with probability and binary prediction.
    """

    # Get product metadata (aisle + department)
    product_row = products.loc[products['product_id'] == product_id]

    # Get all orders made by the user
    user_orders = orders.loc[orders['user_id'] == user_id].copy()

    # Sort orders chronologically
    user_orders = user_orders.sort_values('order_number').copy()

    # First order has NaN days since prior order → replace with 0
    user_orders['days_since_prior_order'] = user_orders['days_since_prior_order'].fillna(0)

    user_order_ids = user_orders['order_id'].unique()

    # Retrieve all products bought in the user's orders
    user_order_products = order_product.loc[order_product['order_id'].isin(user_order_ids)].copy()

    # Merge order metadata with purchased products
    user_history = user_order_products.merge(
        user_orders[
            ['order_id', 'user_id', 'order_number', 'order_hour_of_day', 'days_since_prior_order']
        ],
        on='order_id',
        how='inner',
    )

    # Add product category information
    user_history = user_history.merge(
        products[['product_id', 'aisle_id', 'department_id']],
        on='product_id',
        how='left',
    )

    # Keep only rows related to the selected product
    user_product_history = user_history.loc[user_history['product_id'] == product_id].copy()

    # Number of times the user bought this product
    user_product_count = int(len(user_product_history))

    # Total number of orders made by the user
    user_total_orders = int(user_orders['order_id'].nunique())

    # Ratio of orders containing this product
    user_product_order_ratio = (
        user_product_count / user_total_orders if user_total_orders > 0 else 0.0
    )

    # Last order index
    last_order_number = int(user_orders['order_number'].max())

    # Last order where this product was purchased
    last_product_order_number = int(user_product_history['order_number'].max())

    # Number of orders since last purchase of this product
    orders_since_last_purchase = int(last_order_number - last_product_order_number)

    # Average position of the product inside the basket
    avg_add_to_cart_order = float(user_product_history['add_to_cart_order'].mean())

    # Average basket size of the user
    basket_sizes = user_order_products.groupby('order_id').size()
    avg_basket_size = float(basket_sizes.mean())

    # Compute cumulative days to build a timeline of purchases
    user_orders['cumulative_days'] = user_orders['days_since_prior_order'].cumsum()

    # Extract timeline for this product
    user_product_days = (
        user_product_history.merge(
            user_orders[['order_id', 'cumulative_days']], on='order_id', how='left'
        )[['order_id', 'cumulative_days']]
        .drop_duplicates()
        .sort_values('cumulative_days')
    )

    # Days between each purchase of this product
    days_between = user_product_days['cumulative_days'].diff()

    # Check if product was bought multiple times
    has_multiple_purchases = bool(days_between.notna().any())

    if has_multiple_purchases:
        avg_days_between_user_product_orders = float(days_between.mean())
    else:
        # Special value used when only one purchase exists
        avg_days_between_user_product_orders = -1.0

    # Average hour of day when the user buys this product
    avg_order_hour_for_user_product = float(user_product_history['order_hour_of_day'].mean())

    # Average days between all user orders
    user_avg_days_between_orders = float(user_orders['days_since_prior_order'].mean())

    # Product global statistics

    all_product_orders = order_product.loc[order_product['product_id'] == product_id].copy()

    all_product_orders = all_product_orders.merge(
        orders[['order_id', 'user_id']], on='order_id', how='inner'
    )

    product_user_counts = all_product_orders.groupby('user_id').size().reset_index(name='count')

    # Number of unique users who bought the product
    user_bought = int(product_user_counts['user_id'].nunique())

    # Number of users who reordered the product
    user_reordered = int((product_user_counts['count'] > 1).sum())

    # Reorder probability of this product
    product_reorder_ratio = user_reordered / user_bought if user_bought > 0 else 0.0

    total_order_product_rows = len(order_product)

    product_total_purchases = int((order_product['product_id'] == product_id).sum())

    # Product popularity in the dataset
    product_total_purchases_ratio = (
        product_total_purchases / total_order_product_rows if total_order_product_rows > 0 else 0.0
    )

    aisle_id = int(product_row['aisle_id'].iloc[0])
    department_id = int(product_row['department_id'].iloc[0])

    # Final feature vector used by the ML model
    row = {
        'aisle_id': aisle_id,
        'department_id': department_id,
        'user_product_count': user_product_count,
        'user_total_orders': user_total_orders,
        'user_product_order_ratio': user_product_order_ratio,
        'orders_since_last_purchase': orders_since_last_purchase,
        'avg_add_to_cart_order': avg_add_to_cart_order,
        'avg_basket_size': avg_basket_size,
        'avg_days_between_user_product_orders': avg_days_between_user_product_orders,
        'has_multiple_purchases': has_multiple_purchases,
        'df_avg_ordr_hour_for_user_pr': avg_order_hour_for_user_product,
        'user_avg_days_between_orders': user_avg_days_between_orders,
        'product_reorder_ratio': product_reorder_ratio,
        'product_total_purchases_ratio': product_total_purchases_ratio,
    }

    return pd.DataFrame([row])


def predict_days_until_next_reorder_for_user_product(
    model,
    user_id,
    product_id,
    orders,
    order_product,
    products,
):
    """
    Predict when customer will reorder the product.

    # Parameters
        **model** : Model instance
        **user_id** : User unique identifier
        **product_id** : Product unique identifier
        **orders : Orders dataset
        **order_products** : Order products dataset
        **products** : Products dataset

    # Returns
        Dict of : User id, product id, prediction and features used list
    """
    X_one = build_features_for_user_product(
        user_id=user_id,
        product_id=product_id,
        orders=orders,
        order_product=order_product,
        products=products,
    )

    pred_days = float(model.predict(X_one)[0])

    return pred_days


# Fake client names mapped to user_id
client_names = [
    'Theo',
    'Simon',
    'Romain',
    'Mathieu',
    'Lorenzo',
    'Raphael',
    'Jules',
    'Alexandre',
    'Jean',
    'Laurent',
    'Karen',
    'Leo',
    'Mia',
    'Pablo',
    'Pauline',
    'Paul',
    'Quentin',
    'Rose',
    'Sam',
    'Floriant',
    'Victoria',
    'Victor',
    'Margaux',
    'Xavier',
    'Zachary',
    'Dorian',
    'Rima',
    'Francois',
    'Damien',
    'Melissandre',
]

selected_client = st.selectbox('Client', client_names)

user_id = client_names.index(selected_client) + 1

# Retrieve products already bought by the user
user_orders_ids = orders.loc[orders['user_id'] == user_id, 'order_id']

user_products = order_product[order_product['order_id'].isin(user_orders_ids)][
    'product_id'
].unique()

user_products_df = products[products['product_id'].isin(user_products)]

product_dict = dict(
    zip(user_products_df['product_name'], user_products_df['product_id'], strict=False)
)

selected_product = st.selectbox('Product already bought', list(product_dict.keys()))

product_id = product_dict[selected_product]


if st.button('Predict days before reorder'):
    days = predict_days_until_next_reorder_for_user_product(
        model=model,
        user_id=user_id,
        product_id=product_id,
        orders=orders,
        order_product=order_product,
        products=products,
    )

    st.subheader('Prediction')

    # Convert decimal days into days + hours
    full_days = int(days)
    hours = int((days - full_days) * 24)

    st.write(
        'Estimated time before next purchase',
        f'{full_days} days' + (hours > 0 and f' and {hours} hours' or '') + ".",
    )
