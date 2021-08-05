from copy import deepcopy
from name_comparator import *


class Game(object):
    def __init__(self, name, max_players=4):
        self.name = name
        self.max_players = int(max_players)
        # dizionario con chiave = a nome e valore = a lista con le posizioni
        # e.g. 'rick': [0,0,2,1,0]: significa che non è mai arrivaot primo o secondo o quinto, due volte 3 e una volta 4
        self.users = dict()

    def add_user(self, name):
        self.users[name] = [0] * self.max_players

    def get_user_stats(self, name) -> None:
        for i in self.users.keys():
            if ratio(i.lower(), name.lower()) > 0.5 and len(similar(i.lower(), name.lower())) > 0:
                return self.users[name]
        return None

    def get_users_stats(self) -> dict:
        return deepcopy(self.users)

    def update_user(self, name, position):
        for i in self.users.keys():
            if ratio(i.lower(), name.lower()) > 0.5 and len(similar(i.lower(), name.lower())) > 0:
                if position <= self.max_players:
                    self.users[i][position - 1] = self.users[i][position - 1] + 1
                return
        # da aggiustare
        self.add_user(name)
        if position <= self.max_players:
            self.users[name][position - 1] = self.users[name][position - 1] + 1

        if name not in self.users.keys():
            self.add_user(name)

    def get_Name(self) -> str:
        return self.name

    def get_max_players(self) -> int:
        return self.max_players

    def check_name(self, a):
        print(ratio(a.lower(), self.name.lower()), similar(a.lower(), self.name.lower()))
        return (ratio(a.lower(), self.name.lower()) > 0.5 and len(
            similar(a.lower(), self.name.lower())) > 0 and True) or False
