import pandas as pd
import sqlite3

# Load the CSV files
providers = pd.read_csv("D:/Guvi Project 1/providers_data.csv")
receivers = pd.read_csv("D:/Guvi Project 1/receivers_data.csv")
food_listings = pd.read_csv("D:/Guvi Project 1/food_listings_data.csv")
claims = pd.read_csv("D:/Guvi Project 1/claims_data.csv")

# Create a new SQLite database (or overwrite if exists)
conn = sqlite3.connect("D:/Guvi Project 1/food_waste_management.db")

# Write DataFrames to the database
providers.to_sql("Providers", conn, if_exists="replace", index=False)
receivers.to_sql("Receivers", conn, if_exists="replace", index=False)
food_listings.to_sql("Food_Listings", conn, if_exists="replace", index=False)
claims.to_sql("Claims", conn, if_exists="replace", index=False)

conn.close()
print("✅ Database created and tables loaded successfully!")