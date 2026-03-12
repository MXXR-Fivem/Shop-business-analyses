import streamlit as st
from PIL import Image

st.header('Customer Profiles')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Single Profile Distribution')

    image = Image.open('./assets/Customer Profiles Distribution.png')
    st.image(image)

with col2:
    st.subheader('Multiple Profiles Allowed')

    image = Image.open('./assets/Customer Profiles Distribution (Multiple Profiles Allowed).png')
    st.image(image)

st.markdown('---')

st.subheader('Insight')

st.write("""
Customer segmentation highlights several distinct purchasing behaviors across the platform.

Regular customers represent the vast majority of users when a single profile is assigned, meaning most shoppers follow stable and predictable purchasing patterns.

When multiple profiles are allowed, the analysis reveals a more nuanced behavior. A large portion of customers have characteristics of both casual buyers and cart addicts. This indicates that many users sometimes place small orders but occasionally make large basket purchases.

Cart addicts represent high-value customers due to their consistently large carts, making them an important target for marketing.

Midnight shoppers represent a smaller niche but show clear time-based purchasing habits, suggesting opportunities for targeted promotions or late-night marketing campaigns.
""")

st.subheader('Business Opportunities')

st.write("""
• Loyalty programs targeting regular customers to maintain retention
• Personalized promotions encouraging casual buyers to increase basket size
• Special offers for cart addicts to maximize high-value purchases
• Time-based marketing campaigns targeting late-night shoppers
""")
