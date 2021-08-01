from copy import deepcopy


class Game(object):
    def __init__(self, name, max_players=4):
        self.name = name
        self.max_players = int(max_players)
        # dizionario con chiave = a nome e valore = a lista con le posizioni
        # e.g. 'rick': [0,0,2,1,0]: significa che non è mai arrivaot primo o secondo o quinto, due volte 3 e una volta 4
        self.users = dict()

    def add_user(self, name):
        self.users[name] = [0] * self.max_players

    def get_user_stats(self, name) -> list:
        if name in self.users.keys():
            return self.users[name]
        else:
            return None

    def get_users_stats(self) -> dict:
        return deepcopy(self.users)

    def update_user(self, name, position):
        if name not in self.users.keys():
            self.add_user(name)
        if position<=self.max_players:
            self.users[name][position-1] = self.users[name][position-1] + 1

    def get_Name(self) -> str:
        return self.name

    def get_max_players(self) -> int:
        return self.max_players
