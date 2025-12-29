import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def buscar_noticias():
    url = "https://br.investing.com/economic-calendar"
    
    # Headers mais completos para parecer um navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O Investing às vezes muda o ID. Vamos tentar achar pela classe ou ID
        tabela = soup.find('table', {'id': 'economicCalendarData'})
        
        if not tabela:
            print("Não foi possível encontrar a tabela de notícias. O site pode ter mudado a estrutura.")
            return []

        linhas = tabela.find_all('tr', {'class': 'js-event-item'})
        mensagens = []
        
        for linha in linhas:
            # Verifica o impacto (estrelas/touros)
            impacto_td = linha.find('td', {'class': 'sentiment'})
            if impacto_td:
                # Conta quantos ícones de "touro cheio" existem
                estrelas = impacto_td.find_all('i', {'class': 'grayFullBullishIcon'})
                
                # Se quiser testar agora (que é segunda de manhã), 
                # pode deixar len(estrelas) >= 1 para ver se o Telegram recebe.
                # Para o bot oficial, use == 3.
                if len(estrelas) == 3:
                    hora = linha.find('td', {'class': 'time'}).text.strip()
                    moeda = linha.find('td', {'class': 'left flagCur'}).text.strip()
                    evento = linha.find('td', {'class': 'event'}).text.strip()
                    
                    msg = f"⚠️ *SINAL DE ALTA VOLATILIDADE*\n\n🕒 Hora: {hora}\n🌍 Moeda: {moeda}\n📊 Evento: {evento}"
                    mensagens.append(msg)
        
        return mensagens

    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return []

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        print("Erro: Variáveis de ambiente TELEGRAM_TOKEN ou CHAT_ID não configuradas.")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, data=data)

if __name__ == "__main__":
    noticias = buscar_noticias()
    if noticias:
        for n in noticias:
            enviar_telegram(n)
            print(f"Mensagem enviada: {n[:30]}...")
    else:
        print("Nenhuma notícia de alto impacto encontrada para hoje.")
            
