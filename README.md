# ReCaptcher 🚀🚀🚀

ReCaptcher - Automatic Google reCAPTCHAv2 Solver using YOLO Model Segmentation

![Описание изображения](assets/cap_seg.jpg)

## Описание

ReCaptcher использует Selenium для автоматизированного взаимодействия с веб-страницей,
на которой размещена reCAPTCHA и сегментационную модель YOLO, 
которая позволяет эффективно распознавать и обрабатывать элементы этой капчи. 

YOLO выполняет сегментацию и возвращает маски объектов,
затем осуществляется анализ полученных масок для нахождения пересечений между ними и ячейками капчи.
На основании полученных данных о пересечении, система принимает решение о том, на какие ячейки с объектами необходимо выбрать. 

Пример автоматического решения Google reCAPTCHA представлен ниже.

<img src="assets/demo_solver.gif" alt="Пример решения капч" width="600" />

## Установка зависимостей

   ```bash
  git clone https://github.com/yaroslavorl/ReCaptcher.git
  cd nomerogram-parser
  
  # Python >= 3.10
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

## Demo

```python
import time

from utils.get_driver import get_driver
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
`TIME_SLEEP` — это класс, который управляет временными задержками в процессе взаимодействия
с элементами на веб-странице с капчей. Ниже приведены параметры, которые вы можете настроить для работы решателя капч:

```python
from solver import CaptchaSolver
from config.settings import TimeSleep

# Настройка времени ожидания после любого этапа решения капчи
TIME_SLEEP = TimeSleep(CLICK_IM_NOT_ROBOT=2, # Время (в секундах) ожидания перед нажатием на кнопку "Я не робот".
                       CLICK_RATE=0.1, # Задержка между кликами по ячейкам.
                       CLICK_ON_CELL_DONE=1, # Время ожидания после успешного завершения челленджа.
                       SKIP_CAPTCHA=2, # Время ожидания после пропуска капчи.
                       CAPTCHA_COMPLETED=1, # Время ожидания после успешного завершения капчи.
                       ADDITIONAL_CHALLENGE=10 # Время ожидания появление новых объектов на динамической капче.
                       )

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
