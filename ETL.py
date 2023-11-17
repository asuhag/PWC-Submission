import pandas as pd
import sqlalchemy 
from sqlalchemy import create_engine 
from pathlib import Path
import os 

database_uri = 'sqlite:///bike_rentals.db'
engine = create_engine(database_uri)

data_directory = 'data/'

def determine_schema(csv_file):
    df = pd.read_csv(csv_file, nrows=0)

    # Define unique columns for each schema
    unique_columns_schema1 = set(['Rental Id', 'Bike Id', 'EndStation Id', 'StartStation Id'])
    unique_columns_schema2 = set(['Number', 'Start station number', 'End station number', 'Bike number'])
    unique_columns_schema3 = set(['EndStation Name', 'StartStation Name'])


    # Check which columns the CSV file has
    if unique_columns_schema1.issubset(set(df.columns)):
        return 1
    elif unique_columns_schema2.issubset(set(df.columns)):
        return 2
    elif unique_columns_schema3.issubset(set(df.columns)):
        return 3
    else:
        raise ValueError(f"Unknown schema in file: {csv_file}")
    
def create_tables():
    # SQL to create tables for each schema
    schema1_table = """
    CREATE TABLE IF NOT EXISTS bike_rentals_schema1 (
        Rental_Id INTEGER,
        Duration INTEGER,
        Bike_Id INTEGER,
        End_Date TEXT,
        EndStation_Id INTEGER,
        EndStation_Name TEXT,
        Start_Date TEXT,
        StartStation_Id INTEGER,
        StartStation_Name TEXT
    );
    """

    schema2_table = """
    CREATE TABLE IF NOT EXISTS bike_rentals_schema2 (
        Number TEXT,
        Start_date TEXT,
        Start_station_number TEXT,
        Start_station TEXT,
        End_date TEXT,
        End_station_number TEXT,
        End_station TEXT,
        Bike_number TEXT,
        Bike_model TEXT,
        Total_duration INTEGER,
        Total_duration_ms INTEGER
    );
    """
    schema3_table = """
    CREATE TABLE IF NOT EXISTS bike_rentals_schema3 (
        Rental_Id INTEGER,
        Duration INTEGER,
        Bike_Id INTEGER,
        End_Date TEXT,
        EndStation_Name TEXT,
        Start_Date TEXT,
        StartStation_Id INTEGER,
        StartStation_Name TEXT
    );
    """

    with engine.connect() as conn:
        conn.execute(schema1_table)
        conn.execute(schema2_table)
        conn.execute(schema3_table)


def process_csv_files():
    for file_name in os.listdir(data_directory):
        if file_name.endswith('.csv'):
            file_path = os.path.join(data_directory, file_name)
            schema_type = determine_schema(file_path)
            df = pd.read_csv(file_path)

            if schema_type == 1:
                df.rename(columns={
                    'Rental Id': 'Rental_Id',
                    'Bike Id': 'Bike_Id',
                    'End Date': 'End_Date',
                    'EndStation Id': 'EndStation_Id',
                    'EndStation Name': 'EndStation_Name',
                    'Start Date': 'Start_Date',
                    'StartStation Id': 'StartStation_Id',
                    'StartStation Name': 'StartStation_Name'
                }, inplace=True)

            elif schema_type == 2:
                df.rename(columns={
                    'Number': 'Number',
                    'Start date': 'Start_date',
                    'Start station number': 'Start_station_number',
                    'Start station': 'Start_station',
                    'End date': 'End_date',
                    'End station number': 'End_station_number',
                    'End station': 'End_station',
                    'Bike number': 'Bike_number',
                    'Bike model': 'Bike_model',
                    'Total duration': 'Total_duration',
                    'Total duration (ms)': 'Total_duration_ms'
                }, inplace=True)

            elif schema_type == 3:
                df.rename(columns={
                    'Rental Id': 'Rental_Id',
                    'Bike Id': 'Bike_Id',
                    'End Date': 'End_Date',
                    'EndStation Name': 'EndStation_Name',
                    'Start Date': 'Start_Date',
                    'StartStation Id': 'StartStation_Id',
                    'StartStation Name': 'StartStation_Name'
                }, inplace=True)

            table_name = f'bike_rentals_schema{schema_type}'

            df.to_sql(table_name, engine, if_exists='append', index=False)

def merge_tables_and_save():
    # Query each table and create a DataFrame
    query_schema1 = 'SELECT Rental_Id, Duration, Bike_Id, End_Date, EndStation_Id, EndStation_Name, Start_Date, StartStation_Id, StartStation_Name FROM bike_rentals_schema1'
    query_schema2 = 'SELECT Number AS Rental_Id, ROUND(Total_duration_ms / 1000.0) AS Duration, Bike_number AS Bike_Id, End_date AS End_Date, End_station_number AS EndStation_Id, End_station AS EndStation_Name, Start_date AS Start_Date, Start_station_number AS StartStation_Id, Start_station AS StartStation_Name FROM bike_rentals_schema2'
    query_schema3 = 'SELECT Rental_Id, Duration, Bike_Id, End_Date, EndStation_Name, Start_Date, StartStation_Id, StartStation_Name FROM bike_rentals_schema3'

    df_schema1 = pd.read_sql_query(query_schema1, engine)
    df_schema2 = pd.read_sql_query(query_schema2, engine)
    df_schema3 = pd.read_sql_query(query_schema3, engine)

    # Merge (concatenate) the DataFrames
    merged_df = pd.concat([df_schema1, df_schema2, df_schema3], ignore_index=True)


    # Save only the relevant columns to different, smaller csv files 
    merged_df[['Duration','Rental_Id']].to_csv('duration.csv', index=False)

# Create the tables
create_tables()

# Process CSV files
process_csv_files()

merge_tables_and_save()