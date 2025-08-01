# scraper.py
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def scrape_page(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for JS to render (can be adjusted)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return html, text

def scrape_and_save_all(df, skip_existing=True):
    driver = init_driver()

    for idx, row in df.iterrows():
        org_name = str(row.get("Organisation Name", f"org_{idx}")).strip().replace(" ", "_").lower()
        org_link = row.get("Org Link")
        linkedin_link = row.get("LinkedIn")

        for label, url in [("org", org_link), ("linkedin", linkedin_link)]:
            if isinstance(url, str) and url.startswith("http"):
                base_name = f"{org_name}_{label}"
                txt_path = f"data/text/{base_name}.txt"

                if skip_existing and os.path.exists(txt_path):
                    print(f"⏭️ Skipping {base_name} (already exists)")
                    continue

                try:
                    html, text = scrape_page(driver, url)

                    with open(f"data/raw_html/{base_name}.html", "w", encoding="utf-8") as f_html:
                        f_html.write(html)

                    with open(txt_path, "w", encoding="utf-8") as f_txt:
                        f_txt.write(text)

                    print(f"✅ Scraped {base_name}")
                    time.sleep(5)  # Delay to avoid blocking

                except Exception as e:
                    print(f"❌ Failed to scrape {url}: {e}")

    driver.quit()
