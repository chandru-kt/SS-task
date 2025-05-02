from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_nth_instagram_post(n, username, password, target_profile):
    # Set up the browser
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Go to Instagram login page
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        # 2. Log in
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
        time.sleep(7)

        # 3. Go to target profile
        driver.get(f"https://www.instagram.com/{target_profile}/")
        time.sleep(5)

        # 4. Scroll and collect post links in order
        seen = set()
        post_links = []

        while len(post_links) < n:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            for link in links:
                href = link.get_attribute("href")
                if href and href not in seen:
                    seen.add(href)
                    post_links.append(href)

        # 5. Visit nth post
        nth_post_url = post_links[n - 1]
        driver.get(nth_post_url)
        time.sleep(3)

                # 6. Extract caption
        try:
            # Try h1 (if Instagram currently uses it)
            caption = driver.find_element(By.XPATH, "//h1").text
        except:
            try:
                # Try known span class for captions
                caption = driver.find_element(By.XPATH, "//div[contains(@class, '_a9zs')]/span").text
            except:
                try:
                    # Try within dialog modal structure
                    caption = driver.find_element(By.XPATH, "//div[@role='dialog']//ul//li//span").text
                except:
                    try:
                        # Final fallback: any span in article
                        caption = driver.find_element(By.XPATH, "//article//span").text
                    except:
                        caption = "No caption found"

        # 7. Extract image URL
        try:
            image_url = driver.find_element(By.XPATH, "//article//img").get_attribute("src")
        except:
            image_url = "No image found"

        # 8. Output result
        print(f"\nPost #{n}:")
        print(f"URL: {nth_post_url}")
        print(f"Caption: {caption}")
        print(f"Image URL: {image_url}")

    finally:
        driver.quit()

# --- Usage ---
get_nth_instagram_post(
    n=1,  # Replace with desired post number
    username="sampllee1029",
    password="sample1234",
    target_profile="bbcnews"
)
