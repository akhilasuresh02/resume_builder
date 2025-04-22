import os
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurations
BASE_URL = "http://localhost:5000"

# Setup Selenium WebDriver
driver = webdriver.Chrome()  # or provide ChromeDriver path to ChromeService
wait = WebDriverWait(driver, 5)

def generate_random_string(length=8):
    """Generate a random string of specified length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_email(domain="example.com"):
    """Generate a random email address."""
    username = generate_random_string()
    return f"{username}@{domain}"

def navigate_to_landing_page():
    """Navigate to the landing page."""
    driver.get(BASE_URL)
    print("Navigated to landing page:", driver.current_url)
    time.sleep(2)  # Wait for page to load

def click_get_started():
    """Click the 'Get Started' button to go to login page."""
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "get-started"))).click()
        print("Clicked 'Get Started', navigating to login page")
    except (TimeoutException, NoSuchElementException):
        print("Get Started button not found with ID. Trying by text...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Get Started')]"))).click()
        print("Clicked 'Get Started' using XPath")
    time.sleep(2)  # Wait for login page to load
    assert "login" in driver.current_url.lower(), "Failed to reach login page"
    print("Reached login page:", driver.current_url)

def click_register_here():
    """Click 'Register Here' link to go to registration page."""
    try:
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Register Here"))).click()
        print("Clicked 'Register Here', navigating to registration page")
    except (TimeoutException, NoSuchElementException):
        print("Register Here link not found with LINK_TEXT. Trying by XPath...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Register')]"))).click()
        print("Clicked 'Register Here' using XPath")
    time.sleep(2)  # Wait for registration page to load
    assert "register" in driver.current_url.lower(), "Failed to reach registration page"
    print("Reached registration page:", driver.current_url)

def register_user(username, email, password, delay=3):
    """Fill and submit the registration form with random inputs."""
    try:
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "email").clear()
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.TAG_NAME, "form").submit()
        print(f"Submitted registration for: Username={username}, Email={email}")
        time.sleep(delay)  # Wait for registration to process
        assert "login" in driver.current_url.lower(), "Registration did not redirect to login page"
        print("Registration successful, redirected to login page")
    except Exception as e:
        print(f"Registration failed: {e}")
        print("Current page source:", driver.page_source)
        raise

def login_user(email, password, delay=3):
    """Fill and submit the login form with the registered credentials."""
    try:
        wait.until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").clear()
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.TAG_NAME, "form").submit()
        print(f"Submitted login for: Email={email}")
        time.sleep(delay)  # Wait for login to process
        assert "dashboard" in driver.current_url.lower(), "Failed to reach dashboard after login"
        print("Login successful, reached dashboard:", driver.current_url)
    except Exception as e:
        print(f"Login failed: {e}")
        print("Current page source:", driver.page_source)
        raise

# ----- Start Automation -----
try:
    # 1. Navigate to landing page
    print("Starting automation...")
    navigate_to_landing_page()

    # 2. Click 'Get Started' to go to login page
    click_get_started()

    # 3. Click 'Register Here' to go to registration page
    click_register_here()

    # 4. Register with random inputs
    random_username = generate_random_string(10)
    random_email = generate_random_email()
    random_password = generate_random_string(12)
    print(f"Registering with: Username={random_username}, Email={random_email}, Password={random_password}")
    register_user(random_username, random_email, random_password)

    # 5. Log in with the same credentials
    print(f"Logging in with: Email={random_email}, Password={random_password}")
    login_user(random_email, random_password)

    # 6. Verify successful login (already handled in login_user)

except Exception as e:
    print(f"Automation failed: {e}")

finally:
    # End
    print("Automation complete!")
    time.sleep(3)  # Allow time to see the dashboard
    driver.quit()