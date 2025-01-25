import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set up the Streamlit page configuration
st.set_page_config(layout="wide", page_title="Sales Dashboard")

# Load dataset from OneDrive
csv_file_path = r'https://1drv.ms/u/s!9f3ccf37d8e48827?download=1'

# Load the CSV file
try:
    combined_data = pd.read_csv(csv_file_path, parse_dates=['date'], on_bad_lines='skip')  # Load and parse dates
    st.write(combined_data.head())  # Display the first few rows
    st.write(combined_data.columns)  # Print the columns to check
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()  # Stop execution if the file cannot be loaded

# Check if 'date' column exists
if 'date' in combined_data.columns:
    combined_data['Year'] = combined_data['date'].dt.year
else:
    st.error("The 'date' column is missing from the data.")
    st.stop()ar

# Sidebar for user inputs
st.sidebar.header("User  Input Features")
show_data = st.sidebar.checkbox('Show Data', False)

# User input selections
outlet_class = st.sidebar.selectbox('Select Outlet Class', combined_data['outlet class'].unique())
category = st.sidebar.selectbox('Select Category', combined_data['category'].unique())
subcategory = st.sidebar.selectbox('Select Subcategory', combined_data['subcategory'].unique())
year = st.sidebar.selectbox('Select Year', combined_data['Year'].unique()) 

# Filter data based on user input
filtered_data = combined_data[
    (combined_data['outlet class'] == outlet_class) &
    (combined_data['category'] == category) &
    (combined_data['subcategory'] == subcategory) &
    (combined_data['Year'] == year)
]

# Check if filtered_data is empty
if filtered_data.empty:
    st.warning("No data available for the selected filters.")
else:
    # Create tabs for different sections
    tabs = st.tabs(["Charts", "Statistics"])

    # Charts Tab
    with tabs[0]:
        st.header("Sales Overview")
        
        # Total Sales by Month
        sales_by_month = filtered_data.groupby(filtered_data['date'].dt.to_period('M'))['total price'].sum().reset_index()
        sales_by_month['date'] = sales_by_month['date'].dt.to_timestamp()  # Convert back to timestamp for plotting
        
        fig_sales = px.line(sales_by_month, x='date', y='total price', title='Total Sales by Month', markers=True)
        st.plotly_chart(fig_sales, use_container_width=True)

        # Total Quantity by Outlet
        quantity_by_outlet = filtered_data.groupby('outlet name')['quantity'].sum().reset_index()
        fig_quantity = px.bar(quantity_by_outlet, x='outlet name', y='quantity', title='Total Quantity by Outlet', color='quantity', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_quantity, use_container_width=True)

    # Statistics Tab
    with tabs[1]:
        st.header("Summary Statistics")
        st.write(filtered_data.describe())

        # Top 10 Products by Total Price
        top_products = filtered_data.groupby('product name_x')['total price'].sum().nlargest(10).reset_index()
        st.subheader("Top 10 Products by Total Price")
        fig_top_products = px.bar(top_products, x='product name_x', y='total price', title='Top 10 Products by Total Price')
        st.plotly_chart(fig_top_products, use_container_width=True)

        # Average Order Value by Outlet Class
        avg_order_value_by_outlet = filtered_data.groupby('outlet class')['total price'].mean().reset_index()
        st.subheader("Average Order Value by Outlet Class")
        fig_avg_order_value = px.bar(avg_order_value_by_outlet, x='outlet class', y='total price', title='Average Order Value by Outlet Class')
        st.plotly_chart(fig_avg_order_value, use_container_width=True)

        # Distribution of Total Price
        st.subheader("Distribution of Total Price")
        fig_distribution = px.histogram(filtered_data, x='total price', title='Distribution of Total Price', nbins=30)
        st.plotly_chart(fig_distribution, use_container_width=True)

        # Box Plot of Quantity Distribution
        st.subheader("Box Plot of Quantity Distribution")
        fig_quantity_box = px.box(filtered_data, y='quantity', title='Box Plot of Quantity Distribution')
        st.plotly_chart(fig_quantity_box, use_container_width=True)

# Display dataset sample
if show_data:
    st.header('Dataset Sample')
    st.dataframe(combined_data.head(10))
