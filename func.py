import datetime
import telebot
from bs4 import BeautifulSoup as bs

import config
import db
import json
import menu
import random

import requests

from pay import Wrapper
from request import url, post, btc_url, btc_cash_url

bot = telebot.TeleBot(config.BOT_TOKEN)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def first_start(user_id, name, code):
    conn, cursor = db.connect()
    if code == '':
        code = 0
    row = cursor.execute('select * from users where "user_id"=?', (user_id,)).fetchall()
    if len(row) == 0:
        cursor.execute('insert into users values (?,?,?,?,?,0,0,0)',
                       (user_id, name, datetime.datetime.now(), user_id, code,))
        conn.commit()
    if db.get_value('value', base='adm_id') is None:
        cursor.execute('insert into adm_id values(?)', (user_id,))
        conn.commit()
    bot_name = bot.get_me().username
    cursor.execute('update config set bot_url=?', (bot_name,))
    conn.commit()
    cursor.close()
    conn.close()


def get_user(user_id):
    conn, cursor = db.connect()
    user = cursor.execute('select * from users where user_id=?', (user_id,)).fetchone()
    cursor.close()
    conn.close()
    return user


def qiwi_money(user_id):
    conn, cursor = db.connect()
    code = random.randint(1111111111, 9999999999)

    numbers = db.get_values('number', base='qiwi')
    number = random.choice(numbers)[0]
    msg = cursor.execute('select qiwi_text from config').fetchone()[0].format(
        number=number,
        code=code,
    )
    try:
        row = cursor.execute('select * from check_qiwi where user_id=?', (user_id,)).fetchone()
        if row is not None:
            cursor.execute(f'update check_qiwi set code=?,number=? WHERE user_id = ?', (code, number, user_id))
            conn.commit()
        else:
            cursor.execute(f'insert into check_qiwi values(?,?,?)', (user_id, code, number,))
            conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()
    return msg


def check_qiwi_money(user_id):
    conn, cursor = db.connect()
    try:
        text = cursor.execute('select * from check_qiwi where user_id=?', (user_id,)).fetchone()
        number = text[2]
        token = db.get_value('token', 'number', "{}".format(number), 'qiwi')
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + token

        parameters = {'rows': '5'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(number),
            params=parameters)
        req = json.loads(h.text)
        comment = text[1]
        for j in range(len(req['data'])):
            if str(comment) == str(req['data'][j]['comment']):
                cursor.execute(f'DELETE FROM check_qiwi WHERE user_id = ?', (user_id,))
                conn.commit()

                referral_percent(user_id, float(req["data"][j]["sum"]["amount"]))
                cursor.close()
                conn.close()
                return 1, req["data"][j]["sum"]["amount"]
    except Exception as e:
        print(e)
    return 0, 0


def kuna_code(user_id):
    msg = '''━━━━━━━━━━━━━━━━━━━━\n💳 Відправте свій KUNA code в чат\n
📋 Приймається: 
💵 UAH 
━━━━━━━━━━━━━━━━━━━━

1️⃣ Через будь-який термінал EasyPay:
   • Виберіть меню → грошові перекази
   • Обираємо Kuna Code
   • Вводите свій номер телефону
   • Вносите потрібну суму + комісія
   • Отримуємо SMS з Kuna Кодом

2️⃣ Через сайт Kuna.io:
   • Швидка реєстрація через пошту
   • Заходите в свій кабінет
   • Вибираєте Активи → UAH → поповнити
   • Поповнюєте банківською картою
   • Генеруєте Kuna Code

━━━━━━━━━━━━━━━━━━━━
📝 Відправте код:'''
    return msg


def aperon_code(user_id):
    session = requests
    get_wallet_form_server = session.post(url, data=json.dumps(post))
    get_wallet = get_wallet_form_server.json()
    get_wallet_address = get_wallet['address']

    msg = '''� Поповнення балансу

📍 Ваша персональна адреса LTC для поповнення гаманця нижче

⏰ Баланс вашого гаманця буде оновлено після підтвердження мережі (зазвичай протягом години)

⚠️ Адреса одноразова, не використовуйте її повторно!

━━━━━━━━━━━━━━━━━━━━━━━━'''

    db.post_wallet_ltc_address(user_id, get_wallet_address)

    return msg, get_wallet_address


def check_aperon_money(user_id):
    wallet = db.get_payment_ltc_address(user_id)
    wallet_address = db.get_wallet_form_bot('wallet_ltc')
    print("Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}".format(user_id, wallet[1]))
    try:
        session = requests
        get = session.get('https://apirone.com/api/v2/wallets/{}/addresses/{}' \
                          .format(db.get_wallet_form_bot('wallet_ltc')[0], wallet[1]))
        resp = get.json()
        jstr = resp['balance']
        balance_amount = jstr['available']
        a = """
        ---------Информация кошелька!----------
        ID пользователя: {}
        Кошелек: {}
        Общий баланс кошелька: {}
        Доступные для вывода средства: {}
        -------------------------------------------
        """.format(user_id, wallet[1], jstr['total'], jstr['available'])
        print(a)
        request = requests.get("https://apirone.com/api/v2/ticker?currency=ltc")
        ltc_curse = request.json()
        get_curser_btc = ltc_curse["usd"]
        get_avail_btc = get_curser_btc / 100000000
        payment_request = balance_amount * get_avail_btc
        if balance_amount > 0:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Успешно".format(user_id,
                                                                                                              wallet[
                                                                                                                  1]))
            return 1, payment_request
        else:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Отказано".format(user_id,
                                                                                                               wallet[
                                                                                                                   1]))

    except Exception as e:
        print(e)

    return 0, 0


