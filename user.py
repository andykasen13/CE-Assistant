class User:
    def __init__(self, name, currentRolls):
        self.currentRolls = currentRolls
        self.name = name
    
    def __str__(self):
        return f"User name: {self.name} with currentRolls {self.currentRolls}"