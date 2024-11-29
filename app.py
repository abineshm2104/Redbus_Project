import streamlit as st
import pymysql
import pandas as pd

# Connect to MySQL database
def get_connection():
    return pymysql.connect(
         host = 'localhost', user = 'root', 
         password = '12345', database = 'guvi_project')

# Function to fetch route names starting with a specific letter, arranged alphabetically
def fetch_route_names(connection, starting_letter):
    query = f"SELECT DISTINCT route_name FROM bus_routes WHERE route_name LIKE '{starting_letter}%' ORDER BY route_name"
    route_names = pd.read_sql(query, connection)['route_name'].tolist()
    return route_names

# Function to fetch data from MySQL based on selected Route_Name and price sort order
def fetch_data(connection, route_name, price_sort_order):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = f"SELECT * FROM bus_routes WHERE route_name = %s ORDER BY start_rating DESC, price {price_sort_order_sql}"
    df = pd.read_sql(query, connection, params=(route_name))
    return df

# Function to filter data based on Star_Rating and Bus_Type
def filter_data(df, star_ratings, bus_types):
    filtered_df = df[df['start_rating'].isin(star_ratings) & df['bustype'].isin(bus_types)]
    return filtered_df

# Main Streamlit app
def main():
    st.header('Welcome to Yugan Booking service')

    connection = get_connection()

    try:
        # Sidebar - Input for starting letter
        starting_letter = st.sidebar.text_input('Enter starting letter of Route Name', '')

        # Fetch route names starting with the specified letter
        if starting_letter:
            route_names = fetch_route_names(connection, starting_letter.upper())

            if route_names:
                # Sidebar - Selectbox for Route_Name
                selected_route = st.sidebar.radio('Select Route Name', route_names)

                if selected_route:
                    # Sidebar - Selectbox for sorting preference
                    price_sort_order = st.sidebar.selectbox('Sort by Price', ['Low to High', 'High to Low'])

                    # Fetch data based on selected Route_Name and price sort order
                    data = fetch_data(connection, selected_route, price_sort_order)

                    if not data.empty:
                        # Display data table with a subheader
                        st.write(f"### Data for Route: {selected_route}")
                        st.write(data)

                        # Filter by Star_Rating and Bus_Type
                        star_ratings = data['start_rating'].unique().tolist()
                        selected_ratings = st.multiselect('Filter by Star Rating', star_ratings)

                        bus_types = data['bustype'].unique().tolist()
                        selected_bus_types = st.multiselect('Filter by Bus Type', bus_types)

                        if selected_ratings and selected_bus_types:
                            filtered_data = filter_data(data, selected_ratings, selected_bus_types)
                            # Display filtered data table with a subheader
                            st.write(f"### Filtered Data for Star Rating: {selected_ratings} and Bus Type: {selected_bus_types}")
                            st.write(filtered_data)
                    else:
                        st.write(f"No data found for Route: {selected_route} with the specified price sort order.")
            else:
                st.write("No routes found starting with the specified letter.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
