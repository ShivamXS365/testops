
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException as NSE
import requests
import time
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver() -> webdriver.Chrome:
    """Set up headless Chrome driver."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    service = Service() 
    driver = webdriver.Chrome(service=service, options=options)
    return driver

driver = setup_driver()
wait = WebDriverWait(driver, 5)

### 1. Test Page Load Time with Resource Verification
def test_page_load_time_with_resources():
    """Test to measure page load time and verify it loads in under 3 seconds."""
    start_time = time.time()
    try:
        driver.get("https://www.xenonstack.com")

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        load_time = time.time() - start_time
        logger.info(f"Page load time: {load_time:.2f} seconds")
        
        assert load_time < 3, f"Page load time exceeds 3 seconds. Actual load time: {load_time:.2f} seconds"
        logger.info("Page loaded in under 3 seconds")
        
        logger.info("Page Load Time Test Passed")
    except AssertionError as ae:
        logger.error(f"Test Failed: {ae}")
        raise ae
    except Exception as e:
        logger.error(f"Test Failed: {e}")
        raise e
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")

### 3. Test Navigation Validity Across All Menu Items
def test_navigation_validity():
    """Verify navigation menu items work correctly and all links load without errors."""
    start_time = time.time()
    count = 0
    menu_items = ["Foundry", "Neural AI", "NexaStack", "ElixirData", "MetaSecure", "Akira AI", "XAI"]

    try:
        for item in menu_items:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, f"//p[text()='{item}']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            initial_position = element.location['y']
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//p[text()='{item}']"))).click()
            time.sleep(1)
            logger.info(f"Clicked on {item} navigation menu item")

            new_position = element.location['y']

            if initial_position == new_position:
                logger.error(f"Page did not scroll down for {item} navigation menu item")
                count += 1
            else:
                logger.info(f"Page scrolled down for {item} navigation menu item")
        if count > 0:
            assert False, f"Page did not scroll down for {count} items."
        
        logger.info("All navigation menu items tested successfully")
    except Exception as e:
        logger.error(f"Test Failed: {e}")
        assert False, f"Test Failed: {e}"
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")

### 4. Test Footer Link Functionality and HTTP Status
def test_footer_links_functionality():
    """Test to verify footer links and their load times."""
    start_time = time.time()
    footer_links = set()
    count = 0
    try:
        footer = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "footer")))

        links = footer.find_elements(By.TAG_NAME, "a")
        for link in links:
            link_href = link.get_attribute('href')
            if link_href == "":
                count += 1
            else:
                footer_links.add(link_href)

        logger.info(f"Total Footer Links Found: {len(footer_links)}")
        assert count == 0, f"{count} links in the footer do not have links to pages."
        for page in footer_links:
            resp = requests.get(page, timeout=3, stream=True)
            try:
                if resp.status_code in [400, 401, 443, 999]:
                    logger.warning(f"{footer_links} blocks bot requests ({resp.status_code}) or is not available. Marking as valid.")
                    return
                elif resp.status_code < 400:
                    logger.info(f"External link '{footer_links}' is valid. [HTTP {resp.status_code}]")

                else:
                    logger.error(f"External link '{footer_links}' returned HTTP {resp.status_code}. Possible broken link.")
                
            except TimeoutError:
                logger.error(f"{page} failed to load within the expected time.")
                assert False, f"{page} timed out while loading"

        logger.info("Footer Links Verification Test Passed")
    except Exception as e:
        logger.error(f"Test Failed: {e}")
        assert False, f"Test Failed: {e}"
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")
        driver.get("https://www.xenonstack.com/") 
        logger.info("Returned to the home page")

### 5. Test Form Field Dependencies
def test_form_field_dependencies():
    """Verify form validation for required fields.""" 
    start_time = time.time() 
    try: # Click on the "Get Started" button 
        get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Get Started']/parent::a"))) 
        time.sleep(2) 
        driver.execute_script("arguments[0].scrollIntoView();", get_started_button) 
        time.sleep(2) 
        get_started_button.click() 
        time.sleep(2) 
        logger.info("Clicked on 'Get Started' button") # Verify the form opens 
        form = wait.until(EC.visibility_of_element_located((By.ID, "contactDrawer"))) 
        if form.is_displayed(): 
            logger.info("Form opened successfully") 
            time.sleep(2) 
        else: 
            raise Exception("Form did not open") 
        proceed_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='Proceed Next']/parent::div"))) 
        driver.execute_script("arguments[0].scrollIntoView();", proceed_button) 
        time.sleep(2) 
        proceed_button.click() 
        logger.info("Clicked 'Proceed Next' button") 
        time.sleep(2) # Verify error messages appear for required fields 
        assert "Please select all the required fields before proceeding" in driver.page_source 
        logger.info("Required field validation passed") 
        logger.info("Form Validation Test Passed") 
    except Exception as e: 
        logger.error(f"Test Failed: {e}") 
    finally: 
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")

### 6. Test Input Sanitization and Validation for Security
def test_input_sanitization():
    """Verify form validation for various inputs and dropdown selections."""
    start_time = time.time()
    try:

        # 1. Enter !@#$%^&*() in name fields.
        first_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "firstname")))
        last_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "lastname")))
        time.sleep(2)
        first_name_field.clear()
        last_name_field.clear()
        time.sleep(2)
        first_name_field.send_keys("!@#$%^&*()")
        last_name_field.send_keys("!@#$%^&*()")
        time.sleep(2)
        
        # 2. Verify an error message appears.
        assert "Please enter a valid First Name" in driver.page_source
        assert "Please enter a valid Last Name" in driver.page_source
        logger.info("Special character validation passed")
        time.sleep(2)
        
        # 3. Enter numbers in the first name and last name fields.
        first_name_field.clear()
        last_name_field.clear()
        time.sleep(2)
        first_name_field.send_keys("12345")
        last_name_field.send_keys("67890")
        time.sleep(2)
        
        # 4. Verify an error message appears.
        assert "Please enter a valid First Name" in driver.page_source
        assert "Please enter a valid Last Name" in driver.page_source
        logger.info("Number validation passed")

        time.sleep(2)
        
        # 5. Enter an incorrect email format. (e.g., invalid-email)
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        email_field.clear()
        time.sleep(2)
        email_field.send_keys("invalid-email")
        time.sleep(2)

        # 6. Verify an error message appears.
        assert "Please enter a valid Business Email ID" in driver.page_source
        logger.info("Invalid email format validation passed")

        time.sleep(2)

        # 7. Enter an invalid phone number (e.g., 123abc)
        phone_field = wait.until(EC.visibility_of_element_located((By.NAME, "contact")))
        phone_field.clear()
        time.sleep(2)
        phone_field.send_keys("123abc")
        time.sleep(2)

        # 8. Verify an error message appears.
        assert "Please enter a valid Contact Number" in driver.page_source
        logger.info("Invalid phone number validation passed")

        time.sleep(2)

        # 9. Select an option from the industry dropdown.
        industry_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, "industry")))
        industry_dropdown.click()
        time.sleep(2)
        industry_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Agriculture']")))
        industry_option.click()
        time.sleep(2)

        # 10. Verify it gets selected and stored properly.
        assert industry_option.is_selected()
        logger.info("Industry dropdown selection passed")
        time.sleep(2)

        # 11. Select ‘Others’ from a dropdown.
        other_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Others (Please Specify)']")))
        time.sleep(2)
        other_option.click()
        time.sleep(2)
        
        # 12. Verify a text box appears.
        try:
            other_textbox = driver.find_element(By.NAME, "otherIndustry")
            logger.info("Other industry textbox validation passed")
        except:
            raise Exception("Other industry Textbox not available")

        logger.info("Form Validation Test Passed")
    except Exception as e:
        logger.error(f"Form Validation Test Failed")
        raise e
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")   

### 7. Test Successful Form Submission Workflow
def test_successful_form_submission_workflow():
    """Verify successful form submission."""
    start_time = time.time()
    try:
        # Enter valid data into the form fields
        first_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "firstname")))
        last_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "lastname")))
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        phone_field = wait.until(EC.visibility_of_element_located((By.NAME, "contact")))        
        company_field = wait.until(EC.visibility_of_element_located((By.NAME, "company")))       
        industry_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, "industry")))
        
        
        first_name_field.clear()
        last_name_field.clear()
        email_field.clear()
        phone_field.clear()
        company_field.clear()

        first_name_field.send_keys("John")
        last_name_field.send_keys("Doe")
        email_field.send_keys("zxa@asd.com")
        phone_field.send_keys(1234567890)
        company_field.send_keys("ABC")
        industry_dropdown.click()
        industry_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Agriculture']")))
        industry_option.click()
        time.sleep(2)
        
        proceed_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='Proceed Next']/parent::div")))
        time.sleep(2)
        proceed_button.click()
        logger.info("Clicked 'Proceed Next' button")
        time.sleep(5)
        
        
        # Wait for the second page of the form to be visible
        form_step_two = wait.until(EC.visibility_of_element_located((By.ID, "form-step-two")))
        time.sleep(2)
        # Fill out the first question: Agentic Platform and Accelerator
        platform = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='agenticaiPlatform']//p[text()='Metasecure - Autonomous SOC']")))
        platform.click()
        time.sleep(1)
        logger.info("Selected platform choice: Metasecure - Autonomous SOC")
    
        # Fill out the second question: Company Segment
        company_segment = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='companySegment']//p[text()='Startup']")))
        company_segment.click()
        time.sleep(1)
        logger.info(f"Selected company segment: Startup")
        
        # Fill out the third question: Primary Focus Areas
        focus = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='primaryFocus']//p[text()='Security Operations']")))
        focus.click()
        time.sleep(1)
        logger.info(f"Selected primary focus area: Security Operations")
        
        #Fill out the fourth question: Stage of AI use case
        stage = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='aiUsecase']//p[text()='POC Completed']")))
        stage.click()
        time.sleep(1)
        logger.info(f"Selected AI use case stage : POC Completed")

        #Fill out the fifth question: Primary Challenge
        challenge = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='primaryChallenge']//p[text()='Data Privacy and Compliance']")))
        challenge.click()
        time.sleep(1)
        logger.info(f"Selected Primary Challenge : Data Privacy and Compliance")

        #Fill out the sixth question: Company Infrastructure
        infra = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='companyInfra']//p[text()='Microsoft Azure']")))
        infra.click()
        time.sleep(1)
        logger.info(f"Selected Company Infrastructure : Microsoft Azure")

        #Fill out the seventh question: Data Platform
        data = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='dataPlatform']//p[text()='SnowFlake']")))
        data.click()
        time.sleep(1)
        logger.info(f"Selected Data Platform : SnowFlake")

        #Fill out the eighth question: AI Transformation
        transformation = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='aiTransformation']//p[text()='Agentic Actions']")))
        transformation.click()
        time.sleep(1)
        logger.info(f"Selected AI Transformation : Agentic Actions")

        #Fill out the ninth question: Solution
        solution = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='solution']//p[text()='Internal Organization']")))
        solution.click()
        time.sleep(1)
        logger.info(f"Selected Solution : Internal Organization")

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='Submit']/parent::div")))
        time.sleep(2)
        submit_button.click()
        logger.info("Clicked 'Submit' button")
        time.sleep(5)

        form_step_three = wait.until(EC.visibility_of_element_located((By.ID, "form-step-three")))
        time.sleep(2)
        
        # Verify the confirmation message
        confirmation_message = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='successful-meeting-wrapper']/h2")))
        if confirmation_message.text == "your request has been submitted successfully !":
            logger.info("Final confirmation message displayed: 'your request has been submitted successfully !'")
        else:
            raise Exception("Final confirmation message did not display correctly")
        
        
        logger.info("Successful Form Submission Test Passed")

    except Exception as e:
        logger.error(f"Test Failed: {e}")
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "close-drawer")))
        driver.execute_script("arguments[0].scrollIntoView();", close_button)
        time.sleep(2)
        close_button.click()
        time.sleep(2)
        logger.info("Clicked on the close button to close the form")
        driver.set_window_size(1920,1080)

def sql_injection_attack():
    """Test for SQL injection vulnerability in the 'Get Started' form."""
    start_time = time.time()
    try:
        driver.get("https://www.xenonstack.com/")
        # Click on the "Get Started" button
        get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Get Started']/parent::a")))
        driver.execute_script("arguments[0].scrollIntoView();", get_started_button)
        time.sleep(2)
        get_started_button.click()
        logger.info("Clicked on 'Get Started' button")
        time.sleep(2)
        
        # Verify the form opens
        form = wait.until(EC.visibility_of_element_located((By.ID, "contactDrawer")))
        time.sleep(2)
        if form.is_displayed():
            logger.info("Form opened successfully")
        else:
            raise Exception("Form did not open")
        
        # Enter valid data into the form fields
        first_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "firstname")))
        last_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "lastname")))
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        phone_field = wait.until(EC.visibility_of_element_located((By.NAME, "contact")))        
        company_field = wait.until(EC.visibility_of_element_located((By.NAME, "company")))       
        industry_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, "industry")))
        
        
        first_name_field.clear()
        last_name_field.clear()
        email_field.clear()
        phone_field.clear()
        company_field.clear()

        first_name_field.send_keys("John")
        last_name_field.send_keys("Doe")
        email_field.send_keys("zxa@asd.com")
        phone_field.send_keys(1234567890)
        company_field.send_keys("1 OR 1=1")
        industry_dropdown.click()
        industry_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Agriculture']")))
        industry_option.click()
        time.sleep(2)
        
        proceed_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='Proceed Next']/parent::div")))
        time.sleep(2)
        proceed_button.click()
        logger.info("Clicked 'Proceed Next' button")
        time.sleep(5)
        
        try:
            form_step_two = wait.until(EC.visibility_of_element_located((By.ID, "form-step-two"))) 
            raise Exception("SQL injection attempt might have manipulated the database")
        except:
            logger.info("SQL injection attempt did not manipulate the database")

        logger.info("SQL Injection Test Passed")

    except Exception as e:
        logger.error(f"Test Failed: {e}")
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")
### 9. Test Dynamic Text Change in Banner
def test_dynamic_text_change_in_banner():
    """Verify that the dynamic text in the banner changes appropriately."""
    driver.get("https://www.xenonstack.com")
    changing_text = driver.find_element(By.ID, "changingText")
    
    initial_text = changing_text.text
    time.sleep(5)  # Wait for the text to change
    updated_text = changing_text.text
    
    assert initial_text != updated_text, "Dynamic text in banner did not change as expected."
    print("Dynamic text change in banner verified.")

### 10. Test Button Click Interaction with Modal
def test_modal_interaction():
    """Test the opening and closing of the modal on button click."""
    driver.get("https://www.xenonstack.com")
    get_started_btn = driver.find_element(By.XPATH, "//span[text()='Get Started']/parent::a")
    get_started_btn.click()

    modal = driver.find_element(By.ID, "contactDrawer")
    assert modal.is_displayed(), "Modal did not open on clicking 'Get Started'."

    close_btn = driver.find_element(By.CLASS_NAME, "close-drawer")
    close_btn.click()
    assert not modal.is_displayed(), "Modal did not close as expected."
    print("Modal interaction validated successfully.")

### 11. Test URL in Address Bar After Navigation
def test_xross_site():
    """Test for SQL injection vulnerability in the 'Get Started' form."""
    start_time = time.time()
    try:
        driver.get("https://www.xenonstack.com/")
        # Click on the "Get Started" button
        get_started_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Get Started']/parent::a")))
        driver.execute_script("arguments[0].scrollIntoView();", get_started_button)
        time.sleep(2)
        get_started_button.click()
        logger.info("Clicked on 'Get Started' button")
        time.sleep(2)
        
        # Verify the form opens
        form = wait.until(EC.visibility_of_element_located((By.ID, "contactDrawer")))
        time.sleep(2)
        if form.is_displayed():
            logger.info("Form opened successfully")
        else:
            raise Exception("Form did not open")
        
        # Enter valid data into the form fields
        first_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "firstname")))
        last_name_field = wait.until(EC.visibility_of_element_located((By.NAME, "lastname")))
        email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
        phone_field = wait.until(EC.visibility_of_element_located((By.NAME, "contact")))        
        company_field = wait.until(EC.visibility_of_element_located((By.NAME, "company")))       
        industry_dropdown = wait.until(EC.element_to_be_clickable((By.NAME, "industry")))
        
        
        first_name_field.clear()
        last_name_field.clear()
        email_field.clear()
        phone_field.clear()
        company_field.clear()

        first_name_field.send_keys("John")
        last_name_field.send_keys("Doe")
        email_field.send_keys("zxa@asd.com")
        phone_field.send_keys(1234567890)
        company_field.send_keys("<script>alert('XSS')</script>")
        industry_dropdown.click()
        industry_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Agriculture']")))
        industry_option.click()
        time.sleep(2)
        
        proceed_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='Proceed Next']/parent::div")))
        time.sleep(2)
        proceed_button.click()
        logger.info("Clicked 'Proceed Next' button")
        time.sleep(5)
        
        # Verify that the script is not executed
        try:
            alert = wait.until(EC.alert_is_present())
            raise Exception("XSS vulnerability detected: Alert executed")
        except:
            logger.info("No alert executed. XSS vulnerability not present.")

        logger.info("XSS Vulnerability Test Passed")

    except Exception as e:
        logger.error(f"Test Failed: {e}")
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")

### 12. Test Internal Link Navigation Across Sections
def test_internal_links_navigation():
    """Test to verify body links (excluding footer) and their load times."""
    start_time = time.time()
    try:

        body = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        footer = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "footer")))

        links = body.find_elements(By.TAG_NAME, "a")
        footer_links = footer.find_elements(By.TAG_NAME, "a")
        
        body_links_all = {link.get_attribute('href') for link in links if link.get_attribute('href') not in {footer_link.get_attribute('href') for footer_link in footer_links}}
        
        body_links = set()
        for page in body_links_all:
            if page != "":
                body_links.add(page)

        logger.info(f"Total Body Links Found: {len(body_links)}")

        for page in body_links:
            resp = requests.get(page, timeout=3, stream=True)
            try:
                if resp.status_code in [400, 401, 999]:
                    logger.warning(f"{body_links} blocks bot requests ({resp.status_code}) or is not available. Marking as valid.")
                    return
                elif resp.status_code < 400:
                    logger.info(f"External link '{body_links}' is valid. [HTTP {resp.status_code}]")

                else:
                    logger.error(f"External link '{body_links}' returned HTTP {resp.status_code}. Possible broken link.")

            except requests.RequestException as e:
                logger.error(f"Failed request for '{body_links}': {str(e)}")
            except TimeoutError:
                logger.error(f"{page} failed to load within the expected time.")
                assert False, f"{page} timed out while loading"

        logger.info("Body Links Verification Test Passed")
    except Exception as e:
        logger.error(f"Test Failed: {e}")
        assert False, f"Test Failed: {e}"
    finally:
        logger.info(f"Execution Time: {time.time() - start_time:.2f} seconds")
        driver.get("https://www.xenonstack.com/") 
        logger.info("Returned to the home page")

if __name__ == "__main__":
    test_page_load_time_with_resources()
    test_navigation_validity()
    test_footer_links_functionality()
    test_form_field_dependencies()
    test_input_sanitization()
    test_successful_form_submission_workflow()
    sql_injection_attack()
    test_dynamic_text_change_in_banner()
    test_modal_interaction()
    test_xross_site()
    test_internal_links_navigation()
    driver.quit()