import streamlit as st
from PIL import Image

st.header('Top Selling Products')

col1, col2 = st.columns([3, 2])

with col1:
    image = Image.open('./assets/bestsellers.png')
    st.image(image)

with col2:
    st.subheader('Insight')

    st.write("""
The ranking shows that everyday grocery dominate sales.

These products are frequently reordered and represent the core of customer baskets.
""")

    st.subheader('Business Opportunities')

    st.write("""
• Ensure constant stock availability
• Highlight bestsellers on the homepage
• Use them in promotional campaigns
• Optimize store placement
""")
