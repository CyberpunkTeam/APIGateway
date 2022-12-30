from enum import Enum


class Currency(str, Enum):
    DOLAR = "DOLAR"
    PESO_ARG = "PESO_ARG"
    REAL = "REAL"
    EURO = "EURO"
