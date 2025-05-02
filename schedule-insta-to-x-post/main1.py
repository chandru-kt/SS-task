import os
import time
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import tweepy
import requests
from dotenv import load_dotenv

load_dotenv()

LAST_POST_FILE = "last_post.json"
INSTAGRAM_USERNAME = "sampllee1029"
INSTAGRAM_PASSWORD = "sample1234"
BBC_INSTAGRAM_URL = "https://www.instagram.com/bbcnews/"

def get_latest_instagram_post():
    # Set up the browser
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Go to Instagram login page
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        # 2. Log in
        driver.find_element(By.NAME, "username").send_keys(INSTAGRAM_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(INSTAGRAM_PASSWORD + Keys.RETURN)
        time.sleep(7)

        # 3. Go to target profile
        driver.get(f"https://www.instagram.com/bbcnews/")
        time.sleep(5)

        # 4. Scroll and collect post links in order
        seen = set()
        post_links = []

        while len(post_links) < 1:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            for link in links:
                href = link.get_attribute("href")
                if href and href not in seen:
                    seen.add(href)
                    post_links.append(href)

        # 5. Visit nth post
        nth_post_url = post_links[1 - 1]
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
        print(f"\nPost #{1}:")
        print(f"URL: {nth_post_url}")
        print(f"Caption: {caption}")
        print(f"Image URL: {image_url}")
        return {
    "caption": caption,
    "image_url": image_url,
    "post_url": nth_post_url
}


    finally:
        driver.quit()

def summarize_for_tweet(caption, max_length=280):
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        prompt = f"Summarize this Instagram caption into a tweet (under {max_length} characters):\n{caption}"
        response = model.generate_content(prompt)
        tweet_summary = response.text.strip()
        return tweet_summary[:max_length]
    except Exception as e:
        print(f"Summarization error: {e}")
        return None

def post_to_x(tweet_text):
    try:
        client = tweepy.Client(
            consumer_key=os.environ["X_CONSUMER_KEY"],
            consumer_secret=os.environ["X_CONSUMER_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
        )
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet posted: https://x.com/user/status/{response.data['id']}")
        return True
    except Exception as e:
        print(f"Tweet error: {e}")
        return False

def load_last_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_post(post):
    with open(LAST_POST_FILE, "w") as f:
        json.dump(post, f)

def automation_job():
    print(f"\n[{datetime.now()}] Checking for new Instagram post...")
    try:
        post = get_latest_instagram_post()
        if not post:
            print("Skipping — no post data retrieved.")
            return
        last_post = load_last_post()

        if post["post_url"] != last_post.get("post_url"):
            print("New post detected!")
            tweet = summarize_for_tweet(post['caption'])
            if tweet:
                success = post_to_x(tweet)
                if success:
                    save_last_post(post)
        else:
            print("No new post.")
    except Exception as e:
        print(f"Automation error: {e}")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(automation_job, 'interval', minutes=2)
    scheduler.start()
    print("Instagram to Twitter bot started.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Bot stopped.")
