import streamlit as st
import requests
import time
import pandas as pd
from streamlit_lottie import st_lottie

# Page configuration
st.set_page_config(
    page_title="Houses of Ice and Fire",
    page_icon="🔥❄️",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #1e1e2f, #3a3a5f, #5f1e1e);
        color: #f0f0f0;
    }
    .stButton button {
        background: linear-gradient(90deg, #d72638, #3f88c5);
        color: #fff;
        border-radius: 12px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #3f88c5, #d72638);
        transform: scale(1.05);
    }
    .stDataFrame, .stMetric {
        border-radius: 12px;
        box-shadow: 0px 6px 14px rgba(0, 0, 0, 0.4);
        background: rgba(255, 255, 255, 0.08);
    }
    .title-text {
        font-size: 48px;
        font-weight: bold;
        color: #d72638;
        text-shadow: 3px 3px 12px rgba(215, 38, 56, 0.7);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
@st.cache_data()
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Fetch houses with caching
@st.cache_data(ttl=3600)
def get_all_houses():
    url = "https://anapioficeandfire.com/api/houses"
    houses = []
    page, page_size = 1, 50
    progress_bar = st.progress(0)
    status_text = st.empty()

    while True:
        params = {'page': page, 'pageSize': page_size}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.error("Error fetching data from API")
            break
        data = response.json()
        if not data:
            break
        for house in data:
            houses.append({
                "House Name": house.get('name', 'Unknown'),
                "Region": house.get('region', 'Unknown')
            })
        progress_bar.progress(min(page * page_size / 500, 1.0))
        status_text.text(f"Fetching data... {len(houses)} houses loaded")
        time.sleep(0.3)
        page += 1

    return pd.DataFrame(houses).sort_values(by="House Name")

# Main app
def main():
    st.markdown("<h1 class='title-text'>❄️ Houses of Ice and Fire 🔥</h1>", unsafe_allow_html=True)

    # Load and display Lottie animation
    lottie_url = "https://assets6.lottiefiles.com/packages/lf20_w51pcehl.json"  # Ice & Fire swirl effect
    lottie_json = load_lottie_url(lottie_url)

    st.markdown("""
    <div style="text-align: center; font-size: 20px; margin-top: -20px; color: #FFFFFF;">
        Explore the noble houses of <em>A Song of Ice and Fire</em> with an icy and fiery theme!
    </div>
    """, unsafe_allow_html=True)

    if lottie_json:
        st_lottie(lottie_json, height=300, key="ice_fire_animation")
    else:
        st.error("⚠️ Failed to load animation. Please check the animation link or your internet connection.")

    # Session state for houses
    if "houses" not in st.session_state:
        st.session_state.houses = pd.DataFrame()

    # Button to load houses
    if st.button("🔥 Summon the Houses ❄️", use_container_width=True):
        with st.spinner("Summoning Houses..."):
            st.session_state.houses = get_all_houses()
        st.success(f"Loaded {len(st.session_state.houses)} houses!")

    # Display search and filters if data is loaded
    if not st.session_state.houses.empty:
        search_col, region_col = st.columns(2)
        with search_col:
            search_term = st.text_input("🔍 Search houses by name:")
        with region_col:
            regions = sorted(st.session_state.houses["Region"].unique())
            selected_region = st.selectbox("🌍 Filter by region:", ["All"] + regions)

        # Filter data
        filtered_houses = st.session_state.houses.copy()
        if search_term:
            filtered_houses = filtered_houses[filtered_houses["House Name"].str.contains(search_term, case=False)]
        if selected_region != "All":
            filtered_houses = filtered_houses[filtered_houses["Region"] == selected_region]

        st.subheader(f"Displaying {len(filtered_houses)} houses")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.dataframe(filtered_houses, height=600, use_container_width=True)
        with col2:
            text_content = "\n".join(f"{row['House Name']} - {row['Region']}" for _, row in filtered_houses.iterrows())
            st.download_button("⬇️ Download List", text_content, "houses.txt", "text/plain")
            st.metric("🏰 Total Houses", len(st.session_state.houses))
            st.metric("📜 Showing Houses", len(filtered_houses))

if __name__ == "__main__":
    main()