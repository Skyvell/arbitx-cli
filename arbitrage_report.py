from unicodedata import decimal


import constants

class ArbitrageReport:
    def __init__(self, token: str, profit: str, iterations: str):
        self.token = token
        self.profit = int(profit, 16) // constants.EXA
        self.iterations = int(iterations, 16)