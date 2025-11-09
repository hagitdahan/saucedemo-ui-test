import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

class SaucedemoTest:
    """
    A calss that runs a comlete test flow in Saucedemo website.
    """
    def __init__(self):
        """Load data fron config file. """
        conf = json.loads(Path("config/config.json").read_text(encoding = "utf-8"))
        self.base_url = conf["base_url"]
        self.username = conf["user"]["user_name"]
        self.password = conf["user"]["password"]
        self.products = conf["products"]
        self._pw = None
        self.browser = None
        self.page = None
        self.context = None

    def setup(self):
        print("Step 1 : Setup - launching browser")
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def login(self):
        """ 
        Go to login page, enter user name and password, then click on login button'
        Also verify that the login was successed.
        """
        print("Step 2 : Login - enter credentials and click")
        self.page.goto(self.base_url)
        self.page.get_by_placeholder("Username").fill(self.username)
        self.page.get_by_placeholder("Password").fill(self.password)
        self.page.get_by_role("button", name = "Login").click()
        assert "inventory" in self.page.url, "Login failed: did not reach inventory page"
    
    def teardown(self):
        """Close the browser and Playwright """
        print("Step 8 : Teadown - closing browser")
        if self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()
    
    def run(self):
        """ 
        Executes the entire scenario:
        1. Setup and open browser
        2. Login with valid credentials
        3. Add three products to the cart
        4. Verify the cart badge and items cound
        5. Proceed to checkout and fill user details
        6. Complete the order and verify confirm message 
        """
        try:
            self.setup()

            self.login()

            print("Step 3 : Add to cart - clicking on 3 products fron the config file")
            for product_id in self.products:
                self.page.locator(f'[data-test="{product_id}"]').click()

            print("Step 4 : Cart badge shows 3 ")
            badge_inner = self.page.locator(".shopping_cart_badge").inner_text().strip()
            assert badge_inner == "3", f"expected cart badge = 3, got{badge_inner}"

            print("Step 5 : Open cart and verify 3 items are listed")
            self.page.locator(".shopping_cart_link").click()
            assert self.page.locator(".cart_item").count() == 3,"cart should list 3 items"

            print("Step 6 : Checkout - open the form and fill the details")
            self.page.get_by_role("button", name = "Checkout").click()

            self.page.get_by_placeholder("First Name").fill("Hagit")
            self.page.get_by_placeholder("Last Name").fill("Dahan")
            self.page.get_by_placeholder("Zip/Postal Code").fill("11111")
            self.page.get_by_role("button", name = "Continue").click()

            print("Step 7 : Complete the order and verify success")
            self.page.get_by_role("button", name = "Finish").click()
            self.page.get_by_text("Checkout: Complete!").is_visible()

            print("PASS")
            sys.exit(0)


        except AssertionError as ae:
            print(f"FAIL: {ae}")
            sys.exit(1)
        
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        
        finally:
            self.teardown()

if __name__ == "__main__":
    SaucedemoTest().run()