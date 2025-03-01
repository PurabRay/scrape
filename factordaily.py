import requests
from bs4 import BeautifulSoup
import json

def scrape_factordaily(query, page=1):
  
    if page == 1:
        url = f"https://factordaily.com/?s={query}"
    else:
        url = f"https://factordaily.com/page/{page}/?s={query}"
    
    print(f"Scraping URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}: Status code {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    search_post_list = soup.find("div", class_="search-post-list")
    if not search_post_list:
        print("No search post list found on the page.")
        return []
    
    posts = search_post_list.find_all("div", class_="single")
    results = []
    
    for post in posts:
     
        image = None
        img_div = post.find("div", class_="img-div")
        if img_div:
            a_img = img_div.find("a")
            if a_img:
                img_tag = a_img.find("img")
                if img_tag and img_tag.has_attr("src"):
                    image = img_tag["src"]
        
       
        category = None
        cat_div = post.find("div", class_="category-div")
        if cat_div:
            a_cat = cat_div.find("a")
            if a_cat:
                category = a_cat.get_text(strip=True)
        
    
        title = None
        link = None
        h3 = post.find("h3")
        if h3:
            a_title = h3.find("a")
            if a_title:
                title = a_title.get_text(strip=True)
                link = a_title.get("href")
        
        
        date = None
        date_div = post.find("div", class_="date")
        if date_div:
            date = date_div.get_text(strip=True)
        
        
        excerpt = None
        excerpt_div = post.find("div", class_="excerpt")
        if excerpt_div:
            excerpt = excerpt_div.get_text(strip=True)
        
      
        author = None
        author_div = post.find("div", class_="author-div")
        if author_div:
            a_author = author_div.find("a")
            if a_author:
                author = a_author.get_text(strip=True)
        
        results.append({
            "title": title,
            "link": link,
            "image": image,
            "category": category,
            "date": date,
            "excerpt": excerpt,
            "author": author
        })
    return results


queries = ["founders", "indians", "startups"]

all_results = {}


for query in queries:
    print(f"\n--- Results for query: {query} ---")
    posts = scrape_factordaily(query, page=1)
    all_results[query] = posts
    for post in posts:
        print(f"Title: {post['title']}")
        print(f"Link: {post['link']}")
        print(f"Date: {post['date']}")
        print(f"Category: {post['category']}")
        print(f"Excerpt: {post['excerpt']}")
        print(f"Author: {post['author']}")
        print(f"Image: {post['image']}\n")


with open("factordaily_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print("Results saved to factordaily_results.json")
