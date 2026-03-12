import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    orders = pd.read_csv('./datasets/orders.csv')
    order_product = pd.read_csv('./datasets/order_products.zip')
    products = pd.read_csv('./datasets/products.csv')
    aisles = pd.read_csv('./datasets/aisles.csv')
    departments = pd.read_csv('./datasets/departments.csv')

    return orders, order_product, products, aisles, departments

orders, order_product, products, aisles, departments = load_data()