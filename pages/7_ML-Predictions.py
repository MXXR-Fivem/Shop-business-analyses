import joblib
import pandas as pd
import streamlit as st

from data_loader import orders, order_product, products

# Streamlit page title
st.header('ML Prediction - Will the user reorder a product?')

# Create two columns for layout
col1, col2 = st.columns(2)

with col1:

    def load_my_model(model_name: str = './models/model.joblib') -> tuple[object, float]:
        """
        Load the trained ML model saved with joblib.
        The file contains a bundle where the model is stored under the key 'model'.

        # Parameters
            **model_name** : The model name

        # Returns
            The model instance
        """

        # Load the serialized model bundle
        bundle = joblib.load(model_name)

        # Extract the trained model
        model = bundle['model']

        return model

    # Load model and threshold when the app starts
    model = load_my_model()


def build_features_for_user_product(
    user_id: int,
    product_id: int,
    orders: pd.DataFrame,
    order_product: pd.DataFrame,
    products: pd.DataFrame,
) -> dict:
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

    user_orders = orders.loc[orders['user_id'] == user_id].copy()

    if user_orders.empty:
        raise ValueError(f'user_id = {user_id} not found in orders.')

    product_row = products.loc[products['product_id'] == product_id]

    if product_row.empty:
        raise ValueError(f'product_id = {product_id} not found in products.')

    user_orders = user_orders.dropna(subset=['order_id', 'user_id', 'order_number']).copy()
    user_orders = user_orders.sort_values('order_number').copy()
    user_orders['days_since_prior_order'] = user_orders['days_since_prior_order'].fillna(0)

    user_order_ids = user_orders['order_id'].unique()

    user_order_products = order_product.loc[order_product['order_id'].isin(user_order_ids)].copy()

    user_history = user_order_products.merge(
        user_orders[
            ['order_id', 'user_id', 'order_number', 'order_hour_of_day', 'days_since_prior_order']
        ],
        on='order_id',
        how='inner',
    )

    user_history = user_history.merge(
        products[['product_id', 'aisle_id', 'department_id']],
        on='product_id',
        how='left',
    )

    user_product_history = user_history.loc[user_history['product_id'] == product_id].copy()
    if user_product_history.empty:
        raise ValueError(f'user_id={user_id} has never bought product_id={product_id}.')

    user_product_count = int(len(user_product_history))

    user_total_orders = int(user_orders['order_id'].nunique())

    user_product_order_ratio = (
        user_product_count / user_total_orders if user_total_orders > 0 else 0.0
    )

    last_order_number = int(user_orders['order_number'].max())
    last_product_order_number = int(user_product_history['order_number'].max())
    orders_since_last_purchase = int(last_order_number - last_product_order_number)

    avg_add_to_cart_order = float(user_product_history['add_to_cart_order'].mean())

    basket_sizes = user_order_products.groupby('order_id').size()
    avg_basket_size = float(basket_sizes.mean())

    user_orders['cumulative_days'] = user_orders['days_since_prior_order'].cumsum()

    user_product_days = (
        user_product_history.merge(
            user_orders[['order_id', 'cumulative_days']],
            on='order_id',
            how='left',
            suffixes=('', '_dup'),
        )[['order_id', 'cumulative_days']]
        .drop_duplicates()
        .sort_values('cumulative_days')
    )

    days_between = user_product_days['cumulative_days'].diff()

    has_multiple_purchases = bool(days_between.notna().any())

    if has_multiple_purchases:
        avg_days_between_user_product_orders = float(days_between.mean())
    else:
        avg_days_between_user_product_orders = -1.0

    avg_order_hour_for_user_product = float(user_product_history['order_hour_of_day'].mean())

    user_avg_days_between_orders = float(user_orders['days_since_prior_order'].mean())

    all_product_orders = order_product.loc[order_product['product_id'] == product_id].copy()
    all_product_orders = all_product_orders.merge(
        orders[['order_id', 'user_id']],
        on='order_id',
        how='inner',
    )

    product_user_counts = all_product_orders.groupby('user_id').size().reset_index(name='count')

    user_bought = int(product_user_counts['user_id'].nunique())
    user_reordered = int((product_user_counts['count'] > 1).sum())

    product_reorder_ratio = user_reordered / user_bought if user_bought > 0 else 0.0

    total_order_product_rows = len(order_product)
    product_total_purchases = int((order_product['product_id'] == product_id).sum())
    product_total_purchases_ratio = (
        product_total_purchases / total_order_product_rows if total_order_product_rows > 0 else 0.0
    )

    aisle_id = int(product_row['aisle_id'].iloc[0])
    department_id = int(product_row['department_id'].iloc[0])

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
    X_one = pd.DataFrame([row])

    return X_one


def predict_next_reorder_for_user_product(
    model,
    user_id: int,
    product_id: int,
    orders: pd.DataFrame,
    order_product: pd.DataFrame,
    products: pd.DataFrame,
    threshold: float = 0.15,
):
    """
    Predict when if customer will reorder the product.

    # Parameters
        **model** : Model instance
        **user_id** : User unique identifier
        **product_id** : Product unique identifier
        **orders : Orders dataset
        **order_product** : Order products dataset
        **products** : Products dataset
        **threshold** : Prediction threshold

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
    proba = float(model.predict_proba(X_one)[:, 1][0])
    pred = int(proba >= threshold)

    return {
        'user_id': user_id,
        'product_id': product_id,
        'probability_reorder_next_order': proba,
        'threshold': threshold,
        'prediction': pred,
        'features_used': X_one.iloc[0].to_dict(),
    }


# List of fake client names (used to map to user_id)
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

# Client selection
selected_client = st.selectbox('Client', client_names)
user_id = client_names.index(selected_client) + 1

# Get products already bought by this user
user_orders_ids = orders.loc[orders['user_id'] == user_id, 'order_id']
user_products = order_product[order_product['order_id'].isin(user_orders_ids)][
    'product_id'
].unique()
product_sample = products[products['product_id'].isin(user_products)].head(20)
product_dict = dict(zip(product_sample['product_name'], product_sample['product_id'], strict=False))

# Product selection
selected_product = st.selectbox('Product', list(product_dict.keys()))
product_id = product_dict[selected_product]

# Prediction threshold slider
threshold = st.slider('Prediction threshold', 0.0, 1.0, 0.15, 0.01)

if st.button('Predict'):
    result = predict_next_reorder_for_user_product(
        model=model,
        user_id=user_id,
        product_id=product_id,
        orders=orders,
        order_product=order_product,
        products=products,
        threshold=threshold,
    )

    # Display results
    st.subheader('Prediction Result')
    st.write('Probability:', f'{round(result["probability_reorder_next_order"], 4) * 100}%')
    answer = 'Yes' if result['prediction'] == 1 else 'No'
    st.write('Will reorder next order:', answer)

    # Optional: show feature values used
    with st.expander('Features used for prediction'):
        st.json(result['features_used'])
