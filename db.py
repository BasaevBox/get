import sqlite3, datetime, time


def connect():
    conn = sqlite3.connect('stat.db', check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor


def db():
    conn, cursor = connect()
    try:
        cursor.execute(
            "create table users ('user_id' integer,'name' text,'date' text,'ref_code' text,'invite_by' text,'balance' text,'discount' integer,'ref_earn' text)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table check_qiwi ('user_id' integer,'code' integer,number text)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table btc_address ('user_id' integer default 1,'address' text default 'qwe')")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table ponyexp ('user_id' integer,'address' text)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table history ('user_id' integer,'message_history' integer )")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table wallet_ltc ('wallet_id' integer, 'wallet_address' text )")
        cursor.execute("insert into wallet_ltc values(?, ?)", (1, "qweqwe"))
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table wallet_btc ('wallet_id' integer, 'wallet_address' text)")
        cursor.execute("insert into wallet_btc values(?, ?)", (1, "qweqwe"))
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table wallet_bch ('wallet_id' integer, 'wallet_address' text)")
        cursor.execute("insert into wallet_bch values(?, ?)", (1, "qweqwe"))
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table bch_address ('user_id' integer,'address' text)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table ltc_address ('user_id' integer,'address' text)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute(
            """create table easypay_global_check (user_id integer,receiptId integer,amount integer)""")
        conn.commit()
        cursor.execute("insert into easypay_global_check values(1111,1,1)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("""create table check_id (id integer)""")
        conn.commit()
        cursor.execute("insert into check_id values(1111)")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("""create table promo_code (promo text,bonus text)""")
        conn.commit()
    except:
        pass
    try:
        cursor.execute("create table buy_log (user_id integer,date text,product text")
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            'create table catalog (catalog_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,name text not null,parent_catalog_id integer)')
        conn.commit()
        cursor.execute(
            'create table product (product_id integer not null PRIMARY KEY AUTOINCREMENT,catalog_id integer not null,name text not null,descriptions text,cost NUMERIC)')
        conn.commit()
        cursor.execute('create table address (link text,product_id integer,person_id integer, user_id_pony)')
        conn.commit()
        cursor.execute('insert into address values("test",0,0, 0)')
        conn.commit()
    except Exception as e:
        print(e)
    try:
        qiwi_text = '⚠️ Пополните баланс QIWI:\n\n📱 Номер:  {number}\n💬 Коментарий:  {code}\n💲 Сумма  от 1 до 15000'
        easypay_text = '💸Пополнение баланса\n\n⚠️Оплата EasyPay\n\n👉Номер кошелька: {number}\n\n👉Отправьте в чат ID перевода и сумму платежа как на фото\n https://ibb.co/RSHhTjm \n'
        global24_text = '💸Пополнение баланса\n\n⚠️Оплата GlobalMoney\n\n👉Номер кошелька: {number}\n\n👉Отправьте в чат ID перевода и сумму платежа как на фото\n https://ibb.co/RSHhTjm \n'
        apirone_ltc = '💸Пополнение баланса\n\n⚠️Оплата GlobalMoney\n\n👉Номер кошелька: {number}\n\n👉Отправьте в чат ID перевода и сумму платежа как на фото\n https://ibb.co/RSHhTjm \n'
        info_message = """📎 Информация - Кто мы и чем занимаемся\n\n🟧 (Название магазина)\n\n➖➖➖➖➖➖➖➖\n♻️ Детальное описание (Тут пишем все о нашем прекрасном магазине)\n➖➖➖➖➖➖➖➖\n\n📗 Оставляем контакты тут"""

        cursor.execute("""create table config (bot_url text,money_value text,referral_percent integer,
        info_message text,need_global24 integer,need_qiwi integer,need_kuna integer,need_ltc integer,need_btc integer,need_btc_c integer,need_easypay integer,need_promo integer,
        qiwi_text text,easypay_text text,global24_text text)""")
        conn.commit()

        cursor.execute('insert into config values(0,"UAH",5,?,1,1,1,1,1,1,1,1,?,?,?)',
                       (info_message, qiwi_text, easypay_text, global24_text,))
        conn.commit()
    except:
        pass
    try:
        cursor.execute("""create table adm_id (value integer)""")
        conn.commit()
        cursor.execute('create table kur_id (value integer)')
        conn.commit()
        cursor.execute('create table channel_id (value text)')
        conn.commit()
        cursor.execute('create table qiwi (number text,token text)')
        conn.commit()
        cursor.execute('create table easypay (value integer)')
        conn.commit()
        cursor.execute('create table global24 (value integer)')
        conn.commit()
    except:
        pass
    try:
        cursor.execute('create table purchases (user_id integer,date text,product text)')
        conn.commit()
    except:
        pass

    cursor.close()
    conn.close()


def add_adm(id):
    conn, cursor = connect()
    cursor.execute('insert into adm_id values(?)', (id,))
    conn.commit()
    cursor.close()
    conn.close()


def remove_adm(id):
    conn, cursor = connect()
    try:
        cursor.execute('delete from adm_id where value=?', (id,))
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def add_kur(id):
    conn, cursor = connect()
    cursor.execute('insert into kur_id values(?)', (id,))
    conn.commit()
    cursor.close()
    conn.close()


def remove_kur(id):
    conn, cursor = connect()
    try:
        cursor.execute('delete from kur_id where value=?', (id,))
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def get_value(text, where="none", are="none", base='config'):
    conn, cursor = connect()
    try:
        if where == "none" and are == "none":
            message = cursor.execute(f'select {text} from {base}').fetchone()[0]
            return message
        elif where != 'none' and are != 'none':
            msg = cursor.execute(f'select {text} from {base} where {where}="{are}"').fetchone()[0]
            return msg
        else:
            m = cursor.execute(text).fetchone()[0]
            return m
    except:
        pass
    cursor.close()
    conn.close()


def get_valuedata(text):
    conn, cursor = connect()
    try:
        m = cursor.execute(text).fetchone()[0]
        return m
    except:
        pass
    cursor.close()
    conn.close()


def getLastWeekCount():
    date = datetime.date
    lsdsr = "select count(*) from purchases where "
    for i in range(0, 7):
        t = date.fromtimestamp(time.time() - i * 24 * 3600).isoformat()
        str = "date like '" + t + "%'"
        if i < 6:
            str = str + " or "
        lsdsr = lsdsr + str
    return lsdsr


def get_value_long(text):
    conn, cursor = connect()
    try:
        return cursor.execute(text).fetchone()[0]
    except:
        pass
    cursor.close()
    conn.close()


def get_values(text, where="none", are="none", base='config'):
    conn, cursor = connect()
    try:
        if where == "none" and are == "none":
            message = cursor.execute(f'select {text} from {base}').fetchall()
            return message
        elif where != 'none' and are != 'none':
            return cursor.execute(f'select {text} from {base} where {where}={are}').fetchall()
        else:
            pass
    except:
        pass
    cursor.close()
    conn.close()


def get_values_long(text):
    conn, cursor = connect()
    try:
        return cursor.execute(text).fetchall()
    except:
        pass
    cursor.close()
    conn.close()


def set_ref_code(user_id, code):
    conn, cursor = connect()
    cursor.execute('update users set invite_by=? where invite_by=?', (user_id, code,))
    conn.commit()
    cursor.execute('update users set ref_code=? where user_id = ?', (user_id, user_id,))
    conn.commit()
    cursor.close()
    conn.close()


def set_payments_value(type='need_qiwi'):
    conn, cursor = connect()
    if get_value(type) == 1:
        try:
            cursor.execute(f'update config set {type}=0')
            conn.commit()
        except Exception as e:
            print(e)
    else:
        try:
            cursor.execute(f'update config set {type}=1')
            conn.commit()
        except:
            pass
    cursor.close()
    conn.close()



def add_replenish(type='easypay', number=None, token=None):
    conn, cursor = connect()
    try:
        if token is None:
            cursor.execute(f'insert into {type} values(?)', (number,))
            conn.commit()
        else:
            cursor.execute(f'insert into {type} values(?,?)', (number, token,))
            conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def remove_replanish(type='easypay', number=None):
    conn, cursor = connect()
    try:
        if type != 'qiwi':
            cursor.execute(f'delete from {type} where value=?', (number,))
            conn.commit()
        else:
            cursor.execute(f'delete from {type} where number=?', (number,))
            conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def add_promo(promo, bonus):
    conn, cursor = connect()
    try:
        cursor.execute('insert into promo_code values(?,?)', (promo, bonus,))
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def set_discount(user_id, count):
    conn, cursor = connect()
    try:
        cursor.execute('update users set discount = ? where user_id=?', (count, user_id,))
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def set_balance(user_id, count):
    conn, cursor = connect()
    try:
        cursor.execute('update users set balance = ? where user_id=?', (count, user_id,))
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def remove_product(product_id, count):
    conn, cursor = connect()
    try:
        cursor.execute(
            f'delete from address where person_id in (select person_id from address where product_id={product_id} limit {count})')
        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()
    conn.close()


def update_value(set, value):
    conn, cursor = connect()
    cursor.execute(f'update config set {set}="{value}"')
    conn.commit()
    cursor.close()
    conn.close()


def get_categories_subcategories(columns="catalog_id, name"):
    conn, cursor = connect()
    try:
        if columns != "catalog_id, name":
            message = cursor.execute(f'select {columns} from catalog').fetchall()
            return message
        else:
            message = cursor.execute(f'select catalog_id, name from catalog').fetchall()
            return message
    except Exception as e:
        pass

    finally:
        cursor.close()
        conn.close()


def delete_category_subcategory(id):
    array = daos('select catalog_id from catalog where catalog_id=? or parent_catalog_id=?', (id, id))
    for i in array:
        dao('delete from product where catalog_id=?', i)

    dao('delete from catalog where catalog_id=? or parent_catalog_id=?', (id, id))


def delete_product(id):
    dao('delete from product where product_id=?', id)


def get_products():
    return daos('select product_id, name from product')


def dao(text, param=None):
    conn, cursor = connect()
    try:
        if param is not None:
            cursor.execute(text, param)
        else:
            cursor.execute(text)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def daos(text, param=None):
    conn, cursor = connect()
    try:
        if param is not None:
            return cursor.execute(text, param).fetchall()
        else:
            return cursor.execute(text).fetchall()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



# >>>>>>>>>>>>>>>>>>Обработчик запросов к бд по BTC адресам<<<<<<<<<<<<<<<<<<<<<<<<<<
def post_wallet_address(user_id, address):
    conn, cursor = connect()
    cursor.execute('SELECT user_id FROM btc_address WHERE user_id = {}'.format(user_id))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO btc_address VALUES (?, ?)", (user_id, address))
        conn.commit()
    else:
        cursor.execute(f"UPDATE btc_address SET address = '{address}' WHERE user_id = {user_id}")
        conn.commit()


def get_payment_btc_address(user_id):
    conn, cursor = connect()
    for value in cursor.execute(
            "SELECT user_id, address FROM btc_address WHERE user_id = {}".format(user_id)):
        return value


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Конец LTC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# >>>>>>>>>>>>>>>>>>Обработчик запросов к бд по LTC адресам<<<<<<<<<<<<<<<<<<<<<<<<<<
def post_wallet_ltc_address(user_id, address):
    conn, cursor = connect()
    cursor.execute('SELECT user_id FROM ltc_address WHERE user_id = {}'.format(user_id))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO ltc_address VALUES (?, ?)", (user_id, address))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor.execute(f"UPDATE ltc_address SET address = '{address}' WHERE user_id = {user_id}")
        conn.commit()
        cursor.close()
        conn.close()


def get_payment_ltc_address(user_id):
    conn, cursor = connect()
    for value in cursor.execute(
            "SELECT user_id, address FROM ltc_address WHERE user_id = {}".format(user_id)):
        return value
    conn.commit()
    cursor.close()
    conn.close()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Конец LTC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# >>>>>>>>>>>>>>>>>>Обработчик запросов к бд по BCH адресам<<<<<<<<<<<<<<<<<<<<<<<<<<
def post_wallet_bch_address(user_id, address):
    conn, cursor = connect()
    cursor.execute('SELECT user_id FROM bch_address WHERE user_id = {}'.format(user_id))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO bch_address VALUES (?, ?)", (user_id, address))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor.execute(f"UPDATE bch_address SET address = '{address}' WHERE user_id = {user_id}")
        conn.commit()
        cursor.close()
        conn.close()


def get_payment_bch_address(user_id):
    conn, cursor = connect()
    for value in cursor.execute(
            "SELECT address FROM bch_address WHERE user_id = {}".format(user_id)):
        return value
    conn.commit()
    cursor.close()
    conn.close()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Конец LTC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def insert_message_history(user_id, message_id):
    conn, cursor = connect()
    cursor.execute("INSERT INTO history VALUES (?, ?)", (user_id, message_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_history_info(user_id):
    conn, cursor = connect()
    for value in cursor.execute(
            "SELECT user_id, message_history FROM history WHERE user_id = {}".format(user_id)):
        return value
    conn.commit()
    cursor.close()
    conn.close()


def delete_message_history(user_id, message_id):
    conn, cursor = connect()
    cursor.execute(
        f'delete from history where user_id={user_id} or message_history={message_id}')
    conn.commit()
    cursor.close()
    conn.close()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Смена кошельков через бота <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def change_ltc_bot(address):
    conn, cursor = connect()
    cursor.execute('SELECT wallet_address FROM wallet_ltc WHERE wallet_id = {}'.format(1))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO wallet_ltc VALUES (?, ?)", (1, address))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor.execute(f"UPDATE wallet_ltc SET wallet_address = '{address}' WHERE wallet_id = {1}")
        conn.commit()
        cursor.close()
        conn.close()


def change_btc_bot(address):
    conn, cursor = connect()
    cursor.execute('SELECT wallet_address FROM wallet_btc WHERE wallet_id = {}'.format(1))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO wallet_btc VALUES (?, ?)", (1, address))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor.execute(f"UPDATE wallet_btc SET wallet_address = '{address}' WHERE wallet_id = {1}")
        conn.commit()
        cursor.close()
        conn.close()


def change_bch_bot(address):
    conn, cursor = connect()
    cursor.execute('SELECT wallet_address FROM wallet_bch WHERE wallet_id = {}'.format(1))
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO wallet_bch VALUES (?, ?)", (1, address))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        cursor.execute(f"UPDATE wallet_bch SET wallet_address = '{address}' WHERE wallet_id = {1}")
        conn.commit()
        cursor.close()
        conn.close()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>БЕРЕМ АДРЕСА ДЛЯ БОТА <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def get_wallet_form_bot(wallet):
    conn, cursor = connect()
    for value in cursor.execute(f"SELECT wallet_address FROM {wallet} WHERE wallet_id = {1}"):
        return value
    conn.commit()
    cursor.close()
    conn.close()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>НАЧИСЛЕНИЯ КУРЬЕРАМ <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def get_pony(user_id):
    conn, cursor = connect()
    for value in cursor.execute(f"SELECT * FROM ponyexp WHERE user_id = {user_id}"):
        return value
    conn.commit()
    cursor.close()
    conn.close()


def add_pony(user_id, text):
    conn, cursor = connect()
    cursor.execute(f"INSERT INTO ponyexp VALUES (?, ?)", (user_id, text))
    conn.commit()
    cursor.close()
    conn.close()


def delete_pony(user_id):
    conn, cursor = connect()
    cursor.execute(
        f'delete from ponyexp where user_id={user_id}')
    conn.commit()
    cursor.close()
    conn.close()

db()