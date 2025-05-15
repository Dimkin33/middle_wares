# Примеры решений для распространенных проблем линтинга
# filepath: c:\Users\dimki\Project\middle_wares\EXAMPLES.md

# Примеры исправления распространенных проблем

## 1. Добавление документации к модулю (D100)

```python
"""Модуль для работы с теннисным скорингом.

Этот модуль содержит классы и функции, необходимые для работы
с логикой теннисного матча и управления состоянием игры.
"""

import logging
import os
```

## 2. Добавление документации к функциям и методам (D103, D102)

```python
def render_template(template_name: str, **context: dict[str, object]) -> bytes:
    """Отрендерить шаблон с заданным контекстом.

    Args:
        template_name: Имя шаблона для рендеринга
        context: Контекст для шаблона (переменные)

    Returns:
        Байтовая строка с HTML-кодом
    """
    template = env.get_template(template_name)
    return template.render(**context).encode("utf-8")
```

## 3. Добавление документации к классам (D101)

```python
class LoggingMiddleware:
    """Промежуточное ПО для логирования HTTP-запросов.

    Отвечает за логирование входящих запросов и времени их выполнения.
    Может настраиваться для различных уровней детализации.
    """
```

## 4. Документация для методов __init__ (D107)

```python
def __init__(self, template_name: str, default_context: dict = None):
    """Инициализировать контроллер с шаблоном и контекстом по умолчанию.

    Args:
        template_name: Имя шаблона для рендеринга
        default_context: Контекст по умолчанию
    """
    self.template_name = template_name
    self.default_context = default_context or {}
```

## 5. Одно-строчная документация (D200)

```python
def get_score_json(self):
    """Формирует JSON для сохранения счета."""
    # код функции...
```

## 6. Добавление точки в конце первой строки документации (D415)

```python
"""Контроллер для простых GET-запросов."""  # правильно

"""Контроллер для простых GET-запросов"""   # неправильно
```

## 7. Исправление многострочных документаций (D205)

```python
"""Модель теннисного матча, хранящая текущее состояние.

Содержит только данные и методы доступа к ним.
Бизнес-логика обновления счета перенесена в MatchService.
"""
```

## 8. Упрощение выражения if-else (SIM108)

```python
# Неправильно
if body and size > 0:
    body_bytes = body.read(size)
else:
    body_bytes = b""

# Правильно
body_bytes = body.read(size) if body and size > 0 else b""
```

## 9. Обновление импорта из коллекций (UP035)

```python
# Неправильно
from typing import Callable, Iterable, TypeAlias

# Правильно
from collections.abc import Callable, Iterable  
from typing import TypeAlias
```

## 10. Разбиение длинных строк (E501)

```python
# Неправильно
self.logger.info(f"Request: {method} {path}{' ?' + query_string if query_string else ''} from {client_addr}")

# Правильно
log_path = f"{path}{' ?' + query_string if query_string else ''}"
self.logger.info(f"Request: {method} {log_path} from {client_addr}")

# или
self.logger.info(
    f"Request: {method} {path}"
    f"{' ?' + query_string if query_string else ''} "
    f"from {client_addr}"
)
```
