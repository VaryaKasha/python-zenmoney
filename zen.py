#!/usr/bin/env python3
import json
from collections import defaultdict
from time import time
from urllib.parse import urlencode

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

import settings


bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def get_auth_url():
    auth_url = "https://api.zenmoney.ru/oauth2/authorize/?{}"
    auth_params = urlencode({
        "response_type": "code",
        "client_id": settings.ZEN_CONSUMER_KEY,
        "redirect_uri": "https://t.me/zenmoney_statistics_bot?start=",
    })
    return auth_url.format(auth_params)


def extract_unique_code(text):
    parts = text.split()
    if len(parts) > 1:
        try:
            return parts[1].split('=')[1]
        except IndexError:
            pass
    return None


def get_auth_data():
    try:
        with open("auth.json") as auth_file:
            user_data = json.load(auth_file)
    except (FileNotFoundError, KeyError):
       user_data = {}

    return user_data


def write_auth_data(data):
    with open("auth.json", "w") as auth_file:
        json.dump(data, auth_file)


def get_token(code):
    r = requests.post(
        "https://api.zenmoney.ru/oauth2/token/",
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.ZEN_CONSUMER_KEY,
            'client_secret': settings.ZEN_CONSUMER_SECRET,
            'code': code,
            'redirect_uri': "https://t.me/zenmoney_statistics_bot?start=",
        }
    )
    result = r.json()
    print(result)
    return result


def get_balance(user_data):
    r = requests.post("https://api.zenmoney.ru/v8/diff/", json={
        "currentClientTimestamp": int(time()),
        "serverTimestamp": 0
    }, headers={
        "Authorization": "Bearer {}".format(user_data["access_token"])
    })
    result = r.text

    print(result)

    if result != "Unathorized":
        data = json.loads(result)

        balance_per_instrument = defaultdict(float)

        for acc in data["account"]:
            if acc["inBalance"]:
                balance_per_instrument[acc["instrument"]] += acc["balance"]

        result = []
        for k, v in balance_per_instrument.items():
            result.append("{} {}".format(
                v,
                next(filter(lambda x: x["id"] == k, data["instrument"]))["symbol"],
            ))

        return "\n".join(result)
    else:
        return "fail"


def get_diff(user_data):
    r = requests.get("https://api.zenmoney.ru/v8/diff/", {
        "access_token": user_data["access_token"]
    })
    result = r.text
    print(result)


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_data = get_auth_data()

    unique_code = extract_unique_code(message.text)

    print(unique_code)

    if unique_code:
        auth_token = get_token(unique_code)

        if "error" in auth_token:
            bot.reply_to(message, "Всё пиздец", reply_markup=ReplyKeyboardRemove())
            return

        user_data[message.chat.id] = auth_token
        write_auth_data(user_data)
        bot.reply_to(message, "Добро пожаловать!", reply_markup=ReplyKeyboardRemove())
        balance = get_balance(auth_token)
        bot.reply_to(message, balance)
    else:
        auth_url = get_auth_url()

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(text="Войти", url=auth_url)
        )

        bot.reply_to(message, "Пожалуйста, авторизуйтесь", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    bot.reply_to(message, "PONG")


bot.polling()


# https://api.zenmoney.ru/oauth2/authorize/?response_type=code&client_id=g5009eef688def248ad91fc7287387&redirect_uri=https://t.me/zenmoney_statistics_bot
