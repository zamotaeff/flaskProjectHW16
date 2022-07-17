import json


def load_users_data():
    with open('data/users.json') as file:
        # print(type(json.load(file)))
        return json.load(file)


def load_orders_data():
    with open('data/orders.json', encoding='utf-8') as file:
        return json.load(file)


def load_offers_data():
    with open('data/offers.json') as file:
        return json.load(file)
