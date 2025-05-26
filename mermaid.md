classDiagram
    class AppOrchestrator {
        +create_app()
        +wsgi_app()
    }
    class RoutesHandler {
        +route_request()
    }
    class MatchService {
        +create_match()
        +update_current_match_score()
        +reset_current_match()
    }
    class OrmMatchRepository {
        +create_match()
        +save_finished_match()
        +list_matches_paginated()
    }
    class MatchController {
        +new_match_controller()
        +match_score_controller()
    }
    AppOrchestrator --> RoutesHandler
    RoutesHandler --> MatchController
    MatchController --> MatchService
    MatchService --> OrmMatchRepository