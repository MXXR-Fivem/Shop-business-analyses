import streamlit as st
from PIL import Image

st.header('Optimal Timing for Promotions')

col1, col2 = st.columns([3, 2])

with col1:
    image = Image.open('./assets/Probability of Reordering Based on Days Since Last Order.png')
    st.image(image)

with col2:
    st.subheader('Insight')
    st.write("""
The probability of a customer reordering varies depending on the number of days since their last purchase.

Understanding this delay allows businesses to identify the most effective moment to send promotional offers.
""")

    st.subheader('Business Opportunities')
    st.write("""
• Send reminders when reorder probability increases
• Trigger targeted promotions before churn risk
• Personalize marketing campaigns based on customer habits
""")
