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
        "1. How many food providers and receivers are there in each city?": 
        """SELECT Providers.City,
                   COUNT(DISTINCT Providers.Provider_ID) AS Providers,
                   COUNT(DISTINCT Receivers.Receiver_ID) AS Receivers
            FROM Providers
            JOIN Receivers ON Providers.City = Receivers.City
            GROUP BY Providers.City;""",

        "2. Which type of food provider provides the most food (by quantity)?": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM Food_Listings
            GROUP BY Provider_Type
            ORDER BY Total_Quantity DESC;
        """,

        "3. What is the contact information of food providers in Stevenchester?": """
            SELECT Name, Contact, City
            FROM Providers
            WHERE City = 'Stevenchester';
        """,

        "4. Which receivers have claimed the most food?": """
            SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM Receivers r
            JOIN Claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Name
            ORDER BY Total_Claims DESC;
        """,

        "5. What is the total quantity of food available from all providers?": """
            SELECT SUM(Quantity) AS Total_Food_Available
            FROM Food_Listings;
        """,

        "6. Which city has the highest number of food listings?": """
            SELECT Location, COUNT(*) AS Total_Listings
            FROM Food_Listings
            GROUP BY Location
            ORDER BY Total_Listings DESC;
        """,

        "7. What are the most commonly available food types?": """
            SELECT Food_Type, COUNT(*) AS Count
            FROM Food_Listings
            GROUP BY Food_Type
            ORDER BY Count DESC;
        """,

        "8. Which food listings are expiring soon (within the next 3 days)?": """
            SELECT Food_Name, Expiry_Date
            FROM Food_Listings
            WHERE Expiry_Date <= DATE('now', '+3 days')
            ORDER BY Expiry_Date;
        """,

        "9. How many food claims have been made for each food item?": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM Claims c
            JOIN Food_Listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Food_Name
            ORDER BY Total_Claims DESC;
        """,

        "10. Which provider has had the highest number of successful food claims?": """
            SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM Claims c
            JOIN Food_Listings f ON c.Food_ID = f.Food_ID
            JOIN Providers p ON f.Provider_ID = p.Provider_ID
            WHERE LOWER(c.Status) = 'completed'
            GROUP BY p.Name
            ORDER BY Successful_Claims DESC;
        """,

        "11. Which city has the fastest claim rate (average time)?": """
            SELECT f.Location,
                   ROUND(AVG(JULIANDAY(c.Claim_Date) - JULIANDAY(f.Listing_Date)), 2) AS Avg_Claim_Delay
            FROM Claims c
            JOIN Food_Listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Location
            ORDER BY Avg_Claim_Delay ASC;
        """,

        "12. What percentage of food claims are completed vs. pending vs. canceled?": """
            SELECT Status, COUNT(*) AS Total,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) AS Percentage
            FROM Claims
            GROUP BY Status;
        """,

        "13. What is the average quantity of food claimed per receiver?": """
            SELECT r.Name, ROUND(AVG(c.Quantity), 2) AS Avg_Claimed
            FROM Claims c
            JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Name
            ORDER BY Avg_Claimed DESC;
        """,

        "14. Which meal type is claimed the most?": """
            SELECT Meal_Type, COUNT(*) AS Total_Claims
            FROM Food_Listings f
            JOIN Claims c ON f.Food_ID = c.Food_ID
            GROUP BY Meal_Type
            ORDER BY Total_Claims DESC;
        """,

        "15. What is the total quantity of food donated by each provider?": """
            SELECT p.Name, SUM(f.Quantity) AS Total_Quantity
            FROM Providers p
            JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Name
            ORDER BY Total_Quantity DESC;
        """,

        "16. Which 5 cities have the highest percentage of food claims?": """
            SELECT Location,
                   ROUND(COUNT(Claims.Claim_ID) * 100.0 / COUNT(Food_Listings.Food_ID), 2) AS Claim_Percentage
            FROM Food_Listings
            LEFT JOIN Claims ON Food_Listings.Food_ID = Claims.Food_ID
            GROUP BY Location
            ORDER BY Claim_Percentage DESC;
        """,

        "17. Which food items have never been claimed (grouped)?": """
            SELECT Food_Name, Provider_ID, Quantity
            FROM Food_Listings
            WHERE Food_ID NOT IN (SELECT DISTINCT Food_ID FROM Claims)
            ORDER BY Quantity DESC;
        """,

        "18. Which meal types are donated the most in each city?": """
            SELECT Location, Meal_Type, COUNT(*) AS Total
            FROM Food_Listings
            GROUP BY Location, Meal_Type
            ORDER BY Total DESC;
        """,

        "19. What is the most claimed food type in each city?": """
            SELECT f.Location, f.Food_Type, COUNT(c.Claim_ID) AS Total
            FROM Food_Listings f
            JOIN Claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Location, f.Food_Type
            ORDER BY Total DESC;
        """,

        "20. Which provider has the lowest claim rate?": """
            SELECT p.Name,
                   ROUND(COUNT(c.Claim_ID) * 100.0 / COUNT(DISTINCT f.Food_ID), 2) AS Claim_Rate
            FROM Providers p
            JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
            LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
            GROUP BY p.Name
            ORDER BY Claim_Rate ASC;
        """,

        "21. What is the overall claim success rate for all listings?": """
            SELECT ROUND(COUNT(DISTINCT Claims.Food_ID) * 100.0 / COUNT(DISTINCT Food_Listings.Food_ID), 2) AS Claim_Success_Rate
            FROM Food_Listings
            LEFT JOIN Claims ON Food_Listings.Food_ID = Claims.Food_ID;
        """
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
