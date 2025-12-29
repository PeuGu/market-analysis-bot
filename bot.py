import os
import requests
from bs4 import BeautifulSoup

# Configurações de acesso
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    """Função que envia mensagens para o Telegram"""
    if not TOKEN or not CHAT_ID:
        print("Erro: Variáveis TELEGRAM_TOKEN ou CHAT_ID não encontradas.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso ao Telegram!")
        else:
            print(f"Erro ao enviar ao Telegram: {response.status_code}")
    except Exception as e:
        print(f"Falha na conexão com Telegram: {e}")

def buscar_noticias():
    """Função que raspa as notícias do Investing"""
    url = "https://br.investing.com/economic-calendar"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tentando localizar a tabela
        tabela = soup.select_one('#economicCalendarData')
        if not tabela:
            return []

        linhas = tabela.select('tr.js-event-item')
        noticias_encontradas = []
        
        for linha in linhas:
            # Filtro: 3 Touros (impacto alto)
            impacto = linha.select('td.sentiment i.grayFullBullishIcon')
            
            # TESTE: Se quiser que o bot fale AGORA mesmo, mude '== 3' para '>= 1'
            if len(impacto) == 3:
                hora = linha.select_one('td.time').text.strip()
                moeda = linha.select_one('td.left.flagCur').text.strip()
                evento = linha.select_one('td.event').text.strip()
                
                noticias_encontradas.append(f"⚠️ *ALTA VOLATILIDADE*\n\n🕒 Hora: {hora}\n🌍 Moeda: {moeda}\n📊 Evento: {evento}")
        
        return noticias_encontradas
    except Exception as e:
        print(f"Erro no scraping: {e}")
        return []

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    # 1. Primeiro teste: O Bot avisa que acordou
    enviar_telegram("🤖 *Bot de Notícias:* Iniciando verificação do mercado...")
    
    # 2. Busca as notícias
    lista_noticias = buscar_noticias()
    
    # 3. Se houver notícias, envia cada uma
    if lista_noticias:
        for noticia in lista_noticias:
            enviar_telegram(noticia)
    else:
        print("Nenhuma notícia de 3 touros encontrada no momento.")
