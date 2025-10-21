import json
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster
from pathlib import Path

# Path to your JSON file
DATA_PATH = Path("grouped_filtered_properties.json")

@st.cache_data
def load_data():
    """Load all property data from JSON file."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.set_page_config(page_title="🏙️ Bratislava Listings Map", layout="wide")
    st.title("🏙️ Bratislava Listings – Filtered Map")

    data = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")

    # Price range
    min_price = st.sidebar.number_input("Min price (€)", value=0, step=1000)
    max_price = st.sidebar.number_input("Max price (€)", value=300000, step=1000)

    # Show only listings with price change
    show_changed = st.sidebar.checkbox("Show only listings with price change", value=False)

    # Room filter
    room_filter = st.sidebar.selectbox(
        "Filter by room type",
        options=["All", "1", "2", "Garzónky"],
        index=0,
    )

    # Text search
    text_search = (
        st.sidebar.text_input(
            "Search text (title, category, county):",
            value="",
            placeholder="e.g. Ružinov, loggia, centrum...",
        )
        .strip()
        .lower()
    )

    # --- Filtering logic ---
    filtered = []
    for l in data:
        title = str(l.get("title", "")).lower()
        category = str(l.get("category", "")).lower()
        county = str(l.get("county", "")).lower()
        price = l.get("latest_price")

        # Price filter
        if not (price and min_price <= price <= max_price):
            continue

        # Price change filter
        if show_changed and not l.get("price_changed"):
            continue

        # Room filter
        if room_filter.lower() != "all":
            # Numeric room match or garzonka keyword
            if "1" in room_filter and "1" not in category:
                continue
            if "2" in room_filter and "2" not in category:
                continue
            if "garz" in room_filter.lower() and "garz" not in category:
                continue

        # Text search
        if text_search:
            combined = f"{title} {category} {county}"
            if text_search not in combined:
                continue

        filtered.append(l)

    # --- Map setup ---
    m = folium.Map(location=[48.1486, 17.1077], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)

    shown = 0
    for listing in filtered:
        lat = listing.get("latitude")
        lon = listing.get("longitude")
        if not lat or not lon:
            continue

        shown += 1
        title = listing.get("title", "No title")
        popup_html = f"""
        <b>{title}</b><br>
        <a href="{listing.get('link')}" target="_blank">Open Listing</a><br>
        <b>Price:</b> {listing.get('latest_price')} €<br>
        <b>Size:</b> {listing.get('size_m2')} m²<br>
        <b>Avg price:</b> {listing.get('avg_price')}<br>
        <b>Avg price per m²:</b> {listing.get('average_price_per_m2')}<br>
        <b>County:</b> {listing.get('county')}<br>
        <b>Category:</b> {listing.get('category')}<br>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=title,
            icon=folium.Icon(
                color="red" if listing.get("price_changed") else "blue",
                icon="home",
                prefix="fa",
            ),
        ).add_to(marker_cluster)

    # --- Display map ---
    st_folium(m, width=1200, height=700)
    st.markdown(f"**Properties displayed:** {shown} / {len(data)}")

if __name__ == "__main__":
    main()
