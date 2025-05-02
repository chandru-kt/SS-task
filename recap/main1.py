from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Start the browser
driver = webdriver.Chrome()  # or use Edge, Firefox, etc.

# Load the page
driver.get("http://127.0.0.1:5000/")

# Fill the form
driver.find_element(By.NAME, "userid").send_keys("testuser")
driver.find_element(By.NAME, "password").send_keys("mypassword")

# Solve reCAPTCHA manually
print("✅ Please solve the reCAPTCHA manually in the browser...")
input("⏳ Press Enter here after completing the reCAPTCHA...")

# Increase wait time and handle iframe if present

    # Wait for the submit button to be visible and clickable
submit_btn = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@type='submit']"))
)
submit_btn.click()

#     # Wait for page to load and check for success
#     time.sleep(2)
#     html = driver.page_source

#     if "Login Successful" in html:
#         print("🎉 Login passed reCAPTCHA and form was submitted.")
#     else:
#         print("❌ CAPTCHA or form failed.")
# except Exception as e:
#     print(f"❌ Error: {str(e)}")


# finally:
#     driver.quit()

# Wait for success.html to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//h1[text()='Login Successful']"))
)

# Extract details from <p> tags
try:
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    welcome_text = paragraphs[0].text
    account_type = paragraphs[1].text
    last_login = paragraphs[2].text

    print("\n🎉 Login passed reCAPTCHA and form was submitted.")
    print("✅ Extracted Data from success.html:")
    print(welcome_text)
    print(account_type)
    print(last_login)

except Exception as e:
    print("❌ Failed to extract data:", e)