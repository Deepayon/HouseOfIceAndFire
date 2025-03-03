import streamlit as st
import requests
import time
import pandas as pd
import csv
from streamlit_lottie import st_lottie


# Page configuration
st.set_page_config(
    page_title="World of Ice and Fire",
    page_icon="🔥❄️",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #1e1e2f, #3a3a5f, #5f1e1e);
        color: #f0f0f0;
    }
    .title-text {
        font-size: 48px;
        font-weight: bold;
        color: #d72638;
        text-shadow: 3px 3px 12px rgba(215, 38, 56, 0.7);
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(90deg, #d72638, #3f88c5);
        color: white;
        padding: 10px 24px;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
        transition: 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #3f88c5, #d72638);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data()
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


@st.cache_data(ttl=3600)
def get_all_houses():
    url = "https://anapioficeandfire.com/api/houses"
    houses = []
    page = 1
    while True:
        params = {'page': page, 'pageSize': 50}
        response = requests.get(url, params=params)
        data = response.json()
        if not data:
            break
        houses.extend([{"House Name": h.get('name', 'Unknown'), "Region": h.get('region', 'Unknown')} for h in data])
        page += 1
    return pd.DataFrame(houses).sort_values(by="House Name")


@st.cache_data(ttl=3600)
def get_all_books():
    url = "https://anapioficeandfire.com/api/books"
    books = []
    page = 1
    while True:
        params = {'page': page, 'pageSize': 50}
        response = requests.get(url, params=params)
        data = response.json()
        if not data:
            break
        books.extend(data)
        page += 1

    books_dict = {}
    for book in books:
        books_dict[book['name']] = [
            book.get('numberOfPages', 'Unknown'),
            book.get('released', 'Unknown').split('T')[0],
            book.get('isbn', 'Unknown'),
            book.get('publisher', 'Unknown')
        ]
    return books_dict


@st.cache_data()
def create_books_csv(books_dict):
    csv_filename = "books_of_ice_and_fire.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Book Name", "Pages", "Release Date", "ISBN", "Publisher"])
        for name, details in books_dict.items():
            writer.writerow([name] + details)
    return csv_filename


@st.cache_data(ttl=3600)
def get_all_characters():
    url = "https://anapioficeandfire.com/api/characters"
    characters = []
    page = 1
    while True:
        params = {'page': page, 'pageSize': 50}
        response = requests.get(url, params=params)
        data = response.json()
        if not data:
            break
        for char in data:
            seasons = len(char.get('tvSeries', []))
            characters.append({
                "Name": char.get('name', 'Unknown'),
                "Seasons": seasons
            })
        page += 1
    return pd.DataFrame(characters).sort_values(by="Seasons", ascending=False)


def main():
    st.sidebar.title("⚔️ Navigate")
    selected_section = st.sidebar.radio(
        "Choose Section", ["Houses", "Books", "Characters"]
    )

    st.markdown("<h1 class='title-text'>🌌 World of Ice and Fire 🌌</h1>", unsafe_allow_html=True)

    lottie_url = "https://assets6.lottiefiles.com/packages/lf20_w51pcehl.json"
    lottie_json = load_lottie_url(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=300, key="ice_fire_animation")
    else:
        st.error("⚠️ Failed to load animation.")

    st.markdown("---")

    if selected_section == "Houses":
        st.header("🏰 Noble Houses")
        if "houses" not in st.session_state:
            st.session_state.houses = pd.DataFrame()

        with st.container():
            summon_button = st.button("🔥 Summon the Houses ❄️", use_container_width=True)
            if summon_button:
                with st.spinner("Summoning Houses..."):
                    st.session_state.houses = get_all_houses()
                st.success(f"Loaded {len(st.session_state.houses)} houses!")

        if not st.session_state.houses.empty:
            search_term = st.text_input("🔍 Search Houses")
            region_filter = st.selectbox(
                "🌍 Filter by Region",
                ["All"] + list(st.session_state.houses["Region"].unique())
            )
            filtered = st.session_state.houses.copy()
            if search_term:
                filtered = filtered[filtered["House Name"].str.contains(search_term, case=False)]
            if region_filter != "All":
                filtered = filtered[filtered["Region"] == region_filter]

            st.dataframe(filtered, use_container_width=True)
            text_content = "\n".join(f"{row['House Name']} - {row['Region']}" for _, row in filtered.iterrows())
            st.download_button("⬇️ Download Houses", text_content, "houses.txt", "text/plain")

    elif selected_section == "Books":
        st.header("📚 Books of Ice and Fire")
        books_dict = get_all_books()
        df_books = pd.DataFrame([
            {"Book Name": name, "Pages": d[0], "Release Date": d[1], "ISBN": d[2], "Publisher": d[3]}
            for name, d in books_dict.items()
        ])
        st.dataframe(df_books, use_container_width=True)
        csv_file = create_books_csv(books_dict)
        with open(csv_file, "rb") as f:
            st.download_button("⬇️ Download Books CSV", f, csv_file, "text/csv")

    elif selected_section == "Characters":
        st.header("🧙‍♂️ Characters of Ice and Fire")
        df_characters = get_all_characters()
        st.dataframe(df_characters, use_container_width=True)
        st.metric("Total Characters", len(df_characters))


if __name__ == "__main__":
    main()
