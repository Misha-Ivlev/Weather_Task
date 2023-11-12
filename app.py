import requests
import datetime
import http.client
import const

def main():
    print("\nЗдравствуйте!\n"\
          "Вы запустили консольное приложение для определения погоды.")
    while True:
        print("\nСписок команд:\n"\
            "1 - определить погоду в любом городе\n"\
            "2 - определить погоду в своём городе\n"\
            "3 - увидеть историю запросов\n"\
            "4 - очистить историю запросов\n"\
            "5 - завершить работу приложения\n")
        command = input("Выберите то, что вы хотите сделать: ")
        match command:
            case "1":
                city = input("Введите название города: ")
                info = get_weather_by_city({"output": city, "success": True})
                output = output_constructor(info)
                print(output)
                if info["success"]:
                    const.history.append(output)
            case "2":
                my_ip = get_my_ip_adress()
                city = get_city_by_ip(my_ip)
                info = get_weather_by_city(city)
                output = output_constructor(info)
                print(output)
                if info["success"]:
                    const.history.append(output)
            case "3":
                try:
                    number = int(input("Введите количество записей которые вы хотите получить: "))
                    if  number > 0:
                        get_history(int(number))
                    else:
                        print('Количество записей может быть только числом больше нуля.')
                except ValueError:
                    print('Количество записей может быть только целым числом.')
            case "4":
                const.history = []
                print("История запросов очищена.")
            case "5":
                print("До новых встреч!")
                break
            case _:
                print("Неверная команда, внимательнее прочитайте список команд.")


def get_my_ip_adress() -> {str: str, str: bool}:
    try:
        my_ip_adress = http.client.HTTPConnection("ifconfig.me")
        my_ip_adress.request("GET", "/ip")
        return {"output": my_ip_adress.getresponse().read().decode(), "success": True}
    except:
        return {"output": "Неизвестный IP. Возможно отсутсвует подключение к сети.", "success": False}


def get_city_by_ip(ip_adress: {str: str, str: bool}) -> {str: str, str: bool}:
    if ip_adress["success"]:
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_adress["output"]}').json()
            return {"output": response["city"], "success": True}
        except requests.exceptions.ConnectionError:
            return {"output": "Ошибка определения города по IP. Проверьте подключение к сети.", "success": False}
    else:
        return {"output": ip_adress["output"], "success": False}


def get_weather_by_city(city: {str: str, str: bool}) -> {str: str, str: bool}:
    if city["success"]:
        city = city["output"]
        try:
            response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={const.api_key}", timeout=5)
            return {"output": response.json(), "success": True}
        except requests.exceptions.ConnectionError:
            return {"output": "Отсутствует связь с сервером. Проверьте подключение к сети.", "success": False}
        except requests.exceptions.ReadTimeout:
            return {"output": "Превышено время ожидания. Попробуйте позже.", "success": False}
    else:
        return {"output": city["output"], "success": False}


def output_constructor(weather_info: {str: dict, str: bool}) -> str:
    if weather_info["success"]:
        weather_info = weather_info["output"]
        match weather_info["cod"]:
            case 200:
                output =\
                    f"Текущие дата и время: {datetime.datetime.fromtimestamp(weather_info['dt'])}\n"\
                    f"Название города:      {weather_info['name']}\n"\
                    f"Погодные условия:     {weather_info['weather'][0]['description']}\n"\
                    f"Текущая температура:  {round(weather_info['main']['temp'] - 273.15, 2)} градусов по цельсию\n"\
                    f"Ощущается как:        {round(weather_info['main']['feels_like'] - 273.15, 2)} градусов по цельсию\n"\
                    f"Скорость ветра:       {weather_info['wind']['speed']} м/c"
            case 400:
                output = "Неверный запрос. Возможно Вы допустили ошибку в названии города."
            case 401:
                output = "Нет доступа. Возможно указан неверный или неработающий API-ключ."
            case '404':
                output = "Данные не найдены."
            case 429:
                output = "Превышен лимит запросов."
            case _:
                output = "Неизвестная ошибка."
    else:
        output = weather_info["output"]
    return output


def get_history(number: int) -> str:
    if len(const.history) >= number:
        for info in const.history[-number:]:
            print(info)
            print()
    else:
        print("В истории запросов нет столько записей. Показываю всё, что есть:")
        for info in const.history:
            print(info)
            print()

