import streamlit as st
import pymysql
import pandas as pd

# Creating Empty DataFrame and Storing it in variable df
filtered_data = pd.DataFrame()

# Connect to MySQL database
def get_connection():
    return pymysql.connect(
         host = 'localhost', user = 'root', 
         password = '12345', database = 'guvi_project')

# Function to fetch route names starting with a specific letter, arranged alphabetically
def fetch_route_names(connection):
    query = f"SELECT DISTINCT route_name FROM bus_routes  ORDER BY route_name"
    route_names = pd.read_sql(query, connection)['route_name'].tolist()
    source_place=[]
    destination_place=[]
    if route_names:
        for i in route_names:
            source_place.append(i.split("to")[0].strip())
            destination_place.append(i.split("to")[1].strip())
        
        source_place=list(set(source_place))
        source_place.sort()
        destination_place=list(set(destination_place))
        destination_place.sort()

    return source_place,destination_place

# Function to fetch data from MySQL based on selected Route_Name 
def fetch_data(connection,selected_source,selected_destination):
    query = f"SELECT * FROM bus_routes WHERE route_name = %s ORDER BY star_rating DESC"
    df = pd.read_sql(query, connection, params=(selected_source.strip()+" to "+selected_destination.strip()))
    if len(df) >1:
        df['departing_time'] =(df['departing_time'].dt.components[['hours','minutes','seconds']].astype(str).agg(':'.join,axis=1))
        df['reaching_time'] = (df['reaching_time'].dt.components[['hours','minutes','seconds']].astype(str).agg(':'.join,axis=1))
    return df

#Function to filter based on rating
def rating_filter_data(df,star_ratings):
    rating_filtered_df=df[df['star_rating'].between(0.0,star_ratings)]
    return rating_filtered_df
#Function to filter based on bus type
def bus_type_filter_data(df,bus_type):
    bus_type_filter_df=df[df['bustype'].isin(bus_type)]    
    return bus_type_filter_df
#Function to filter based on price
def Sort_by_Price(df, price_sort_order):
    if price_sort_order =='Below 500':
        price_filtered_df=df[df['price'] < 500 ]
    elif price_sort_order=='500 to 1000':
        price_filtered_df=df[df['price'].between(500, 1000)]
    elif price_sort_order=='Above 1000':
        price_filtered_df=df[df['price']>1000]
    return price_filtered_df
def time_order_filtered_data(df,time_order_filtered,column_name):
    df[f"{column_name}"]=pd.to_datetime(df[f"{column_name}"],format='%H:%M:%S')
    if time_order_filtered=="Before 6.am":
        time_filtered_data =df[(df[f"{column_name}"]>=pd.to_datetime('00:00:00',format='%H:%M:%S')) & (df[f"{column_name}"]<=pd.to_datetime('05:59:59',format='%H:%M:%S'))]
    elif time_order_filtered=='6am to 12pm':
        time_filtered_data=df[(df[f"{column_name}"]>=pd.to_datetime('06:00:00',format='%H:%M:%S')) & (df[f"{column_name}"]<=pd.to_datetime('11:59:59',format='%H:%M:%S'))]
    elif time_order_filtered=='12pm to 6pm':
        time_filtered_data=df[(df[f"{column_name}"]>=pd.to_datetime('12:00:00',format='%H:%M:%S')) & (df[f"{column_name}"]<=pd.to_datetime('17:59:59',format='%H:%M:%S'))]
    else:
        time_filtered_data= df[(df[f"{column_name}"]>=pd.to_datetime('18:00:00',format='%H:%M:%S')) & (df[f"{column_name}"]<=pd.to_datetime('23:59:59',format='%H:%M:%S'))]
    time_filtered_data[f"{column_name}"] =time_filtered_data[f"{column_name}"].dt.time
    return time_filtered_data
    #Function to filter based on seat available

def seat_availability_list(df,seats_available):
    seat_available_filtered_data=df[df['seats_available']==seats_available]
    return seat_available_filtered_data

# Main Streamlit app
def main():
    st.header('Welcome to Yugan Booking service')

    connection = get_connection()

    try:

        source_place,destination_place= fetch_route_names(connection)        
        # Sidebar - Input for source place
        selected_source = st.sidebar.selectbox('Select source place', source_place,index=None,placeholder="enter source place")
        if selected_source :
            #destination_place.remove(selected_source)
            # Sidebar - Input for destination place:
            if selected_source in destination_place:
                destination_place.remove(selected_source)
                
            selected_destination = st.sidebar.selectbox('Select destination place', destination_place,index=None,placeholder="enter destination place")
                    
            if selected_destination:
                # Fetch data based on selected Route_Name
                data = fetch_data(connection,selected_source,selected_destination)
                
                if not data.empty:
                    # Display data table with a subheader
                    st.write(f"### Data for Route: {selected_source} to {selected_destination}")
                    st.write(data)

                    rowcount=len(data)
                    if rowcount >1:                            
                        filtered_data =data;

                        # Sidebar - Selectbox for sorting preference
                        price_sort_order = st.sidebar.selectbox('Sort by Price', ['Below 500', '500 to 1000','Above 1000'],index=None,placeholder="Select price to filter")
                        if price_sort_order:
                            filtered_data =Sort_by_Price(filtered_data,price_sort_order)
                        #Time
                        time_order_filtered=st.sidebar.selectbox('Filter by Departing time', ['Before 6am', '6am to 12pm','12pm to 6pm','After 6pm'],index=None,placeholder="Select time to filter")
                        if time_order_filtered:
                            filtered_data = time_order_filtered_data(filtered_data,time_order_filtered,'departing_time')


                        reaching_time_order_filtered=st.sidebar.selectbox('Filter by reaching_time', ['Before 6am', '6am to 12pm','12pm to 6pm','After 6pm'],index=None,placeholder="Select time to filter")
                        if reaching_time_order_filtered:
                            filtered_data = time_order_filtered_data(filtered_data,reaching_time_order_filtered,'reaching_time') 
 

                         
                            
                        # Filter by Star_Rating and Bus_Type
                        selected_ratings = st.sidebar.slider("Sort by Star Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
                        if selected_ratings:
                            filtered_data = rating_filter_data(filtered_data, selected_ratings)

                        

                        bus_types = data['bustype'].unique().tolist()
                        selected_bus_types = st.sidebar.multiselect('Filter by Bus Type', bus_types)
                        if selected_bus_types:
                            filtered_data = bus_type_filter_data(filtered_data,  selected_bus_types)

                        seats= data['seats_available'].unique().tolist()
                        seats_available=st.sidebar.selectbox('Enter by Seat Availability',seats,index=None,placeholder="Select seats_available to filter")
                        if seats_available: 
                            filtered_data =seat_availability_list(filtered_data,seats_available)
                        
                        if filtered_data.empty  :                            
                            st.write(f"No data found for Route:{selected_source}  to {selected_destination}")
                        elif filtered_data.equals(data):
                            st.write(f"No data found for Route:{selected_source}  to {selected_destination}")
                        else :
                            st.write(f"### Filtered Data :")
                            st.write(filtered_data)
                else:
                    st.write(f"No data found for Route:{selected_source}  to {selected_destination}")
            else:
                st.write("Please select destination place")
    finally:
        connection.close()

if __name__ == '__main__':
    main()