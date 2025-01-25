import streamlit as st
import pymysql
import pandas as pd
import re 
from datetime import datetime
# Creating Empty DataFrame and Storing it in variable df
filtered_data = pd.DataFrame()

# Connect to MySQL database
def get_connection():
    return pymysql.connect(
         host = 'localhost', user = 'root', 
         password = '12345', database = 'guvi_project')

#Function to fetch state
def fetch_state_name(connection):
    query = f"SELECT DISTINCT state FROM bus_routes  ORDER BY state"
    state = pd.read_sql(query, connection)['state'].tolist()
    return state;

# Function to fetch route names starting with a specific letter, arranged alphabetically
def fetch_route_names(connection,selected_state):
    query = f"SELECT DISTINCT route_name FROM bus_routes WHERE state= %s  ORDER BY route_name"
    route_names = pd.read_sql(query, connection,params=(selected_state))['route_name'].tolist()
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


def filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order=3500,departing_time='23:59:59',reaching_time='23:59:59',selected_ratings=5,selected_bus_types='',seats_available=70):

    if selected_bus_types =='A/C Seater':
        bus_type_filter =' AND (UPPER(bustype) LIKE %s OR UPPER(bustype) LIKE %s OR UPPER(bustype) LIKE %s  OR UPPER(bustype) LIKE %s AND (UPPER(bustype) NOT LIKE %s  AND UPPER(bustype)  LIKE %s))'  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,'%A/C%','%A.C.%','%A.C%','%AC%','%NON%','%SEATER%')
    elif selected_bus_types =='A/C Sleeper':
        bus_type_filter =' AND (UPPER(bustype) LIKE %s OR UPPER(bustype) LIKE %s OR UPPER(bustype) LIKE %s  OR UPPER(bustype) LIKE %s AND (UPPER(bustype) NOT LIKE %s  AND UPPER(bustype)  LIKE %s))'  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%A/C%","%A.C.%","%A.C%","%AC%","%NON%","%SLEEPER%")
    elif selected_bus_types =='Non A/C Seater':
        bus_type_filter =' AND UPPER(bustype) LIKE %s AND UPPER(bustype)  LIKE %s '  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%NON%","%SEATER%")
    elif selected_bus_types =='Non A/C Sleeper':
        bus_type_filter =' AND UPPER(bustype) LIKE %s AND UPPER(bustype)  LIKE %s '  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%NON%","%SLEEPER%")
    elif selected_bus_types =='MULTI AXLE':
        bus_type_filter =' AND UPPER(bustype) LIKE %s'  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%MULTI%")
    elif selected_bus_types =='Semi Sleeper':
        bus_type_filter =' AND UPPER(bustype) LIKE %s'  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%SEMI%")
    elif selected_bus_types =='Push Back':
        bus_type_filter =' AND UPPER(bustype) LIKE %s'  
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available,"%PUSH%")
    else:
        bus_type_filter=""
        params=(selected_state,selected_source.strip()+" to "+selected_destination.strip(),price_sort_order,departing_time,reaching_time,selected_ratings,seats_available)


    departing_time=datetime.strptime(departing_time, '%H:%M:%S').time()
    reaching_time=datetime.strptime(reaching_time, '%H:%M:%S').time()
    
    query = f"SELECT * FROM bus_routes WHERE state = %s AND route_name = %s  AND price <= %s AND departing_time <= %s AND  reaching_time <= %s AND star_rating <= %s AND seats_available <= %s "+ bus_type_filter +" ORDER BY star_rating DESC"
    
    output_filtered_data = pd.read_sql(query, connection, params=params)
    
    if len(output_filtered_data) >0:
        output_filtered_data['departing_time'] =(output_filtered_data['departing_time'].dt.components[['hours','minutes','seconds']].astype(str).agg(':'.join,axis=1))
        output_filtered_data[f"departing_time"]=pd.to_datetime(output_filtered_data[f"departing_time"],format='%H:%M:%S').dt.time
        output_filtered_data['reaching_time'] = (output_filtered_data['reaching_time'].dt.components[['hours','minutes','seconds']].astype(str).agg(':'.join,axis=1))
        output_filtered_data[f"reaching_time"]=pd.to_datetime(output_filtered_data[f"reaching_time"],format='%H:%M:%S').dt.time
    return output_filtered_data

# Main Streamlit app
def main():
    st.header("Welcome to Yugan Booking service")

    connection = get_connection()

    try:

        state_data = fetch_state_name(connection)
        selected_state = st.sidebar.selectbox('Select State', state_data,index=None,placeholder="enter state")

        if selected_state:
            source_place,destination_place= fetch_route_names(connection,selected_state)        
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
                            price_sort_order = st.sidebar.number_input('Sort by Price', min_value=0,max_value=3500,step=500,value=0,label_visibility="visible",placeholder="Select price to filter")
                            if price_sort_order >0:
                                filtered_data =filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order)
                            else :
                                price_sort_order=3500
                            #Time
                            time_order_filtered=st.sidebar.time_input('Filter by Departing time',value=None,label_visibility="visible")
                            if time_order_filtered:
                                time_order_filtered=str(time_order_filtered)
                                filtered_data = filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order,time_order_filtered)
                            else:
                                time_order_filtered='23:59:59'


                            reaching_time_order_filtered=st.sidebar.time_input('Filter by reaching_time',value=None, label_visibility="visible")
                            if reaching_time_order_filtered:
                                reaching_time_order_filtered=str(reaching_time_order_filtered)
                                filtered_data = filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order,time_order_filtered,reaching_time_order_filtered) 
                            else:
                                reaching_time_order_filtered='23:59:59'                            
                                
                            # Filter by Star_Rating and Bus_Type
                            selected_ratings = st.sidebar.slider("Sort by Star Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
                            if selected_ratings>0.0:
                                filtered_data = filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order,time_order_filtered,reaching_time_order_filtered, selected_ratings)
                            else:
                                selected_ratings=5                            

                            #bus_types = data['bustype'].unique().tolist()
                            selected_bus_types = st.sidebar.selectbox('Filter by Bus Type', ['A/C Seater','A/C Sleeper','Non A/C Seater','Non A/C Sleeper','Push Back','MULTI AXLE','Semi Sleeper'],index=None)
                            if selected_bus_types:
                                filtered_data = filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order,time_order_filtered,reaching_time_order_filtered, selected_ratings,  selected_bus_types)

                            #seats= data['seats_available'].unique().tolist()
                            seats_available=st.sidebar.selectbox('Enter by Seat Availability',[10,20,30,40,50,60,70],index=None,placeholder="Select seats_available to filter")
                            if seats_available: 
                                filtered_data =filter_data(connection,selected_state,selected_source,selected_destination,price_sort_order,time_order_filtered,reaching_time_order_filtered, selected_ratings,  selected_bus_types,seats_available)
                            else:
                                seats_available=70

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