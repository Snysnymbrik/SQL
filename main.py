import sqlite3
import random
from datetime import date


def rand_date():  # функция для генерации случайной даты
    start_dt = date.today().replace(day=1, month=1, year=2019).toordinal()
    end_dt = date.today().toordinal()
    random_dt = date.fromordinal(random.randint(start_dt, end_dt))
    return random_dt


def avg_in_age(age_start: int, age_stop: int):  # функция для определения средних трат в выбранном возрастном интервале
    cursor2.execute('''SELECT DISTINCT strftime('%Y%m', date)
                            FROM Purchases
                            ''')
    cursor.execute('''SELECT  COUNT(DISTINCT strftime('%Y%m', date))
                            FROM Purchases
                            ''')
    res = []
    for itr in range(cursor.fetchall()[0][0]):
        cursor.execute('''SELECT AVG(Items.price)
                            FROM Purchases LEFT JOIN Users ON Users.userId = Purchases.userId
                                            LEFT JOIN Items ON Purchases.itemId = Items.itemId
                            WHERE (Users.age >=? AND Users.age<=?) AND strftime('%Y%m', Purchases.date) == ?
                                ''', [age_start, age_stop, cursor2.fetchone()[0]])
        avg_m = cursor.fetchall()[0][0]
        if avg_m:
            res.append(avg_m)
        return sum(res) / len(res)


sqlite_connection = sqlite3.connect('sqlite.db')  # создание базы данных
cursor = sqlite_connection.cursor()
cursor2 = sqlite_connection.cursor()

cursor.execute(''' SELECT count(name) FROM sqlite_master ''')
if cursor.fetchall()[0][0] == 0:  # Проверка небыла ли уже создана база данных, если она пуста то создаем таблици и наполняем их
    cursor.execute('''CREATE TABLE Users (
                                    userId INTEGER PRIMARY KEY,
                                    age INTEGER NOT NULL)''')

    cursor.execute('''CREATE TABLE Purchases (
                                    purchaseId INTEGER PRIMARY KEY,
                                    userId INTEGER NOT NULL,
                                    itemId INTEGER NOT NULL,
                                    date datetime NOT NULL)''')

    cursor.execute('''CREATE TABLE Items  (
                                    itemId INTEGER PRIMARY KEY,
                                    price INTEGER NOT NULL)''')
    sqlite_connection.commit()

    val_User = []
    val_Items = []
    val_Purchases = []
    for IdUser in range(1, 501):
        val_User.append((IdUser, random.randint(18, 70)))
    for IdItems in range(1, 201):
        val_Items.append((IdItems, random.randint(1000, 10000)))
    for IdPurchases in range(1, 1000):
        val_Purchases.append((IdPurchases, random.randint(1, 500), random.randint(1, 200), rand_date()))

    cursor.executemany("INSERT INTO Users (userId,age) VALUES  (?,?)", val_User)
    cursor.executemany("INSERT INTO Items (itemId,price) VALUES  (?,?)", val_Items)
    cursor.executemany("INSERT INTO Purchases (purchaseId,userId,itemId,date) VALUES  (?,?,?,?)", val_Purchases)
    sqlite_connection.commit()

print("Сумма, которую в среднем в месяц тратят пользователи в возрастном диапазоне от 18 до 25 лет включительно: ",
      avg_in_age(18, 25))
print("Сумма, которую в среднем в месяц тратят пользователи в возрастном диапазоне от 26 до 35 лет включительно: ",
      avg_in_age(26, 35))
cursor2.execute('''SELECT DISTINCT strftime('%m', date)
                            FROM Purchases
                            ''')
cursor.execute('''SELECT  COUNT(DISTINCT strftime('%m', date))
                        FROM Purchases
                        ''')

res = []
for itr in range(cursor.fetchall()[0][0]):
    month = cursor2.fetchone()[0]
    cursor.execute('''SELECT SUM(Items.price)
                                FROM Purchases LEFT JOIN Users ON Users.userId = Purchases.userId
                                                LEFT JOIN Items ON Purchases.itemId = Items.itemId
                                WHERE (Users.age >=35 ) AND strftime('%m', Purchases.date) == ?
                                    ''', [month])
    sum_m = cursor.fetchall()[0][0]
    if sum_m:
        res.append((sum_m, month))

print("Самая большая выручка от пользователей в возрастном диапазоне 35+ на сумму %s, фиксируется в %s месяце" %
      max(res))
cursor2.execute('''SELECT DISTINCT strftime('%Y%m', date)
                            FROM Purchases
                            WHERE  strftime('%Y%m', date) > strftime('%Y%m','now','-1 year')
                            ORDER BY date
                            ''')
args = []
for itr in cursor2.fetchall():
    args.append(itr[0])

cursor.execute('''SELECT SUM(Items.price), Items.itemId
                                FROM Purchases LEFT JOIN Items ON Purchases.itemId = Items.itemId
                                WHERE strftime('%Y%m', Purchases.date)  IN ({seq})
                                GROUP BY Items.itemId
                                ORDER BY SUM(Items.price) DESC'''.format(seq=','.join(['?'] * len(args))), args)

print("Наибольший вклад в выручку за последний год в размере %s, обеспечивает тавар № %s" %
      max(cursor.fetchall()))

cursor.execute('''SELECT SUM(Items.price), Items.itemId
                                FROM Purchases LEFT JOIN Items ON Purchases.itemId = Items.itemId 
                                WHERE strftime('%Y', Purchases.date) == '2020'
                                GROUP BY Items.itemId
                                ORDER BY SUM(Items.price) DESC''')
args = []
sum_y = 0
count = 0
sum_cont = 0
for itr in cursor.fetchall():
    sum_y += itr[0]
    if count < 3:
        args.append(itr[1])
        count += 1
        sum_cont += itr[0]

output = [(", ".join(str(item) for item in args), sum_cont / sum_y * 100)]
print("В топ-3 товаров по выручке входят продукты под № %s и их доля в общей выручке за 2020 год составляет %s%%" %
      output[0])
