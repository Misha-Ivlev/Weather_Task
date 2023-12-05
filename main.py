import const
import app

def main():
    print(const.welcome_text)
    while True:
        print(const.commands_list)
        command = input(const.command_enter).strip()
        match command:
            case "1":
                app.get_weather(1)
            case "2":
                app.get_weather(2)
            case "3":
                app.show_history()
            case "4":
                app.clear_history()
            case "5":
                print(const.bye_bye)
                break
            case _:
                print(const.wrong_command)


if __name__ == '__main__':
    main()

