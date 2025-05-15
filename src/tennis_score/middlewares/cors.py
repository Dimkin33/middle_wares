"""middlewares/cors.py."""

class CORSMiddleware:
    """Класс CORSMiddleware.
    
    Отвечает за функциональность, связанную с CORS заголовками.
    """
    
    def __init__(self, app):
        """Инициализирует объект класса.
        
        Args:
            app: WSGI приложение, которое будет обернуто
        """
        self.app = app
    
    def __call__(self, environ, start_response):
        """Обрабатывает WSGI вызов и добавляет CORS заголовки.
        
        Args:
            environ: Окружение WSGI с информацией о запросе
            start_response: Функция для инициализации ответа
            
        Returns:
            Итерируемый объект с байтовым содержимым ответа
        """
        def custom_start_response(status, headers, exc_info=None):
            """Обертка для start_response, добавляющая CORS заголовки.
            
            Args:
                status: Статус HTTP ответа
                headers: Заголовки HTTP ответа
                exc_info: Информация об исключении, если есть
                
            Returns:
                Результат выполнения оригинальной функции start_response
            """
            headers.append(("Access-Control-Allow-Origin", "*"))
            headers.append(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"))
            headers.append(("Access-Control-Allow-Headers", "Content-Type"))
            return start_response(status, headers, exc_info)
        
        if environ.get("REQUEST_METHOD", "") == "OPTIONS":
            custom_start_response("200 OK", [("Content-Length", "0")])
            return [b""]
        return self.app(environ, custom_start_response)
