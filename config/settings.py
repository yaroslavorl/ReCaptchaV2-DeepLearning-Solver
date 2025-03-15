from typing import NamedTuple


class CaptchaElements:
    IFRAME = 'iframe'
    IFRAME_XPATH = "//iframe[@title='reCAPTCHA']"
    CAPTCHA_TYPE_XPATH = "//img[contains(@class, 'rc-image-tile')]"
    CAPTCHA_SOLVED_XPATH = "//div[@class='recaptcha-checkbox-border' and @style='display: none;']"
    IMG_SELECT_XPATH = "//*[contains(@class, 'rc-imageselect-desc')]"
    IMG_SELECT_ERROR_XPATH = "//div[contains(@class, 'rc-imageselect-error')][@tabindex='0']"
    IMG_SELECTOR = 'rc-imageselect'
    STRONG_TXT_STYLE = 'strong'
    SPAN_TXT_STYLE = 'span'
    ADDITIONAL_CHALLENGE = 'Когда изображения закончатся, нажмите "Подтвердить"'
    SKIP_BUTTON = 'recaptcha-reload-button'
    VERIFY_BUTTON = 'recaptcha-verify-button'


class TimeSleep(NamedTuple):
    CLICK_IM_NOT_ROBOT: float = 2
    CLICK_RATE: float = 0.4
    CLICK_ON_CELL_DONE: float = 5
    SKIP_CAPTCHA: float = 2
    CAPTCHA_COMPLETED: float = 1
    ADDITIONAL_CHALLENGE: float = 10


CLICK_SCRIPT = 'document.elementFromPoint({x_center}, {y_center}).click();'

CAPTCHA_CLASS_NAME = {'car': ['автомобиль', 'автомобили'],
                      'bus': ['автобус', 'автобусы', 'автобусами'],
                      'motorcycle': ["мотоцикл", 'мотоциклы'],
                      'bicycle': ['велосипед', "велосипеды"],
                      'fire hydrant': ['гидрант', 'гидрантами', 'пожарные гидранты', 'пожарный гидрант'],
                      'traffic light': ["светофор", 'светофоры'],
                      'boat': ['лодки', 'лодками']

                      }

CAPTCHA_SOLVED = 'Captcha solved!'
