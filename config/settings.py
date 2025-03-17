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
    ADDITIONAL_CHALLENGE_RU = 'Когда изображения закончатся, нажмите "Подтвердить"'
    ADDITIONAL_CHALLENGE_ENG = 'Click verify once there are none left'
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

CAPTCHA_CLASS_NAME = {'car': ['автомобиль', 'автомобили', 'car', 'cars'],
                      'bus': ['автобус', 'автобусы', 'автобусами', 'bus'],
                      'motorcycle': ["мотоцикл", 'мотоциклы', 'motorcycle', 'motorcycles'],
                      'bicycle': ['велосипед', 'велосипеды', 'bicycle', 'bicycles'],
                      'fire hydrant': ['гидрант', 'гидрантами', 'пожарные гидранты', 'пожарный гидрант', 'fire hydrant',
                                       'hydrant', 'hydrants', 'fire hydrants'],
                      'traffic light': ["светофор", 'светофоры', 'traffic light', 'traffic lights'],
                      'boat': ['лодки', 'лодками', 'boat', 'boats']

                      }

CAPTCHA_SOLVED = 'Captcha solved!'
