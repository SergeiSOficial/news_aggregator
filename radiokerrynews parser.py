import requests
from bs4 import BeautifulSoup

url = "https://www.radiokerry.ie/news/"  # Replace with the actual website URL

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

news_articles = []

# Find all the div elements with class 'grid-cols-2'
for article in soup.find_all('div', class_='grid-cols-2'):
    news_data = {}
    
    # Extracting news title and link
    title_tag = article.find('h3', class_='text-gray-900')
    news_data['title'] = title_tag.text.strip() if title_tag else None
    news_data['link'] = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else None
    
    # Extracting image URL
    img_tag = article.find('img', class_='max-w-full')
    news_data['image_url'] = img_tag['src'] if img_tag else None
    
    # Extracting date
    date_tag = article.find('span', class_='text-xs uppercase font-semibold text-gray-600')
    news_data['date'] = date_tag.text.strip() if date_tag else None
    
    # Add news data to the list
    news_articles.append(news_data)

# Display the scraped news data
for news in news_articles:
    print("Title:", news['title'])
    print("Link:", news['link'])
    print("Image URL:", news['image_url'])
    print("Date:", news['date'])
    print("\n")
