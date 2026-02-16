# -*- coding: utf-8 -*-
"""
Cornell US Code Title Scraper
Uses requests and BeautifulSoup for reliable extraction
"""

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from bs4 import BeautifulSoup
import json
import time
import ssl

# Final TLS configuration that suppresses warnings while allowing data
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = ssl._create_unverified_context()
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

# Create session with custom SSL/TLS settings
session = requests.Session()
session.mount('https://', TLSAdapter())
session.verify = False  # Temporary - should verify certificates in production
# Add retry logic
retry_strategy = requests.adapters.HTTPAdapter(max_retries=3)
session.mount("https://", retry_strategy)
session.mount("http://", retry_strategy)

TARGET_URL = "https://www.law.cornell.edu/uscode/text"
OUTPUT_FILE = "lii_title.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.law.cornell.edu/"
}
def extract_chapter_info(li_elem):
    """Extract chapter name, section range, and URL from list item"""
    try:
        full_text = li_elem.get_text(strip=True)
        
        # Extract chapter name (before parentheses)
        chapter_name = full_text.split('(§§')[0].strip() if '(§§' in full_text else full_text
        
        # Extract section range if present
        section_range = ""
        if '(§§' in full_text and ')' in full_text:
            start = full_text.find('§§') + 2
            end = full_text.find(')', start)
            section_range = full_text[start:end].strip().replace('–', '-')
        
        # Extract URL
        url = ""
        a_tag = li_elem.find('a', href=True)
        if a_tag and a_tag['href']:
            url = a_tag['href'] if a_tag['href'].startswith('http') else "https://www.law.cornell.edu{0}".format(a_tag['href'])
        
        return {
            'chapter_name': chapter_name,
            'section_range': section_range,
            'url': url
        }
    except Exception as e:
        print("Error parsing chapter info: {0}".format(str(e)))
        return None

