import requests
from lxml import html

words_to_remove = ['', 'CADASTRE-SE', 'ÁREA DO ANUNCIANTE', 'Compre seu veículo', 'Destaques', 'Busca Detalhada',
                   'Busca por Categoria', 'Fichas Técnicas', 'Banco de Pedidos', 'Meus Favoritos', 'Venda seu veículo',
                   'Anunciar Veículos', 'Adesão de Lojas', 'Serviços', 'Avalie seu Veículo', 'Produtos e Serviços',
                   'Links/Detrans', 'Receba Novidades', 'Preços de Combustíveis', 'Notícias', 'Capa', '2 Rodas',
                   'Avaliações', 'Fotos e Vídeos', 'Imóveis', 'Consórcios', 'Voltar', 'Página inicial',
                   'Veículos em destaque', 'Busca detalhada', 'Banco de pedidos', 'Anunciar veículos',
                   'Adesão de lojas', 'Publicidade no site', 'Área do anunciante', 'EMPRESA AMIGA',
                   'Avalie seu veículo', 'Produtos e serviços', 'Preço de combustíveis', 'Receba novidades',
                   'Papéis de parede', 'Veículo do Leitor', 'Quem somos', 'Política de uso', 'Fale conosco',
                   'Ver política de uso', '« Voltar']

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
    'Referer': 'https://www.shopcar.com.br/',
    'Priority': 'u=0, i',
}

response = requests.get('https://www.shopcar.com.br/fichatecnica/', headers=headers)

html_content = response.text
tree = html.fromstring(html_content)

links = tree.xpath('//a')

result = {}
for link in links:
    href = link.get('href')
    text = link.text_content().strip()
    result[text] = href

result = {k: v for k, v in result.items() if k not in words_to_remove if '?id=' not in v}

print(result)