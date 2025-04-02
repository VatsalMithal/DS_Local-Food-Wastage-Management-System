import streamlit as st
import sqlite3
import pandas as pd

# Function to load data from database
def load_data(query, params=None):
    conn = sqlite3.connect("food_waste_management.db")
    if params:
        df = pd.read_sql_query(query, conn, params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to insert data
def insert_data(table, columns, values):
    conn = sqlite3.connect("food_waste_management.db")
    cursor = conn.cursor()
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# Streamlit UI
st.title("Food Waste Management System")

# Sidebar for navigation
menu = st.sidebar.radio("Menu", ["Providers", "Receivers", "Claims", "Food Listings", "Analytics"])

if menu == "Providers":
    st.subheader("Providers List")
    df = load_data("SELECT * FROM Providers")
    st.dataframe(df)

    st.subheader("Add New Provider")
    name = st.text_input("Name")
    city = st.text_input("City")
    contact = st.text_input("Contact")
    if st.button("Add Provider"):
        insert_data("Providers", ["Name", "City", "Contact"], [name, city, contact])
        st.success("Provider added successfully!")

elif menu == "Receivers":
    st.subheader("Receivers List")
    df = load_data("SELECT * FROM Receivers")
    st.dataframe(df)

    st.subheader("Add New Receiver")
    name = st.text_input("Name")
    city = st.text_input("City")
    contact = st.text_input("Contact")
    if st.button("Add Receiver"):
        insert_data("Receivers", ["Name", "City", "Contact"], [name, city, contact])
        st.success("Receiver added successfully!")

elif menu == "Claims":
    st.subheader("Food Claims")
    df = load_data("SELECT * FROM Claims")
    st.dataframe(df)

    st.subheader("Claim Food")
    receiver_id = st.number_input("Receiver ID", min_value=1, step=1)
    food_id = st.number_input("Food ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Claim Food"):
        insert_data("Claims", ["Receiver_ID", "Food_ID", "Quantity"], [receiver_id, food_id, quantity])
        st.success("Food claimed successfully!")

elif menu == "Food Listings":
    st.subheader("Available Food")
    df = load_data("SELECT * FROM Food_Listings")
    st.dataframe(df)

    st.subheader("Add New Food Listing")
    provider_id = st.number_input("Provider ID", min_value=1, step=1)
    food_type = st.text_input("Food Type")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    expiry_date = st.date_input("Expiry Date")
    if st.button("Add Food Listing"):
        insert_data("Food_Listings", ["Provider_ID", "Food_Type", "Quantity", "Expiry_Date"], 
                    [provider_id, food_type, quantity, expiry_date])
        st.success("Food listing added successfully!")

elif menu == "Analytics":
    st.subheader("Analytics Dashboard")

    queries = {
        #Count providers and receivers in each city
    "How many food providers and receivers are there in each city?": """
        SELECT 
            Providers.City, 
            COUNT(DISTINCT Providers.Provider_ID) AS Providers, 
            COUNT(DISTINCT Receivers.Receiver_ID) AS Receivers 
        FROM Providers 
        JOIN Receivers ON Providers.City = Receivers.City 
        GROUP BY Providers.City;
    """,
    
    #Type of provider that contributes the most food
    "Which type of food provider contributes the most food?":
    """SELECT Provider_Type, COUNT(*) AS Food_Contributions 
       FROM Food_Listings GROUP BY Provider_Type ORDER BY Food_Contributions DESC LIMIT 1;""",

    #Total quantity of food available
    "What is the total quantity of food available from all providers?":
    """SELECT SUM(Quantity) AS Total_Food_Available FROM Food_Listings;""",

    #Most commonly available food types
    "What are the most commonly available food types?":
    """SELECT Food_Type, COUNT(*) AS Count FROM Food_Listings 
       GROUP BY Food_Type ORDER BY Count DESC;""",

    #Food listings expiring soon
    "Which food listings are expiring soon (within the next 3 days)?":
    """SELECT * FROM Food_Listings WHERE Expiry_Date <= DATE('now', '+3 days');""",

    #Percentage of claims status
    "What percentage of food claims are completed vs. pending vs. canceled?":
    """SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims) AS Percentage 
       FROM Claims GROUP BY Status;""",

    #Overall claim success rate
    "What is the overall claim success rate for all listings?":
    """SELECT (COUNT(CASE WHEN Status = 'Completed' THEN 1 END) * 100.0 / COUNT(*)) AS Success_Rate FROM Claims;"""
    }

    selected_query = st.selectbox("Select an analytics query", list(queries.keys()))
    
    if selected_query == "Contact info of providers in a city":
        city = st.text_input("Enter City Name")
        if st.button("Get Data") and city:
            df = load_data(queries[selected_query], (city,))
            st.dataframe(df)
    else:
        df = load_data(queries[selected_query])
        st.dataframe(df)
