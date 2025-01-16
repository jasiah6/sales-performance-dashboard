import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('data.csv')

# Ensure 'Sales' column is numeric and 'Order Date' is in datetime format
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')

# Create the Month column from the Order Date if not already present
df['Month'] = df['Order Date'].dt.month

# Calculate the Delivery Time (Days between Order Date and Ship Date)
df['Delivery Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# Check if the 'Year' column exists, otherwise create it
if 'Year' not in df.columns:
    df['Year'] = df['Order Date'].dt.year

# Ensure there are no missing values
df = df.dropna(subset=['Sales', 'Delivery Time'])

# Calculate basic metrics
total_sales = df['Sales'].sum()
avg_sales_per_order = df['Sales'].mean()
total_orders = df['Order ID'].nunique()

# Streamlit title and metrics
st.title("Sales Performance Dashboard")
st.metric("Total Sales", f"${total_sales:,.2f}")
st.metric("Average Sales per Order", f"${avg_sales_per_order:,.2f}")
st.metric("Total Orders", total_orders)

# Sidebar Filters for interactivity
st.sidebar.header("Filters")
selected_region = st.sidebar.multiselect("Select Region(s)", options=df['Region'].unique(), default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())
selected_year = st.sidebar.slider("Select Year Range", min_value=int(df['Year'].min()), max_value=int(df['Year'].max()), value=(int(df['Year'].min()), int(df['Year'].max())))

# Filter the data based on the selections
filtered_df = df[
    (df['Region'].isin(selected_region)) &
    (df['Category'].isin(selected_category)) &
    (df['Year'] >= selected_year[0]) &
    (df['Year'] <= selected_year[1])
]

# Sales by Region
sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
fig1 = px.bar(sales_by_region, x='Region', y='Sales', title='Total Sales by Region', color='Sales', color_continuous_scale='Viridis')
st.plotly_chart(fig1)

# Sales Trends Over Time (Year and Month)
sales_by_month = filtered_df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
fig2 = px.line(sales_by_month, x='Month', y='Sales', color='Year', title='Sales Trends Over Time')
st.plotly_chart(fig2)

# Top 10 Products by Sales
top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top_products, x='Product Name', y='Sales', title='Top 10 Products by Sales', color='Sales', color_continuous_scale='YlGnBu')
st.plotly_chart(fig3)

# Sales vs Delivery Time (Scatter plot)
fig4 = px.scatter(filtered_df, x='Delivery Time', y='Sales', title='Sales vs Delivery Time', color='Delivery Time', color_continuous_scale='Plasma')
st.plotly_chart(fig4)

# Histogram for Delivery Time Distribution
fig5 = px.histogram(filtered_df, x='Delivery Time', title='Delivery Time Distribution', color='Region', nbins=30)
st.plotly_chart(fig5)

# Boxplot for Delivery Time by Region
fig6 = px.box(filtered_df, x='Region', y='Delivery Time', title='Delivery Time by Region', color='Region')
st.plotly_chart(fig6)

# Heatmap for Sales vs Delivery Time by Region
plt.figure(figsize=(10, 6))
sales_delivery_heatmap = filtered_df.pivot_table(values='Sales', index='Delivery Time', columns='Region', aggfunc='sum')
sns.heatmap(sales_delivery_heatmap, cmap='YlGnBu', annot=True, fmt='.1f')
st.pyplot(plt)

# Additional Information
st.sidebar.subheader("Dataset Overview")
st.sidebar.write(f"Data contains {len(filtered_df)} rows after applying the selected filters.")
