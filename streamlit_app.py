import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Data App Assignment, on March 17th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Interactive Analysis")

# Add Profit_Margin column (safely avoid divide-by-zero)
df['Profit_Margin'] = df['Profit'] / df['Sales'].replace(0, pd.NA)

# Global average profit margin (for delta reference)
overall_avg_margin = df['Profit_Margin'].mean()

# Reset index for filtering by Category/Sub-Category
df_reset = df.reset_index()

# (1) Dropdown for Category
category = st.selectbox("Select Category", df_reset['Category'].unique())

# (2) Multi-select for Sub-Category filtered by selected Category
available_subcats = df_reset[df_reset['Category'] == category]['Sub_Category'].unique()
selected_subcats = st.multiselect("Select Sub-Category(s)", available_subcats)

# Filter the data
filtered_df = df_reset[
    (df_reset['Category'] == category) &
    (df_reset['Sub_Category'].isin(selected_subcats))
]

# Only show visuals/metrics if sub-categories are selected
if not filtered_df.empty:

    # (3) Line chart of sales for selected items (grouped monthly)
    sales_by_month_filtered = (
        filtered_df
        .set_index('Order_Date')
        .groupby(pd.Grouper(freq='M'))['Sales']
        .sum()
        .reset_index()
    )

    st.subheader("Sales Over Time for Selected Sub-Categories")
    st.line_chart(sales_by_month_filtered.set_index("Order_Date"))

    # (4) Show metrics
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    profit_margin = (total_profit / total_sales) if total_sales != 0 else 0
    delta_margin = profit_margin - overall_avg_margin

    st.subheader("Key Metrics for Selected Items")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Profit Margin", f"{profit_margin * 100:.2f}%", f"{delta_margin * 100:+.2f}%")

else:
    st.info("Please select at least one sub-category to view results.")

st.write("### (1) add a drop down for Category (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)")
st.write("### (2) add a multi-select for Sub_Category *in the selected Category (1)* (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)")
st.write("### (3) show a line chart of sales for the selected items in (2)")
st.write("### (4) show three metrics (https://docs.streamlit.io/library/api-reference/data/st.metric) for the selected items in (2): total sales, total profit, and overall profit margin (%)")
st.write("### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)")
