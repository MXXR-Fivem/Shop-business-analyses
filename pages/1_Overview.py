import streamlit as st

st.header('Project Overview')

col1, col2, col3, col4 = st.columns(4)

col1.metric('Total Orders', '3.4M')
col2.metric('Total Users', '200K')
col3.metric('Total Products', '49K')
col4.metric('Departments', '21')

st.markdown('---')

st.subheader('Objective')

st.markdown("""
The objective of this project is to transform raw grocery transaction data into
actionable business insights.

By analyzing millions of orders we aim to:

• Identify top selling products
• Understand customer shopping patterns
• Detect product associations
• Predict reorder behavior
• Build recommendation systems
""")

st.markdown('---')

st.subheader('Business Questions')

st.markdown("""
- Which products are the bestsellers?
- What other products do users frequently order with chocolate ?
- What aisle and departments have the best selling rate ?
- What are the main customer profiles, such as midnight shopper, casual buyer, or cart addict ?
- Is there a good timing to send an offer to someone based on the last time he ordered ?
- What products should we recommend to a customer ?
- Can we predict whether a customer will reorder a given product in their next order ?
- Can we predict how many days after their last observed order a customer will purchase a given product again ?
""")
