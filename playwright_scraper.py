from playwright.sync_api import sync_playwright
import os

# URL of the chapter to scrape
url = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"

output_dir = "scraper/output" # directory to save output
os.makedirs(output_dir,exist_ok=True)

def scrape_chapter():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(url)

        #Take screenshot(Full page)
        screenshot_path=os.path.join(output_dir,"chapter1_screenshot.png") #path of ss
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved at {screenshot_path}")

        # Extract text content
        content = page.locator("#mw-content-text").inner_text()

        #Save content to text file
        text_path = os.path.join(output_dir,"chapter1_content.txt")
        with open(text_path, "w",encoding="utf-8") as f:
            f.write(content)
        print(f"Chapter content saved at {text_path}")  

        browser.close()  

if __name__ == "__main__":
    scrape_chapter()
      

