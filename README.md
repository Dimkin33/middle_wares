    ```mermaid
    classDiagram
        direction LR
        class WSGIApp {
            +handle_request()
        }
        class Router {
            +route(request) Controller
        }
        class BaseController {
            <<Interface>>
            +handle(request_data) Response
        }
        class MatchController {
            +MatchService
            +new_match(data)
            +update_score(data)
        }
        class MatchService {
            <<Interface>>
            +create_new_match(player1_name, player2_name) MatchDTO
            +add_point(match_id, player_key) MatchDTO
        }
        class MatchServiceImpl {
            +MatchRepository
            +ScoreCalculator
            +create_new_match()
            +add_point()
        }
        class MatchRepository {
            <<Interface>>
            +get_by_id(id) Match
            +save(match) Match
            +get_current() Match
            +set_current(match)
        }
        class ScoreCalculator {
            <<Interface>>
            +apply_point(match_state, player_key) new_match_state
        }
        class DomainModel_Match {
          +uuid
          +player1_name
          +player2_name
          +score_state
          +winner
        }

        WSGIApp --> Router
        Router --> BaseController
        MatchController --|> BaseController
        MatchController o--> MatchService
        MatchServiceImpl --|> MatchService
        MatchServiceImpl o--> MatchRepository
        MatchServiceImpl o--> ScoreCalculator
        MatchRepository ..> DomainModel_Match : CRUD
        ScoreCalculator ..> DomainModel_Match : Reads/Updates
    ```