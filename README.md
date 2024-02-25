# Smart-assistant - умный голосовой помощник Галя

## Структруа проекта:
-  Файл source.py - основной файл
-  functions.py - файл со всеми функциями
-  window.py - файл с окном (Tkinter)
-  password - файл со всеми паролями и api ключами (токенами)
-  commands.json - все команды в отдельном файле json

## Работа голосового помощника:
+ Работает smart-assistant по кнопке. Нажали, затем ждем на экране (в консоли) надпись "Я вас слушаю >>>" - в это время можно говорить
+ Как только ассистент выполнил команду, кнопка перестет нажиматься. Для следующего действия надо нажать еще раз. И так с каждым действием

 ## Функции голосового помощника:
  1. Приветствие
***Описание:***
    + Говорит приветствие (ответ сделан рандомно)
    + Если пользователь сказал "доброе утро" или "добрый вечер" и тд., то ассистент определяет какое сейчас время и отвечает в зависимости отвермени суток "доброе утро" - если утро и тд.
     
  2. Прощание
***Описание:***
    + Прощается (выбор фразы рандомный)
     
  3. Узнать дату
***Описание:***
    + Говорит ту информацию о дате, которую попросите: день недели, год, месяц или полную дату (без времени)
     
  4. Узнать время
***Описание:***
    + Говорит время (часы - минууты)
     
  5. Узнать погоду (использует OpenWeather)
***Описание:***
    + Говорить город нужно в им. падеже: "Москва", "Нижний Новгород" и тд.
    + Помощник говорит темепературу и состояние на улице (пасмурно, ясно, облачно и тд.)
    
  6. Найти определение на wikipedia
***Описание:***
    + Записывает результат в файл (кодировка utf-8). Название файла "wiki_result.txt"
    
  7. Найти видео по запросу на youtube
***Описание:***
    + Открывает youtube в браузере и ищет видео по запросу
    
  8. Найти информацию по запросу в google
***Описание:***
    + Открывает браузер и в google ищет информацию по запросу 


  
