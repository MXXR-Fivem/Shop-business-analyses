import streamlit as st
from PIL import Image

st.header('Products Frequently Bought With Chocolate')

col1, col2 = st.columns([3, 2])

with col1:
    image = Image.open('./assets/Chocolate Co-Purchase Bubble.png')
    st.image(image)

with col2:
    st.subheader('Insight')

    st.write("""
The co-purchase analysis reveals that chocolate is frequently bought alongside everyday grocery staples rather than only dessert products.

Bananas and bags of organic bananas appear as the strongest associations, suggesting that chocolate purchases often occur within larger routine grocery baskets rather than impulse snack purchases alone.

Fresh produce such as strawberries, avocados, raspberries and spinach also appear frequently. This indicates that customers tend to buy chocolate during regular grocery shopping trips that include healthy items.

Some chocolate-related products also appear in the list, meaning customers sometimes buy several chocolate products in the same basket.
""")

    st.subheader('Business Opportunities')
    st.write("""
• Cross-category promotions between chocolate and fresh produce
• Bundle offers combining snacks and everyday grocery staples
• Strategic shelf placement near high-frequency products
• Personalized recommendations based on basket composition
""")
