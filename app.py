from flask import Flask, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import firebase_admin
from firebase_admin import credentials, db
from waitress import serve
import time

app = Flask(__name__)

# Function to create and configure the WebDriver
def create_driver():
    options = webdriver.ChromeOptions()
    #options.add_experimental_option("detach", True)
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    #driver.set_page_load_timeout(3)  # Set the page load timeout to 3 seconds
    return driver

# Function to log in to HackerRank
def login(username, password):
    driver = create_driver()
    try:
        driver.get('https://www.hackerrank.com/auth/login')

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'button'))
        )
        login_button.click()

        #driver.find_element(By.NAME, 'username').send_keys(username)
        #driver.find_element(By.NAME, 'password').send_keys(password)
        #driver.find_element(By.TAG_NAME,'button').click()

        #time.sleep(2)

        #WebDriverWait(driver, 3).until(
            #EC.url_contains("hackerrank.com/dashboard")
        #)
        print("Login successful.")
        return driver

    #except TimeoutException:
        #print("Login page took too long to load. Driver closed.")
        #driver.quit()
        #return None
    except Exception as e:
        print("Login failed:", e)
        driver.quit()
        return None

# Function to scrape usernames and scores from a given page URL
def scrape_leaderboard(driver, url, seen_usernames):
    try:
        driver.get(url)
        start_time = time.time()

        while True:
            if time.time() - start_time > 3:
                print("Page load took too long. Skipping page:", url)
                return [], []

            if "leaderboard" in driver.current_url:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                all_a_tags = soup.find_all('a')

                usernames_list = []
                scores_list = []
                for a_tag in all_a_tags:
                    if a_tag.get('data-value') and a_tag.get('data-attr10'):
                        username = a_tag.get('data-value')
                        score = a_tag.get('data-attr10')

                        if username not in seen_usernames:
                            usernames_list.append(username)
                            scores_list.append(score)
                            seen_usernames.add(username)
                return usernames_list, scores_list

    except Exception as e:
        print("Failed to scrape leaderboard:", e)
        return [], []

# Function to scrape usernames and scores from 20 pages max
def scrape_all_leaderboard(driver):
    try:
        all_user_scores = {}
        seen_usernames = set()

        for page in range(1, 21):
            url = f'https://www.hackerrank.com/leaderboard?filter=follows&filter_on=friends&page={page}&track=algorithms&type=practice'
            usernames, scores = scrape_leaderboard(driver, url, seen_usernames)

            for i in range(len(usernames)):
                all_user_scores[usernames[i]] = scores[i]

            if len(usernames) < 2:
                break

            time.sleep(3)

        return all_user_scores
    except Exception as e:
        print("Failed to scrape the first 20 pages of data:", e)
        return {}

# Function to update data in Firebase        
def firebase_upload(leaderboard_data):
    try:
        credential = credentials.Certificate('credentials.json')
        firebase_admin.initialize_app(credential, {'databaseURL': 'https://certain-root-333610-default-rtdb.asia-southeast1.firebasedatabase.app/'})
        ref = db.reference('/')
        ref.set({})

        rank = 1
        for username, score in leaderboard_data.items():
            ref.child('Leaderboard').child(str(rank)).set({'Username': username, 'score': score})
            rank += 1
        print("Firebase database has updated")

    except Exception as e:
        print("Failed to upload data to Firebase:", e)

@app.route('/scrape', methods=['POST','GET'])
def scrape_and_update():
    try:
        # Hardcoded credentials
        username = 'thalakratos5@gmail.com'
        password = 'Zeusfatherkratos'

        driver = login(username, password)
        if driver:
            all_user_scores = scrape_all_leaderboard(driver)
            if all_user_scores:
                sorted_user_scores = {k: v for k, v in sorted(all_user_scores.items(), key=lambda item: float(item[1]), reverse=True)}
                firebase_upload(sorted_user_scores)
                driver.quit()
                return jsonify({'message': 'Scraping successful'}), 200
            else:
                driver.quit()
                return jsonify({'message': 'Failed to scrape data'}), 500
        else:
            return jsonify({'message': 'Login failed'}), 500
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run()
    #serve(app, host='0.0.0.0', port=8080)
