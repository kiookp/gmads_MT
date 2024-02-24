import time
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.ads_api import get_user_ids

# 选择器
SELECTORS = {
    "username": "//input[@id='identifierId']",
    "password": "//input[@name='Passwd']",
    "next": [
        "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b']",
        "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe P62QJc LQeN7 xYnMae TrZEUc lw1w4b']",
        "//button[contains(text(),'Next')]",
        "//*[@id='next']",
        "//button[contains(text(),'次へ')]",
        "//*[@class='VfPpkd-Jh9lGc']"
        "//button[contains(text(),'I agree')]",
        "//button[contains(text(),'Ich stimme zu')]",
        "//div[@class='VfPpkd-RLmnJb']"
        "//*[@id='identifierNext']/div/button",
        "//*[@id='yDmH0d']/c-wiz/div/div[2]/div/div[2]/div/div[1]/div/div/button",
    ],
    "code": '//input[@name="code"]',
    "html": [
        "//*[@id='maia-main']/form/p/input",
        "/html/body/div/div/div[2]/form[2]/button",
    ]
}

card_details_queue = Queue()  # 创建一个队列
WAIT = 10  # 等待时间
THREADS = 12  # 线程数


# 从文件中读取账号信息到队列
def read_card_details_to_queue():
    with open('card.txt', 'r') as file:
        for line in file:
            card_details_queue.put(line.strip().split('----'))

# 打开浏览器
def open_browser(ads_id):
    try:
        if card_details_queue.empty():
            print("没有可用的信息")
            return

        # 从队列中获取账号信息
        username, password, recovery_email = card_details_queue.get()
        open_url = f"http://local.adspower.net:50325/api/v1/browser/start?user_id={ads_id}"
        resp = requests.get(open_url).json()
        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id:", ads_id)
            return

        chrome_driver = resp["data"]["webdriver"]

        chrome_options = Options()
        service = Service(executable_path=chrome_driver)
        chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(610, 800)
        print("清除浏览器的所有cookie")
        driver.get("https://myaccount.google.com/signinoptions/two-step-verification")
        time.sleep(3)
        # 等待邮箱输入框出现，并是可输入状态
        print('################ 等待id="identifierId"元素出现，并是可输入状态 ################')
        try:
            # 等待页面中的输入框元素出现，最多等待WAIT秒
            acc_phone_number = WebDriverWait(driver, WAIT).until(
                EC.element_to_be_clickable((By.XPATH, SELECTORS['username'])))

            # 找到输入框，并输入邮箱地址
            acc_phone_number.send_keys(username)
            print('################ 输入邮箱 ################')
        except Exception as e:
            print('Error occurred while waiting for/typing in the element:', e)

        time.sleep(1)
        print('################ 点击下一步按钮 ################')
        for selector in SELECTORS['next']:
            try:
                next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
                next_button.click()
                break
            except:
                pass

        # 等待密码输入框出现，并是可输入状态
        print('################ 等待密码输入框出现，并是可输入状态 ################')
        try:
            # 等待页面中的输入框元素出现，最多等待WAIT秒
            acc_phone_number = WebDriverWait(driver, WAIT).until(
                EC.element_to_be_clickable((By.XPATH, SELECTORS['password'])))

            # 找到输入框，并输入邮箱地址
            acc_phone_number.send_keys(password)
            print('################ 输入邮箱 ################')
        except Exception as e:
            print('Error occurred while waiting for/typing in the element:', e)

        time.sleep(3)
        print('################ 点击下一步按钮 ################')
        for selector in SELECTORS['next']:
            try:
                next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
                next_button.click()
                break
            except:
                pass

        try:
            challenge_elements = WebDriverWait(driver, 5).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'lCoei.YZVTmd.SmR8'))
            )
            print("找到元素 class='lCoei YZVTmd SmR8'")

            if len(challenge_elements) >= 3:

                challenge_element = challenge_elements[2]
                challenge_element.click()
                print("点击第三个 class='lCoei YZVTmd SmR8'")

                input_element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, 'knowledge-preregistered-email-response'))
                )
                print("找到输入框")

                input_element.send_keys(recovery_email)
                print("输入user2变量的值")
                # 等待1秒
                time.sleep(1)

                print('################ 点击下一步按钮 ################')
                for selector in SELECTORS['next']:
                    try:
                        next_button = WebDriverWait(driver, WAIT).until(
                            EC.element_to_be_clickable((By.XPATH, selector)))
                        next_button.click()
                        break
                    except:
                        pass
            else:
                print("未找到足够的元素 class='lCoei YZVTmd SmR8'")

        except TimeoutException:
            print("在5秒内未找到元素 class='lCoei YZVTmd SmR8'")

        time.sleep(4)
        # 等待选择列表展开

        driver.get("https://mail.google.com/mail/u/0/h/go2vmozvj94t/?v=lui")
        time.sleep(3)
        # 设置显性等待时间，最多等待10秒
        wait = WebDriverWait(driver, 10)

        print('################ 选择html  ################')
        for selector in SELECTORS['html']:
            try:
                next_button = WebDriverWait(driver, WAIT).until(
                    EC.element_to_be_clickable((By.XPATH, selector)))
                next_button.click()
                break
            except:
                pass
        print("点击“Take me to latest Gmail”按钮")

    except Exception as e:
        print(f"Error occurred for ads_id: {ads_id}", e)


def main():
    read_card_details_to_queue()  # 初始化队列
    profile_ids = get_user_ids(page_size=THREADS)
    print("Profile IDs:", profile_ids)

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for profile_id in profile_ids:
            if not card_details_queue.empty():
                executor.submit(open_browser, profile_id)
                time.sleep(3)
            else:
                print("没有可供分配的信息。.")
                break

    print("All tasks finished!")

# 执行main函数
if __name__ == "__main__":
    main()
