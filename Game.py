class Game(object):
    def __init__(self, name, max_players=4):
        self.name = name
        self.max_players = max_players
        # dizionario con chiave = a nome e valore = a lista con le posizioni
        # e.g. 'rick': [0,0,2,1,0]: significa che non è mai arrivaot primo o secondo o quinto, due volte 3 e una volta 4
        self.users = dict()

    def add_user(self, name):
        self.users[name] = [0] * self.max_players

    def get_user_stats(self, name):
        if name in self.users.keys():
            return self.users[name]
        else:
            return None

    def get_users_stats(self):
        return
    def update_user(self, name, position):
        if name not in self.users.keys():
            self.add_user(name)
        self.users[name][position] = self.users[name][position] + 1

    def get_Name(self):
        return self.name