import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import logging

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
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main title (h1)
            title_element = soup.find('h1', class_='page-heading-md')
            title = title_element.get_text(strip=True) if title_element else "Unknown Mission"
            
            # Extract mission description (subtitle)
            subtitle_element = soup.find('p', class_='p-lg')
            subtitle = subtitle_element.get_text(strip=True) if subtitle_element else ""
            
            # Extract all narrative paragraphs from the main content
            paragraphs = []
            entry_content = soup.find('div', class_='entry-content')
            if entry_content:
                # Get paragraphs from encyclopedic content
                content_columns = entry_content.find('div', class_='hds-encyclopedic-primary-column')
                if content_columns:
                    for p in content_columns.find_all('p'):
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out very short paragraphs
                            paragraphs.append(text)
                
                # Also get paragraphs from mission meta description
                meta_section = entry_content.find('div', class_='mission-single-meta')
                if meta_section:
                    for p in meta_section.find_all('p', class_='p-lg'):
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:
                            paragraphs.append(text)            
            
            # --- extract metadata from both possible containers ---
            metadata_table = []
            seen_keys = set()

            # grab all the <div class="grid-row"> blocks living under either meta‐section
            rows = soup.select(
                "div.mission-single-meta div.grid-row, div.hds-mission-header div.grid-row"
            )

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
            
            # --- extract mission status ---
            mission_status = self.scrape_mission_status(soup)
                   
            # [CHALLENGE] Extract publication/last updated date - here we try multiple approaches
            pub_date = self.extract_publication_date(soup, url)
            
            # [EXTENDED SCRAPPING] Get mission stories/news links from the main page
            stories = self.extract_mission_stories(soup, url)
            
            # Find and scrape the dedicated stories/news page
            stories_page_url = self.find_mission_stories_page(soup, url)

            return {
                "title": title,
                "subtitle": subtitle,
                "url": url,
                "date": pub_date,
                "paragraphs": paragraphs,
                "metadata_table": metadata_table,
                "stories": stories,
                'mission_status' : mission_status,
                "stories_page_url": stories_page_url,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def extract_publication_date(self, soup, url):
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
    
    def extract_mission_stories(self, soup, base_url):
        """Extract related stories and news articles from the main mission page"""
        stories = []
        
        # Look for news items in the automated news section
        news_section = soup.find('div', class_='wp-block-nasa-blocks-news-automated')
        if news_section:
            news_items = news_section.find_all('a', class_='latest-news-item')
            for item in news_items:
                story_url = item.get('href')
                title_elem = item.find('p', class_='heading-22') or item.find('p', class_='heading-14')
                
                if story_url and title_elem:
                    stories.append({
                        "title": title_elem.get_text(strip=True),
                        "url": urljoin(base_url, story_url),
                        "type": "news"
                    })
        
        return stories
    
    def find_mission_stories_page(self, soup, base_url):
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


    def scrape_stories_page(self, stories_url):
        """Scrape all story URLs from a mission's stories page"""
        try:
            logger.info(f"Scraping stories page: {stories_url}")
            response = self.session.get(stories_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            story_urls = []
            
            # Look for story links in various possible containers
            selectors_to_try = [
                'hds-content-item-thumbnail a[href]',
                # 'article a[href]',
                '.hds-content-item a[href]',
                # '.news-item a[href]',
                # '.story-item a[href]',
                # '.post a[href]',
                # '.wp-block-post a[href]',
                # '[class*="news"] a[href]',
                # '[class*="story"] a[href]',
                # '[class*="article"] a[href]',
                # '.grid-col a[href*="/news/"]',
                # '.grid-col a[href*="/article/"]',
                # '.grid-col a[href*="/story/"]',
                # '.grid-col a[href*="/blog/"]',
                # 'a[href*="/press-release/"]'
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    full_url= href
                    if full_url not in story_urls:
                        story_urls.append(full_url)
            
            
            logger.info(f"Found {len(story_urls)} story URLs from {stories_url}")
            return story_urls
            
        except Exception as e:
            logger.error(f"Error scraping stories page {stories_url}: {e}")
            return []
       
    def scrape_mission_status(self, soup):
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


    def scrape_individual_story(self, story_url):
        """Scrape content from an individual story/article"""
        try:
            response = self.session.get(story_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract story title
            title = None
            title_selectors = ['h1', '.entry-title', '.article-title', '.post-title', '.page-heading-md']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extract publication date
            pub_date = self.extract_story_date(soup)
            
            # Extract article content (be careful not to reproduce full copyrighted text)
            content_summary = self.extract_story_summary(soup)
            
            # Extract key facts/metadata
            metadata = self.extract_story_metadata(soup)
            
            return {
                "title": title or "Unknown Title",
                "url": story_url,
                "publication_date": pub_date,
                "summary": content_summary,
                "metadata": metadata,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping story {story_url}: {e}")
            return None

    def extract_story_date(self, soup):
        """Extract publication date from story page"""
        # Try multiple date extraction methods
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.published-date',
            '.article-date',
            '.post-date',
            '.date'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                date_value = elem.get('content') or elem.get('datetime') or elem.get_text(strip=True)
                if date_value:
                    return date_value
        
        return None

    def extract_story_summary(self, soup):
        """Extract a brief summary of the story (not full copyrighted content)"""
        # Extract only the first paragraph or meta description as summary
        # This avoids reproducing copyrighted material
        
        # Try meta description first
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try first paragraph of main content
        content_selectors = [
            '.entry-content p:first-of-type',
            '.article-content p:first-of-type',
            '.post-content p:first-of-type',
            'main p:first-of-type',
            '.content p:first-of-type'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                # Limit to first sentence or 200 characters to avoid copyright issues
                if text:
                    sentences = text.split('.')
                    if sentences:
                        return sentences[0][:200] + ('...' if len(sentences[0]) > 200 else '.')
        
        return ""

    def extract_story_metadata(self, soup):
        """Extract structured metadata from story"""
        metadata = {}
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            '.author-name',
            '.byline',
            '[rel="author"]',
            '.author'
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                author = elem.get('content') or elem.get_text(strip=True)
                if author:
                    metadata['author'] = author
                    break
        
        # Extract categories/tags
        categories = []
        category_selectors = [
            '.category',
            '.tag',
            '.post-category',
            '[rel="category tag"]',
            '.tags'
        ]
        
        for selector in category_selectors:
            elems = soup.select(selector)
            for elem in elems:
                cat = elem.get_text(strip=True)
                if cat and cat not in categories:
                    categories.append(cat)
        
        if categories:
            metadata['categories'] = categories
        
        return metadata
    
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
