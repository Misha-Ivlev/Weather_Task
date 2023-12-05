class CityError(Exception):
    def __init__(self):
        super().__init__('Нет такого города.')