def bitcoin(user_id):
    session = requests
    get_from_server = session.post(btc_url, data=json.dumps(post))
    post_server = get_from_server.json()
    btc_address = post_server['address']
    msg = '''� Поповнення балансу

📍 Ваша персональна адреса BTC для поповнення гаманця нижче

⏰ Баланс вашого гаманця буде оновлено після підтвердження мережі (зазвичай протягом години)

⚠️ Адреса одноразова, не використовуйте її повторно!

━━━━━━━━━━━━━━━━━━━━━━━━'''
    db.post_wallet_address(user_id, address=btc_address)
    return msg, btc_address


def check_payment_bitcoin(user_id):
    wallet = db.get_payment_btc_address(user_id)
    btc = db.get_wallet_form_bot('wallet_btc')
    print("Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}".format(user_id, wallet[1]))
    try:
        session = requests
        get = session.get('https://apirone.com/api/v2/wallets/{}/addresses/{}' \
                          .format(btc[0], wallet[1]))
        resp = get.json()
        table = resp['balance']
        table_value_available = table['available']
        a = """
        ---------Информация кошелька!----------
        ID пользователя: {}
        Кошелек: {}
        Общий баланс кошелька: {}
        Доступные для вывода средства: {}
        -------------------------------------------
        """.format(user_id, wallet[1], table['total'], table_value_available)
        print(a)
        request = requests.get("https://apirone.com/api/v2/ticker?currency=btc")
        ltc_curse = request.json()
        get_curser_btc = ltc_curse["usd"]
        get_avail_btc = get_curser_btc / 100000000
        payment_request = table_value_available * get_avail_btc
        if payment_request > 0:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Успешно".format(user_id,
                                                                                                              wallet))
            return 1, payment_request
        else:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Отказано".format(user_id,
                                                                                                               wallet))
    except Exception as e:
        print(e)

    return 0, 0


def bitcoin_cash(user_id):
    session = requests
    get_from_server = session.post(btc_cash_url, data=json.dumps(post))
    post_server = get_from_server.json()
    bch_address = post_server['address']
    msg = '''� Поповнення балансу

📍 Ваша персональна адреса BCH для поповнення гаманця нижче

⏰ Баланс вашого гаманця буде оновлено після підтвердження мережі (зазвичай протягом години)

⚠️ Адреса одноразова, не використовуйте її повторно!

━━━━━━━━━━━━━━━━━━━━━━━━'''
    db.post_wallet_bch_address(user_id, address=bch_address)
    return msg, bch_address


def check_payment_bitcoin_cash(user_id):
    wallet = db.get_payment_bch_address(user_id)
    bch_admin_wallet = db.get_wallet_form_bot('wallet_bch')
    print("Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}".format(user_id, wallet[0]))
    try:
        session = requests
        get = session.get('https://apirone.com/api/v2/wallets/{}/addresses/{}' \
                          .format(bch_admin_wallet[0], wallet[0]))
        print(bch_admin_wallet[0], wallet[0])
        resp = get.json()
        table = resp['balance']
        table_value_available = table['available']
        print(table_value_available)
        a = """
        ---------Информация кошелька!----------
        ID пользователя: {}
        Кошелек: {}
        Общий баланс кошелька: {}
        Доступные для вывода средства: {}
        -------------------------------------------
        """.format(user_id, wallet, table['total'], table_value_available)
        print(a)
        request = requests.get("https://apirone.com/api/v2/ticker?currency=bch")
        ltc_curse = request.json()
        get_curser_btc = ltc_curse["usd"]
        get_avail_btc = get_curser_btc / 100000000
        payment_request = table_value_available * get_avail_btc
        if payment_request > 0:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Успешно".format(user_id,
                                                                                                              wallet))
            return 1, payment_request
        else:
            print(
                "Пользователь с ID: {}, Создал TASK проверки баланса кошелька: {}, Результат: Отказано".format(user_id,
                                                                                                               wallet))
    except Exception as e:
        print(e)

    return 0, 0


def ref_cur(cur_sum, name):
    address = db.get_values("user_id_pony", where="product_id", are=name, base="address")
    end_balance_for_pony = 5 * cur_sum / 100
    add_balance(address[0][0], end_balance_for_pony)



