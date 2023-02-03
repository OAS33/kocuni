import stripe
from flask import Flask, request, send_from_directory
import requests
import modules.chatbot as ai
from modules.database.database import db
import modules.database.database_clean
from threading import Thread
from json import loads, load, dump
from os import system
from modules.stripe import session
from time import time


class Debug:
    def __init__(self, status):
        self.status = status

    def Print(self, message):
        if self.status != 1:
            return
        print(message)


def send_msg(num, msg):
    headers = {
        'Authorization': config["BACKEND"]["WHATSAPP"]["TOKEN"],
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': num,
        'type': 'text',
        "text": {
            "body": msg
        }
    }
    debug.Print(f"[SYSTEM][MAIN][SEND_MSG]: Sending to {num}: {msg}")
    database = db("modules/database/user.db")
    user = database.get(num)
    if user != False:
        database.update(num, "chatlog", f"{user[0][6]}\nBot: {msg}")
    response = requests.post(
        f'https://graph.facebook.com/v13.0/{config["BACKEND"]["WHATSAPP"]["NUMBER_ID"]}/messages', headers=headers, json=json_data)

    print("[SYSTEM][MAIN][SEND_MSG]: Response for", num, ":", response.text)


def received(number, message):
    number = number.replace("+", "")
    database = db("modules/database/user.db")
    estimation = len(message) / 3 * 4
    user = database.get(number)
    if user != False:
        database.update(number, "chatlog",
                        f"{user[0][6]}\n{number}: {str(message)}")

    if message.lower() == "credits":
        send_msg(number, config["UI"]["COMMANDS"]["credits"])
        return
    if message.lower() == "support":
        send_msg(number, config["UI"]["COMMANDS"]["support"])
        return
    if user == False:
        if message.lower() == config["UI"]["PURCHASE_TRIAL_COMMAND"]:
            send_msg(number, config["UI"]["PRE_PURCHASE_TEXT"].replace(
                "[link]", session.get_checkout_session("rizzify_trial")))
            return
        print("SENDING NEWCOMER MESSAGE")
        send_msg(number, config["UI"]["NEW_USER_MESSAGE"])
        return
    elif user[0][1] == 0:
        print("USER BLOCKED")
        send_msg(number, config["UI"]["USER_BLOCKED_MSG"])
        return
    elif user[0][2] < estimation:
        print("USER BALANCE ERROR", user[0][2], estimation)
        if message.lower() == config["UI"]["PURCHASE_COMMAND"]:
            send_msg(number, config["UI"]["PRE_PURCHASE_TEXT"].replace(
                "[link]", session.get_checkout_session("rizzify")))
            return
        send_msg(number, config["UI"]["USER_BALANCE_NONE"])
        return
    elif message.lower() == config["UI"]["PURCHASE_COMMAND"]:
        send_msg(number, config["UI"]["PRE_PURCHASE_TEXT"].replace(
            "[link]", session.get_checkout_session("rizzify")))
        return
    if message.lower() == "commands":
        send_msg(number, config["UI"]["AVAILABLE_COMMANDS"])
        return
    if message.lower() == "balance":
        send_msg(number, config["UI"]["COMMANDS"]
                 ["balance"].replace("[number]", str(user[0][2])))
        return
    if message.startswith("usecode:"):
        code = message.split(":")[1]
        with open("modules/coupon_codes/codes.json", "r", encoding="utf-8") as file:
            json = load(file)
        try:
            words = json[code]["words"]
        except KeyError:
            send_msg(number, "Invalid code")
            return
        if code in user[0][5]:
            send_msg(number, "You have already used this code")
            return
        database.update(number, "balance", user[0][2] + words)
        database.update(number, "usedcodes", user[0][5] + "-" + code)
        json[code]["used"] += 1
        with open("modules/coupon_codes/codes.json", "w", encoding="utf-8") as file:
            dump(json, file)
        send_msg(number, config["UI"]["COUPON_CODE_USED"].replace(
            "[number]", str(words)))
        return
    if message.lower() == "reset":
        database.update(number, "prompt",
                        config["BACKEND"]["AI"]["START_PROMPT"])
        return
    if message.lower() == "--prompt":
        send_msg(number, user[0][3])
        return
    user_prompt = user[0][3] + f"⚿\n¡Human: {message}\n¡Chatbot:⚿"
    user_prompt = user_prompt.replace("\n\n\n", "\n").replace(
        "\n\n", "\n")
    send = user_prompt.replace("¡", "")
    response = ai.get_completion(send, config["BACKEND"]["AI"]["MODEL"])
    new_bal = user[0][2] - response[1]
    response = response[0]
    user_prompt = config["UI"]["PROMPT_ENTERANCE"] + \
        "\n¡".join(f"{user_prompt}{response}".split(
            ";")[1][1::].split("¡")[2::])
    database.update(number, "prompt", user_prompt.replace(
        '"', "").replace("'", ""))

    database.update(number, "balance", new_bal)

    send_msg(number, response)

    database.exit()
    return True


app = Flask(__name__)


@app.route("/success", methods=["GET", "POST"])
def payment_success():
    print("SUCCESS")
    return send_from_directory("modules\\stripe\\ui\\", "success.html")


