import streamlit as st
import requests
import pandas as pd

# Configuration
st.set_page_config(
    page_title="Global News Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL for the flask app
API_BASE_URL = "http://localhost:5000"

# function for fetching all the news articles
def fetch_all_news():
    response = requests.get(f"{API_BASE_URL}/news")
    if response.status_code == 200:
        return response.json()
    return []

#function for filtered news
def fetch_filtered_news(params):
    response = requests.get(f"{API_BASE_URL}/news/filter", params=params)
    if response.status_code == 200:
        return response.json()
    return []

#function for fetching countries for filters
def fetch_countries():
    response = requests.get(f"{API_BASE_URL}/news/countries")
    if response.status_code == 200:
        return response.json()
    return []

#function for fetching sources for filters
def fetch_sources():
    response = requests.get(f"{API_BASE_URL}/news/sources")
    if response.status_code == 200:
        return response.json()
    return []

#function for fetching languages for filters
def fetch_languages():
    response = requests.get(f"{API_BASE_URL}/news/languages")
    if response.status_code == 200:
        return response.json()
    return []

# Main App
def main():
    st.title("🌍 Global News Explorer")
    st.markdown("Explore news articles from around the world collected from various sources.")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Fetch available filters
        countries = fetch_countries()
        sources = fetch_sources()
        languages = fetch_languages()
        
        selected_countries = st.multiselect(
            "Select Countries",
            countries,
            default=None,
            help="Filter by country"
        )
        
        selected_sources = st.multiselect(
            "Select Sources",
            sources,
            default=None,
            help="Filter by news source"
        )
        
        selected_languages = st.multiselect(
            "Select Languages",
            languages,
            default=None,
            help="Filter by language"
        )
        
        keyword_search = st.text_input(
            "Keyword Search",
            "",
            help="Search in news titles (comma-separated for multiple keywords)"
        )
        
        year_filter = st.text_input(
            "Year Filter",
            "",
            help="Filter by publication year (comma-separated for multiple years)"
        )
        
        apply_filters = st.button("Apply Filters")

    # Main content
    st.subheader("News Articles")
    
    if apply_filters or not (selected_countries or selected_sources or selected_languages or keyword_search or year_filter):
        # Prepare filter params
        params = {}
        if selected_countries:
            params['country'] = ','.join(selected_countries)
        if selected_sources:
            params['source'] = ','.join(selected_sources)
        if selected_languages:
            params['language'] = ','.join(selected_languages)
        if keyword_search:
            params['keyword'] = keyword_search
        if year_filter:
            params['year'] = year_filter
        
        # Fetch data
        news_data = fetch_filtered_news(params) if params else fetch_all_news()
        
        if news_data:
            df = pd.DataFrame(news_data)
            
            
            if 'publication_date' in df.columns:
                df['publication_date'] = df['publication_date'].apply(lambda x: str(x) if pd.notna(x) else x)
            
            # Show data
            st.write(f"Found {len(df)} news articles")
            
            # Sorting options
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox(
                    "Sort by",
                    ["publication_date", "title", "source", "country"],
                    index=0
                )
            with col2:
                sort_order = st.selectbox(
                    "Order",
                    ["Descending", "Ascending"],
                    index=0
                )
            
            df = df.sort_values(
                by=sort_by,
                ascending=(sort_order == "Ascending")
            )
            
            # Display as expandable cards with all fields
            for _, row in df.iterrows():
                with st.expander(f"{row.get('title', 'No title')}"):
                    st.markdown(f"**News Title:** {row.get('title', 'N/A')}")
                    st.markdown(f"**Publication Date:** {row.get('publication_date', 'N/A')}")
                    st.markdown(f"**Source (News Agency):** {row.get('source', 'N/A')}")
                    st.markdown(f"**Country:** {row.get('country', 'N/A')}")
                    st.markdown(f"**Language:** {row.get('language', 'N/A')}")
                    st.markdown(f"**Summary:** {row.get('summary', 'No summary available')}")
                    st.markdown(f"**Author:** {row.get('author', 'N/A')}")
                    url = row.get('url', row.get('link', 'No URL available'))
                    if url != 'No URL available':
                        st.markdown(f"**Link to full Article:** [Click here]({url})")
                    else:
                        st.markdown(f"**Link to full Article:** {url}")
        else:
            st.warning("No news articles found with the current filters.")

    # bottom section which shows all the data according to countries, sources and languages.
    st.divider()
    st.subheader("Available Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Countries")
        countries = fetch_countries()
        if countries:
            st.write(f"Total countries: {len(countries)}")
            st.dataframe(pd.DataFrame(countries, columns=["Country"]), height=200)
        else:
            st.warning("No countries data available")
    
    with col2:
        st.markdown("### Sources")
        sources = fetch_sources()
        if sources:
            st.write(f"Total sources: {len(sources)}")
            st.dataframe(pd.DataFrame(sources, columns=["Source"]), height=200)
        else:
            st.warning("No sources data available")
            
    with col3:
        st.markdown("### Languages")
        languages = fetch_languages()
        if languages:
            st.write(f"Total languages: {len(languages)}")
            st.dataframe(pd.DataFrame(languages, columns=["Language"]), height=200)
        else:
            st.warning("No languages data available")

if __name__ == "__main__":
    main()