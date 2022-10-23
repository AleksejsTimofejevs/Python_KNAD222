import telebot
import re
import pymorphy2
import FinNews as fn
import datetime as dt
import xlsxwriter
import shutil
import os
import time
from pandas_datareader import data as pdr
from requests import get
from lxml import html
from wordcloud import WordCloud
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# Рандомный мем
def random_meme():
    try:
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')

        driverLocation = os.getcwd() + '/chromedriver'
        driver = webdriver.Chrome(driverLocation, options=chrome_options)
        driver.get('https://imgflip.com/i/40in6j')

        folder = driver.find_element(By.XPATH, "//div[@class='nav img-flip']")
        folder.click()
        time.sleep(1)
        folder = driver.find_element(By.XPATH, "//img[@id='im']")
        get_url = folder.get_attribute('src')
        driver.close()

        file_name = 'random_meme.png'
        res = get(get_url, stream = True)

        if res.status_code == 200:
            with open(file_name,'wb') as f:
                shutil.copyfileobj(res.raw, f)
    except:
        file_name = None
    return file_name

# Последние котировки ключевых индексов
def indicies(ticker):
    end = dt.datetime.now()
    start = end - dt.timedelta(days=365)
    data = pdr.get_data_yahoo(ticker, start, end)
    data['Return'] = (data['Close'] - data['Open']) / data['Open']
    current_value = round(data['Adj Close'][-1], 5)
    average_daily_return = round(sum(data['Return']) / len(data['Return']), 5)
    average_daily_risk = round(data['Return'].std(), 5)
    return current_value, average_daily_return, average_daily_risk


def financial_statement(ticker):
    url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=120&apikey=501470113436c661b129ea68ba5fd3d9'
    r = get(url)
    r = dict(r.json()[0])
    financial_statement_workbook = xlsxwriter.Workbook(f'Financial statement {r["symbol"]}.xlsx')
    worksheet = financial_statement_workbook.add_worksheet(f'Financial results {r["date"]}')

    j = 0
    for k, v in r.items():
        worksheet.write(j, 0, k)
        worksheet.write(j, 1, v)
        j += 1

    financial_statement_workbook.close()


# Рандомная финансовая новость
def news_usa():
    result = []
    cnbc_feed = fn.CNBC(topics=['finance'])
    for i in cnbc_feed.get_news():
        result.append(i['links'][0]['href'])
    return result[randint(0, len(result))]

# Функция получения текста последних новостей с сайта лета.ру через XPath
def news_rf():
    info = {}
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
    lenta_link = 'https://lenta.ru/'
    response = get(lenta_link, headers=header)

    root = html.fromstring(response.text)
    result = []
    items = root.xpath('//div[@class="last24"]//a/@href')

    # Обработка каждой отедльной новости, создание словарей из (Имя источника, Имя новости, Ссылка, Дата и Основной текст новости)
    for item in items:
        response_sub = get(lenta_link + item, headers=header)

        if response_sub.ok:
            root_sub = html.fromstring(response_sub.text)
            body = root_sub.xpath("//div[@class='topic-body__content']//p//text()")
        info['body'] = body

        # Добавление словаря по каждой отдельной новости в список словарей
        result.append(info)
    return result

def mood_rf():
    # Создание полотна текста из словаря новостей
    all_news = news_rf()
    day_text = []
    for i in all_news:
        day_text.append(str(i.get('body')).replace("',", '').replace("'", '').replace("[", '').replace("]", ''))

    day_text = str(day_text).replace("\'", '').replace("[", '').replace("]", '')

    # Обработка "полотна" текста
    morph = pymorphy2.MorphAnalyzer()
    word_list = []
    for i in re.findall(r'\b\S+\b', day_text):
        if morph.parse(i)[0].tag.POS in ('NOUN', 'ADJF', 'ADJS', 'INFN'):
            word_list.append(morph.parse(i)[0].normal_form)

    text_mass = str(word_list).replace("'", "").replace(",", "").replace("[", "").replace("]", "")

    # Визуализация
    wc = WordCloud(background_color='white', height=600, width=400)
    wc.generate(text_mass)
    wc.to_file('mood_rf.png')

# Сам бот
bot = telebot.TeleBot('5644634075:AAFeJpc_HDuTu2nVPE8ja4xA9OAg0eRoeD0')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Повестка дня в РФ"), telebot.types.KeyboardButton("Ключевые индексы"))
    markup.add(telebot.types.KeyboardButton("Финансовые новости"), telebot.types.KeyboardButton("Отчетность по компании"))
    markup.add(telebot.types.KeyboardButton("Рандомный мем"))


    if message.from_user.first_name == None:
        name = 'Неизвестный пользователь'
    else:
        name = message.from_user.first_name

    bot.send_message(message.chat.id, f'Привет, {name}! Выбери команду.', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == "Повестка дня в РФ":
        bot.send_message(message.chat.id, 'Сбор информации займет какое-то время...')
        mood_rf()
        photo = open("mood_rf.png", 'rb')
        bot.send_photo(message.chat.id, photo)
    elif message.text == "Финансовые новости":
        result = news_usa()
        bot.send_message(message.chat.id, result)
    elif message.text == "Ключевые индексы":
        current_value_1, average_daily_return_1, average_daily_risk_1 = indicies("^GSPC")
        current_value, average_daily_return, average_daily_risk = indicies("^DJI")
        bot.send_message(message.chat.id, f"На текущий момент индекс S&P500 находится на отметке {current_value_1} пунктов. \n"
                                          f"За последний год S&P500 показал среднюю дневную доходность {average_daily_return_1*100} % годовых. \n"
                                          f"Дневное среднеквадратическое отклонение (риск) составило {average_daily_risk_1*100} %. \n \n"
                                          f"На текущий момент индекс Dow Jones Industrial Average находится на отметке {current_value} пунктов. \n"
                                          f"За последний год Dow Jones Industrial Average показал среднюю дневную доходность {average_daily_return*100} % годовых. \n"
                                          f"Дневное среднеквадратическое отклонение (риск) составило {average_daily_risk*100} %.")
    elif message.text == "Отчетность по компании":
        button1 = telebot.types.InlineKeyboardButton(text='Apple', callback_data='Apple_stock')
        button2 = telebot.types.InlineKeyboardButton(text='Google', callback_data='Google_stock')
        keyboard_inline = telebot.types.InlineKeyboardMarkup().add(button1, button2)
        bot.send_message(message.chat.id, 'Выберите компанию:', reply_markup=keyboard_inline)
    elif message.text == "Рандомный мем":
        meme = random_meme()
        if meme != None:
            photo = open(meme, 'rb')
            bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, "Неудалось создать мем, попробуйте еще раз!")
        pass
    else:
        bot.send_message(message.chat.id, "Введите другую команду!")



@bot.callback_query_handler(func=lambda call: True)
def financial_analysis(call):
    if call.data == 'Apple_stock':
        financial_statement('AAPL')
        statement = open("Financial statement AAPL.xlsx", 'rb')
        bot.send_document(call.message.chat.id, statement)
    elif call.data == 'Google_stock':
        financial_statement('GOOG')
        statement = open("Financial statement GOOG.xlsx", 'rb')
        bot.send_document(call.message.chat.id, statement)
    bot.answer_callback_query(callback_query_id=call.id)


bot.infinity_polling()