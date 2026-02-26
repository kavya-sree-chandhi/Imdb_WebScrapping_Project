import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.imdb.com/chart/top/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

soup = BeautifulSoup(response.text, "lxml")

movies = soup.select("li.ipc-metadata-list-summary-item")

# List to store all movie data
movie_data = []

for i in movies:

    # Rank (blue badge)
    rank_tag = i.select_one("div.ipc-signpost")
    rank = rank_tag.text.replace("#", "").strip() if rank_tag else None

    # Title
    title = i.h3.text.strip()

    # Rating
    rating = i.select_one("span.ipc-rating-star").text.strip()

    # Year & Duration
    metadata = i.select("span.sc-a55f6282-6")
    year = metadata[0].text.strip() if len(metadata) > 0 else None
    duration = metadata[1].text.strip() if len(metadata) > 1 else None

    # Poster Image URL
    img_tag = i.select_one("img")
    poster_url = img_tag["src"] if img_tag else None

    # Store as dictionary
    movie_data.append({
        "Rank": rank,
        "Title": title,
        "Year": year,
        "Duration": duration,
        "Rating": rating,
        "Poster_URL": poster_url
    })

# Save to CSV
file_name = "imdb_top_250.csv"

with open(file_name, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=movie_data[0].keys())
    writer.writeheader()
    writer.writerows(movie_data)

print(f"Saved {len(movie_data)} movies to {file_name}")