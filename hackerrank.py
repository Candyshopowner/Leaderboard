from selenium import webdriver
from selenium.webdriver.common.by import By
import time


id1 = "thalakratos5@gmail.com"
password1 = "Zeusfatherkratos"


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)


driver = webdriver.Chrome(options=options)

url = "https://www.hackerrank.com/auth/login"

driver.get(url)

driver.find_element(By.NAME, 'username').send_keys(id1)
driver.find_element(By.NAME, 'password').send_keys(password1)
driver.find_element(By.TAG_NAME,'button').click()

time.sleep(2)

driver.get("https://www.hackerrank.com/leaderboard")

time.sleep(5)

#Go to the leaderboard page(practice problems)
driver.get("https://www.hackerrank.com/leaderboard?page=1&track=algorithms&type=practice")

leaderboard = {}

for i in range(1,5):
    link = "https://www.hackerrank.com/leaderboard?page={}&track=algorithms&type=practice".format(i)
    driver.get(link)

    rows = driver.find_elements(By.CLASS_NAME,"general-table")

    x = rows[0].find_elements(By.CLASS_NAME,"table-row-column.ellipsis.hacker")
    y = rows[0].find_elements(By.CLASS_NAME,"table-row-column.ellipsis.rank")
    z = rows[0].find_elements(By.CLASS_NAME,"table-row-column.ellipsis.score")

    for a,b in zip(y,x):
        leaderboard[a.text]=b.text


    time.sleep(3)

print(leaderboard)
















