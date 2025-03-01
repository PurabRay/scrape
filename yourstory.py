import tempfile
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_yourstory_dynamic(query, page=1):
    url = f"https://yourstory.com/search?q={query}&page={page}"
    print(f"Scraping URL: {url}")
    
    
    temp_data_dir = tempfile.mkdtemp()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
   
    chrome_options.add_argument(f"--user-data-dir={temp_data_dir}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    try:
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.container-results"))
        )
    except Exception as e:
        print("Search results container not found:", e)
        driver.quit()
        return []
    
    html = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    container = soup.find("section", class_="container-results")
    if not container:
        print("Results section not found.")
        return []
    
    li_items = container.find_all("li", class_="sc-c9f6afaa-0 cuRydj")
    if not li_items:
        print("No result items found.")
        return []
    
    results = []
    for li in li_items:
        
        a_tag = li.find("a", {"data-sectiontype": "default"})
        if a_tag:
            link = a_tag.get("href")
            if link and link.startswith("/"):
                link = "https://yourstory.com" + link
            img_tag = a_tag.find("img")
            image = img_tag.get("src") if img_tag else None
        else:
            link, image = None, None
        
       
        date_span = li.find("span", class_="sc-36431a7-0 dpmmXH")
        date = date_span.get_text(strip=True) if date_span else None
        
       
        title_span = li.find("span", attrs={"pathname": "/search"})
        title = title_span.get_text(strip=True) if title_span else None
        
        
        category = None
        cat_div = li.find("div", class_="sc-c9f6afaa-10 jqCVBY")
        if cat_div:
            cat_span = cat_div.find("span", class_="sc-c9f6afaa-4 exBjWC")
            if cat_span:
                category = cat_span.get_text(strip=True)
        
        results.append({
            "title": title,
            "link": link,
            "image": image,
            "date": date,
            "category": category
        })
    
    return results


queries = ["founders", "startups", "indians"]
all_results = {}

for query in queries:
    print(f"\n--- Results for query: '{query}' ---")
    data = scrape_yourstory_dynamic(query, page=1)
    all_results[query] = data
    for item in data:
        print(json.dumps(item, indent=2))
        
with open("yourstory_results_dynamic.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print("Results saved to yourstory_results_dynamic.json")