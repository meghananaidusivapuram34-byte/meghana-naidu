import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =========================
# Configuration
# =========================

BASE_URL = "https://newsapi.org/v2/top-headlines"

st.set_page_config(
    page_title="Advanced News Dashboard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Advanced News Dashboard")
st.markdown("Search and filter news articles in real time.")

# =========================
# Sidebar Filters
# =========================

st.sidebar.header("News Filters")

api_key = st.sidebar.text_input(
    "News API Key",
    type="password",
    help="Enter your NewsAPI.org API key"
)

country = st.sidebar.selectbox(
    "Country",
    {
        "India": "in",
        "United States": "us",
        "United Kingdom": "gb",
        "Australia": "au",
        "Canada": "ca",
        "Germany": "de",
        "France": "fr",
        "Japan": "jp"
    }
)

category = st.sidebar.selectbox(
    "Category",
    [
        "general",
        "business",
        "entertainment",
        "health",
        "science",
        "sports",
        "technology"
    ]
)

page_size = st.sidebar.slider(
    "Number of Articles",
    min_value=5,
    max_value=100,
    value=20
)

keyword = st.sidebar.text_input(
    "Search Keywords",
    placeholder="AI, Tesla, Cricket..."
)

search_btn = st.sidebar.button("Fetch News")

# =========================
# News Fetch Function
# =========================

@st.cache_data(ttl=300)
def fetch_news(api_key, country_code, category, page_size, keyword):
    params = {
        "apiKey": api_key,
        "country": country_code,
        "category": category,
        "pageSize": page_size
    }

    if keyword:
        params["q"] = keyword

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return None, response.json()

    return response.json(), None


# =========================
# Display Results
# =========================

if search_btn:

    if not api_key:
        st.error("Please enter your API key.")
        st.stop()

    with st.spinner("Fetching latest news..."):
        data, error = fetch_news(
            api_key,
            country,
            category,
            page_size,
            keyword
        )

    if error:
        st.error(error.get("message", "Failed to fetch news"))
        st.stop()

    articles = data.get("articles", [])

    if not articles:
        st.warning("No articles found.")
        st.stop()

    st.success(f"Found {len(articles)} articles")

    # -------------------------
    # Summary Metrics
    # -------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("Articles", len(articles))
    col2.metric("Category", category.title())
    col3.metric("Country", country.upper())

    st.divider()

    # -------------------------
    # Search within results
    # -------------------------

    local_filter = st.text_input(
        "Filter displayed results",
        placeholder="Search title or source..."
    )

    filtered_articles = []

    for article in articles:
        title = article.get("title", "")
        source = article.get("source", {}).get("name", "")

        if (
            local_filter.lower() in title.lower()
            or local_filter.lower() in source.lower()
            or local_filter == ""
        ):
            filtered_articles.append(article)

    # -------------------------
    # Display Articles
    # -------------------------

    for article in filtered_articles:

        with st.container():

            cols = st.columns([1, 3])

            image_url = article.get("urlToImage")

            with cols[0]:
                if image_url:
                    st.image(image_url, use_container_width=True)

            with cols[1]:

                st.subheader(article.get("title", "No Title"))

                source = article.get("source", {}).get("name", "Unknown")
                author = article.get("author", "Unknown")

                st.caption(
                    f"📰 {source} | ✍️ {author}"
                )

                description = article.get("description")
                if description:
                    st.write(description)

                published = article.get("publishedAt")

                try:
                    dt = datetime.fromisoformat(
                        published.replace("Z", "+00:00")
                    )
                    st.text(
                        f"Published: {dt.strftime('%d %b %Y %H:%M')}"
                    )
                except:
                    pass

                st.link_button(
                    "Read Full Article",
                    article.get("url")
                )

            st.divider()

    # -------------------------
    # Download News Data
    # -------------------------

    records = []

    for article in filtered_articles:
        records.append({
            "Title": article.get("title"),
            "Source": article.get("source", {}).get("name"),
            "Author": article.get("author"),
            "Published": article.get("publishedAt"),
            "URL": article.get("url")
        })

    df = pd.DataFrame(records)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Articles CSV",
        csv,
        file_name="news_articles.csv",
        mime="text/csv"
    )