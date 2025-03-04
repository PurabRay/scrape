import os
import time
import pickle
import json
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Define the path for the cookies file.
cookies_file = "cookies_inc42.pkl"

def login_and_save_cookies():
    options = uc.ChromeOptions()
    # Launch browser in non-headless mode for manual login.
    driver = uc.Chrome(options=options)
    driver.get("https://inc42.com/login")
    print("Please log in manually within the next 40 seconds...")
    time.sleep(40)  # Adjust waiting time as needed.
    with open(cookies_file, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("Cookies saved successfully!")
    driver.quit()

# If the cookies file doesn't exist, log in manually and save cookies.
if not os.path.exists(cookies_file):
    login_and_save_cookies()

# Set up headless Chrome and load inc42.com with saved cookies.
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)

# Open the homepage to add cookies.
driver.get("https://inc42.com")
time.sleep(5)

# Get the current domain from the URL.
current_domain = urlparse(driver.current_url).netloc

with open(cookies_file, "rb") as f:
    cookies = pickle.load(f)
    for cookie in cookies:
        # Remove 'sameSite' if present.
        if "sameSite" in cookie:
            cookie.pop("sameSite")
        # Override cookie domain to match the current domain.
        cookie["domain"] = current_domain
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Error adding cookie {cookie}: {e}")

driver.refresh()
time.sleep(5)

# Navigate to the search URL.
search_url = "https://inc42.com/?s=indians#inc-search-popup"
driver.get(search_url)
time.sleep(5)  # Allow time for JavaScript-rendered results to load.

soup = BeautifulSoup(driver.page_source, "html.parser")
base_url = "https://inc42.com"
results = []

# Find the search results container.
hits_list = soup.find("ol", class_="ais-Hits-list")
if hits_list:
    hit_items = hits_list.find_all("li", class_="ais-Hits-item")
    for item in hit_items:
        content_div = item.find("div", class_="ais-hits--content")
        if not content_div:
            continue
        
        h2 = content_div.find("h2", class_="entry-title")
        if not h2:
            continue
        a_tag = h2.find("a")
        title = a_tag.get_text(strip=True) if a_tag else "N/A"
        link = a_tag["href"] if a_tag and a_tag.has_attr("href") else "N/A"
        if link.startswith("/"):
            link = base_url + link

        # Extract date from the meta-wrapper.
        date = "N/A"
        meta_div = content_div.find("div", class_="meta-wrapper")
        if meta_div:
            span_date = meta_div.find("span", class_="date")
            if span_date:
                date = span_date.get_text(strip=True)

        # Derive a category from the URL (example logic).
        category = "Stories"
        if link != "N/A":
            if "/buzz/" in link:
                category = "Buzz"
            elif "/features/" in link:
                category = "Features"
            elif "/startups/" in link:
                category = "Startups"

        # Define a helper function to get the excerpt.
        def get_excerpt(url):
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 3))
                article_soup = BeautifulSoup(driver.page_source, "html.parser")
                # Try to get the meta description.
                meta_desc = article_soup.find("meta", {"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    return meta_desc["content"].strip()
                # Fallback: get the first paragraph from the post content.
                article_body = article_soup.find("div", class_="post-content")
                if article_body:
                    p_tag = article_body.find("p")
                    if p_tag:
                        return p_tag.get_text(strip=True)
                return ""
            except Exception as e:
                print(f"Error fetching excerpt from {url}: {e}")
                return ""

        excerpt = get_excerpt(link) if link != "N/A" else ""

        result_item = {
            "title": title,
            "link": link,
            "date": date,
            "category": category,
            "excerpt": excerpt
        }
        results.append(result_item)
else:
    print("No search results found.")

# Save the results to a JSON file.
with open("inc42_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print(json.dumps(results, indent=4))
driver.quit()