def check_kuna_code(code):
    kuna = Wrapper(config.KUNA_PUBLIC, config.KUNA_PRIVATE)
    try:
        print("check_k-code_funcs")
        response = kuna.load(code)
        print(response)
        if response["currency"] == "uah":
            return 1, response['amount']
        else:
            return 0, 0
    except Exception as e:
        print(e)

    return 0, 0


def global24_check(user_id):
    conn, cursor = db.connect()
    check_data = list(cursor.execute("select * from easypay_global_check where user_id=?", (user_id,)).fetchone())

    cursor.execute("select * from check_id")
    id_check = cursor.fetchall()
    massive = []
    for i in id_check:
        for j in i:
            massive.append(j)

    if int(check_data[1]) not in massive:
        session = requests.Session()
        url = 'https://www.city24.ua/ua/payment/check?payId='
        test = session.get(url + str(check_data[1]))
        if '<Response [200]>' == str(test):
            try:
                soup = bs(test.text)
                if str(check_data[1]) in str(soup.body.check.text) and 'Зараховано: ' + str(check_data[2]) in str(
                        soup.body.check.text):
                    for i in db.get_values('value', base='global24'):
                        if str(i[0]) in str(soup.body.check.text):
                            print("Успешная оплата!")
                            cursor.execute("insert into check_id values(?)", (check_data[1],))
                            conn.commit()
                            referral_percent(user_id, check_data[2])
                            cursor.close()
                            conn.close()
                            return 1, check_data[2]
                        else:
                            print("Что-то не так")
                    return 0, 0
            except:
                print("Ошибка")
                return 0, 0
            else:
                print("успешный ответ. но что-то не нашел")
                return 0, 0
        else:
            print("Нет ответа от сервера")
            return 0, 0
    else:
        print("ID квитанции уже есть в базе!!!")
        return 0, 0


def easypay_check(user_id):
    conn, cursor = db.connect()
    check_data = list(cursor.execute("select * from easypay_global_check where user_id=?", (user_id,)).fetchone())

    id_check = list(cursor.execute("select * from check_id").fetchall())
    massive = []
    for i in id_check:
        for j in i:
            massive.append(j)
    if int(check_data[1]) not in massive:
        base_url = 'https://api.easypay.ua/api/payment/getReceipt'
        data = {'receiptId': check_data[1], 'amount': check_data[2]}
        headers = {'accept': 'text/html'}
        response = requests.get(base_url, data, headers=headers)
        response.encoding = 'utf-8'
        full_status = response.text
        if '{"error":{"errorCode"' in full_status:
            print("Нет ответа от сервера")
            return 0, 0
        elif '<Response [200]>' == str(response):
            if str(check_data[1]) in full_status and str(check_data[2]) in full_status:
                for i in db.get_values('value', base='easypay'):
                    if str(i[0]) in full_status:
                        print("Успешная оплата!")
                        cursor.execute("insert into check_id values(?)", (check_data[1],))
                        conn.commit()
                        referral_percent(user_id, check_data[2])
                        return 1, check_data[2]
                    else:
                        print('Опять что-то не так с оплатой.')
                return 0, 0
            else:
                print("успешный ответ. но что-то не нашел")
                return 0, 0
        for i in db.get_values('value', base='easypay'):
            if f'EasyPay - електронних грошей {i[0]}' in full_status or f"EasyPay - электронных денег {i[0]}" in full_status:
                print("Оплатили!!!!")
                cursor.execute("insert into check_id values(?)", (check_data[1],))
                conn.commit()
                referral_percent(user_id, check_data[2])
                return 1, check_data[2]
            else:
                pass
            return 0, 0
        else:
            print("Что-то не так")
            return 0, 0
    else:
        return 0, 0


def referral_percent(user_id, sum):
    conn, cursor = db.connect()
    try:
        invite_by = cursor.execute('select invite_by from users where user_id=?', (user_id,)).fetchone()
        if invite_by[0] != '0':
            ref_id = list(cursor.execute('select user_id from users where ref_code = ?',
                                         (invite_by[0],)).fetchone())
            money_to_add = float(sum) / 100 * db.get_value('referral_percent')
            add_balance(ref_id[0], money_to_add)
            cursor.execute(f'update users set ref_earn=ref_earn+{money_to_add} where user_id=?',
                           (ref_id[0],))
            conn.commit()
            cursor.close()
            conn.close()
    except:
        print('Что-то не так с добавлением баланса рефералу')


