import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def main():
    # Start vite preview or dev server
    proc = subprocess.Popen(["npm", "run", "preview", "--", "--port", "4173"], shell=True, cwd=os.getcwd())
    time.sleep(3)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            
            # Go to preview
            page.goto("http://localhost:4173")
            page.wait_for_timeout(1000)
            
            # Take screenshot of login page
            page.screenshot(path="scratch/liquid_glass_login.png")
            print("Login screenshot captured")
            
            # Perform login if inputs present
            if page.locator("input[type='text']").count() > 0:
                page.fill("input[type='text']", "christo")
                page.fill("input[type='password']", "Christo123")
                page.click("button[type='submit']")
                page.wait_for_timeout(3000)
                
                # Take screenshot of dashboard
                page.screenshot(path="scratch/liquid_glass_dashboard.png")
                print("Dashboard screenshot captured")
            
            browser.close()
    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, shell=True)

if __name__ == "__main__":
    main()
