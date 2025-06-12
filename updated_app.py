import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database connection
def get_connection():
    return sqlite3.connect("food_waste_management.db", check_same_thread=False)

conn = get_connection()

# ---------------------------- Sidebar Navigation -------------------------------
st.sidebar.title("🍽️ Navigation")
section = st.sidebar.radio("Go to:", [
    "Home",
    "Receiver Management",
    "Provider Management",
    "Claim Management",
    "Food Listings",
    "Run Queries"
])

# ---------------------------- Sidebar Filters -------------------------------
st.sidebar.header("🔍 Filter Records")
cities = pd.read_sql_query("SELECT DISTINCT City FROM Providers", conn)['City'].tolist()
providers = pd.read_sql_query("SELECT DISTINCT Provider_ID FROM Providers", conn)['Provider_ID'].tolist()
food_names = pd.read_sql_query("SELECT DISTINCT Food_Name FROM Food_Listings", conn)['Food_Name'].tolist()
meal_types = pd.read_sql_query("SELECT DISTINCT Meal_Type FROM Food_Listings", conn)['Meal_Type'].tolist()

filter_city = st.sidebar.selectbox("City", ["All"] + cities)
filter_provider = st.sidebar.selectbox("Provider ID", ["All"] + [str(p) for p in providers])
filter_food = st.sidebar.selectbox("Food Name", ["All"] + food_names)
filter_meal = st.sidebar.selectbox("Meal Type", ["All"] + meal_types)

# ---------------------------- Home -------------------------------
if section == "Home":
    st.title("🥗 Food Waste Management System")
    st.subheader("📢 Welcome to the Dashboard")
    st.markdown("Use the sidebar to navigate between sections and manage food waste records efficiently.")

# ---------------------------- Receiver Management -------------------------------
elif section == "Receiver Management":
    st.title("🧑‍🦰 Manage Receivers")
    df = pd.read_sql_query("SELECT * FROM Receivers", conn)
    if filter_city != "All":
        df = df[df['City'] == filter_city]
    st.dataframe(df)

    st.subheader("➕ Add New Receiver")
    rid = st.text_input("Receiver ID")
    name = st.text_input("Receiver Name")
    city = st.text_input("City")
    contact = st.text_input("Contact")
    if st.button("Add Receiver"):
        conn.execute("INSERT INTO Receivers (Receiver_ID, Name, City, Contact) VALUES (?, ?, ?, ?)",
                     (rid, name, city, contact))
        conn.commit()
        st.success("✅ Receiver Added")

    st.subheader("❌ Delete Receiver")
    delete_id = st.text_input("Receiver ID to Delete")
    if st.button("Delete Receiver"):
        conn.execute("DELETE FROM Receivers WHERE Receiver_ID = ?", (delete_id,))
        conn.commit()
        st.success("✅ Receiver Deleted")

# ---------------------------- Provider Management -------------------------------
elif section == "Provider Management":
    st.title("🏪 Manage Providers")
    df = pd.read_sql_query("SELECT * FROM Providers", conn)
    if filter_city != "All":
        df = df[df['City'] == filter_city]
    st.dataframe(df)

    st.subheader("➕ Add New Provider")
    pid = st.text_input("Provider ID")
    name = st.text_input("Provider Name")
    ptype = st.text_input("Provider Type")
    city = st.text_input("City")
    contact = st.text_input("Contact")
    if st.button("Add Provider"):
        conn.execute("INSERT INTO Providers (Provider_ID, Name, Provider_Type, City, Contact) VALUES (?, ?, ?, ?, ?)",
                     (pid, name, ptype, city, contact))
        conn.commit()
        st.success("✅ Provider Added")

    st.subheader("❌ Delete Provider")
    delete_id = st.text_input("Provider ID to Delete")
    if st.button("Delete Provider"):
        conn.execute("DELETE FROM Providers WHERE Provider_ID = ?", (delete_id,))
        conn.commit()
        st.success("✅ Provider Deleted")

