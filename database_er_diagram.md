# Tennis Score App - Архитектура базы данных

## ER Диаграмма базы данных

```mermaid
---
title: Tennis Score App - Entity Relationship Diagram
---
erDiagram
    PLAYERS ||--o{ MATCHES_PLAYER1 : "участвует как player1"
    PLAYERS ||--o{ MATCHES_PLAYER2 : "участвует как player2"
    PLAYERS ||--o{ MATCHES_WINNER : "побеждает в"
    
    PLAYERS {
        int id PK "Первичный ключ"
        string name UK "Уникальное имя игрока"
    }

    MATCHES {
        int id PK "Первичный ключ" 
        string uuid UK "UUID для идентификации"
        int player1_id FK "Ссылка на первого игрока"
        int player2_id FK "Ссылка на второго игрока"
        int winner_id FK "Ссылка на победителя (nullable)"
        string score_str "Финальный счет матча"
        timestamp created_at "Дата создания записи"
    }

    %% Связи
    MATCHES }o--|| PLAYERS : player1_id
    MATCHES }o--|| PLAYERS : player2_id  
    MATCHES }o--o| PLAYERS : winner_id
```

## Детальное описание сущностей

### Таблица PLAYERS (Игроки)
- **id** (INTEGER, PRIMARY KEY) - Уникальный идентификатор игрока
- **name** (VARCHAR, UNIQUE, NOT NULL) - Имя игрока (должно быть уникальным)

### Таблица MATCHES (Матчи)
- **id** (INTEGER, PRIMARY KEY) - Уникальный идентификатор матча в БД
- **uuid** (VARCHAR, UNIQUE, NOT NULL) - UUID для активных матчей (используется для поиска)
- **player1_id** (INTEGER, FOREIGN KEY → players.id, NOT NULL) - Первый игрок
- **player2_id** (INTEGER, FOREIGN KEY → players.id, NOT NULL) - Второй игрок
- **winner_id** (INTEGER, FOREIGN KEY → players.id, NULLABLE) - Победитель матча
- **score_str** (VARCHAR, NOT NULL) - Финальный счет в строковом формате
- **created_at** (TIMESTAMP) - Время создания записи

## Архитектура данных в памяти

```mermaid
---
title: Структура данных в памяти приложения
---
graph TB
    subgraph "В памяти (Active Matches)"
        AM[Active Matches Dict]
        AM --> |"match_uuid: str"| MO[Match Object]
        MO --> P1[Player Object 1]
        MO --> P2[Player Object 2]
        MO --> SC[Score State]
        MO --> SH[Set History]
    end
    
    subgraph "База данных PostgreSQL"
        PT[players table]
        MT[matches table]
        PT --> |"FK relationships"| MT
    end
    
    subgraph "DTO Layer"
        MD[MatchDTO]
        MD --> |"для API/View"| JSON[JSON Response]
    end
    
    MO --> |"save_finished_match()"| MT
    MT --> |"orm_to_dto()"| MD
    MO --> |"to_live_dto()"| MD
```

## Потоки данных

### 1. Создание нового матча
1. **MatchService.create_match()** → создает объект Match в памяти
2. **OrmMatchRepository._active_matches[uuid]** → сохраняет в словаре активных матчей
3. Игроки НЕ создаются в БД до завершения матча

### 2. Завершение матча
1. **OrmMatchRepository.save_finished_match()** → сохраняет матч в БД
2. **get_or_create_player_by_name()** → создает/находит игроков в БД
3. Создается запись в таблице **matches**
4. Матч удаляется из **_active_matches**

### 3. Получение данных
- **Активные матчи**: из _active_matches → Match.to_live_dto() → MatchDTO
- **Завершенные матчи**: из БД → orm_to_dto() → MatchDTO
- **Список матчей**: комбинация активных + завершенных с пагинацией

## Ограничения целостности

1. **UNIQUE** constraint на `players.name` - имена игроков уникальны
2. **UNIQUE** constraint на `matches.uuid` - UUID матчей уникальны  
3. **FOREIGN KEY** constraints для связей с таблицей players
4. **NOT NULL** constraints для обязательных полей
5. **CHECK** constraint: player1_id ≠ player2_id (на уровне приложения)

## Индексы для производительности

Рекомендуемые индексы:
- `CREATE INDEX idx_matches_uuid ON matches(uuid);`
- `CREATE INDEX idx_matches_player1 ON matches(player1_id);`
- `CREATE INDEX idx_matches_player2 ON matches(player2_id);`
- `CREATE INDEX idx_matches_winner ON matches(winner_id);`
- `CREATE INDEX idx_players_name ON players(name);`
