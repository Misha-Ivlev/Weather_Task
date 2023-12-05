import os
import err
import const
import requests
import geocoder
import datetime
import urllib.request


class Weather:
    def __init__(self, code, date=None, timz=None, city=None, desc=None, temp=None, like=None, wind=None):
        self.code = code
        self.date = date
        self.timz = timz
        self.city = city
        self.desc = desc
        self.temp = temp
        self.like = like
        self.wind = wind

    def get(self):
        match self.code:
            case 200:
                if self.timz >= 0:
                    timezone = '+' + str(self.timz//3600) + ':'
                    minutes = str((self.timz%3600)//60)
                else:
                    timezone = '-' + str(-self.timz//3600) + ':'
                    minutes = str((-self.timz%3600)//60)
                
                if len(minutes) < 2:
                    timezone += minutes + '0'
                else:
                    timezone += minutes
                return\
                    'Текущие дата и время: ' + str(datetime.datetime.fromtimestamp(self.date)) + ' (' + timezone + ')\n'\
                    'Название города:      ' + self.city + '\n'\
                    'Погодные условия:     ' + self.desc + '\n'\
                    'Текущая температура:  ' + str(self.temp) + ' градусов по Цельсию\n'\
                    'Ощущается как:        ' + str(self.like) + ' градусов по Цельсию\n'\
                    'Скорость ветра:       ' + str(self.wind) + ' м/c\n'
            case 400:
                return 'Неверный запрос. Возможно Вы допустили ошибку в названии города.'
            case 401:
                return 'Нет доступа. Возможно указан неверный или неработающий API-ключ.'
            case '404':
                return 'Данные не найдены.'
            case 429:
                return 'Превышен лимит запросов.'
            case _:
                return 'Неизвестная ошибка.'


def get_weather(code: int):
    try:
        match code:
            case 1:
                city_name = input(const.city_enter)
            case 2:
                city_name = get_my_city()
        country_code = get_country_code_by_city(city_name)
        weather = get_weather_by_country_code(country_code)
        if weather.code == 200:
            add_to_history(weather.get())
        print(weather.get())
    except err.CityError:
        print(const.city_not_exist)
    except ConnectionError:
        print(const.connection_error)
    except TimeoutError:
        print(const.timeout_error)


def get_country_code_by_city(city: str) -> dict:
    '''
    Эта функция на вход получает название города и прибавляет к нему код страны.
    '''
    try:
        params = {'q': city, 'limit': '1', 'appid': const.key}
        response = requests.get(const.url_geo, params=params, timeout=5).json()
        if response:
            return response[0]['name'] + ',' + response[0]['country']
        else:
            raise err.CityError()
    except requests.exceptions.ConnectionError:
        raise ConnectionError()
    except requests.exceptions.ReadTimeout:
        raise TimeoutError()


def get_weather_by_country_code(country_code: dict) -> Weather:
    try:
        params = {'q': country_code, 'units': 'metric', 'lang': 'ru', 'appid': const.key}
        response = requests.get(const.url, params=params, timeout=5).json()
        if response['cod'] == 200:
            weather = Weather(response['cod'],
                              response['dt'],
                              response['timezone'],
                              response['name'],
                              response['weather'][0]['description'],
                              response['main']['temp'],
                              response['main']['feels_like'],
                              response['wind']['speed'])
        else:
            weather = Weather(response['cod'])
        return weather
    except requests.exceptions.ConnectionError:
        raise ConnectionError()
    except requests.exceptions.ReadTimeout:
        raise TimeoutError()
    except TypeError:
        pass


def get_my_city() -> str:
    '''
    Функция возвращает название Вашего города.
    '''
    try:
        if internet_on():
            return geocoder.ip('me').city
    except Exception:
        raise ConnectionError()


def add_to_history(entry: str):
    history = open(os.path.dirname(__file__)+'\history.txt', 'a', encoding='utf-8')
    history.write(entry + const.separator)
    history.close()


def clear_history():
    open(os.path.dirname(__file__)+'\history.txt', 'w', encoding='utf-8')


def show_history():
    try:
        num = int(input(const.how_much_history).strip())
        if  num > 0:
            history = open(os.path.dirname(__file__)+'\history.txt', 'r', encoding='utf-8')
            history = history.read()
            history = history.split(const.separator)
            history.reverse()
            history = history[1:]
            num = int(num)
            if not history:
                print(const.no_history)
            elif len(history) < num:
                print(const.short_history)
                for i in range(len(history)):
                    print(history[i])
            else:
                for i in range(num):
                    print(history[i])
        else:
                print(const.wrong_num)            
    except TypeError:
        print(const.wrong_num)
    except ValueError:
        print(const.wrong_num)


def internet_on():
    try:
        urllib.request.urlopen("http://google.com")
        return True
    except IOError:
        return False

