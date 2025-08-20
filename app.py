
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DB Connection
conn = sqlite3.connect('food_sharing.db')
c = conn.cursor()

# Helper functions
def run_query(query, params=()):
    c.execute(query, params)
    conn.commit()

def fetch_query(query, params=()):
    return pd.read_sql_query(query, conn, params=params)

# Streamlit UI
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")
st.title("🍽️ Local Food Wastage Management System")

menu = ["Home", "Data Exploration", "SQL Analysis", "CRUD Operations"]
choice = st.sidebar.selectbox("Navigation", menu)

# Home Page
if choice == "Home":
    st.subheader("Project Overview")
    st.write("""
    This app connects surplus food providers with receivers to reduce food wastage.
    You can explore data, run SQL analysis queries, and perform CRUD operations.
    """)
    st.markdown("**Datasets Used:** Providers, Receivers, Food Listings, Claims")

# Data Exploration
elif choice == "Data Exploration":
    st.subheader("📊 Explore the Data")
    table = st.selectbox("Select a table", ["Providers", "Receivers", "Food_Listings", "Claims"]) # Corrected table names to match DB
    data = fetch_query(f"SELECT * FROM {table}")
    st.dataframe(data)

    if table == "Food_Listings": # Corrected table name
        city_filter = st.selectbox("Filter by Location", ["All"] + list(data['Location'].unique())) # Changed to Location
        if city_filter != "All":
            data = data[data['Location'] == city_filter]
            st.dataframe(data)

# SQL Analysis
elif choice == "SQL Analysis":
    st.subheader("📈 SQL Analysis Insights")

    queries = {
        "1. Count of Providers per City":
            "SELECT City, COUNT(*) AS Provider_Count FROM Providers GROUP BY City", # Corrected table name
        "2. Count of Receivers per City":
            "SELECT City, COUNT(*) AS Receiver_Count FROM Receivers GROUP BY City", # Corrected table name
        "3. Top Provider Types":
            "SELECT Type, COUNT(*) AS Count FROM Providers GROUP BY Type ORDER BY Count DESC", # Corrected table name
        "4. Most Claimed Food Items":
            """SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
               FROM Claims c # Corrected table name
               JOIN Food_Listings f ON c.Food_ID = f.Food_ID # Corrected table name
               GROUP BY f.Food_Name
               ORDER BY Claim_Count DESC""",
        "5. Completed vs Pending vs Cancelled Claims":
            "SELECT Status, COUNT(*) AS Count FROM Claims GROUP BY Status", # Corrected table name
        "6. Food Listings Expiring Soon":
            """SELECT * FROM Food_Listings # Corrected table name
               WHERE julianday(Expiry_Date) - julianday('now') <= 2""",
        "7. Providers with Most Food Listings":
            """SELECT Provider_ID, COUNT(*) AS Listing_Count
               FROM Food_Listings GROUP BY Provider_ID # Corrected table name
               ORDER BY Listing_Count DESC""",
        "8. Receivers with Most Claims":
            """SELECT Receiver_ID, COUNT(*) AS Claim_Count
               FROM Claims GROUP BY Receiver_ID # Corrected table name
               ORDER BY Claim_Count DESC""",
        "9. Average Quantity of Food per Listing":
            "SELECT AVG(Quantity) AS Avg_Quantity FROM Food_Listings", # Corrected table name
        "10. Vegetarian vs Non-Vegetarian Listings":
            "SELECT Food_Type, COUNT(*) AS Count FROM Food_Listings GROUP BY Food_Type", # Corrected table name
        "11. Meal Type Distribution":
            "SELECT Meal_Type, COUNT(*) AS Count FROM Food_Listings GROUP BY Meal_Type", # Corrected table name
        "12. Food Listings per Location":
            "SELECT Location, COUNT(*) AS Count FROM Food_Listings GROUP BY Location", # Corrected table name
        "13. Claims per Provider":
            """SELECT p.Name, COUNT(c.Claim_ID) AS Claim_Count
               FROM Claims c # Corrected table name
               JOIN Food_Listings f ON c.Food_ID = f.Food_ID # Corrected table name
               JOIN Providers p ON f.Provider_ID = p.Provider_ID # Corrected table name
               GROUP BY p.Name""",
        "14. Claims in Last 7 Days":
            """SELECT * FROM Claims # Corrected table name
               WHERE julianday('now') - julianday(Timestamp) <= 7""",
        "15. Expired Food Listings":
            """SELECT * FROM Food_Listings # Corrected table name
               WHERE date(Expiry_Date) < date('now')"""
    }

    selected_query = st.selectbox("Select a query to run", list(queries.keys()))
    if st.button("Run Query"):
        st.dataframe(fetch_query(queries[selected_query]))

# CRUD Operations
elif choice == "CRUD Operations":
    st.subheader("🛠️ Manage Food Listings")

    crud_action = st.radio("Choose Action", ["Add", "Update", "Delete"])

    if crud_action == "Add":
        with st.form("add_form"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1)
            expiry = st.date_input("Expiry Date")
            provider_id = st.number_input("Provider ID", min_value=1)
            provider_type = st.text_input("Provider Type")
            location = st.text_input("Location")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            submitted = st.form_submit_button("Add Listing")

            if submitted:
                run_query("""
                    INSERT INTO Food_Listings # Corrected table name
                    (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (food_name, quantity, expiry, provider_id, provider_type, location, food_type, meal_type))
                st.success("Food listing added successfully.")

    elif crud_action == "Update":
        listings = fetch_query("SELECT Food_ID, Food_Name FROM Food_Listings") # Corrected table name
        selected_id = st.selectbox("Select Food ID to Update", listings['Food_ID'])
        new_quantity = st.number_input("New Quantity", min_value=1)
        new_name = st.text_input("New Food Name")
        if st.button("Update Listing"):
            run_query("UPDATE Food_Listings SET Quantity=?, Food_Name=? WHERE Food_ID=?", (new_quantity, new_name, selected_id)) # Corrected table name
            st.success("Food listing updated successfully.")

    elif crud_action == "Delete":
        listings = fetch_query("SELECT Food_ID, Food_Name FROM Food_Listings") # Corrected table name
        selected_id = st.selectbox("Select Food ID to Delete", listings['Food_ID'])
        if st.button("Delete Listing"):
            run_query("DELETE FROM Food_Listings WHERE Food_ID=?", (selected_id,)) # Corrected table name
            st.success("Food listing deleted successfully.")

