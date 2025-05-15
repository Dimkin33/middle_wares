# Рекомендации по ручному исправлению ошибок линтера
# filepath: c:\Users\dimki\Project\middle_wares\FIX_MANUAL_INSTRUCTIONS.md

# Руководство по ручному исправлению ошибок линтера

После запуска проверки кода с помощью ruff (`.\scripts\lint.ps1`), вы можете увидеть различные ошибки. Ниже приведены инструкции по исправлению наиболее распространенных ошибок вручную.

## 1. Добавление документации к модулям (D100)

Для исправления ошибок типа `D100 Missing docstring in public module`, добавьте документацию в начало файла:

```python
"""Модуль для работы с теннисным матчем.

Этот модуль предоставляет классы и функции для управления теннисными матчами.
"""

import logging
import os
# остальные импорты
```

## 2. Добавление документации к классам (D101)

Для исправления ошибок типа `D101 Missing docstring in public class`, добавьте документацию сразу после объявления класса:

```python
class MatchRepository:
    """Репозиторий для управления объектами матча.
    
    Обеспечивает хранение, получение и манипуляцию объектами матчей.
    """
```

## 3. Добавление документации к методам и функциям (D102, D103)

Для исправления ошибок типа `D102 Missing docstring in public method` или `D103 Missing docstring in public function`:

```python
def update_match_score(self, player: str) -> Match | None:
    """Обновляет счет матча для указанного игрока.
    
    Args:
        player: Идентификатор игрока ('player1' или 'player2')
        
    Returns:
        Обновленный объект матча или None, если матч не найден
    """
```

## 4. Документация для методов инициализации (D107)

Для исправления ошибок типа `D107 Missing docstring in __init__`:

```python
def __init__(self, template_name: str, default_context: dict = None):
    """Инициализирует контроллер представления.
    
    Args:
        template_name: Имя шаблона
        default_context: Контекст по умолчанию для шаблона
    """
```

## 5. Исправление форматирования документации (D205, D415)

### D205: Пустая строка между заголовком и подробным описанием

Неправильно:
```python
"""Модель теннисного матча.
Содержит данные о текущем состоянии матча.
"""
```

Правильно:
```python
"""Модель теннисного матча.

Содержит данные о текущем состоянии матча.
"""
```

### D415: Завершение первой строки документации точкой

Неправильно:
```python
"""DTO для передачи данных матча"""
```

Правильно:
```python
"""DTO для передачи данных матча."""
```

## 6. Однострочные документации (D200)

Неправильно:
```python
def get_score_json(self):
    """Формирует JSON для сохранения счета
    """
```

Правильно:
```python
def get_score_json(self):
    """Формирует JSON для сохранения счета."""
```

## 7. Разбиение длинных строк (E501)

Для исправления ошибок типа `E501 Line too long`, разбейте длинные строки:

Неправильно:
```python
self.logger.info(f"Request: {method} {path}{' ?' + query_string if query_string else ''} from {client_addr}")
```

Правильно:
```python
log_path = f"{path}{' ?' + query_string if query_string else ''}"
self.logger.info(f"Request: {method} {log_path} from {client_addr}")
```

или:

```python
self.logger.info(
    f"Request: {method} {path}"
    f"{' ?' + query_string if query_string else ''} "
    f"from {client_addr}"
)
```

## 8. Упрощение условных выражений (SIM108)

Для исправления ошибок типа `SIM108 Use ternary operator`:

Неправильно:
```python
if body and size > 0:
    body_bytes = body.read(size)
else:
    body_bytes = b""
```

Правильно:
```python
body_bytes = body.read(size) if body and size > 0 else b""
```

## 9. Обновление импортов (UP035)

Для исправления ошибок типа `UP035 Import from collections.abc instead`:

Неправильно:
```python
from typing import Callable, Iterable
```

Правильно:
```python
from collections.abc import Callable, Iterable
```

## Последовательность исправлений

1. Исправьте сначала структурные проблемы: импорты, длинные строки и т.д.
2. Затем исправьте форматирование документации
3. Добавьте недостающие документации к модулям, классам и функциям
4. Запустите проверку снова для подтверждения исправлений

## Полезные команды

- Проверка только определенных типов ошибок:
  ```
  ruff check --select D100 src/tennis_score
  ```

- Проверка с автоматическим исправлением:
  ```
  ruff check --fix src/tennis_score
  ```

- Проверка с более подробной информацией:
  ```
  ruff check --verbose src/tennis_score
  ```
