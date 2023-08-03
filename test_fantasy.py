import time
import datetime
import sys

import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


driver_path = "D:\\Workspace\\AutoFantasy\\chromedriver_win32\\chromedriver.exe"
N = 72


def main():
    # Opciones de navegación
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    # Evitar warnings
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)
    # Abrir perfil de chrome
    options.add_argument(
        "user-data-dir=C:\\Users\\Usuario\\AppData\\Local\\Google\\Chrome\\User Data"
    )
    options.add_argument("profile-directory=Default")

    driver = webdriver.Chrome(options=options)# , executable_path=driver_path
    time.sleep(1)

    # Inicializamos el navegador
    url = f"https://{MODE}.superfantasylol.com/login"

    driver.get(url)

    # Loggear con twitch
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (
                By.CLASS_NAME,
                "twitch-btn",
            )
        )
    ).click()

    # Ir a calendario
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/app-root/app-header-laout/div/div/app-menu/div/div/a[6]/span",
            )
        )
    ).click()

    time.sleep(1)

    # Obtener partidos jugados
    elements = driver.find_elements(By.CLASS_NAME, "match.played")
    for el in range(len(elements)):
        elements[el].click()
        time.sleep(2)
        read_data(driver)
        driver.back()
        time.sleep(1)
        elements = driver.find_elements(By.CLASS_NAME, "match.played")

    driver.close()
    # driver.quit()


def read_data(driver):
    try:
        table = driver.find_element_by_xpath(
            "/html/body/app-root/app-header-laout/div/div/div/app-match/div[2]/div[3]"
        )
    except:
        return
    data_raw = table.text.split("\n")
    # data_filtered = data_raw
    data_dict = process_data_raw(data_raw)
    items = data_dict.pop("items")
    for i, item in enumerate(items):
        if item not in DATA:
            DATA[item] = {}
        for player in data_dict.keys():
            DATA[item].setdefault(player, []).append(data_dict[player][i])

    return


def process_data_raw(data):
    if len(data) > 936:
        data = list(filter(lambda x: len(x) < 30, data))
    data_dict = {}
    for i in range(0, len(data), N):
        column = data[i : i + N]
        name = column[0].lower()
        if name == "items":
            values = column[1:]
        else:
            values = [int(v) if v.isdigit() else 0 for v in column[1:]]
        data_dict[name] = values
    return data_dict


def create_excel():
    results = {item: {} for item in DATA}
    for item, players in DATA.items():
        for player, values in players.items():
            if np.max(values) == 0:
                results[item][player] = 0
            else:
                results[item][player] = (1 - np.std(values) / np.mean(values)) * np.max(
                    values
                )
    df = pd.DataFrame.from_dict(results).T
    name = MODE + "_" + datetime.datetime.now().strftime("%Y.%m.%d %H-%M-%S")
    df.to_excel(name + ".xlsx")
    # df.to_csv(name + ".csv")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        mode_in = input("LEC o SuperLiga?\n")
    else:
        mode_in = " ".join(args)

    if "lec" in mode_in.lower():
        MODE = "lec"
    elif any(key in mode_in.lower() for key in ["lvp", "sl", "superliga"]):
        MODE = "lvp"
    else:
        print("Liga no reconocida.")
        sys.exit()

    DATA = {}
    main()
    create_excel()
