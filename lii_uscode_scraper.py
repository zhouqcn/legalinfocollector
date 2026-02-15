"""
Cornell US Code Title Scraper
Uses requests and BeautifulSoup for reliable extraction
"""

import requests
from bs4 import BeautifulSoup
import json
import time

TARGET_URL = "https://www.law.cornell.edu/uscode/text"
OUTPUT_FILE = "lii_title.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.law.cornell.edu/"
}
def scrape_titles():
    """Scrape US Code titles using requests and BeautifulSoup"""
    titles = []
    
    try:
        print(f"Requesting page: {TARGET_URL}")
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.text)} characters")
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all list items that contain title links
        # Target <li> elements with <a> tags that link to /uscode/text/
        li_elements = soup.find_all("li")
        print(f"\nFound {len(li_elements)} list items")
        
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
                        
                        # Convert to integer
                        try:
                            title_number = int(title_num_part)
                        except ValueError:
                            # Handle special cases like "APPENDIX"
                            title_number = title_num_part
                        
                        # Add to results if unique
                        if not any(t["title_number"] == title_number for t in titles):
                            titles.append({
                                "title_number": title_number,
                                "title_name": title_name,
                                "url": f"https://www.law.cornell.edu{href}"
                            })
                            print(f"✓ Extracted: TITLE {title_number} - {title_name}")
            
            except Exception as e:
                print(f"Error processing list item: {str(e)}")
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
                        
                        try:
                            title_number = int(title_num_part)
                        except:
                            title_number = title_num_part
                        
                        if not any(t["title_number"] == title_number for t in titles):
                            titles.append({
                                "title_number": title_number,
                                "title_name": title_name,
                                "url": f"https://www.law.cornell.edu/uscode/text"
                            })
                            print(f"✓ Fallback extracted: TITLE {title_number} - {title_name}")
        
        # Remove duplicates and sort
        unique_titles = []
        seen = set()
        for title in titles:
            key = str(title["title_number"])
            if key not in seen:
                seen.add(key)
                unique_titles.append(title)
        
        # Sort by title number
        unique_titles.sort(key=lambda x: int(x["title_number"]) if isinstance(x["title_number"], int) else 999)
        
        return unique_titles
    
    except Exception as e:
        print(f"Scraping error: {str(e)}")
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
                            print(f"✓ Fallback extracted: TITLE {title_number} - {title_name}")
        
        # Remove duplicates and sort
        unique_titles = []
        seen = set()
        for title in titles:
            key = str(title["title_number"])
            if key not in seen:
                seen.add(key)
                unique_titles.append(title)
        
        # Sort by title number
        unique_titles.sort(key=lambda x: int(x["title_number"]) if isinstance(x["title_number"], int) else 999)
        
        return unique_titles
    
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return []

def main():
    print("🚀 Cornell US Code Title Scraper")
    print("=================================")
    
    titles = scrape_titles()
    
    if titles:
        print(f"\n✅ Successfully extracted {len(titles)} titles")
        
        # Save to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(titles, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {OUTPUT_FILE}")
        
        # Show sample
        print("\nSample of extracted titles:")
        for i, title in enumerate(titles[:5], 1):
            print(f"  {i}. TITLE {title['title_number']} - {title['title_name']}")
        
        if len(titles) > 5:
            print(f"  ... and {len(titles)-5} more titles")
    
    else:
        print("\n⚠️ No titles were extracted")
        print("Possible reasons:")
        print("  1. Page structure changed")
        print("  2. Anti-scraping measures detected")
        print("  3. Network issues")

if __name__ == "__main__":
    main()