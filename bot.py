import os
import requests
from bs4 import BeautifulSoup

# Configurações de acesso (Pegando dos Secrets do GitHub)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def buscar_noticias():
    url = "https://br.investing.com/economic-calendar"
    # O User-Agent simula um navegador real para evitar bloqueios
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Localiza a tabela de eventos
    tabela = soup.find('table', {'id': 'economicCalendarData'})
    linhas = tabela.find_all('tr', {'class': 'js-event-item'})
    
    mensagens = []
    
    for linha in linhas:
        # Filtrar por importância (3 estrelas/touros)
        impacto = linha.find('td', {'class': 'sentiment'})
        estrelas = impacto.find_all('i', {'class': 'grayFullBullishIcon'})
        
        if len(estrelas) == 3:  # Somente alta volatilidade
            hora = linha.find('td', {'class': 'time'}).text.strip()
            moeda = linha.find('td', {'class': 'left flagCur'}).text.strip()
            evento = linha.find('td', {'class': 'event'}).text.strip()
            
            msg = f"⚠️ *SINAL DE VOLATILIDADE*\n\n🕒 Hora: {hora}\n🌍 Moeda: {moeda}\n📊 Evento: {evento}"
            mensagens.append(msg)
            
    return mensagens

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, data=data)

if __name__ == "__main__":
    noticias = buscar_noticias()
    if noticias:
        for n in noticias:
            enviar_telegram(n)
    else:
        print("Nenhuma notícia de alto impacto encontrada agora.")
