import pymysql
import pandas as pd
connection = pymysql.connect(
         host = 'localhost', user = 'root', 
         password = '12345', database = 'guvi_project')
cursor = connection.cursor()

create_table_query = f"""create table bus_routes (id int primary key auto_increment ,route_name varchar(250),route_link varchar(250),busname varchar(250),bustype varchar(250),departing_time time,duration varchar(250),reaching_time time,star_rating float,price decimal,seats_available int);"""
cursor.execute(create_table_query)
print("Table Created Successfully")
connection.commit()

csv_files=['ap_bus_details.csv','chandigarh_bus_details.csv','haryana_bus_details.csv','kerala_bus_details.csv','kadamba_bus_details.csv','rajasthan_bus_details.csv','southbengal_bus_details.csv','telugana_bus_details.csv','up_bus_details.csv','westbengal_bus_details.csv']
df = [pd.read_csv(file) for file in csv_files]
combined_df =pd.concat(df, ignore_index=True)
combined_df.to_csv("bus_routes.csv", index=False)


#extract the digits(0-9)
df = pd.read_csv("bus_routes.csv")
df['Seat_Availability'] = df['Seat_Availability'].str.extract(r"(\d+)")

df = df.dropna() #drop null values
table_insert_declaration = "(route_name ,route_link ,busname ,bustype ,departing_time ,duration ,reaching_time ,star_rating ,price,seats_available) values (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s)"

for i in range(len(df)):
    insert_table_query = f"""insert into bus_routes {table_insert_declaration};"""
    cursor.executemany(insert_table_query, {tuple(df.iloc[i])}) # To insert one record
    connection.commit()
   
    
    