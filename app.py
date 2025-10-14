import json
import streamlit as st
from streamlit_folium import st_folium
import folium
from pathlib import Path

# Load JSON file (replace with your path)
DATA_PATH = Path("grouped_filtered_properties.json")

@st.cache_data
def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="Bratislava 2-Room Listings", layout="wide")
    st.title("🏙️ Bratislava 2-Room Listings Map")

    data = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")

    min_price = st.sidebar.number_input("Min price (€)", value=0, step=1000)
    max_price = st.sidebar.number_input("Max price (€)", value=230000, step=1000)
    show_changed = st.sidebar.checkbox("Show only listings with price change", value=False)

    # Filter listings
    filtered = [
        l for l in data
        if l.get("latest_price") and min_price <= l["latest_price"] <= max_price
        and (not show_changed or l.get("price_changed"))
    ]

    # Map centered roughly around Bratislava
    m = folium.Map(location=[48.1486, 17.1077], zoom_start=12)

    for listing in filtered:
        lat = listing.get("latitude")
        lon = listing.get("longitude")
        if not lat or not lon:
            continue

        # Popup content
        popup_html = f"""
        <b>{listing.get('title')}</b><br>
        <a href="{listing.get('link')}" target="_blank">Open Listing</a><br>
        <b>Price:</b> {listing.get('latest_price')} €<br>
        <b>Size:</b> {listing.get('size_m2')} m²<br>
        <b>Avg price:</b> {listing.get('avg_price')}<br>
        <b>County:</b> {listing.get('county')}<br>
        """

        if listing.get("price_changed") and "price_history" in listing:
            popup_html += "<br><b>Price History:</b><ul>"
            for p in listing["price_history"]:
                popup_html += f"<li>{p['date']}: {p['price']} €</li>"
            popup_html += "</ul>"

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=listing.get("title"),
            icon=folium.Icon(
                color="red" if listing.get("price_changed") else "blue",
                icon="home",
                prefix="fa"
            )
        ).add_to(m)

    st_data = st_folium(m, width=1200, height=700)

    st.markdown(f"**Total listings displayed:** {len(filtered)}")

if __name__ == "__main__":
    main()
