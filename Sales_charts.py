import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# Set the CSV file path
csv_file_path = 'https://1drv.ms/u/s!9f3ccf37d8e48827?download=1'

try:
    # Make a request to the URL
    response = requests.get(csv_file_path)
    
    # Check if the response is HTML
    if response.headers['Content-Type'] == 'text/html':
        st.error("The URL returned HTML content instead of a CSV file. Please check the link.")
        st.write(response.text)  # Display the HTML content for debugging
    else:
        # Load the CSV file from the response content
        combined_data = pd.read_csv(StringIO(response.text), on_bad_lines='skip')
        
        # Display the first few rows and column names for debugging
        st.write("DataFrame Head:")
        st.write(combined_data.head())
        st.write("Column Names:")
        st.write(combined_data.columns)

        # Clean column names by stripping whitespace
        combined_data.columns = combined_data.columns.str.strip()
        
        # Convert all column names to lowercase to avoid case sensitivity issues
        combined_data.columns = combined_data.columns.str.lower()

        # Check if 'date' column exists
        if 'date' in combined_data.columns:
            # Check the data type of the 'date' column
            st.write("Data type of 'date' column:", combined_data['date'].dtype)
            
            # Convert 'date' to datetime format
            combined_data['date'] = pd.to_datetime(combined_data['date'], errors='coerce')
            
            # Check for NaN values in the 'date' column
            st.write("Number of NaN values in 'date' column:", combined_data['date'].isnull().sum())
            
            # If all values are NaN, raise an error
            if combined_data['date'].isnull().all():
                st.error("The 'date' column could not be converted to datetime.")
                st.stop()
            
            # Create a new 'Year' column
            combined_data['Year'] = combined_data['date'].dt.year
        else:
            st.error("The 'date' column is missing from the data.")
            st.stop()

except Exception as e:
    st.error(f"Error loading data: {e}")

# Sidebar for user inputs
st.sidebar.header("User   Input Features")
show_data = st.sidebar.checkbox('Show Data', False)

# User input selections
if 'outlet class' in combined_data.columns:
    outlet_class = st.sidebar.selectbox('Select Outlet Class', combined_data['outlet class'].unique())
else:
    st.error("The 'outlet class' column is missing from the data.")

if 'category' in combined_data.columns:
    category = st.sidebar.selectbox('Select Category', combined_data['category'].unique())
else:
    st.error("The 'category' column is missing from the data.")

if 'subcategory' in combined_data.columns:
    subcategory = st.sidebar.selectbox('Select Subcategory', combined_data['subcategory'].unique())
else:
    st.error("The 'subcategory' column is missing from the data.")

if 'Year' in combined_data.columns:
    year = st.sidebar.selectbox('Select Year', combined_data['Year'].unique())
else:
    st.error("The 'Year' column is missing from the data.")

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
