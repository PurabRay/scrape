import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_indiehackers_search(query):
    base_url = "https://www.indiehackers.com"
    search_url = f"{base_url}/search?q={query}"
    print(f"Scraping URL: {search_url}")

  
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    
    driver.get(search_url)
    
    time.sleep(5)  # Adjust if needed or use explicit waits.
    
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    indie_hackers = []
    
    
    container = soup.find("div", class_="search-page__results-content")
    if not container:
        print("No search results container found.")
        return indie_hackers
    
    
    result_divs = container.find_all("div", class_="search-page__result")
    for div in result_divs:
        a_tag = div.find("a", class_="result__text-link")
        if not a_tag:
            continue
        
        
        title_div = a_tag.find("div", class_="result__title")
        title = title_div.get_text(strip=True) if title_div else "N/A"
        
        
        link = a_tag.get("href", "N/A")
        if link.startswith("/"):
            link = base_url + link
        
        
        snippet_div = a_tag.find("div", class_="result__snippet")
        snippet_text = snippet_div.get_text(" ", strip=True) if snippet_div else ""
        date = "N/A"
        excerpt = ""
        if " - " in snippet_text:
            parts = snippet_text.split(" - ", 1)
            date = parts[0].strip()
            excerpt = parts[1].strip()
        else:
            excerpt = snippet_text
        
       
        category = "Discussion"
        
        item = {
            "title": title,
            "link": link,
            "date": date,
            "category": category,
            "excerpt": excerpt
        }
        indie_hackers.append(item)
    
    return indie_hackers

if __name__ == "__main__":
    query = "Indians" 
    indie_hackers = scrape_indiehackers_search(query)
    
    
    with open("indie_hackers.json", "w", encoding="utf-8") as f:
        json.dump(indie_hackers, f, indent=4)
    
    print(json.dumps(indie_hackers, indent=4))
