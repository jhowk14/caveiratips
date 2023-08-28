from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd
import os.path
print("-------------------------------------------")
login = input("Digite seu login da Caveira tips: ")
print("-------------------------------------------")
senha = input("Informe a senha: ")
print("-------------------------------------------\n")

# Configurações iniciais do Selenium
driver = webdriver.Chrome()
driver.set_window_size(1400, 800)
login_url = 'https://app.caveira.tips/login'
driver.get(login_url)

wait = WebDriverWait(driver, 10)
username_field = wait.until(EC.visibility_of_element_located((By.NAME, 'login')))
password_field = wait.until(EC.visibility_of_element_located((By.NAME, 'password')))

username_field.send_keys(login)
password_field.send_keys(senha)
password_field.send_keys(Keys.RETURN)

sleep(5)
offset=0

# Nome do arquivo Excel
excel_filename = 'dados.xlsx'

while True:
    url = f'https://app.caveira.tips/events/ended?offset={offset}'
    driver.get(url)
    sleep(25)
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, "html.parser")

    # Encontrar os elementos da tabela e extrair os dados
    spans = soup.find_all('span', class_='d-none d-lg-table-row')

    # Inicializar listas para armazenar os dados extraídos
    data_list = []

    # Loop através das divs e extrair os dados necessários
    for div in spans:
        hora_span = div.find('span', attrs={'color': 'light'})
        data_partida_span = div.find('span', class_='text-uppercase')
        liga_div = div.find('div', class_='league')
        if not data_partida_span:
            break
        tds = div.find_all('td')
        if len(tds) >= 8:
            liga_span = tds[1].find('div', class_="league")
            jogador1_span = tds[2].find('span')
            home_team_div = tds[2].find('div', class_='text-muted')
            jogador2_span = tds[6].find('span')
            away_team_div = tds[6].find('div', class_='text-muted')
            score_span = tds[4].find('span')
            score_HT_div = tds[4].find('div', class_='text-muted')

            hora = hora_span.text.split(';') if hora_span else ['data nao informada']
            data_partida = data_partida_span.text.split(';') if data_partida_span else ['data nao informada']
            liga = liga_div.text.split(';') if liga_div else ['liga nao informada']
            jogador1 = jogador1_span.text if jogador1_span else 'jogador 1 nao informado'
            home_team = home_team_div.text if home_team_div else 'time de casa nao informado'
            jogador2 = jogador2_span.text if jogador2_span else 'jogador 2 nao informado'
            away_team = away_team_div.text if away_team_div else 'time de fora nao informado'
            score = score_span.text if score_span else 'placar nao informado'
            score_HT = score_HT_div.text if score_HT_div else 'placar HT nao informado'

            data_list.append([
                    data_partida[0],
                    hora[0],
                    liga[0],
                    jogador1,
                    home_team,
                    jogador2,
                    away_team,
                    score,
                    score_HT
                ])

    columns = ["Data Partida", "Hora",'Liga', "Jogador 1", "Time de casa", "Jogador 2", "Time de fora", "Placar", "Placar HT"]

    if os.path.exists(excel_filename):
        # Carregar o arquivo Excel existente
        existing_df = pd.read_excel(excel_filename)

        # Concatenar os novos dados ao DataFrame existente
        new_df = pd.DataFrame(data_list, columns=columns)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Salvar o DataFrame atualizado de volta no arquivo Excel
        updated_df.to_excel(excel_filename, index=False)
    else:
        # Se o arquivo Excel não existe, criar um novo DataFrame e salvar
        df = pd.DataFrame(data_list, columns=columns)
        df.to_excel(excel_filename, index=False)

    print(f"Dados da Página {offset} adicionados/salvos em {excel_filename}")
    offset += 20

    # Pausa para evitar sobrecarregar o servidor
    sleep(5)

# Fechar o navegador
driver.quit()
