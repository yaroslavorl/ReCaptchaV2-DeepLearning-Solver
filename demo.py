import os
import time

from dotenv import load_dotenv

from utils.get_driver import get_driver
from solver import CaptchaSolver


def main():
    load_dotenv()
    captcha_page = "https://patrickhlauke.github.io/recaptcha/"
    # captcha_page = "https://www.google.com/recaptcha/api2/demo"
    # captcha_page = 'https://democaptcha.com/demo-form-eng/recaptcha-2.html'
    # captcha_page = 'https://terrillthompson.com/tests/recaptcha/'
    # captcha_page = 'https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php'

    driver_path = os.getenv('DRIVER')
    google_driver = get_driver(driver_path)
    google_driver.implicitly_wait(time_to_wait=5)
    google_driver.get(captcha_page)

    solver = CaptchaSolver(google_driver, detector_weight='yolo_weights/yolo11x-seg.pt')

    time.sleep(2)
    if solver.is_captcha():
        solver.solve_captcha()

    google_driver.quit()


if __name__ == '__main__':
    main()