# ---------------------------- Claim Management -------------------------------
elif section == "Claim Management":
    st.title("📥 Manage Claims")
    query = """
        SELECT c.Claim_ID, f.Food_Name, r.Name as Receiver_Name, p.Name as Provider_Name,
               p.Contact as Provider_Contact, r.Contact as Receiver_Contact, c.Status
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    """
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)

    st.subheader("➕ Add New Claim")
    claim_id = st.text_input("Claim ID")
    food_id = st.text_input("Food Listing ID")
    receiver_id = st.text_input("Receiver ID")
    status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
    if st.button("Add Claim"):
        conn.execute("INSERT INTO Claims (Claim_ID, Food_ID, Receiver_ID, Status) VALUES (?, ?, ?, ?)",
                     (claim_id, food_id, receiver_id, status))
        conn.commit()
        st.success("✅ Claim Added")

    st.subheader("❌ Delete Claim")
    delete_id = st.text_input("Claim ID to Delete")
    if st.button("Delete Claim"):
        conn.execute("DELETE FROM Claims WHERE Claim_ID = ?", (delete_id,))
        conn.commit()
        st.success("✅ Claim Deleted")

# ---------------------------- Food Listings -------------------------------
elif section == "Food Listings":
    st.title("📦 Food Listings")

    # Load and join listings with provider data
    df = pd.read_sql_query("SELECT * FROM Food_Listings", conn)
    providers_df = pd.read_sql_query("SELECT Provider_ID, Name, Contact, City FROM Providers", conn)
    df = df.merge(providers_df, on="Provider_ID", how="left")

    # Apply filters
    if filter_food != "All":
        df = df[df['Food_Name'] == filter_food]
    if filter_meal != "All":
        df = df[df['Meal_Type'] == filter_meal]
    if filter_provider != "All":
        df = df[df['Provider_ID'] == int(filter_provider)]
    if filter_city != "All":
        df = df[df['City'] == filter_city]

    # Show filtered table
    st.subheader("📋 Filtered Food Listings")
    st.dataframe(df[['Food_ID', 'Food_Name', 'Food_Type', 'Meal_Type', 'Quantity', 'Expiry_Date', 'Name', 'City']])

    # 🔍 Search Bar for Direct Contact
    st.subheader("🔍 Search & Contact Providers")
    search_term = st.text_input("Search by Food Name, Type, or Meal").strip().lower()

    if search_term:
        filtered = df[df.apply(lambda row:
            search_term in str(row['Food_Name']).lower() or
            search_term in str(row['Food_Type']).lower() or
            search_term in str(row['Meal_Type']).lower(), axis=1
        )]

        if not filtered.empty:
            for i, row in filtered.iterrows():
                st.markdown(f"---")
                st.markdown(f"**🍽️ {row['Food_Name']}** ({row['Meal_Type']}) — **{row['Name']}** ({row['City']})")
                contact = row['Contact']
                link = f"mailto:{contact}" if "@" in contact else f"tel:{contact}"
                st.markdown(f"""
                    <a href="{link}" target="_blank">
                        <button style='padding:8px 16px;margin-top:8px;border:none;border-radius:6px;background-color:#4CAF50;color:white;cursor:pointer;'>
                            📞 Contact
                        </button>
                    </a>
                """, unsafe_allow_html=True)
        else:
            st.warning("No matches found.")
    else:
        st.info("Enter a search term above to show contact options.")

    # ➕ Add New Food Listing
    st.subheader("➕ Add New Food Listing")
    pid = st.text_input("Provider ID")
    food_name = st.text_input("Food Name")
    food_type = st.text_input("Food Type")
    quantity = st.number_input("Quantity", min_value=1)
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
    expiry = st.date_input("Expiry Date")
    contact = st.text_input("Contact Info")

    if st.button("Add Listing"):
        conn.execute("""
            INSERT INTO Food_Listings (Provider_ID, Food_Name, Food_Type, Quantity, Meal_Type, Expiry_Date, Contact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pid, food_name, food_type, quantity, meal_type, expiry, contact))
        conn.commit()
        st.success("✅ Food Listing Added")

    # ❌ Delete Food Listing
    st.subheader("❌ Delete Listing")
    delete_id = st.text_input("Food Listing ID to Delete")
    if st.button("Delete Listing"):
        conn.execute("DELETE FROM Food_Listings WHERE Food_ID = ?", (delete_id,))
        conn.commit()
        st.success("✅ Food Listing Deleted")

# ---------------------------- Run Queries -------------------------------
elif section == "Run Queries":
    st.title("📊 Query-Based Insights")

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

    query_name = st.selectbox("Select a Query", list(queries.keys()))
    if st.button("Run Query"):
        result = pd.read_sql_query(queries[query_name], conn)
        st.dataframe(result)
