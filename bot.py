def buscar_noticias():
    # Usando a URL que o widget deles usa, que costuma ser menos protegida
    url = "https://br.investing.com/economic-calendar"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        session = requests.Session() # Usa sessão para manter cookies
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O Investing às vezes usa classes diferentes para a tabela
        tabela = soup.select_one('#economicCalendarData')
        
        if not tabela:
            # Se falhar, tentamos buscar por qualquer tabela que tenha a classe 'ecTable'
            tabela = soup.select_one('.ecTable')

        if not tabela:
            # LOG DE DEBUG: Se ainda não achar, vamos ver o que o site respondeu
            print(f"Status Code: {response.status_code}")
            if "sucuri" in response.text.lower() or "cloudflare" in response.text.lower():
                print("Bloqueio de Firewall (Cloudflare/Sucuri) detectado.")
            return []

        linhas = tabela.select('tr.js-event-item')
        mensagens = []
        
        for linha in linhas:
            # Busca o impacto pelos touros (ícones)
            # Na versão mobile/atualizada o seletor pode ser 'td.sentiment'
            impacto = linha.select('td.sentiment i.grayFullBullishIcon')
            
            if len(impacto) == 3:
                hora = linha.select_one('td.time').text.strip()
                moeda = linha.select_one('td.left.flagCur').text.strip()
                evento = linha.select_one('td.event').text.strip()
                
                msg = f"⚠️ *ALTA VOLATILIDADE*\n\n🕒 Hora: {hora}\n🌍 Moeda: {moeda}\n📊 Evento: {evento}"
                mensagens.append(msg)
        
        return mensagens
    except Exception as e:
        print(f"Erro: {e}")
        return []
        