def scrape_chapters(title_url):
    """Scrape all chapters from a title page"""
    try:
        response = session.get(title_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        main_elem = soup.find('main') or soup.find('div', role='main')
        
        if not main_elem:
            print("No main element found in {0}".format(title_url))
            return []
            
        chapters = []
        for li in main_elem.find_all('li'):
            chapter = extract_chapter_info(li)
            if chapter:
                chapters.append(chapter)
                range_info = " (§§ {0})".format(chapter['section_range']) if chapter['section_range'] else ""
                print("  ✓ {0}{1}".format(chapter['chapter_name'], range_info))
                
        return chapters
        
    except Exception as e:
        print("Error scraping chapters from {0}: {1}".format(title_url, str(e)))
        return []

def scrape_titles():
    """Scrape US Code titles using requests and BeautifulSoup"""
    titles = []
    
    try:
        print("Requesting page: {0}".format(TARGET_URL))
        response = session.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        print("Request status: {0}".format(response.status_code))
        print("Content length: {0} characters".format(len(response.text)))
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all list items that contain title links
        # Target <li> elements with <a> tags that link to /uscode/text/
        li_elements = soup.find_all("li")
        print("\nFound {0} list items".format(len(li_elements)))
        
        for li in li_elements:
            try:
                # Look for anchor tag within the list item
                a_tag = li.find("a", href=True)
                if not a_tag:
                    continue
                
                href = a_tag["href"]
                if "/uscode/text/" not in href:
                    continue
                
                # Extract title text
                title_text = a_tag.get_text(strip=True)
                
                # Process title text (format: "TITLE 4 - FLAG AND SEAL, SEAT OF GOVERNMENT, AND THE STATES")
                if title_text.startswith("TITLE ") and " - " in title_text:
                    parts = title_text.split(" - ", 1)
                    if len(parts) == 2:
                        title_num_part = parts[0].replace("TITLE", "").strip()
                        title_name = parts[1].strip()
                        
                        # Store title number as string
                        title_number = title_num_part
                        
                        # Add to results if unique
                        if not any(t["title_number"] == title_number for t in titles):
                            url = "https://www.law.cornell.edu{0}".format(href)
                            chapters = scrape_chapters(url)
                            titles.append({
                                "title_number": title_number,
                                "title_name": title_name,
                                "url": url,
                                "chapters": chapters
                            })
                            print("✓ Extracted: TITLE {0} - {1} ({2} chapters)".format(title_number, title_name, len(chapters)))
            
            except Exception as e:
                print("Error processing list item: {0}".format(str(e)))
                continue
        # Fallback: If no titles found, search for all elements containing "TITLE"
        if not titles:
            print("\nTrying fallback method - searching all text for TITLE patterns")
            all_text = soup.get_text()
            
            # Split text into lines and look for title patterns
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("TITLE ") and " - " in line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        title_num_part = parts[0].replace("TITLE", "").strip()
                        title_name = parts[1].strip()
                        
                        title_number = title_num_part  # Store as string
                        
                        if not any(t["title_number"] == title_number for t in titles):
                            url = "https://www.law.cornell.edu/uscode/text"
                            chapters = scrape_chapters(url)
                            titles.append({
                                "title_number": title_number,
                                "title_name": title_name,
                                "url": url,
                                "chapters": chapters
                            })
                            print("✓ Fallback extracted: TITLE {0} - {1} ({2} chapters)".format(title_number, title_name, len(chapters)))
        
        # Remove duplicates and sort
        unique_titles = []
        seen = set()
        for title in titles:
            key = str(title["title_number"])
            if key not in seen:
                seen.add(key)
                unique_titles.append(title)
        
        # Sort by title number (as string)
        unique_titles.sort(key=lambda x: str(x["title_number"]).zfill(5))  # Pad with zeros for consistent sorting
        
        return unique_titles
    
    except Exception as e:
        print("Scraping error: {0}".format(str(e)))
        return []
        
        # Fallback: If no titles found, search for all elements containing "TITLE"
        if not titles:
            print("\nTrying fallback method - searching all text for TITLE patterns")
            all_text = soup.get_text()
            
            # Split text into lines and look for title patterns
            lines = all_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("TITLE ") and " - " in line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        title_num_part = parts[0].replace("TITLE", "").strip()
                        title_name = parts[1].strip()
                        
                        try:
                            title_number = int(title_num_part)
                        except:
                            title_number = title_num_part
                        
                        if not any(t["title_number"] == title_number for t in titles):
                            titles.append({
                                "title_number": title_number,
                                "title_name": title_name
                            })
                            print("✓ Fallback extracted: TITLE {0} - {1}".format(title_number, title_name))
        
        # Remove duplicates and sort
        unique_titles = []
        seen = set()
        for title in titles:
            key = str(title["title_number"])
            if key not in seen:
                seen.add(key)
                unique_titles.append(title)
        
        # Sort by title number (as string)
        unique_titles.sort(key=lambda x: str(x["title_number"]).zfill(5))  # Pad with zeros for consistent sorting
        
        return unique_titles
    
    except Exception as e:
        print("Scraping error: {0}".format(str(e)))
        return []

def main():
    print("🚀 Cornell US Code Title Scraper")
    print("=================================")
    
    titles = scrape_titles()
    
    if titles:
        print("\n✅ Successfully extracted {0} titles".format(len(titles)))
        
        # Save to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(titles, f, indent=2, ensure_ascii=False)
        
        print("💾 Results saved to: {0}".format(OUTPUT_FILE))
        
        # Show sample
        print("\nSample of extracted data:")
        for i, title in enumerate(titles[:3], 1):
            print("  {0}. TITLE {1} - {2}".format(i, title['title_number'], title['title_name']))
            if title.get('chapters'):
                print("    Chapters: {0}".format(len(title['chapters'])))
                for chap in title['chapters'][:2]:  # Show first 2 chapters as sample
                    range_info = " (§§ {0})".format(chap['section_range']) if chap['section_range'] else ""
                    print("      {0}{1}".format(chap['chapter_name'], range_info))
        
        if len(titles) > 5:
            print("  ... and {0} more titles with chapters".format(len(titles)-3))
    
    else:
        print("\n⚠️ No titles were extracted")
        print("Possible reasons:")
        print("  1. Page structure changed")
        print("  2. Anti-scraping measures detected")
        print("  3. Network issues")

if __name__ == "__main__":
    try:
        main()
    except IOError as e:
        if e.errno == 32:  # Broken pipe when piping to json.tool
            pass  # This is expected when piping output
        else:
            raise