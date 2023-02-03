from json import load
from stripe import checkout

file = open("config.json", "r", encoding="utf-8")
config = load(file)


def get_checkout_session(product):
    print("[SYSTEM][STRIPE][CHECKOUT]: Generating link")
    try:
        checkout_session = checkout.Session.create(
            line_items=[
                {
                    'price': config["BACKEND"]["STRIPE"]["PRODUCTS"][config["APP_MODE"]][product]["id"],
                    'quantity': 1
                },
            ],
            mode='payment',
            success_url=config["BACKEND"]["STRIPE"]["SUCCESS_URL"].replace(
                "[number]", config["BACKEND"]["WHATSAPP"]["NUMBER"]),
            phone_number_collection={
                'enabled': True,
            }
        )
    except Exception as e:
        print("[SYSTEM][STRIPE][CHECKOUT]: Fail")
        print(str(e))
        if config["APP_MODE"] == "DEVELOPMENT":
            return str(e)
        else:
            return config["UI"]["FAILED_TO_GENERATE_STRIPE_SESSION"]

    print("[SYSTEM][STRIPE][CHECKOUT]: Success")
    return checkout_session.url


if __name__ == "__main__":
    import stripe
    stripe.api_key = config["BACKEND"]["STRIPE"]["API_KEY"]
    print(get_checkout_session(input("::")))
