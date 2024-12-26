import sublime
import sublime_plugin
import urllib.request
import urllib.parse
import json

def get_suggestions(self, current_word):
        """
        Метод для получения списка предложений через API.
        current_word: текст для анализа (слово или фраза до курсора).
        Возвращает список предложений.
        """
        
        options = send_to_lisa(current_word)
        suggestions = None

        url = options[0]
        headers = options[1]
        data = options[2]

        # Преобразуем данные в JSON
        json_data = json.dumps(data).encode('utf-8')

        # Добавляем заголовок Content-Length
        headers['Content-Length'] = str(len(json_data))

        # Создаем запрос
        req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                response_json = json.loads(response_data)
                result = response_json['choices'][0]['message']['content']
                
        except urllib.error.HTTPError as e:
            print("Ошибка:",e.code)
            print(e.read().decode('utf-8'))
        except Exception as e:
            print("Ошибка:",str(e))

        suggestions = result

        return suggestions

def send_to_lisa(text):

    # Получаем API-ключ из настроек
    settings = sublime.load_settings('DetectLanguage.sublime-settings')
    api_key = settings.get('api_key')
    
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer "+api_key
    }

    data = {
        "model": "mistral-large-latest",
        "stream": False,
        "messages": [
            {"role": "user", "content": "Привет можешь взять на себя роль девушки по имени Лиза"},
            {"role": "assistant", "content": "Привет! Конечно, я могу взять на себя роль Лизы. Как я могу помочь?"},
            {"role": "user", "content": "Привет как тебя зовут?"},
            {"role": "assistant", "content": "Привет! Меня зовут Лиза. А тебя как зовут?"},
            {"role": "user", "content": "Егор"},
            {"role": "assistant", "content": "Привет, Егор! Рада познакомиться. Как я могу помочь?"},
            {"role": "user", "content":"Можешь посоветовать как дополнить этот код. Отвечай максимально кратко и не используй ```  ``` просто пиши код"},
            {"role": "assistant", "content": "Конечно, Егор! Давай попробуем. "},
            {"role": "user", "content": text},
        ]
    }

    return [url,headers,data]


