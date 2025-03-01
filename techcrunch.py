import requests
from bs4 import BeautifulSoup
import json

def scrape_techcrunch(query):
    url = f"https://techcrunch.com/?s={query}"
    print(f"Scraping URL: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    results_ul = soup.find('ul', class_='wp-block-post-template')
    if not results_ul:
        print(f"No results found for query: {query}")
        return []
    
    results = []
   
    for li in results_ul.find_all('li', recursive=False):
        card = li.find('div', class_='wp-block-techcrunch-card')
        if not card:
            continue
        
        loop_card = card.find('div', class_='loop-card')
        if not loop_card:
            continue
        
       
        image_url = "N/A"
        figure = loop_card.find('figure', class_='loop-card__figure')
        if figure:
            img = figure.find('img')
            if img and img.get('src'):
                image_url = img.get('src')
        
        
        content_div = loop_card.find('div', class_='loop-card__content')
        if not content_div:
            continue
        
        
        category = "N/A"
        cat_group = content_div.find('div', class_='loop-card__cat-group')
        if cat_group:
            cat_tag = cat_group.find(['a', 'span'], class_='loop-card__cat')
            if cat_tag:
                category = cat_tag.get_text(strip=True)
        
        
        title = "N/A"
        link = "N/A"
        h3 = content_div.find('h3', class_='loop-card__title')
        if h3:
            a_tag = h3.find('a', class_='loop-card__title-link')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href')
        
        
        author = "N/A"
        meta_div = content_div.find('div', class_='loop-card__meta')
        if meta_div:
            author_list = meta_div.find('ul', class_='loop-card__meta-item')
            if author_list:
                author_links = author_list.find_all('a', class_='loop-card__author')
                if author_links:
                    authors = [a.get_text(strip=True) for a in author_links]
                    author = ", ".join(authors)
        
        
        date = "N/A"
        time_tag = content_div.find('time')
        if time_tag:
            date = time_tag.get_text(strip=True)
        
        article_data = {
            "title": title,
            "link": link,
            "date": date,
            "category": category,
            "author": author,
            "image": image_url
        }
        results.append(article_data)
    
    return results

if __name__ == "__main__":
    queries = ["indians", "startups", "founders"]
    all_results = {}

    for query in queries:
        print(f"\n--- Scraping results for query: '{query}' ---")
        articles = scrape_techcrunch(query)
        all_results[query] = articles
        
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"Link: {article['link']}")
            print(f"Date: {article['date']}")
            print(f"Category: {article['category']}")
            print(f"Author: {article['author']}")
            print(f"Image: {article['image']}\n")
    
    
    with open("techcrunch_articles.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    
    print("Results saved to techcrunch_articles.json")
