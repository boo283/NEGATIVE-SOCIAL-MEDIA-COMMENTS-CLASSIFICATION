import os
import pandas as pd
import numpy as np
import json
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from io import StringIO

def configure_driver():
    #Configurations
    webdriver_path = "C:\\Program Files\\Scrapper1\\chromedriver.exe" #your webdriver path
    chrome_options = Options()
    # Turn off Chrome notification
    chrome_options.add_argument("--disable-notifications")
    # Start the service
    service = Service(webdriver_path)
    # Open URL
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def set_up_driver(url, service):
    driver = configure_driver()
    #driver = webdriver.Chrome(service=service)
    driver.get(url)
    return driver

def login_facebook(username, password, driver):
    try:
        # Wait until the login form is loaded
        # username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, ":r1:")))
        username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "email")))
        username_field.send_keys(username)

        # Wait until the password field is loaded
        #password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, ":r4:")))
        password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "pass")))
        password_field.send_keys(password)

        # Submit log in form 
        password_field.send_keys(Keys.RETURN)

    except Exception as e:
        print("Logged in failed. \n Trying to log in again...")

    finally:
        print("Logged in successfully")

def scroll_and_click_button(driver):
    try:
        # Scroll down until the button is found and clickable
        while True:
            try:
                # Locate the button using its class names
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x9f619.x1n2onr6.x1ja2u2z.x6s0dn4.x3nfvp2.xxymvpz"))
                )
                button.click()
                print("Button clicked successfully.")
                break
            except Exception as e:
                # Scroll down a bit and try again
                driver.execute_script("window.scrollBy(0, 1000);")
    except Exception as e:
        print("Unable to locate and click the button.", e)

def click_view_more_btn(driver):

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Find the view more button
    view_more_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'more comments')]")))
    view_more_btn.click()

def click_showed_type_btn(driver, btn_name):
    try:
        # Scroll down to the button and click
        driver.execute_script("window.scrollTo(0, window.scrollY)")  # Đổi giá trị 200 thành khoảng cách muốn cuộn
        most_relevant_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '%s')]"%(btn_name))))
        most_relevant_button.click()
    except Exception as e:
        print("Can't click", btn_name)
        return False

def show_more_comments(driver):
    # Limit the number of attempts to load more comments
    max_attempts = 10  # Adjust based on typical post length and your needs
    attempts = 0
    last_count = 0
    stable_attempts = 10  # Number of attempts with no new comments before considering end

    while attempts < max_attempts:
        try:
            click_view_more_btn(driver)
            time.sleep(2)  # Give some time for comments to load
            current_count = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'x1iorvi4 x4uap5 x18d9i69 x46jau6')]"))

            if current_count == last_count:
                stable_attempts -= 1
                if stable_attempts == 0:
                    print("No more comments to load.")
                    break
            else:
                last_count = current_count
                stable_attempts = 3  # Reset the stable_attempts counter

            attempts += 1
        except Exception as e:
            print("Out of comments or error encountered:")
            break

def count_replied_comments(driver):
    try:
        all_replied_comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x1q0g3np x87ps6o x1lku1pv x1a2a7pz x6s0dn4 xi81zsa x1iyjqo2 xs83m0k xsyo7zv x1mnrxsn')]")
        return len(all_replied_comments)
    except:
        return 0
    
def show_all_replies(driver, threshold, ite):
    #n = 30
    arr = []
    cnt = 1
    #n = count_replied_comments(driver)
    #print(n)
    #print('Show all replies cmt')
    start1 = time.time()
    while True:
        start2 = time.time()
        if cnt > threshold: #Threshold
            break
        try:
            #print("Finding comments")
            #all_replied_comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1iorvi4 x4uap5 x18d9i69 x46jau6')]")
            all_replied_comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x9f619 x1n2onr6 x1ja2u2z')]")
        except:
            break
        
        arr.append(len(all_replied_comments))
        if arr.count(max(arr)) >= ite:
            print("Limited")
            print(arr.count(max(arr)))
            return
        for comment in all_replied_comments:
            if cnt % 50 == 0:
                print(cnt)
            cnt += 1
            driver.execute_script("window.scrollBy(0, -50);")  # Cuộn lên 50 dòng
        
            try:
                #print("Tim thay binh luan duoc reply")
                #start = time.time()
                view_more_buttons = WebDriverWait(comment, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'html-div xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x78zum5 x1iyjqo2 x21xpn4 x1n2onr6')]")))
                #print("Chuan bi click")
                view_more_buttons.click()
               # print("Show all replies")
                for sub_cmt in comment:
                # driver.execute_script("window.scrollTo(0, 900);")
                    try:
                        view_more_sub_buttons = WebDriverWait(sub_cmt, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'html-div xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x78zum5 x1iyjqo2 x21xpn4 x1n2onr6')]")))
                        view_more_sub_buttons.click()
                    except:
                        break
            except Exception as e:
                # print(e)
                # if "out of contents" in str(e).lower():
                #     return
                #print('Gap loi')
                break
            finally:
                #print("Vao finally")
                end2 = time.time()
                if end2 - start2 > 2:
                    print("Finally")
                    return
        #print("Vao finally2")
        # end1 = time.time()
        # if end1 - start1 > 2:
        #     print("Finally")
        #     return


