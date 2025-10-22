import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables or use hardcoded fallback
USERNAME = os.getenv('USERNAME', 'atomicstore7717@gmail.com')
PASSWORD = os.getenv('PASSWORD', 'atomicstore7717@gmail.com')
SERVER_URL = os.getenv('SERVER_URL', 'https://www.mcserverhost.com/servers/79c2fa2c/dashboard')

# Global driver variable to maintain session
driver = None
logged_in = False

def initialize_driver():
    """Initialize the Chrome driver"""
    global driver
    
    if driver is not None:
        return driver
        
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    # Headless mode for server environments
    chrome_options.add_argument("--headless")
    
    try:
        # Initialize WebDriver
        print("[INFO] Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("[SUCCESS] Chrome driver initialized successfully!")
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to initialize Chrome driver: {e}")
        return None

def login():
    """Perform login process"""
    global driver, logged_in
    
    if logged_in:
        return True
        
    if driver is None:
        driver = initialize_driver()
        if driver is None:
            return False
    
    try:
        # Navigate to login page
        print("[INFO] Navigating to login page...")
        driver.get("https://www.mcserverhost.com/login")
        print("[SUCCESS] Login page loaded!")
        print(f"[DEBUG] Current URL: {driver.current_url}")
        print(f"[DEBUG] Page title: {driver.title}")
        
        # Wait for page to fully load
        print("[INFO] Waiting for page to fully load...")
        time.sleep(5)
        
        # Wait for login form to be present
        print("[INFO] Waiting for login form to load...")
        wait = WebDriverWait(driver, 20)
        
        try:
            # Wait for the login form container to be present
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form, .login-form, #login-form")))
            print("[SUCCESS] Login form detected!")
        except:
            print("[WARNING] Login form container not found, continuing anyway...")
        
        # Find username/email and password fields with specific IDs
        print("[INFO] Looking for login form elements...")
        
        # Find username field with specific ID
        print("[INFO] Looking for username/email field...")
        username_field = None
        try:
            # Try the specific IDs we found in the debug output
            username_selectors = [
                "#auth-username",
                "#auth-email",
                "input[name='username']",
                "input[type='email']",
                "input#username",
                "input.form-control"
            ]
            
            for selector in username_selectors:
                try:
                    username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"[SUCCESS] Username field found with selector '{selector}'!")
                    break
                except:
                    continue
            
            if not username_field:
                raise Exception("Could not find username field with any selector")
        except Exception as e:
            print(f"[ERROR] Could not find username field: {e}")
            return False
        
        # Find password field with specific ID
        print("[INFO] Looking for password field...")
        password_field = None
        try:
            # Try the specific ID we found in the debug output
            password_selectors = [
                "#auth-password",
                "input[name='password']",
                "input[type='password']",
                "input#password",
                "input.form-control[type='password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"[SUCCESS] Password field found with selector '{selector}'!")
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Could not find password field with any selector")
        except Exception as e:
            print(f"[ERROR] Could not find password field: {e}")
            return False
        
        # Fill credentials
        print("[INFO] Filling credentials...")
        try:
            username_field.send_keys(USERNAME)
            print("[SUCCESS] Username entered!")
            password_field.send_keys(PASSWORD)
            print("[SUCCESS] Password entered!")
        except Exception as e:
            print(f"[ERROR] Failed to fill credentials: {e}")
            return False
        
        # Check for CAPTCHA
        print("[INFO] Checking for CAPTCHA...")
        try:
            captcha_elements = driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha, [id*='captcha'], [class*='captcha']")
            if captcha_elements:
                print("[WARNING] CAPTCHA detected! Manual intervention required.")
                print("[ACTION] Please complete the CAPTCHA in the browser window NOW!")
                print("[INFO] Waiting 45 seconds for you to complete the CAPTCHA...")
                time.sleep(45)  # Give more time for manual CAPTCHA completion
                print("[INFO] Continuing with login...")
            else:
                print("[INFO] No CAPTCHA detected.")
        except Exception as e:
            print(f"[INFO] CAPTCHA check completed: {e}")
        
        # Find and click login button
        print("[INFO] Looking for login button...")
        login_button = None
        try:
            # Wait for login button to be present and clickable
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-login, #login-button, button.btn-primary, button.btn")))
            print("[SUCCESS] Login button found!")
        except Exception as e:
            print(f"[ERROR] Could not find login button with WebDriverWait: {e}")
            # Try to find any button as a last resort
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"[DEBUG] Found {len(buttons)} buttons:")
                for i, btn in enumerate(buttons):
                    print(f"  {i}: text='{btn.text}', type='{btn.get_attribute('type')}', class='{btn.get_attribute('class')}'")
                if buttons:
                    login_button = buttons[0]  # Try first button
                    print("[INFO] Using first available button as login button")
            except:
                pass
            
            if not login_button:
                return False
        
        print("[INFO] Clicking login button...")
        try:
            login_button.click()
            print("[SUCCESS] Login button clicked!")
        except Exception as e:
            print(f"[ERROR] Failed to click login button: {e}")
            # Try JavaScript click as fallback
            try:
                driver.execute_script("arguments[0].click();", login_button)
                print("[SUCCESS] Login button clicked via JavaScript!")
            except Exception as e2:
                print(f"[ERROR] Failed to click login button via JavaScript: {e2}")
                return False
        
        # Wait for login to complete
        print("[INFO] Waiting for login to complete...")
        try:
            # Wait for dashboard or redirect to indicate successful login (longer wait for manual CAPTCHA)
            WebDriverWait(driver, 60).until(
                lambda d: "/dashboard" in d.current_url or 
                         "dashboard" in d.title.lower() or 
                         "panel" in d.title.lower() or
                         "servers" in d.current_url or
                         len(d.window_handles) == 0
            )
            print("[SUCCESS] Login appears to be successful!")
        except Exception as e:
            print(f"[INFO] Login wait completed. Current URL: {driver.current_url}")
            # Additional wait to ensure page loads
            time.sleep(10)
        
        print(f"[DEBUG] After login - Current URL: {driver.current_url}")
        print(f"[DEBUG] After login - Page title: {driver.title}")
        
        logged_in = True
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def renew_server():
    """Function to renew the server"""
    global driver, logged_in
    
    print("=" * 50)
    print("Starting server renewal process...")
    print("=" * 50)
    print(f"[INFO] Using username: {USERNAME}")
    print(f"[INFO] Using server URL: {SERVER_URL}")
    
    # Initialize driver if needed
    if driver is None:
        driver = initialize_driver()
        if driver is None:
            return
    
    # Login if not already logged in
    if not logged_in:
        if not login():
            print("[ERROR] Login failed, cannot proceed with renewal")
            return
    
    try:
        # Navigate to the specific server dashboard
        print("[INFO] Navigating to specific server dashboard...")
        try:
            driver.get(SERVER_URL)
            time.sleep(5)  # Wait for page to load
            print(f"[DEBUG] After navigation - Current URL: {driver.current_url}")
            print(f"[DEBUG] After navigation - Page title: {driver.title}")
        except Exception as e:
            print(f"[ERROR] Failed to navigate to server dashboard: {e}")
            # Try to re-login if navigation fails
            logged_in = False
            if not login():
                return
            # Try navigation again after re-login
            driver.get(SERVER_URL)
            time.sleep(5)
        
        # Look for renew button on the server dashboard
        print("[INFO] Looking for renew button...")
        renew_button = None
        
        # Try multiple methods to find the renew button
        try:
            # Method 1: Look for buttons with specific attributes
            renew_selectors = [
                "button[title*='Renew']",
                "button[data-action='renew']",
                "[data-action='renew']",
                "button.btn-renew",
                "a[title*='Renew']",
                ".renew-button",
                ".btn-success",  # Renew buttons are often green/success buttons
                ".btn-primary"   # Or primary buttons
            ]
            
            for selector in renew_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Look for the one that's visible and clickable
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                renew_button = element
                                print(f"[SUCCESS] Renew button found with selector '{selector}'!")
                                break
                        if renew_button:
                            break
                except:
                    continue
            
            # Method 2: If still not found, look for buttons with "Renew" text
            if not renew_button:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.is_displayed() and "renew" in btn.text.lower():
                        renew_button = btn
                        print(f"[SUCCESS] Renew button found by text: '{btn.text}'")
                        break
            
            # Method 3: Look for links with "Renew" text
            if not renew_button:
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    if link.is_displayed() and "renew" in link.text.lower():
                        renew_button = link
                        print(f"[SUCCESS] Renew button found by link text: '{link.text}'")
                        break
                        
        except Exception as e:
            print(f"[ERROR] Error while searching for renew button: {e}")
        
        # If we still can't find it, show what buttons are available
        if not renew_button:
            print("[INFO] Showing available buttons for debugging:")
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for i, btn in enumerate(buttons):
                    if btn.is_displayed():
                        print(f"  Button {i}: text='{btn.text}', class='{btn.get_attribute('class')}', title='{btn.get_attribute('title')}'")
                
                links = driver.find_elements(By.TAG_NAME, "a")
                for i, link in enumerate(links):
                    if link.is_displayed() and link.text.strip():
                        print(f"  Link {i}: text='{link.text}', class='{link.get_attribute('class')}', href='{link.get_attribute('href')}'")
            except Exception as e:
                print(f"[ERROR] Error while listing elements: {e}")
            
            # Try clicking the first visible button as a last resort
            try:
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        renew_button = btn
                        print(f"[INFO] Using first visible button as fallback: '{btn.text}'")
                        break
            except:
                pass
        
        if not renew_button:
            print("[ERROR] Could not find renew button")
            print("[DEBUG] Page source preview:", driver.page_source[:5000])
            # Reset login status to force re-login on next attempt
            logged_in = False
            return
        
        print("[INFO] Clicking renew button...")
        try:
            # Scroll to the button to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", renew_button)
            time.sleep(1)
            
            renew_button.click()
            print("[SUCCESS] Renew button clicked!")
        except Exception as e:
            print(f"[ERROR] Failed to click renew button: {e}")
            # Try JavaScript click as fallback
            try:
                driver.execute_script("arguments[0].click();", renew_button)
                print("[SUCCESS] Renew button clicked via JavaScript!")
            except Exception as e2:
                print(f"[ERROR] Failed to click renew button via JavaScript: {e2}")
                # Reset login status to force re-login on next attempt
                logged_in = False
                return
        
        # Wait for confirmation
        print("[INFO] Waiting for confirmation...")
        time.sleep(10)
        print("[SUCCESS] Server renewal process completed!")
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        # Reset login status to force re-login on next attempt
        logged_in = False
    print("=" * 50)

def start_scheduler():
    """Start the scheduler"""
    print("[INFO] Scheduler started!")
    print("[INFO] Performing initial renewal...")
    renew_server()
    print("[INFO] Scheduling renewals every 5 minutes...")
    schedule.every(5).minutes.do(renew_server)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def cleanup():
    """Clean up resources"""
    global driver
    if driver is not None:
        try:
            driver.quit()
            print("[SUCCESS] Browser closed!")
        except Exception as e:
            print(f"[ERROR] Failed to close browser: {e}")
        finally:
            driver = None

if __name__ == "__main__":
    print("MC Server Renewal Bot Starting...")
    print("==================================")
    print(f"[INFO] USERNAME: {USERNAME}")
    print(f"[INFO] SERVER_URL: {SERVER_URL}")
    
    # Start scheduler
    print("[INFO] Starting scheduler thread...")
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    print("Bot is now running! It will renew your server every 5 minutes.")
    print("IMPORTANT: When CAPTCHA appears, complete it manually in the browser window.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBot stopped.")
        cleanup()