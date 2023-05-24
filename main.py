import sqlite3
import requests
from bs4 import BeautifulSoup as BS
import lxml
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox

history_list = []
list = []

def request_currency():
    url = 'https://finance.rambler.ru/currencies/?ysclid=lf5c2nj4dn388282270'
    r = requests.get(url)
    soup = BS(r.text, 'lxml')

    for div in soup.find_all("div", class_="finance-currency-table__cell finance-currency-table__cell--denomination"):
        list.append([int(div.find_next(string=True).strip())])
    count = len(list)

    k = 0
    for div in soup.find_all("div", class_="finance-currency-table__cell finance-currency-table__cell--currency"):
        list[k].append(div.find_next(string=True).strip())
        k = k + 1

    k = 0
    for div in soup.find_all("div", class_="finance-currency-table__cell finance-currency-table__cell--value"):
        list[k].append(float(div.find_next(string=True).strip()))
        k = k + 1

    if len(list) != 0:
        print("Запрос выполнен успешно. Список полученных данных:")
        print(list)
        print()

    return list

def creating_database():
    with sqlite3.connect('C:\\Users\\Вероника\\Desktop\\pythonProject1\\data_base.db') as db:
        cur = db.cursor()

        db.execute("""CREATE TABLE IF NOT EXISTS data (nominal INT, currency TEXT, value REAL)""")
        db.commit()

        previous_list = cur.execute("""SELECT * FROM data""").fetchall()
        cur.execute("""DELETE FROM data""")

        cur.executemany("""INSERT INTO data VALUES(?, ?, ?)""", (list))
        db.commit()
        print("Актуальные данные были помещены в базу данных.")

    return previous_list

def difference_analysis(list, previous_list):
    differencies = []
    k = 0
    for x in list:
        differencies.append([x[0], x[1], x[2] - previous_list[k][2]])
        k = k + 1
    max_diff = 0
    ind_max = 0
    min_diff = 1000000
    ind_min = 0
    count = len(list)
    for i in range(count):
        if abs(differencies[i][2]) > 0 and abs(differencies[i][2]) > max_diff:
            ind_max = i
            max_diff = abs(differencies[i][2])

    rez = []

    if max_diff == 0:
        print("Изменений в базе данных не было.")
        rez.append("Изменений в базе данных не было.")
        if len(history_list) == 0:
            history_list.append(list)
    else:
        print("Максимальное абсолютное изменение у ", differencies[ind_max][0], differencies[ind_max][1], ". Оно равно: ", differencies[ind_max][2])
        rez.append("Максимальное абсолютное изменение у " + str(differencies[ind_max][0]) + " " + str(differencies[ind_max][1]) + ". Оно равно: " + str(differencies[ind_max][2]))
        if len(history_list) == 10:
            history_list.pop(0)
        history_list.append(list)

    return rez

def creating_interface(history_list, list, previous_list, rez):

    root = Tk()
    root.title("Окно")
    root.geometry("750x500")
    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Просмотр данных')
    tab_control.add(tab2, text='Анализ данных')


    def clicked():
        lbl = Label(tab1, text="Данные с Запрос 1")
        lbl.grid(column=0, row=3)
        res = "Данные с {}".format(combobox.get())
        lbl.configure(text=res)
        columns = ("nominal", "currency", "value")

        tree = ttk.Treeview(tab1, columns=columns, show="headings")
        tree.grid(column=0, row=4, sticky="nsew")

        tree.heading("nominal", text="Номинал")
        tree.heading("currency", text="Валюта")
        tree.heading("value", text="Значение")

        count = int((combobox.get())[7:])
        if count <= len(history_list):
            for currency in history_list[count - 1]:
                tree.insert("", END, values=currency)

            scrollbar = ttk.Scrollbar(tab1, orient=VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=4, column=1, sticky="ns")
        else:
            lbl = Label(tab1, text="Невозможно выполнить запрос")
            lbl.grid(column=0, row=5)

    def clicked1():
        lbl4 = Label(tab2, text= rez[0])
        lbl4.grid(column=0, row=1)

    requests = []
    for i in range(len(history_list)):
        requests.append("Запрос " + str(i + 1))
    combobox = ttk.Combobox(tab1, values=requests)
    combobox.current(0)
    combobox.grid(column=0, row=2)

    lbl1 = Label(tab1, text="*Данные хранятся с 10 последних различных запросов (постоянно обновляются)")
    lbl1.grid(column=0, row=0)
    lbl2 = Label(tab1, text="*Выберите из выпадающего списка номер запроса")
    lbl2.grid(column=0, row=1)

    btn1 = Button(tab1, text="Получить данные", command=clicked)
    btn1.grid(column=2, row=2)

    lbl3 = Label(tab2, text="*Сравнительный анализ актуальных данных и данных из предыдущего запроса")
    lbl3.grid(column=0, row=0)

    btn2 = Button(tab2, text="Получить данные", command=clicked1)
    btn2.grid(column=1, row=0)

    tab_control.pack(expand=1, fill='both')
    root.mainloop()

list = request_currency()
previous_list = creating_database()
if len(previous_list) != 0:
    rez = difference_analysis(list, previous_list)
else:
    print("Это первый запрос. Провести сравнительный анализ с предыдущим невозможно.")
print(history_list)

creating_interface(history_list, list, previous_list, rez)