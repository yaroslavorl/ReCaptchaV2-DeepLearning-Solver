# ReCaptcher

ReCaptcher - Automatic Russian Google reCAPTCHAv2 Solver using YOLO Model Segmentation
## Описание
Пример автоматического решения гугл капч с помощью сегментационной модели YOLO

<img src="assets/demo_solver.gif" alt="Пример решения капч" width="600" />

## Требования 

* `Python >= 3.10`

## Установка зависимостей

   ```bash
     git clone https://github.com/yaroslavorl/ReCaptcher.git
     cd nomerogram-parser

     python -m venv venv
     source venv/bin/activate
   
     pip install -r requirements.txt
```

## Установка Chromedriver

Для работы с Selenium вам необходимо установить Chromedriver вашей версии Google Chrome

#### Полезные ссылки:

1. [Установка браузер Chrome и Chromedriver Ubuntu 20.04](https://skolo.online/documents/webscrapping/#step-2-install-chromedriver)
2. [Chromedriver GitHub](https://github.com/dreamshao/chromedriver)
3. https://www.selenium.dev/documentation/webdriver/

## Демо

```python
import time

from get_driver import get_driver
from solver import CaptchaSolver


def main():
    captcha_page = "https://www.google.com/recaptcha/api2/demo"

    driver_path = '/path/to/chromedriver'
    google_driver = get_driver(driver_path)
    google_driver.implicitly_wait(5)
    google_driver.get(captcha_page)

    solver = CaptchaSolver(google_driver, detector_weight='yolo_weights/yolov9e-seg.pt')

    time.sleep(2)
    # Данных строк достаточно для автоматического решения гугл-капч.
    if solver.is_captcha():
        solver.solve_captcha()

    google_driver.quit()


if __name__ == '__main__':
    main()
```

### Recaptcher Settings:
`TIME_SLEEP` — это класс, который управляет временными задержками в процессе автоматизации взаимодействия
с элементами на веб-странице. Ниже приведены параметры, которые вы можете настроить для работы решателя капч:

- **CLICK_IM_NOT_ROBOT**: 
  - **Описание**: Время (в секундах) ожидания перед нажатием на кнопку "Я не робот".

- **CLICK_RATE**: 
  - **Описание**: Задержка между кликами по ячейкам.
  - **Примечание**: Имитирует естественное поведение пользователя.
  
- **CLICK_ON_CELL_DONE**: 
  - **Описание**: Время ожидания после успешного завершения челленджа.

- **SKIP_CAPTCHA**: 
  - **Описание**: Время после пропуска капчи.
  - **Примечание**: Если челлендж не может быть выполнент, то капча пропускается.

- **CAPTCHA_COMPLETED**: 
  - **Описание**: Время после успешного завершения капчи.

- **ADDITIONAL_CHALLENGE**: 
  - **Описание**: Время для дополнительных челенджей или сложностей.
  - **Примечание**: Гугл капча может давать дополнительные челленджи, например: после клика на ячейку с объектом,
   в той же ячейке может медленно проявляться новый объект, 
   на который также необходимо нажать для успешного завершения капчи. Такое появление может занимать до 10 секунд.

```python
from solver import CaptchaSolver
from config.settings import TimeSleep

# Настройка времени ожидания после любого этапа решения капчи
TIME_SLEEP = TimeSleep(CLICK_IM_NOT_ROBOT=2,
                       CLICK_RATE=0.1,
                       CLICK_ON_CELL_DONE=1,
                       SKIP_CAPTCHA=2,
                       CAPTCHA_COMPLETED=1,
                       ADDITIONAL_CHALLENGE=10)

# Выбор весов YOLO-seg (YOLOv8-seg/YOLOv9-seg/YOLOv11-seg)
DETECTOR_WEIGHT = 'yolov9e-seg.pt'

solver = CaptchaSolver(driver=google_driver,
                       times_sleep=TIME_SLEEP,
                       detector_weight=DETECTOR_WEIGHT)

if solver.is_captcha():
    solver.solve_captcha()
```

## Ограничения

#### Результаты могут зависеть от:
* Количества запросов, отправленных с вашего IP-адреса;
* Качества интернет соединения;
* Настройки WebDriver (например, низкого time_wait при поиске элементов);
* Настройки time_sleep между этапами взаимодействия с веб-страницей;
* Изменений, внесенных разработчиками в html-код сайтов с искомыми элементами (потребуется новая настройка путей к
  элементам в settings);
* Языка капчи (доступно решение только русских капч).
