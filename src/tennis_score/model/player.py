"""Player model for tennis score application."""

import itertools

from ..dto.player_dto import PlayerDTO

players_dict = {}


class Player:  # noqa: D101
    _id_counter = itertools.count(1)

    def __init__(self, name):
        self.id = next(Player._id_counter)
        self.name = name
        players_dict[self.id] = self.name

    def to_dto(self):
        return PlayerDTO(id=self.id, name=self.name)
