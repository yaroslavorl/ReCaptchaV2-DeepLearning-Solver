from selenium import webdriver


def get_driver(executable_path_driver: str):
    service = webdriver.ChromeService(
        executable_path=executable_path_driver)
    return webdriver.Chrome(service=service)
