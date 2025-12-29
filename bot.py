import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def extrair_detalhes_noticia(url_completa):
    """Entra na página da notícia e pega os valores Atual, Projeção e Anterior"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url_completa, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Localiza os valores (ID comum no Investing para esses campos)
        atual = soup.find(id="releaseInfoActual").text.strip() if soup.find(id="releaseInfoActual") else "Aguardando..."
        previsto = soup.find(id="releaseInfoForecast").text.strip() if soup.find(id="releaseInfoForecast") else "N/A"
        anterior = soup.find(id="releaseInfoPrevious").text.strip() if soup.find(id="releaseInfoPrevious") else "N/A"
        
        return f"\n📊 *Resultado:* {atual}\n🎯 *Projeção:* {previsto}\n📚 *Anterior:* {anterior}"
    except:
        return "\n⚠️ Não foi possível carregar os detalhes do resultado."

def buscar_calendario():
    url = "https://br.investing.com/economic-calendar"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela = soup.find('table', {'id': 'economicCalendarData'})
        if not tabela: return
        
        linhas = tabela.find_all('tr', {'class': 'js-event-item'})
        for linha in linhas:
            impacto = len(linha.find('td', {'class': 'sentiment'}).find_all('i', {'class': 'grayFullBullishIcon'}))
            
            if impacto == 3:
                # Pega o link interno da notícia
                link_tag = linha.find('td', {'class': 'event'}).find('a')
                if link_tag:
                    href = link_tag['href']
                    # Entra na notícia para pegar o resultado real
                    detalhes = extrair_detalhes_noticia("https://br.investing.com" + href)
                    
                    hora = linha.find('td', {'class': 'time'}).text.strip()
                    moeda = linha.find('td', {'class': 'left flagCur'}).text.strip()
                    evento = link_tag.text.strip()
                    
                    msg = f"🔥 *ALTA VOLATILIDADE ENCONTRADA*\n\n🕒 *Hora:* {hora}\n🌍 *Moeda:* {moeda}\n📊 *Evento:* {evento}\n{detalhes}"
                    enviar_telegram(msg)
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    # Se você quiser que o bot verifique uma notícia específica que você colar manualmente:
    # (Isso exigiria o bot estar sempre 'ouvindo'. No GitHub Actions ele só 'roda e morre')
    # Como alternativa, você pode criar um script separado ou adicionar aqui:
    
    buscar_calendario()