def add_balance(user_id, sum):
    conn, cursor = db.connect()
    try:
        cursor.execute(f'update users set balance=balance+{sum} where user_id=?', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        print('ошибка добавления баланса!')


def remove_balance(user_id, sum, discount=0.0):
    conn, cursor = db.connect()
    try:
        balance = float(db.get_value('balance', 'user_id', user_id, 'users'))
        balance = balance - sum + sum / 100 * float(discount)
        cursor.execute(f'update users set balance=? where user_id=?', (balance, user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)


def add_discount(user_id, count):
    conn, cursor = db.connect()
    try:
        discount = list(cursor.execute('select discount from users where user_id = ?', (user_id,)).fetchone())
        discount[0] += float(count)
        if int(discount[0]) > 100:
            discount[0] = 100
        cursor.execute('update users set discount=? where user_id=?', (discount[0], user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass


def write_to_adm(user_id, sum, type='balance'):
    if type != 'balance':
        msg = f'✅ Успішна активація промокоду\n📍 Від <a href="tg://user?id={user_id}">Користувача</a>\n💳 Отримано: {sum} USD'
    else:
        msg = f'✅ Успішне поповнення балансу\n📍 Від <a href="tg://user?id={user_id}">Користувача</a>\n💳 Сума = {sum} {db.get_value("money_value")}'
    try:
        for i in db.get_values('value', base='adm_id'):
            bot.send_message(chat_id=config.CHAT_GROUP_ID, text=msg, parse_mode='html')
    except:
        pass
    try:
        bot.send_message(chat_id=db.get_value('value', base='channel_id'), text=msg, parse_mode='html')
    except:
        pass

def send_order_log(user_id, username, phone, product_name, quantity, price):
    user_info = get_user(user_id)
    total_price = float(price) * int(quantity)
    
    msg = f"""📞 ЗАЯВКА НА ЗАМОВЛЕННЯ

👤 Замовник: {user_info[1] if user_info else 'Невідомо'}
📱 Телефон: {phone}
🔗 Telegram: @{username if username else 'відсутній'}
🆔 ID: {user_id}

🛒 Товар: {product_name}
📦 Кількість: {quantity}
💰 Вартість: {total_price} {db.get_value("money_value")}

📞 Дія: Клієнт повинен зателефонувати"""
    
    try:
        bot.send_message(chat_id=config.CHAT_GROUP_ID, text=msg)
    except:
        pass

def send_full_order_log(user_id, username, phone, cart):
    """Отправляет заказ со всеми позициями в одном сообщении"""
    user_info = get_user(user_id)
    
    if len(cart.items) == 1:
        # Если только одна позиция, используем старую функцию
        for product_id, item in cart.items.items():
            send_order_log(user_id, username, phone, item['name'], item['count'], item['price'])
    else:
        # Если несколько позиций, отправляем одним сообщением
        msg = f"""📞 ЗАЯВКА НА ЗАМОВЛЕННЯ

👤 Замовник: {user_info[1] if user_info else 'Невідомо'}
📱 Телефон: {phone}
🔗 Telegram: @{username if username else 'відсутній'}
🆔 ID: {user_id}

🛒 ТОВАРИ В ЗАМОВЛЕННІ:
"""
        
        total_order_price = 0
        for product_id, item in cart.items.items():
            item_total = float(item['price']) * int(item['count'])
            total_order_price += item_total
            msg += f"  📦 {item['name']} - {item['count']} шт. × {item['price']} = {item_total} {db.get_value('money_value')}\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━
💰 ЗАГАЛЬНА ВАРТІСТЬ: {total_order_price} {db.get_value("money_value")}

📞 Дія: Клієнт повинен зателефонувати"""
        
        try:
            bot.send_message(chat_id=config.CHAT_GROUP_ID, text=msg)
        except:
            pass

def remove_product_from_stock(product_id, quantity):
    """Удаляет товары из базы данных после оформления заказа"""
    conn, cursor = db.connect()
    try:
        addresses = cursor.execute('SELECT link, person_id FROM address WHERE product_id = ? LIMIT ?', 
                                 (product_id, quantity)).fetchall()
        
        for address in addresses:
            cursor.execute('DELETE FROM address WHERE person_id = ? AND product_id = ?', 
                         (address[1], product_id))
        
        conn.commit()
        print(f"Удалено {len(addresses)} единиц товара {product_id} из базы данных")
    except Exception as e:
        print(f"Ошибка при удалении товара из базы: {e}")
    finally:
        cursor.close()
        conn.close()

def print_good_payment(message_id, chat_id, call_id, sum):
    bot.answer_callback_query(callback_query_id=call_id,
                              text=f'✅ Вы успешно пополнили баланс на {sum} {db.get_value("money_value")}')
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=f'✅Успешное пополнение баланса на {sum} {db.get_value("money_value")}',
                              reply_markup=menu.main_menu)
    except:
        pass


def promo(message):
    conn, cursor = db.connect()
    try:
        text = message.text
        bonus = db.get_value('bonus', 'promo', text, 'promo_code')
        if bonus is not None:
            if '%' in bonus:
                add_discount(message.chat.id, bonus.replace('%', ''))
                bot.send_message(chat_id=message.chat.id,
                                 text=f'✅ Ви активували ваучер і отримали {bonus} знижки!',
                                 reply_markup=menu.main_menu)
            else:
                add_balance(message.chat.id, bonus)
                bot.send_message(chat_id=message.chat.id,
                                 text=f'✅ Ви активували ваучер і отримали {bonus} {db.get_value("money_value")}',
                                 reply_markup=menu.main_menu)
            cursor.execute('delete from promo_code where promo=?', (text,))
            conn.commit()
            write_to_adm(message.chat.id, bonus, 'promo')
        else:
            bot.send_message(chat_id=message.chat.id, text='❌ Такого ваучера не існує...',
                             reply_markup=menu.main_menu)
    except:
        bot.send_message(chat_id=message.chat.id, text='📛Такого ваучера не существует...',
                         reply_markup=menu.main_menu)
    cursor.close()
    conn.close()


def change_ref_code(message):
    conn, cursor = db.connect()
    link = message.text
    old_link = db.get_value('ref_code', 'user_id', message.chat.id, 'users')
    user_id = message.chat.id
    text = list(cursor.execute('select * from users where ref_code = ?', (link,)).fetchall())
    if len(text) == 0:
        cursor.execute('update users set invite_by=? where invite_by=?', (link, old_link,))
        conn.commit()
        cursor.execute('update users set ref_code=? where user_id=?', (link, user_id,))
        conn.commit()
        bot.send_message(chat_id=user_id, text='✔Вы успешно изменили свою реферальную ссылку!',
                         reply_markup=menu.main_menu)
        cursor.close()
        conn.close()
    else:
        bot.send_message(chat_id=user_id, text='❗Такая ссылка уже занята! Попробуйте другую!',
                         reply_markup=menu.ref_system)


def easypay_first(message):
    conn, cursor = db.connect()
    easy_data = message.text
    if " " in easy_data and "  " not in easy_data:
        easy_data = easy_data.split(" ")
        if easy_data[0].isdigit():
            receiptId = easy_data[0]
            amount = easy_data[1]
            bot.send_message(chat_id=message.chat.id, text=f"ID перевода = {receiptId}, Сумма = {amount}",
                             reply_markup=menu.easypay_check)
            try:
                cursor.execute("delete from easypay_global_check where user_id=?",
                               (message.chat.id,))
                conn.commit()
            except:
                pass
            cursor.execute("insert into easypay_global_check values(?,?,?)",
                           (message.chat.id, receiptId, amount,))
            conn.commit()
            cursor.close()
            conn.close()

        else:
            bot.send_message(chat_id=message.chat.id, text="❌Неверный ввод! Повторите попытку",
                             reply_markup=menu.main_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text="❌Неверный ввод! Повторите попытку",
                         reply_markup=menu.main_menu)


def global24_first(message):
    conn, cursor = db.connect()
    easy_data = message.text
    if " " in easy_data and "  " not in easy_data:
        easy_data = easy_data.split(" ")
        if easy_data[0].isdigit():
            receiptId = easy_data[0]
            amount = easy_data[1]
            bot.send_message(chat_id=message.chat.id, text=f"ID перевода = {receiptId}, Сумма = {amount}",
                             reply_markup=menu.global24_check)
            try:
                cursor.execute("delete from easypay_global_check where user_id=?",
                               (message.chat.id,))
                conn.commit()
            except:
                pass
            cursor.execute("insert into easypay_global_check values(?,?,?)",
                           (message.chat.id, receiptId, amount,))
            conn.commit()
            cursor.close()
            conn.close()

        else:
            bot.send_message(chat_id=message.chat.id, text="❌Неверный ввод! Повторите попытку",
                             reply_markup=menu.main_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text="❌Неверный ввод! Повторите попытку",
                         reply_markup=menu.main_menu)


def add_easy(message):
    number = message.text
    db.add_replenish(number=number)
    bot.send_message(chat_id=message.chat.id, text='✅Добавил EasyPay',
                     reply_markup=menu.add_remove_payments)


def add_global(message):
    number = message.text
    db.add_replenish('global24', number=number)
    bot.send_message(chat_id=message.chat.id, text='✅Добавил GlobalMoney',
                     reply_markup=menu.add_remove_payments)


def remove_qiwi(message):
    number = message.text
    db.remove_replanish('qiwi', number)
    bot.send_message(chat_id=message.chat.id, text=f'✅Удалил кошелек {number}',
                     reply_markup=menu.remove_replenish_number)


def remove_easy(message):
    number = message.text
    db.remove_replanish('easypay', number)
    bot.send_message(chat_id=message.chat.id, text=f'✅Удалил кошелек {number}',
                     reply_markup=menu.remove_replenish_number)


def remove_global(message):
    number = message.text
    db.remove_replanish('global24', number)
    bot.send_message(chat_id=message.chat.id, text=f'✅Удалил кошелек {number}',
                     reply_markup=menu.remove_replenish_number)


class Add_promo():
    def __init__(self):
        self.promo = None
        self.bonus = None


promocode = Add_promo()


def add_promo1(message):
    promocode.promo = message.text
    values = db.get_values('promo', 'promo', '"{}"'.format(message.text), 'promo_code')
    if len(values) > 0:
        return bot.send_message(message.chat.id, text='❗Такой ваучер уже существует...', reply_markup=menu.adm_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text='▫Выберите тип ваучера: ', reply_markup=menu.promo_type)


def change_ltc(message):
    db.change_ltc_bot(message.text)
    bot.send_message(chat_id=message.chat.id, text="✅Wallet id, успешно изменен!", reply_markup=menu.adm_menu)


def change_btc(message):
    db.change_btc_bot(message.text)
    bot.send_message(chat_id=message.chat.id, text="✅Wallet id, успешно изменен!", reply_markup=menu.adm_menu)


def change_bch(message):
    db.change_bch_bot(message.text)
    bot.send_message(chat_id=message.chat.id, text="✅Wallet id, успешно изменен!", reply_markup=menu.adm_menu)


def add_promo2(message):
    if message.text.isdigit() or '%' in message.text:
        promocode.bonus = message.text
    else:
        return bot.send_message(message.chat.id, text='❗Неправильный ввод...', reply_markup=menu.adm_menu)
    try:
        db.add_promo(promocode.promo, promocode.bonus)
        bot.send_message(chat_id=message.chat.id, text=f'✅Вы добавили ваучер! \n{promocode.promo} - {promocode.bonus}',
                         reply_markup=menu.adm_menu)
    except Exception as e:
        print(e)


def add_promo_discount(message):
    if message.text.isdigit():
        promocode.bonus = message.text + '%'
    elif '%' in message.text:
        promocode.bonus = message.text
    else:
        return bot.send_message(message.chat.id, text='❗Неправильный ввод...', reply_markup=menu.adm_menu)
    try:
        db.add_promo(promocode.promo, promocode.bonus)
        bot.send_message(chat_id=message.chat.id, text=f'✅Вы добавили ваучер! \n{promocode.promo} - {promocode.bonus}',
                         reply_markup=menu.adm_menu)
    except Exception as e:
        print(e)


def is_adm(id):
    if db.get_value('value', 'value', id, 'adm_id') is not None:
        return True
    else:
        return False


def is_kur(id):
    if db.get_value('value', 'value', id, 'kur_id') is not None:
        return True
    else:
        return False


def set_balance1(message):
    text = message.text
    text = text.split(' ')
    ids = text[0]
    if text[0].isdigit() is False:
        ids = text[0].replace('@', '')
        ids = db.get_value('user_id', 'name', ids, 'users')
    if ids is None:
        bot.send_message(message.chat.id, text='❌Такого пользователя нет в базе...', reply_markup=menu.adm_menu)
    else:
        if db.get_value('*', 'user_id', ids, 'users') is not None:
            db.set_balance(ids, text[1])
            msg = bot.send_message(message.chat.id, text=f'✅Установил баланс пользователю {ids} - {text[1]}',
                                   reply_markup=menu.adm_menu)
        else:
            bot.send_message(message.chat.id, text='❌Такого пользователя нет в базе...',
                             reply_markup=menu.adm_menu)


def set_discount1(message):
    text = message.text
    text = text.split(" ")
    if int(text[1]) > 100:
        text[1] = 100
    elif int(text[1]) < 0:
        text[1] = 0
    if text[0].isdigit() is False:
        ids = text[0].replace('@', '')
        ids = db.get_value('user_id', 'name', ids, 'users')
    if ids is None:
        bot.send_message(message.chat.id, text='❌Такого пользователя нет в базе...', reply_markup=menu.adm_menu)
    else:
        if db.get_value('*', 'user_id', ids, 'users') is not None:
            db.set_discount(ids, text[1])
            bot.send_message(chat_id=message.chat.id, text=f'✅Установил скидку пользователю {ids} - {text[1]}',
                             reply_markup=menu.adm_menu)
        else:
            bot.send_message(message.chat.id, text='❌Такого пользователя нет в базе...',
                             reply_markup=menu.adm_menu)


def add_adm(message):
    id = message.text
    if id.isdigit() is False:
        id = id.replace('@', '')
        id = db.get_value('user_id', 'name', id, 'users')
    if db.get_value('*', 'user_id', id, 'users') is not None:
        db.add_adm(id)
        bot.send_message(chat_id=message.chat.id, text=f'Выдал админку пользователю {id}', reply_markup=menu.adm_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Нет такого пользователя в базе', reply_markup=menu.adm_menu)


def remove_adm(message):
    id = message.text
    if id.isdigit() is False:
        id = id.replace('@', '')
        id = db.get_value('user_id', 'name', id, 'users')
    if db.get_value('*', 'user_id', id, 'users') is not None:
        db.remove_adm(id)
        bot.send_message(chat_id=message.chat.id, text=f'Удалил админа {id}', reply_markup=menu.adm_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Нет такого пользователя в базе', reply_markup=menu.adm_menu)


def add_kur(message):
    id = message.text
    if id.isdigit() is False:
        id = id.replace('@', '')
        id = db.get_value('user_id', 'name', id, 'users')
    if db.get_value('*', 'user_id', id, 'users') is not None:
        db.add_kur(id)
        bot.send_message(chat_id=message.chat.id, text=f'Выдал курьера пользователю {id}', reply_markup=menu.adm_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Нет такого пользователя в базе', reply_markup=menu.adm_menu)


def remove_kur(message):
    id = message.text
    if id.isdigit() is False:
        id = id.replace('@', '')
        id = db.get_value('user_id', 'name', id, 'users')
    if db.get_value('*', 'user_id', id, 'users') is not None:
        db.remove_kur(id)
        bot.send_message(chat_id=message.chat.id, text=f'Удалил курьера {id}', reply_markup=menu.adm_menu)
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Нет такого пользователя в базе', reply_markup=menu.adm_menu)


def check_balance(user_id, price, discount=0.0):
    balance = float(db.get_value('balance', 'user_id', user_id, 'users'))
    price = float(price) - float(price) / 100 * float(discount)

    if balance >= price:
        return 1
    else:
        return 0


def parent_list():
    list = []
    catalog = db.get_values("*", 'parent_catalog_id', 'catalog_id', 'catalog')
    for i in catalog:
        back = "parent" + str(i[0])
        list.append(back)
    return list


def catalog_list():
    list = []
    catalog = db.get_values_long(
        'select * from catalog where catalog_id not in (select catalog_id from catalog where parent_catalog_id=catalog_id)')
    for i in catalog:
        back = 'catalog' + str(i[0])
        list.append(back)
    return list


def product_list():
    list = []
    products = db.get_values('*', base='product')
    for i in products:
        back = 'product_' + str(i[0]) + '_' + str(i[1])
        list.append(back)
    return list


def buy_product_list():
    list = []
    products = db.get_values('*', base='product')
    for i in products:
        back = 'buyproduct_' + str(i[0]) + '_' + str(i[1])
        list.append(back)
    return list


class Cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = {}
    
    def add_item(self, product_id, name, price, count=1):
        if product_id in self.items:
            self.items[product_id]['count'] += count
        else:
            self.items[product_id] = {
                'name': name,
                'price': float(price),
                'count': count
            }
    
    def remove_item(self, product_id):
        if product_id in self.items:
            del self.items[product_id]
    
    def get_total(self):
        total = 0
        for item in self.items.values():
            total += item['price'] * item['count']
        return total
    
    def get_count(self):
        return sum(item['count'] for item in self.items.values())
    
    def clear(self):
        self.items.clear()

user_carts = {}

def get_cart(user_id):
    if user_id not in user_carts:
        user_carts[user_id] = Cart(user_id)
    return user_carts[user_id]

def format_product_text(product, count):
    return f"""
🛒 <b>{product[2]}</b>

📝 <b>Опис:</b>
{product[3]}

💰 <b>Ціна:</b> {product[4]} {db.get_value("money_value")}
📦 <b>В наявності:</b> {count} шт.

━━━━━━━━━━━━━━━━━━━━━━━━
"""

def format_cart_text(cart):
    if not cart.items:
        return "🛒 <b>Ваша корзина порожня</b>\n\n🛍️ Додайте товари з каталогу!"
    
    text = "🛒 <b>Ваша корзина:</b>\n\n"
    total = 0
    
    for product_id, item in cart.items.items():
        item_total = item['price'] * item['count']
        total += item_total
        text += f"📦 <b>{item['name']}</b>\n"
        text += f"   💰 {item['price']} × {item['count']} = {item_total} {db.get_value('money_value')}\n\n"
    
    text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"💵 <b>Загальна сума: {total} {db.get_value('money_value')}</b>"
    
    return text

def send_added_to_cart_message(user_id, product_name, cart):
    total_items = cart.get_count()
    total_price = cart.get_total()
    
    msg = f"""✅ <b>Товар додано в корзину!</b>

📦 <b>{product_name}</b>

🛒 <b>У корзині:</b> {total_items} тов.
💰 <b>На суму:</b> {total_price} {db.get_value("money_value")}

🛍️ Продовжити покупки або перейти в корзину?"""
    
    try:
        bot.send_message(
            chat_id=user_id, 
            text=msg, 
            parse_mode='HTML',
            reply_markup=menu.after_add_to_cart_menu
        )
    except:
        pass

class BuyProduct():
    def __init__(self, user_id):
        self.user_id = user_id
        self.product_id = None
        self.catalog_id = None
        self.price = None
        self.count = None
        self.count_max = None
        self.name = None

    def Info(self):
        print(f'{self.user_id}\n{self.product_id}\n{self.catalog_id}\n{self.price}\n{self.count}\n{self.count_max}')


# Admin menu shop settings
def set_money_value(message):
    value = message.text
    try:
        db.update_value('money_value', value)
        bot.send_message(chat_id=message.chat.id, text=f'Теперь валюта - {value}', reply_markup=menu.shop_config)
    except:
        pass


def set_info_message(message):
    value = message.text.format()
    try:
        db.update_value('info_message', value)
        bot.send_message(chat_id=message.chat.id, text=f'Теперь описание: \n{value}', reply_markup=menu.shop_config)
    except:
        pass


def set_ref_percent(message):
    if message.text.isdigit():
        value = message.text.format()
        try:
            db.update_value('referral_percent', value)
            bot.send_message(chat_id=message.chat.id, text=f'Теперь процент: \n{value}', reply_markup=menu.shop_config)
        except:
            pass
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Неверный ввод!', reply_markup=menu.shop_config)


def add_parent_category(message, call, id):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=id)

    if db.get_value('*', 'name', message.text, 'catalog') is None:
        max = db.get_value_long('select max(catalog_id) from catalog')
        if max is None or max == '0':
            max = 0
        conn, cursor = db.connect()
        cursor.execute(f'insert into catalog values({max + 1},"{message.text}",{max + 1})')
        conn.commit()
        cursor.close()
        conn.close()
        bot.answer_callback_query(callback_query_id=call.id, text=f'Добавил категорию {message.text}\n'
                                                                  f'ID - {max + 1}', show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text=f'Такая категория уже имеется!!!',
                                  show_alert=True)


def list_add_category():
    list = []
    parent = db.get_values_long('select * from catalog where catalog_id=parent_catalog_id')
    if len(parent) > 0:
        for i in parent:
            text = '@#!$' + i[1] + '_' + str(i[2])
            list.append(text)
    return list


def add_category(message, name, id, call_id, message_id):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    conn, cursor = db.connect()
    max = int(cursor.execute('select max(catalog_id) from catalog').fetchone()[0])
    if max is None or max == '0':
        max = 0
    cursor.execute('insert into catalog values(?,?,?)', (max + 1, message.text, id))
    conn.commit()
    cursor.close()
    conn.close()
    bot.answer_callback_query(callback_query_id=call_id, text=f'Добавил категорию {message.text} в {name}!',
                              show_alert=True)


def list_add_sub_category():
    list = []
    parent = db.get_values_long('select * from catalog where catalog_id!=parent_catalog_id')
    if len(parent) > 0:
        for i in parent:
            text = '@@#@' + i[1] + '_' + str(i[0])
            list.append(text)
    return list


def add_sub_category(message, name, id, call_id, message_id):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    conn, cursor = db.connect()
    max = int(cursor.execute('select max(catalog_id) from catalog').fetchone()[0])
    if max is None or max == '0':
        max = 0
    cursor.execute('insert into catalog values(?,?,?)', (max + 1, message.text, id))
    conn.commit()
    cursor.close()
    conn.close()
    bot.answer_callback_query(callback_query_id=call_id, text=f'Добавил категорию {message.text} в {name}!',
                              show_alert=True)


def list_add_product_to_category():
    list = []
    parent = db.get_values_long('select * from catalog where catalog_id!=parent_catalog_id')
    if len(parent) > 0:
        for i in parent:
            text = '&&@#' + i[1] + '_' + str(i[0])
            list.append(text)
    return list


def list_add_product_to_category_kur():
    list = []
    parent = db.get_values_long('select * from catalog where catalog_id!=parent_catalog_id')
    if len(parent) > 0:
        for i in parent:
            text = '&&@#' + i[1] + '_' + str(i[0])
            list.append(text)
    return list


class Add_Product():
    message_id = None  # id смс для удаления
    product_id = None  # продукт айди из бд
    catalog_id = None  # айди каталога
    name = None  # название продукта
    call_id = None  # колл для смс
    descriptions = None  # описание
    cost = None  # цена


def list_of_add_product():
    list = []
    products = db.get_values('*', base='product')
    for i in products:
        back = '~~#@' + i[2] + '_' + str(i[0])
        list.append(back)

    return list


class Add_Product_kur():
    message_id = None  # id смс для удаления
    product_id = None  # продукт айди из бд
    catalog_id = None  # айди каталога
    name = None  # название продукта
    call_id = None  # колл для смс
    descriptions = None  # описание
    cost = None  # цена


def list_of_add_product_kur():
    list = []
    products = db.get_values('*', base='product')
    for i in products:
        back = '~~#@' + i[2] + '_' + str(i[0])
        list.append(back)

    return list


def add_product(message, id):
    conn, cursor = db.connect()
    max = int(db.get_value_long('select max(person_id) from address'))
    if max is None or max == '0':
        max = 1

    for tovar in message.text.split("\n"):
        if tovar != '':
            max += 1
            cursor.execute('insert into address values(?,?,?,?)', (tovar, id, max, message.chat.id))

    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(chat_id=message.chat.id, text='Добавил ссылку к товару!', reply_markup=menu.adm_menu)
    bot.send_message(chat_id=config.CHAT_GROUP_ID, text='✅ Курьер успешно добавил содержимое к товару')

def del_category(message):
    conn, cursor = db.connect()
    try:
        id = message.text
        categories = db.get_values("catalog_id", base="catalog")
        if id in categories:
            cursor.execute('delete from catalog where catalog_id = ?', (id,))
            conn.commit()
            bot.send_message(message.chat.id, "Удалено!", reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "id категории не найдено!!!", reply_to_message_id=message.message_id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def list_del_category():
    return ['@dc' + str(i[0]) for i in db.get_categories_subcategories()]


def list_del_product():
    return ['@dp' + str(i[0]) for i in db.get_products()]