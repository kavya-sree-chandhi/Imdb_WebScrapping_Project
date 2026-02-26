from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd

# -----------------------------
# 1. Chrome setup (modern Selenium)
# -----------------------------
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # uncomment if you want headless mode

driver = webdriver.Chrome(options=options)

# -----------------------------
# 2. Open IMDb Top 250 page
# -----------------------------
url = "https://www.imdb.com/chart/top/"
driver.get(url)

# Wait until first movies load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item"))
)

# -----------------------------
# 3. Scroll to load ALL 250 movies
# -----------------------------
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# -----------------------------
# 4. Parse rendered HTML
# -----------------------------
soup = BeautifulSoup(driver.page_source, "lxml")
movies = soup.select("li.ipc-metadata-list-summary-item")

print("Total movies loaded:", len(movies))

# -----------------------------
# 5. Extract data
# -----------------------------
movie_data = []

for i in movies:

    # Rank (blue badge)
    rank_tag = i.select_one("div.ipc-signpost")
    rank = rank_tag.text.replace("#", "").strip() if rank_tag else None

    # Title
    title = i.h3.text.strip()

    # Rating + vote count
    rating = i.select_one("span.ipc-rating-star").text.strip()

    # Year & Duration
    metadata = i.select("span.sc-a55f6282-6")
    year = metadata[0].text.strip() if len(metadata) > 0 else None
    duration = metadata[1].text.strip() if len(metadata) > 1 else None

    # Poster image URL
    img_tag = i.select_one("img")
    poster_url = img_tag["src"] if img_tag else None

    movie_data.append({
        "Rank": rank,
        "Title": title,
        "Year": year,
        "Duration": duration,
        "Rating": rating,
        "Poster_URL": poster_url
    })

driver.quit()

# -----------------------------
# 6. Save to CSV
# -----------------------------
file_name = "imdb_top_250_selenium.csv"

with open(file_name, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=movie_data[0].keys())
    writer.writeheader()
    writer.writerows(movie_data)

print(f"Saved {len(movie_data)} movies to {file_name}")

# Input and output files
csv_file = "imdb_top_250_selenium.csv"
excel_file = "imdb_top_250_selenium.xlsx"

# Read CSV
df = pd.read_csv(csv_file)

# Write to Excel
df.to_excel(excel_file, index=False, engine="openpyxl")

print(f"Converted {csv_file} → {excel_file}")