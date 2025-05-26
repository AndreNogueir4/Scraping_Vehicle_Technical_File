import requests
import re
from lxml import html

def clean_text(text):
    text = re.sub(r'[\n\t\r]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def scrape_shopcar(marca='2'):
    words_to_remove = ['', 'CADASTRE-SE', 'ÁREA DO ANUNCIANTE', 'Compre seu veículo', 'Destaques', 'Busca Detalhada',
                       'Busca por Categoria', 'Fichas Técnicas', 'Banco de Pedidos', 'Meus Favoritos', 'Venda seu veículo',
                       'Anunciar Veículos', 'Adesão de Lojas', 'Serviços', 'Avalie seu Veículo', 'Produtos e Serviços',
                       'Links/Detrans', 'Receba Novidades', 'Preços de Combustíveis', 'Notícias', 'Capa', '2 Rodas',
                       'Avaliações', 'Fotos e Vídeos', 'Imóveis', 'Consórcios', 'Voltar', 'Página inicial',
                       'Veículos em destaque', 'Busca detalhada', 'Banco de pedidos', 'Anunciar veículos',
                       'Adesão de lojas', 'Publicidade no site', 'Área do anunciante', 'EMPRESA AMIGA',
                       'Avalie seu veículo', 'Produtos e serviços', 'Preço de combustíveis', 'Receba novidades',
                       'Papéis de parede', 'Veículo do Leitor', 'Quem somos', 'Política de uso', 'Fale conosco',
                       'Ver política de uso', '« Voltar', 'AUDI', 'BMW', 'BYD', 'CHERY', 'CHRYSLER', 'CITROËN',
                       'DODGE', 'FERRARI', 'FIAT', 'FORD', 'GM - Chevrolet', 'GWM', 'HONDA', 'HYUNDAI', 'JAC', 'JAGUAR',
                       'JEEP', 'KIA', 'LAND ROVER', 'LIFAN', 'MERCEDES-BENZ', 'MINI', 'MITSUBISHI', 'NISSAN', 'PEUGEOT',
                       'PORSCHE', 'RAM', 'RENAULT', 'SUBARU', 'SUZUKI', 'TAC', 'TOYOTA', 'TROLLER', 'VOLVO',
                       'VW - Volkswagen', '»', '1']

    headers = {
        'Host': 'www.shopcar.com.br',
        'Sec-Ch-Ua': '"Not.A/Brand";v="99", "Chromium";v="136"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/136.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.shopcar.com.br/fichatecnica/',
        'Priority': 'u=0, i',
    }

    all_models = []
    all_results = {}

    pag = 1

    while True:
        params = {'marca': marca, 'pag': str(pag)}
        print(f"Scraping página {pag}...")

        response = requests.get(
            'https://www.shopcar.com.br/fichatecnica.php',
            params=params,
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Erro na página {pag}: {response.status_code}")
            break

        tree = html.fromstring(response.text)

        links = tree.xpath('//a')
        result = {}

        for link in links:
            href = link.get('href')
            text = clean_text(link.text_content())
            result[text] = href

        result = {k: v for k, v in result.items() if k not in words_to_remove and '&pag' not in v and
                  'javascript:void(0)' not  in v}

        models = tree.xpath('//a/div/span/text()')
        models = [' '.join(models[i:i+3]) for i in range(0, len(models), 3)]

        if not models:
            print("Nenhum modelo encontrado, encerrando...")
            break

        all_models.extend(models)
        all_results.update(result)

        pag += 1

    return all_models, all_results

all_models, all_results = scrape_shopcar(marca='2')

print(f"Total de modelos encontrados: {len(all_models)}")
print(all_models)
print(f"Total de links encontrados: {len(all_results)}")
print(all_results)