@app.route("/stripe_webhooks", methods=["POST"])
def stripe_webhooks():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)

    try:
        event = stripe.Webhook.construct_event(
            payload, received_sig, webhook_secret
        )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature!")
        return "Bad signature", 400

    print(
        "[SYSTEM][MAIN[STRIPE]: Received event: id={id}, type={type}".format(
            id=event.id, type=event.type
        )
    )
    if event.type != "checkout.session.completed" and event.type != 'checkout.session.async_payment_succeeded':
        return "", 200
    print("DATABASE UPDATE")
    payload = loads(payload)
    try:
        stripe_object = payload["data"]["object"]
        payment_status = stripe_object["payment_status"]
        if payment_status != "paid":
            return "", 200
    except KeyError as e:
        debug.Print("[SYSTEM][MAIN][STRIPE]: Keyerror:\n", e)
        return
    database = db("modules/database/user.db")
    customer_phone = stripe_object["customer_details"]["phone"].replace(
        "+", "")
    total = stripe_object["amount_total"]
    print("[SYSTEM][MAIN][STRIPE]: Session complete, got:",
          total, "from", customer_phone)
    if database.get(customer_phone) == False:
        print("[SYSTEM][MAIN][WEBHOOKS][STRIPE]: New customer: ", total)
        if total == config["BACKEND"]["STRIPE"]["PRODUCTS"][config["APP_MODE"]]["rizzify_trial"]["price"]:
            database.add(customer_phone, 1, config["BACKEND"]["STRIPE"]["PRODUCTS"][config["APP_MODE"]]["rizzify_trial"]["credits"],
                         config["BACKEND"]["AI"]["START_PROMPT"])
            send_msg(customer_phone, config["UI"]["TRIAL_PURCHASED_MESSAGE"])
            return "", 200
    elif total == config["BACKEND"]["STRIPE"]["PRODUCTS"][config["APP_MODE"]]["rizzify"]["price"]:
        database.update(customer_phone, "balance",
                        database.get(customer_phone)[0][2] + config["BACKEND"]["STRIPE"]["PRODUCTS"][config["APP_MODE"]]["rizzify"]["credits"])
        send_msg(customer_phone, config["UI"]["CREDITS_PURCHASED"].replace(
            "[number]", str(database.get(customer_phone)[0][2])))
        return "", 200
    else:
        pass

    return "", 200


@app.route('/')
def index():
    return """<!DOCTYPE html >
<html >
  <style >
     h1 {text-align: center
          }
   </style >
   <body >
      <h1>Hello World</h1>
   </body >
</html >"""


@app.route('/receive_msg', methods=['POST', 'GET'])
async def whatsapp_api_webhook():
    if request.method == "GET":
        try:
            if request.args.get('hub.verify_token') == config["BACKEND"]["WHATSAPP"]["VERIFY_TOKEN"]:
                return request.args.get('hub.challenge')
        except Exception as e:
            print("[SYTEM][MAIN][WHATSAPP_WEBHOOK][GET_FAIL]:", e)
    res = request.get_json()
    try:
        entry = res["entry"][0]["changes"][0]["value"]["messages"][0]
        NUMBER = entry["from"]
        MESSAGE = entry["text"]["body"]
    except KeyError as e:
        print("STATUS:", e)
        mainerror = res["entry"][0]["changes"][0]["value"]["statuses"]
        for error in mainerror:
            print(error["recipient_id"], error["status"])
            try:
                for case in error["errors"]:
                    print(f"{case['title']}\n")
            except KeyError:
                pass
        return "200 OK HTTPS"

    if MESSAGE == None or MESSAGE == "":
        return "200 OK HTTPS"

    print(F"MESSAGE FROM {NUMBER}: {MESSAGE}")

    Thread(target=received, args=(NUMBER, MESSAGE)).start()

    return '200 OK HTTPS.'


def main():
    global config, webhook_secret, CLOCK, debug
    with open("config.json", "r", encoding="utf-8") as f:
        config = loads(f.read())
    config["UI"]["PROMPT_ENTERANCE"] = config["BACKEND"]["AI"]["START_PROMPT"].split(";")[
        0] + ";\n"
    print("[SYSTEM][MAIN]:CONFIG LOADED")

    cleaner = Thread(
        target=modules.database.database_clean.storage_check_clock, daemon=True)
    if CLOCK == False:
        cleaner.start()
        CLOCK = True

    stripe.api_key = config["BACKEND"]["STRIPE"]["API_KEY"]
    webhook_secret = config["BACKEND"]["STRIPE"]["WEBHOOK_SECRET"]

    debug = Debug(1)

    system('start cmd /c ngrok http --region=us --hostname=usdatingadvisor.ngrok.io 5000')
    try:
        print("[SYSTEM]: Online")
        if config["APP_MODE"] == "DEVELOPMENT":
            if input("[SYSTEM][INPUT]: Local test mode(y/n):") != "y":
                if input("Launch stripe listener(y/n): ") == "y":
                    system(
                        "start cmd /c stripe listen --forward-to localhost:5000/stripe_webhooks")
                app.run(debug=False, use_reloader=False)
            else:
                system(
                    "start cmd /c stripe listen --forward-to localhost:5000/stripe_webhooks")
                while True:
                    received(input("number:"), input("message:"))
        else:
            app.run(debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    CLOCK = False
    main()
