import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PROXY_HOST = 'your_proxy'  # rotating proxy or host
PROXY_PORT = 'proxy_port'  # proxy port


# TODO: Нуждается в тестах и в объединении с get_driver()
def get_proxy_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        chrome_options.add_argument(f'--proxy-server={PROXY_HOST}:{PROXY_HOST}')

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver


def __test():
    driver = get_proxy_chromedriver(
        user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0')
    driver.get('https://atomurl.net/myip/')
    time.sleep(15)
    driver.quit()


if __name__ == '__main__':
    __test()
