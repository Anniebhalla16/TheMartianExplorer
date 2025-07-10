import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import logging

from dotenv import load_dotenv
from groq import Groq
load_dotenv()

groq = Groq()


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarsMissionScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create raw_missions directory if it doesn't exist
        os.makedirs('raw_missions', exist_ok=True)
    
    def get_mars_mission_urls(self):
        """Get all Mars mission URLs from NASA's API on /science-missions page"""
        try:
            mars_api_url = "https://science.nasa.gov/wp-json/smd/v1/content-list/?block_id=all-missions&exclude_child_pages=true&layout=grid&listing_page=no&listing_page_category_id=0&number_of_items=51&order=ASC&orderby=title&current_page=1&requesting_id=47243&science_only=true&show_content_type_tags=no&show_excerpts=yes&show_pagination=true&show_publish_date=no&show_readtime=no&show_thumbnails=yes&response_format=html&show_drafts=false&use_content_term_filters=true&post_types=mission&base_terms=%7B%22category%22%3A%22%22%2C%22science-org%22%3A%22%22%2C%22internal-terms%22%3A%22%22%2C%22news-tags%22%3A%22%22%7D&mission_target=4176"
            
            response = self.session.get(mars_api_url)
            response.raise_for_status()
            
            page_mars = response.json()["content"]
            mars_soup = BeautifulSoup(page_mars, "html.parser")
            mars_missions = mars_soup.find_all('a', class_='hds-content-item-thumbnail')
            mars_links = [m.get('href') for m in mars_missions if m.get('href')]
            
            logger.info(f"Found {len(mars_links)} Mars mission URLs")
            return mars_links
            
        except Exception as e:
            logger.error(f"Error fetching Mars mission URLs: {e}")
            return []
    
    def extract_mission_data(self, url):
        """Extract mission data from a single NASA mission page"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- Extract main title (h1) ---
            title_element = soup.find('h1', class_='page-heading-md')
            title = title_element.get_text(strip=True) if title_element else "Unknown Mission"
            
            # --- Extract mission description (subtitle) ---
            subtitle_element = soup.find('p', class_='p-lg')
            subtitle = subtitle_element.get_text(strip=True) if subtitle_element else ""
            
            # --- extract overview from the main content ---
            overview = self.get_mission_overview(url)
            
            # --- extract metadata from both possible containers ---
            metadata_table = self.get_metadata(soup)
            
            # --- extract mission status ---
            mission_status = self.scrape_mission_status(soup)
                   
            # --- [CHALLENGE] Extract publication/last updated date - here we try multiple approaches ---
            pub_date = self.extract_publication_date(soup)
            
            # --- Find and scrape the dedicated stories/news page ---
            stories_page_url = self.find_mission_stories_page_url(soup, url)
            
            # --- Extended scrapping ---
            stories = self.extract_all_mission_stories(stories_page_url)
            

            return {
                "title": title,
                "subtitle": subtitle,
                "url": url,
                "date": pub_date,
                "overview": overview,
                "metadata_table": metadata_table,
                "stories": stories,
                'mission_status' : mission_status,
                "stories_page_url": stories_page_url,
                "scraped_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def get_mission_overview(self, url):

        prompt = f"""
        You are a NASA mission summarizer. Given a single input: a URL pointing to a NASA Science “Mission” webpage, perform the following steps:

        Fetch & Clean
        - Retrieve the page’s HTML.
        - Strip out all navigation, ads, scripts, styles, image captions, footers—anything that isn’t the mission’s human-written content.

        Extract
        - Identify the mission’s name (usually the largest heading or page title).
        - Locate the introductory description and any bulleted or paragraph text that describes what the mission does, why it exists, who’s involved, when it launches, and its goals.
        - Ignore lists of unrelated links, site chrome, and anything not directly describing the mission.

        Summarize
        - Using only the extracted text (no outside knowledge), write a single 3–5 sentence overview paragraph that states:
          • What the mission is and who’s running it  
          • When it will launch or its status  
          • What it will study or accomplish  
          • Any unique aspects (e.g. sample return, first of its kind, etc.)
        - Do not hallucinate or add facts not present on the page.

        Output
        Return only the overview paragraph.

        Here is the Nasa Mission URL: {url}
        """

        chat_completion = groq.chat.completions.create(
        model="llama-3.3-70b-versatile" ,
        messages=[
            {
                "role":"user",
                "content":prompt,

            }
        ])
        return chat_completion.choices[0].message.content
 
        
    def extract_publication_date(self, soup):
        """Extract publication date from various sources"""
        # Try to find date in meta tags
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        if date_meta:
            return date_meta.get('content')
        
        # Try to find date in structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'datePublished' in data:
                    return data['datePublished']
            except:
                continue
        
        # Default to current date if not found
        return datetime.now().isoformat()
    
    def get_metadata(self, soup):
        metadata_table = []
        seen_keys = set()

        # grab all the <div class="grid-row"> blocks living under either meta‐section
        rows = soup.select(
            "div.mission-single-meta div.grid-row, div.hds-mission-header div.grid-row" )

        for row in rows:
                # within each row, the label/value lives in either
                #   <div class="grid-col-6">…</div>
                # or
                #   <div class="grid-col">…</div>
            blocks = row.select("div.grid-col-6, div.grid-col")

            for blk in blocks:
                label_elem = blk.find("p", class_="label")
                value_elem = blk.find("div", class_="p-lg")

                if not (label_elem and value_elem):
                    continue

                key = label_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)

                    # only add each key once
                if key and value and key not in seen_keys:
                    metadata_table.append({"key": key, "value": value})
                    seen_keys.add(key)
                    
        return metadata_table
            
    
    def extract_all_mission_stories(self, stories_url):
        """Scrape all story URLs, thumbnails, titles and types from a mission's stories page"""
        try:
            logger.info(f"Scraping stories page: {stories_url}")
            resp = self.session.get(stories_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # target the three container classes
            story_items = soup.select(
                "div.hds-content-item.content-list-item-post-ext, "
                "div.hds-content-item.content-list-item-post, "
                "div.hds-content-item.content-list-item-press-release-ext"
            )

            stories = []
            for item in story_items:
                # 1) URL & thumbnail
                thumb_link = item.find('a', class_='hds-content-item-thumbnail')
                if not thumb_link or not thumb_link.get('href'):
                    continue
                story_url = thumb_link['href']
                img = thumb_link.find('img')
                story_image_url = img.get('src') if img else None

                # 2) Title
                inner = item.find('div', class_='hds-content-item-inner')
                if not inner:
                    continue

                heading_link = inner.find('a', class_='hds-content-item-heading')
                title = None
                if heading_link:
                    title_div = heading_link.find('div', class_='hds-a11y-heading-22')
                    title = title_div.get_text(strip=True) if title_div else None

                # 3) Type
                type_span = inner.select_one('div.label span')
                story_type = type_span.get_text(strip=True) if type_span else None

                stories.append({
                    "url": story_url,
                    "story_image_url": story_image_url,
                    "title": title,
                    "type": story_type   
                })

            logger.info(f"Found {len(stories)} stories on {stories_url}")
            return stories

        except Exception as e:
            logger.error(f"Error scraping stories page {stories_url}: {e}")
            return []

    
    def find_mission_stories_page_url(self, soup, base_url):
        """Find the dedicated stories/news page URL for a mission"""
        stories_url = None
        
        # Look for "Explore All [Mission] Stories" or "Explore All [Mission] News" button
        # Target the specific button structure with button-primary class
        stories_buttons = soup.find_all('a', class_=lambda x: x and 'button-primary' in x)
        
        for button in stories_buttons:
            button_text = button.get_text(strip=True)
            href = button.get('href')
            
            # Check if this is a stories or news exploration button
            if (href and button_text and 
                ('Explore All' in button_text and 
                 ('Stories' in button_text or 'News' in button_text))):
                stories_url = href
                logger.info(f"Found stories button: '{button_text}' -> {href}")
                break
        
        # Alternative: look for any stories link in the news section
        if not stories_url:
            news_section = soup.find('div', class_='wp-block-nasa-blocks-news-automated')
            if news_section:
                for link in news_section.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if (href and '/stories/' in href and 
                        ('Explore All' in text or 'Stories' in text or 'News' in text)):
                        stories_url = href
                        break
        
        # Fallback: construct stories URL from mission URL
        if not stories_url:
            # Extract mission slug from base URL
            mission_slug = base_url.rstrip('/').split('/')[-1]
            potential_stories_url = f"https://science.nasa.gov/mission/{mission_slug}/stories/"
            
            # Test if this URL exists
            try:
                test_response = self.session.head(potential_stories_url)
                if test_response.status_code == 200:
                    stories_url = potential_stories_url
                    logger.info(f"Using fallback stories URL: {stories_url}")
            except:
                pass
        
        if stories_url:
            logger.info(f"Found stories page: {stories_url}")
        else:
            logger.warning(f"No stories page found for {base_url}")
        
        return stories_url

    def scrape_mission_status(self, soup):
        """ Returns the status of the mission - Active, Future, Past """
        badge = soup.find("div", class_="label tag tag-mission")
        if not badge:
            return None
        
        icon = badge.find("div", class_="mission-status-icon")
        if icon:
            classes = icon.get("class", [])
            if "bg-carbon-30" in classes:
                return "past"
            if "bg-active-green" in classes:
                return "active"
            if "bg-nasa-blue-tint" in classes:
                return "future"

        # text if icon not found ( this will not happen, there will always be the badge)
        span = badge.find("span")
        if span:
            txt = span.get_text(strip=True).lower()
            if "occurred" in txt:
                return "past"
            if "active mission" in txt:
                return "active"
            if "future mission" in txt:
                return "future"

        return None
   
    def save_mission_json(self, mission_data, filename):
        """Save mission data to JSON file"""
        try:
            filepath = os.path.join('raw_missions', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mission_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved: {filepath}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def scrape_all_missions(self):
        """Main method to scrape all Mars missions"""
        logger.info("Starting Mars mission scraping...")
        
        # Get all mission URLs
        mission_urls = self.get_mars_mission_urls()
        
        if not mission_urls:
            logger.error("No mission URLs found. Exiting.")
            return
        
        successful_scrapes = 0
        
        for i, url in enumerate(mission_urls, 1):
            try:
                logger.info(f"Processing mission {i}/{len(mission_urls)}")
                
                # Extract mission data
                mission_data = self.extract_mission_data(url)
                
                if mission_data:
                    
                    # Generate filename from mission title
                    safe_title = re.sub(r'[^\w\s-]', '', mission_data['title']).strip()
                    safe_title = re.sub(r'\s+', '_', safe_title).lower()
                    filename = f"{safe_title}.json"
                    
                    # Save to JSON file
                    self.save_mission_json(mission_data, filename)
                    successful_scrapes += 1
                
                # Be respectful to the servers
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing mission {i}: {e}")
                continue
        
        logger.info(f"Scraping completed. Successfully processed {successful_scrapes}/{len(mission_urls)} missions.")
        logger.info(f"JSON files saved in 'raw_missions/' directory")

def main():
    """Main function to run the scraper"""
    scraper = MarsMissionScraper()
    scraper.scrape_all_missions()

if __name__ == "__main__":
    main()