def filter_spam(text):
    spam_text = ['giá tốt', 'giá cực tốt', 'http', 'miễn phí', '100%', 'kèo bóng', 'khóa học', 'netflix', 'Net Flix', 'shopee', 'lazada', 'vào tường',
        'trang cá nhân','tham khảo', '18+', 'sex', 'see more', 'xem thêm', 'xem chi tiết', 'xem ngay', 'link', 'facebook',
        'ᴋèo', 'ꜰʙ', 'Aᴇ', 'Á𝐎 𝐃Â𝐘', 'ᴋèo ʙóng', 'ʙeᴛ-ʙᴏɴg6666', 'ʙeᴛ.ʙᴏɴg.6666', '6666', 'vùng kín', 'viêm hôi', 'd,âm', 'zú', 'zâm', 'dâm',
        '𝒄𝒉𝒖̛𝒐̛𝒏𝒈 𝒕𝒓𝒊̀𝒏𝒉', '𝒉𝒂̂́𝒑 𝒅𝒂̂̃𝒏', '🎉', 'CỔNG GAME', 'NẠP RÚT', 'lồn', 'cặc']
    for spam in spam_text:
        if spam in text.lower():
            return True
    return False

def get_comments_with_text_and_img(driver):
    cnt = 0
    treasured_comments = []
    is_spam = 0
    comments = driver.find_elements(
        By.XPATH,
          "//div[contains(@class, 'x1n2onr6 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz') or contains(@class, 'x1n2onr6 xurb0ha x1iorvi4 x78zum5 x1q0g3np x1a2a7pz')]")
    for comment in comments:
        try:
            # Check if comment contains text
            text_ele = comment.find_element(By.XPATH, ".//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')]")
            username = comment.find_element(By.XPATH, ".//span[@class='x3nfvp2']/span")
            if text_ele:
                try:
                    name_tag = text_ele.find_element(By.XPATH, ".//span[@class='xt0psk2']/span")
                    name_tag = name_tag.text
                except:
                    name_tag = None

                # Limit the number of comments  
                cnt += 1
                if cnt > 2500:
                    break
                text = text_ele.text
                if cnt % 10 == 0:
                    print("Count: ", cnt)

                # Filter spam comments    
                if filter_spam(text):
                    is_spam = 1
                else:
                    is_spam = 0
                treasured_comments.append({
                    "id" : cnt,
                    "username": username.text,
                    "text": text,
                    'tag_name': name_tag,
                    'is_spam': is_spam
                })
        except Exception as e:
            continue
    print("Crawl successfully!!! \nTotal Comments: ", cnt)
    return treasured_comments, cnt

def crawl(driver, url, username, password, threshold, ite):

    driver.get(url)
    # Login Facebook
    login_facebook(username, password, driver)
    scroll_and_click_button(driver)
    click_showed_type_btn(driver, "All comments")

    #Show more comments
    try:
      show_more_comments(driver)
    except:
       print('No more cmt')

    # Scroll to top
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)

    # Show comment and scroll step by step
    driver.execute_script("window.scrollTo(0, 700);") #cuộn
    driver.execute_script("window.scrollTo(0, 700);")  #cuộn

    # Sleep 5s
    time.sleep(3)

    # Scroll để các button visible and show replies
    driver.execute_script("window.scrollTo(0, 900);")

    #Show replies
    try:
      show_all_replies(driver, threshold, ite)
    except Exception as e:
      print('Replies are limited', e)
      pass


    # Get comments
    cmts, cnt = get_comments_with_text_and_img(driver)
    print(cnt)
    return cmts, cnt

def get_url():
    #get url from input
    url = input("Enter the URL: ")
    return url

def save_to_csv(df, file_name):
    df.to_csv(file_name, index=False)
##################################################3
# Main function

if __name__ == '__main__':

    cnt = 0
    threshold = 50 #Base on the Internet speed (300 - 400)
    ite = 30 # Use to check whether it reaches the end of the page (Should be 20 - 30)

    # Login info
    username = "" #your fb username
    password = "" #your fb password

    url = get_url()
    driver = configure_driver()
    # starter = 0
    # limit = 10

    cmt_data, cnt = crawl(driver, url, username, password, threshold, ite)
    cmt_data_json = json.dumps(cmt_data, ensure_ascii=False)
    cmts = pd.read_json(StringIO(cmt_data_json), orient='records')

    save_to_csv(cmts, 'D:\ki6\Preprocess and Mining\Project\comments.csv')
    time.sleep(50)
