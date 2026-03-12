import streamlit as st
from PIL import Image

st.header('Department & Aisle Performance')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Top Departments')

    image = Image.open('./assets/Top 10 Departments Treemap.png')
    st.image(image)

    st.write("""
The department performance analysis shows that fresh and everyday grocery categories dominate overall sales.

Produce represents the largest share by a large margin, confirming that customers frequently purchase fresh fruits and vegetables during their regular shopping.

Dairy & eggs, snacks, beverages, and frozen products also appear among the top contributors. These categories correspond to common food that are purchased on a weekly basis.

This distribution suggests that the platform is primarily used for routine grocery shopping rather than occasional or specialty purchases.
""")

with col2:
    st.subheader('Top Aisles')

    image = Image.open('./assets/Top 10 Aisles Treemap.png')
    st.image(image)

    st.write("""
At the aisle level, the highest-performing sections are strongly concentrated around fresh products.

Fresh vegetables and fresh fruits clearly dominate the ranking, showing the importance of fresh food in customer baskets.

Other frequently purchased aisles include packaged vegetables & fruits, yogurt, milk, and packaged cheese, indicating that customers often combine fresh produce with dairy products during the same order.

Snack-oriented aisles such as chips & pretzels also appear in the top list, suggesting that customers mix essential groceries with small indulgence products within the same order.
""")
