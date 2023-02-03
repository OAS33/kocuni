from json import load, dump
from os import system

while True:
    choice = int(
        input("1-view all\n2-view one\n3-add one\n4-delete one\nYour choce: "))
    system("cls")
    with open("codes.json", "r", encoding="utf-8") as file:
        json = load(file)
    if choice == 1:
        print(json)
    elif choice == 2:
        code = input("Input code:")
        try:
            print(f"This code has been used {json[code]['used']} times.")
        except KeyError:
            print("Invalid code")
    elif choice == 3:
        code = input("Input code:")
        json[code] = {}
        json[code]["words"] = int(input(
            "How many words will this code give to the user: "))
        json[code]["used"] = 0
        with open("codes.json", "w", encoding="utf-8") as file:
            dump(json, file)
    elif choice == 4:
        try:
            json.pop(input("Input code:"))
            with open("codes.json", "w", encoding="utf-8") as file:
                dump(json, file)
        except:
            print("Invalid code")
    input("press any key to continue...")
    system("cls")
