import time

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from config import CaptchaElements, TimeSleep, CAPTCHA_CLASS_NAME, CAPTCHA_SOLVED
from solver.captcha_manager import CaptchaManager
from .detector import CaptchaDetector


class CaptchaSolver:
    _captcha_element_idx: int = -1

    def __init__(
            self,
            driver: WebDriver,
            times_sleep: TimeSleep = TimeSleep(),
            detector_weight: str = 'yolo_weights/yolov9e-seg.pt'):

        self.__driver = driver
        self._times_sleep = times_sleep
        self._captcha_elements = CaptchaElements()

        self._captcha_manager = CaptchaManager(driver, times_sleep, self._captcha_elements, self._captcha_element_idx)

        self._captcha_detector = CaptchaDetector(model_weight=detector_weight)
        self._detector_classes = self._captcha_detector.get_all_detected_classes
        self._detector_params: dict = {}

    @property
    def times_sleep(self) -> TimeSleep:
        """Returns a tuple that contains delays for functions."""
        return self._times_sleep

    @times_sleep.setter
    def times_sleep(self, value: TimeSleep):
        """This setter allows you to update tuple delays for functions."""
        self._times_sleep = value
        self._captcha_manager.times_sleep = value

    def is_captcha(self) -> bool:
        return bool(self.__driver.find_elements(By.XPATH, value=self._captcha_elements.IFRAME_XPATH))

    def is_solved(self) -> bool:
        if self._check_solved():
            print(f'{self.__class__.__name__}: {CAPTCHA_SOLVED}')
            return True
        return False

    def _check_solved(self) -> bool:
        self.__driver.switch_to.default_content()
        if self.is_captcha():
            try:
                self._captcha_manager.switch_to_iframe(by=By.XPATH, value=self._captcha_elements.IFRAME_XPATH)
                self.__driver.find_element(By.XPATH, self._captcha_elements.CAPTCHA_SOLVED_XPATH)
            except NoSuchElementException:
                return False
        return True

    def solve_captcha(
            self,
            *,
            click_im_not_robot: bool = True,
            is_img_blur: bool = True,
            ksize_blur: tuple[int, int] = (11, 11),
            sigma_blur: float = 1,
            binary_cell_thresh: float = 254,
            area_cell_thresh: float = 5e3,
            error_similar_area: float = 250,
            detect_confidence: float = 0.05,
            mask_cell_overlap_px: int = 5
    ) -> bool:
        """
         Method for automatically solving captcha.

         Args:
            click_im_not_robot (bool): If True, simulates a click on the "I'm not a robot" button.
            is_img_blur (bool): If True, applies blur to the captcha image.
            ksize_blur (tuple[int, int]): Size of the blur kernel.
            sigma_blur (float): The sigma value for the Gaussian blur.
            binary_cell_thresh (float): Threshold value for captcha cell binarization.
            area_cell_thresh (float): Threshold area for defining captcha cells.
            error_similar_area (float): Acceptable area error for similar captcha cells.
            detect_confidence (float): Confidence level when solving a captcha.
            mask_cell_overlap_px (int): Number of mask pixels overlapped by the cell.

         Returns:
            (bool): True, if the captcha was successfully solved
         """

        self._detector_params = {
            'is_img_blur': is_img_blur,
            'ksize_blur': ksize_blur,
            'sigma_blur': sigma_blur,
            'binary_cell_thresh': binary_cell_thresh,
            'area_cell_thresh': area_cell_thresh,
            'error_similar_area': error_similar_area,
            'detect_confidence': detect_confidence,
            'mask_cell_overlap_px': mask_cell_overlap_px
        }

        if click_im_not_robot:
            self._captcha_manager.click_im_not_robot()

        if self.is_solved():
            return True

        while True:
            captcha_bytes, captcha_type, is_additional_challenge, class_idx = self._get_correct_challenge_attributes()

            if is_additional_challenge:
                self._solve_additional_challenge(captcha_bytes=captcha_bytes,
                                                 captcha_type=captcha_type,
                                                 class_idx=class_idx,
                                                 )
            else:
                coord_click = self._captcha_detector.predict_click_coord(captcha=captcha_bytes,
                                                                         captcha_type=captcha_type,
                                                                         required_class_idx=class_idx,
                                                                         **self._detector_params
                                                                         )

                self._captcha_manager.click_on_cell(coord_click)

            self._captcha_manager.captcha_completed()

            if self.is_solved():
                return True

            if self._captcha_manager.is_error_message():
                self._captcha_manager.skip_captcha()

    def _solve_additional_challenge(self, captcha_bytes: bytes, captcha_type: str, class_idx: int):
        while True:
            coord_click = self._captcha_detector.predict_click_coord(captcha=captcha_bytes,
                                                                     captcha_type=captcha_type,
                                                                     required_class_idx=class_idx,
                                                                     **self._detector_params
                                                                     )

            if not coord_click:
                break
            self._captcha_manager.click_on_cell(coord_click)
            time.sleep(self._times_sleep.ADDITIONAL_CHALLENGE)

            captcha_bytes = self._get_all_challenge_attributes(get_only_captcha_bytes=True)

    def _get_correct_challenge_attributes(self) -> tuple[bytes, str, bool, int]:
        """
        The method searches for a captcha class that the detector can recognize.
        And returns the attributes of such a captcha.
        """
        while True:
            captcha_bytes, captcha_type, is_additional_challenge, class_idx = self._get_all_challenge_attributes()
            if class_idx is not None:
                break
            self._captcha_manager.skip_captcha()
        return captcha_bytes, captcha_type, is_additional_challenge, class_idx

    def _get_all_challenge_attributes(self,
                                      get_only_captcha_bytes: bool = False
                                      ) -> bytes | tuple[bytes, str, bool, int]:

        """
         Retrieves all attributes of the current captcha.

         This method does the following:
            1. Switches to the iframe containing the captcha.
            2. Extracts the captcha image bytes.
            3. Optionally returns only the captcha image bytes.
            4. Gets the captcha type from the class attribute of the corresponding element.
            5. Finds the image elements to select and determines the class index for the current captcha challenge.
            6. Checks for the presence of an additional captcha challenge and sets the corresponding flag.

         Args:
            get_only_captcha_bytes (bool): If `True`, the method will return only the captcha image bytes.
            Default is `False`.

         Returns:
            (tuple): A tuple containing the captcha image bytes, captcha type, extra challenge flag, and class index.
         """

        captcha_bytes = self._captcha_manager.switch_to_iframe(by=By.TAG_NAME,
                                                               value=self._captcha_elements.IFRAME,
                                                               get_captcha_screen=True)
        if get_only_captcha_bytes:
            return captcha_bytes

        captcha_type = self.__driver.find_element(By.XPATH,
                                                  self._captcha_elements.CAPTCHA_TYPE_XPATH).get_attribute('class')

        img_selector = self.__driver.find_elements(By.XPATH, self._captcha_elements.IMG_SELECT_XPATH)
        search_element = img_selector[self._captcha_element_idx]
        class_challenge_element = search_element.find_element(By.TAG_NAME, self._captcha_elements.STRONG_TXT_STYLE)
        class_idx = self._find_class_idx(class_challenge_element.text)

        additional_text_element = search_element.find_elements(By.TAG_NAME, self._captcha_elements.SPAN_TXT_STYLE)
        if additional_text_element:
            text = additional_text_element[self._captcha_element_idx].text
            is_additional_challenge = self._check_additional_challenge(text)
        else:
            is_additional_challenge = False

        return captcha_bytes, captcha_type, is_additional_challenge, class_idx

    def _check_additional_challenge(self, text: str) -> bool:
        return (text == self._captcha_elements.ADDITIONAL_CHALLENGE_RU or
                text == f'{self._captcha_elements.ADDITIONAL_CHALLENGE_RU}.' or
                text == self._captcha_elements.ADDITIONAL_CHALLENGE_ENG)

    def _find_class_idx(self, required_class_name: str) -> int | None:
        for english_word, synonym_list in CAPTCHA_CLASS_NAME.items():
            if required_class_name.lower() in synonym_list:
                for idx, value in self._detector_classes.items():
                    if value == english_word:
                        return idx
        return None
