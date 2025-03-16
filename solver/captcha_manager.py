import time

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from config import CLICK_SCRIPT, TimeSleep, CaptchaElements


class CaptchaManager:

    def __init__(self, driver: WebDriver, times_sleep: TimeSleep, captcha_elements: CaptchaElements, element_idx):
        self.__driver = driver
        self._times_sleep = times_sleep
        self._captcha_elements = captcha_elements
        self._captcha_element_idx = element_idx

    @property
    def times_sleep(self) -> TimeSleep:
        return self._times_sleep

    @times_sleep.setter
    def times_sleep(self, value: TimeSleep):
        self._times_sleep = value

    def click_im_not_robot(self):
        self.__driver.find_element(By.XPATH, value=self._captcha_elements.IFRAME_XPATH).click()
        time.sleep(self._times_sleep.CLICK_IM_NOT_ROBOT)

    def is_error_message(self) -> bool:
        self.__driver.switch_to.default_content()
        try:
            self.switch_to_iframe(by=By.TAG_NAME, value=self._captcha_elements.IFRAME)
            self.__driver.find_element(By.XPATH, self._captcha_elements.IMG_SELECT_ERROR_XPATH)
            return True
        except NoSuchElementException:
            return False

    def switch_to_iframe(self, by: By, value: str, get_captcha_screen: bool = False):
        self.__driver.switch_to.default_content()
        iframe = self.__driver.find_elements(by, value)
        if get_captcha_screen:
            captcha_screen = iframe[self._captcha_element_idx].screenshot_as_png
            self.__driver.switch_to.frame(iframe[self._captcha_element_idx])
            return captcha_screen
        self.__driver.switch_to.frame(iframe[self._captcha_element_idx])

    def click_on_cell(self, coord: list[tuple[float, float]]):
        if not coord:
            return

        for x, y in coord:
            self.__driver.execute_script(CLICK_SCRIPT.format(x_center=x, y_center=y))
            time.sleep(self._times_sleep.CLICK_RATE)
        time.sleep(self._times_sleep.CLICK_ON_CELL_DONE)

    def skip_captcha(self):
        self.switch_to_iframe(by=By.TAG_NAME, value=self._captcha_elements.IFRAME)
        self.__driver.find_element(By.ID, self._captcha_elements.SKIP_BUTTON).click()
        time.sleep(self._times_sleep.SKIP_CAPTCHA)

    def captcha_completed(self):
        try:
            self.switch_to_iframe(by=By.TAG_NAME, value=self._captcha_elements.IFRAME)
            self.__driver.find_element(By.ID, self._captcha_elements.VERIFY_BUTTON).click()
        except (NoSuchElementException, Exception):
            self.__driver.switch_to.default_content()
            self.click_im_not_robot()
        time.sleep(self._times_sleep.CAPTCHA_COMPLETED)
