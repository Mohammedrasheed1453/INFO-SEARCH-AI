import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

# ScraperAPI configuration
SCRAPER_API_KEY = "3c1a309cb057b2ca85477dd720fec1e6"  # Replace with your ScraperAPI key

# Function to perform search using ScraperAPI
def search_scraperapi(query):
    url_to_scrape = f"https://www.google.com/search?q={query}"
    scraperapi_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_to_scrape}"

    try:
        response = requests.get(scraperapi_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = []

            for g in soup.find_all('div', class_='tF2Cxc'):  # Adjust for Google's structure
                title = g.find('h3').text if g.find('h3') else 'No title'
                link = g.find('a')['href'] if g.find('a') else 'No link'
                snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else 'No snippet'

                search_results.append({
                    'Title': title,
                    'URL': link,
                    'Snippet': snippet
                })
            return search_results
        else:
            return f"Error: HTTP request failed with status code {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Streamlit App
st.title("INFO SEARCH AI")

# Step 1: Upload CSV
st.header("Upload Data")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
data = pd.DataFrame()

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded Data:")
    st.dataframe(data)

# Proceed if data is available
if not data.empty:
    st.subheader("Select a Column for Queries")
    column_names = data.columns.tolist()
    selected_column = st.selectbox("Select a column:", column_names, key="column_select")

    if selected_column:
        st.subheader("Enter Your Query")
        user_query = st.text_input("Enter your query (e.g., 'What is BMI?' or 'average BMI for males'):")

        if user_query:
            st.write(f"Processing query: {user_query}")
            if any(word in user_query.lower() for word in ["average", "sum"]):
                try:
                    if "average" in user_query.lower():
                        avg_value = data[selected_column].mean()
                        st.success(f"The average {selected_column} is: {avg_value:.2f}")
                    elif "sum" in user_query.lower():
                        sum_value = data[selected_column].sum()
                        st.success(f"The sum of {selected_column} is: {sum_value:.2f}")
                except Exception as e:
                    st.error(f"Error processing query: {e}")
            else:
                # Perform web search using ScraperAPI
                st.write("Performing web search...")
                results = search_scraperapi(user_query)

                if isinstance(results, list) and results:
                    # Display the search results without the snippet
                    st.write("Top Search Results:")
                    result_df = pd.DataFrame(results)
                    for _, row in result_df.head(5).iterrows():  # Show top 5 results
                        st.write(f"**{row['Title']}**")  # Display only the title
                        st.write(f"[Link]({row['URL']})")  # Display the link

                    # Provide CSV download option
                    csv_string = result_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv_string,
                        file_name="search_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("No valid search results found or error occurred.")
