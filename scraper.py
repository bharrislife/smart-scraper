import sys
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_and_parse(url):
    """Fetch HTML content from a target URL with standard headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"[!] Error fetching URL: {e}")
        sys.exit(1)

def extract_and_clean(soup):
    """Extract standard links and titles from the page and clean them."""
    extracted = []
    
    # Target standard anchor links that hold titles and article URLs
    for item in soup.find_all('a'):
        title = item.get_text(strip=True)
        link = item.get('href', '')
        
        # Filter for meaningful titles and absolute URLs
        if title and len(title) > 10 and link.startswith('http'):
            extracted.append({
                "title": title,
                "url": link
            })
            
    # Deduplicate based on title
    seen = set()
    unique_extracted = []
    for entry in extracted:
        if entry['title'] not in seen:
            seen.add(entry['title'])
            unique_extracted.append(entry)
            
    return unique_extracted[:30] # Limit to top 30 items

def export_data(data, filename_prefix="scraped_output"):
    """Export cleaned data to both JSON and CSV formats."""
    if not data:
        print("[!] No data extracted to export.")
        return

    # Export to JSON
    json_filename = f"{filename_prefix}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[✔] Successfully exported JSON to {json_filename}")

    # Export to CSV via Pandas
    df = pd.DataFrame(data)
    csv_filename = f"{filename_prefix}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"[✔] Successfully exported CSV to {csv_filename}")

if __name__ == "__main__":
    target_url = input("Enter URL to scrape (or press Enter for default example): ").strip()
    if not target_url:
        target_url = "https://news.ycombinator.com/"

    print(f"\n[+] Fetching data from: {target_url} ...")
    soup = fetch_and_parse(target_url)
    cleaned_data = extract_and_clean(soup)
    
    print(f"[+] Found {len(cleaned_data)} structured items. Exporting results...")
    export_data(cleaned_data)
