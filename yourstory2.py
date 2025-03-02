import undetected_chromedriver as uc
import time
import pickle
import os
import json
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


cookies_file = "cookies.pkl"

def login_and_save_cookies():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.get("https://yourstory.com/login")
    print("Please log in manually within the next 40 seconds...")
    time.sleep(40)
    with open(cookies_file, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("Cookies saved successfully!")
    driver.quit()

if not os.path.exists(cookies_file):
    login_and_save_cookies()


options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)
driver.get("https://yourstory.com")
time.sleep(5)
with open(cookies_file, "rb") as f:
    cookies = pickle.load(f)
    for cookie in cookies:
        if "sameSite" in cookie:
            cookie.pop("sameSite")
        driver.add_cookie(cookie)
driver.refresh()
time.sleep(5)

def get_excerpt(link):
    """Given an article URL, visit the page and return the excerpt text."""
    try:
        driver.get(link)
        time.sleep(random.uniform(2, 3))
        soup_article = BeautifulSoup(driver.page_source, "html.parser")
        
        meta_desc = soup_article.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
        
        article_tag = soup_article.find("article")
        if article_tag:
            p_tag = article_tag.find("p")
            if p_tag:
                return p_tag.get_text(strip=True)
        return ""
    except Exception as e:
        print(f"Error scraping excerpt from {link}: {e}")
        return ""


def scrape_yourstory(query, page=1):
    results = []
    search_url = f"https://yourstory.com/search?q={query}&page={page}"
    print(f"\nScraping URL: {search_url}")
    try:
        driver.get(search_url)
        time.sleep(random.uniform(5, 8))
        
        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(2, 4))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        container = soup.find("section", class_="container-results")
        if not container:
            print("No container-results found on the page.")
            return results

       
        article_items = container.select("li.sc-c9f6afaa-0")
        if not article_items:
            print("No article items found in container.")
            return results

        for item in article_items:
            
            a_tags = item.find_all("a", href=True)
            title = None
            link = None
            for a in a_tags:
                span = a.find("span")
                if span:
                    text = span.get_text(strip=True)
                    if text:
                        title = text
                        link = a["href"]
                        break

           
            if link and link.startswith("/"):
                link = "https://yourstory.com" + link

          
            date_tag = item.find("span", class_="sc-36431a7-0 dpmmXH")
            date = date_tag.get_text(strip=True) if date_tag else None

           
            cat_container = item.select_one("div.sc-c9f6afaa-10.jqCVBY span")
            category = cat_container.get_text(strip=True) if cat_container else None

            
            excerpt = get_excerpt(link) if link else ""

            results.append({
                "title": title,
                "link": link,
                "date": date,
                "category": category,
                "excerpt": excerpt
            })
            print(f"Title: {title}\nLink: {link}\nDate: {date}\nCategory: {category}\nExcerpt: {excerpt}\n")
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
    return results

# Scrape results for multiple queries and save the results in a JSON file.
queries = ["founders", "startups", "indians"]
all_results = {}
for query in queries:
    print(f"\n--- Results for query: '{query}' ---")
    query_results = []
    for page in range(1, 2):  # Increase range if you want more pages.
        data = scrape_yourstory(query, page)
        query_results.extend(data)
    all_results[query] = query_results

with open("yourstory_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4)

print("\nScraping completed. Results saved to 'yourstory_results.json'.")
driver.quit()
