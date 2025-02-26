import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from markdownify import markdownify as md
import os

url = 'https://www.favikon.com/blog/top-10-most-followed-tiktok-influencers'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
all_elements = list(soup.descendants)

items = []

# Locate section that starts the list
start_section = soup.find('h2', string=lambda text: text and 'Top 10 Most Followed on TikTok' in text)
end_scraping = soup.find('h3', string=lambda text: text and 'Also See 👀 : ' in text)
end_secend_scrapingtion = end_scraping.find_parent()

if start_section:
    container = start_section.find_parent()
    all_divs = container.find_all('div') if container else []

    for i in range(len(all_divs)):
        div = all_divs[i]
        # <div> <img> </div>
        img = div.find('img')

        if img:
            image_url = img['src']
            
            # <h3> Title with a link </h3>
            title_element = div.find_next('h3')
            title = title_element.get_text(strip=True) if title_element else 'No title'

            link = title_element.find('a')['href'] if title_element and title_element.find('a') else '#'

            description = ''
            
            end_section = title_element.find_next('div')
            
            # Terminate scraping if on "Also see"
            if not end_section or all_elements.index(end_section) >= all_elements.index(end_scraping):
                break
            
            p = title_element.find_next('p')
            while all_elements.index(p) < all_elements.index(end_section):
                description += str(p) + '\n'
                p = p.find_next('p')
            items.append({
                'title': title,
                'description': md(description.strip()),
                'link': link,
                'image': image_url
            })

def get_additional_info(query):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=1)

    return results[0]['body'] if results else 'No additional info found.'

# Save scraped data into markdown files
os.makedirs('items', exist_ok=True)

md_content = '''
# Top 10 Most Followed on TikTok
Social media influencers at their best can inspire millions,
drive positive change, and build communities around shared interests.
Here's what makes these top influencers truly special:
'''

for item in items:
    additional_info = get_additional_info('info on ' + item['title'])
    item_filename = f"items/{item['title'].replace(' ', '_').lower()}.md"

    with open(item_filename, 'w', encoding='utf-8') as item_file:
        item_file.write(f"# {item['title']}\n")
        if item['image']:
            item_file.write(f"![Image]({item['image']})\n")
        item_file.write(f"**Description:** {item['description']}\n\n")
        item_file.write(f"**Link:** [TikToker's page]({item['link']})\n\n")

    md_content += f"- [{item['title']}]({item_filename})\n"
    md_content += f"**Description:** {additional_info}\n\n"

with open('scraped_data.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print("Markdown files created successfully.")
