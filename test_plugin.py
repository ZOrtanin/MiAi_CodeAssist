import sublime
import sublime_plugin
from .api_client import get_suggestions

# Список предложений по умолчанию
suggestions = [
    "# Мне нечего предложить",
]

# Переменная для хранения выделенного текста или текущей строки
selected_text = None

# Переменная для хранения ответа
return_text = None

# Класс реализует команду, которая отображает меню предложений через Phantom
class TestPluginCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        """
        Основной метод запуска команды.
        Получает выделенный текст или строку до курсора, а затем вызывает метод отображения Phantom.
        """
        global selected_text,return_text

        # Получаем API-ключ из настроек
        settings = sublime.load_settings('DetectLanguage.sublime-settings')
        api_key = settings.get('api_key')
        if not api_key:
            sublime.message_dialog("API key is not set. Please set the API key in the plugin settings.")
            return

        # Получаем выделенный текст
        selected_text = "".join([self.view.substr(region) for region in self.view.sel() if not region.empty()])

        # Если текст не выделен, берем строку до курсора
        if not selected_text:            

            current_region = self.view.sel()[0]  # Текущая позиция курсора
            line_region = self.view.line(current_region)  # Регион строки
            cursor_position = current_region.end()  # Позиция курсора в строке
            selected_text = self.view.substr(sublime.Region(line_region.begin(), cursor_position))  # Текст до курсора

        out_text = str(get_suggestions(self,self.get_language()+selected_text))
        return_text = out_text
        # Отображаем Phantom с предложениями
        self.show_phantom(out_text)

    def show_phantom(self, selected_text):
        """
        Метод отображения Phantom (встроенного HTML-элемента) для взаимодействия.
        selected_text: текст, который будет использоваться для предложений.
        """
        current_region = self.view.sel()[0]  # Позиция курсора
        # Получаем координаты после выделенного текста
        end_positions = [region.end() for region in self.view.sel() if not region.empty()]
        print(current_region,end_positions)
        current_region_my = sublime.Region(end_positions[-1], end_positions[-1])

        text_to_show = self.build_phantom_html(selected_text)  # Генерируем HTML для отображения

        # HTML-содержимое для Phantom
        content = (
            '<body style="color:grey">'
            '<div></div>'
            '<div>' + text_to_show + '</div>'
            '<a href="insert">Вставить</a> <a href="exit">Отменить</a>'
            '<div></div>'
            '</body>'
        )

        # Добавляем Phantom в редактор
        self.view.add_phantom(
            "example_phantom",  # Уникальный идентификатор Phantom
            current_region_my,  # Привязка к текущей позиции курсора
            content,  # HTML-контент
            sublime.LAYOUT_BLOCK,  # Расположение блока Phantom
            self.on_navigate_phantom  # Метод для обработки кликов на ссылки
        )

    def on_navigate_phantom(self, href):
        """
        Метод для обработки действий в Phantom.
        href: строка, содержащая действие (например, "insert" или "exit").
        """
        global selected_text,return_text
        if href == "insert":
            # Вставляем текст на место курсора
            self.view.run_command("insert", {"characters": return_text})
            # Удаляем Phantom
            self.view.erase_phantoms("example_phantom")

        elif href == "exit":
            # Удаляем Phantom без вставки текста
            self.view.erase_phantoms("example_phantom")

    def build_phantom_html(self, selected_text="предложений нет"):
        """
        Метод для генерации HTML-контента для Phantom.
        Преобразует текст в HTML-разметку для отображения в Sublime Text.
        """
        
        arr = selected_text.split("\n")  # Разбиваем текст на строки
        text_out = ""

        for item in arr:
            # Заменяем пробелы на неразрывные пробелы для корректного отображения
            text_out += "<div>" + item.replace(" ", "&nbsp;") + "</div>"

        return text_out


    def get_language(self):
        # Получаем текущий синтаксис файла
        syntax = self.view.settings().get('syntax')

        # Извлекаем имя языка программирования из синтаксиса
        if syntax:
            language = syntax.split('/')[-1].split('.')[0]
            
            return str(language)
        else:
            return 'язык не выбран'
