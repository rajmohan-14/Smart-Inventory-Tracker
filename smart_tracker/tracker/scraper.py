import requests
from bs4 import BeautifulSoup

def scrape_price(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    price_element = soup.find("p", class_="price_color")
    
    if price_element:
        price_text = price_element.text.strip()
        
      
        cleaned_price = ''.join(char for char in price_text if char.isdigit() or char == '.')
        
        return float(cleaned_price)
    
    return None