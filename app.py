from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route("/politica.html")
def politica():
    return send_from_directory('.', 'politica.html')

@app.route("/regras.html")
def regras():
    return send_from_directory('.', 'regras.html')

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

def resposta_automatica(pergunta):
    pergunta = pergunta.lower()

    regras_variacoes = [
        "quais as regras", "quais são as regras", "me diz as regras", 
        "fala as regras", "tem regras", "qual é a regra", "qual a regra"
    ]

    politica_variacoes = [
        "qual a política", "qual é a política", "qual a sua política", 
        "me mostra a política", "tem política", "política de uso"
    ]

    if any(frase in pergunta for frase in regras_variacoes):
        return (
            "Use esta IA apenas para fins educativos e de aprendizado.<br>"
            "• Não envie conteúdos ofensivos, impróprios ou que não estejam relacionados aos estudos.<br>"
            "• Evite digitar ou compartilhar informações pessoais.<br>"
            "• A IA é uma ferramenta auxiliar, e o conteúdo gerado pode conter erros. Sempre revise com orientação de professores.<br>"
            "• Não utilize a IA para colas ou trapaças em provas ou avaliações."
        ), True

    if any(frase in pergunta for frase in politica_variacoes):
        return (
            "A política de uso da IA é simples:<br>"
            "• Usar sempre com responsabilidade e respeito.<br>"
            "• Proibido uso indevido, como discriminação, bullying ou exposição de dados pessoais.<br>"
            "• Foco sempre em aprendizado, ética e segurança digital.<br>"
            "Você pode acessar a política completa clicando em <a href='/politica.html'>Política de Uso</a>."
        ), True

    if "qual o seu nome" in pergunta:
        return "Meu nome é <b>Aurora</b>!", True

    if "boa noite" in pergunta:
        return "Boa noite! Que você tenha um descanso top!", True

    if "bom dia" in pergunta:
        return "Bom dia! Que hoje seja um dia abençoado.", True

    if "obrigado" in pergunta or "obrigada" in pergunta:
        return "De nada! Qualquer coisa, tô por aqui.", True

    if "valeu" in pergunta:
        return "Tamo junto!", True

    if "oi" in pergunta or "olá" in pergunta:
        return "Oi! Como posso te ajudar?", True

    return "", False

def resumir_texto(texto):
    frases = re.split(r'(?<=[.!?]) +', texto)
    return " ".join(frases[:2])

def buscar_bing_scraping(pergunta):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = pergunta.replace(" ", "+")
    url = f"https://www.bing.com/search?q={query}"
    resposta = requests.get(url, headers=headers)
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = soup.select("li.b_algo h2 a")

    links = []
    for tag in resultados:
        href = tag.get("href")
        if href and "bing.com" not in href and "microsoft.com" not in href:
            links.append(href)
        if len(links) >= 3:
            break
    return links

@app.route("/perguntar", methods=["POST"])
def perguntar():
    data = request.get_json()
    pergunta = data.get("pergunta", "")

    resposta_predefinida, encontrada = resposta_automatica(pergunta)
    if encontrada:
        return jsonify({"resposta": resposta_predefinida})

    links = buscar_bing_scraping(pergunta)

    respostas_extraidas = []
    for link in links:
        try:
            html = requests.get(link, timeout=5).text
            soup = BeautifulSoup(html, 'html.parser')
            paragrafos = soup.find_all("p")
            texto = " ".join([p.get_text() for p in paragrafos if len(p.get_text()) > 50])
            resumo = resumir_texto(texto)
            if resumo:
                respostas_extraidas.append(resumo)
        except:
            continue

    if respostas_extraidas:
        resposta_final = (
            f"Então, eu dei uma olhada em algumas fontes e aqui vai um resumo sobre <b>{pergunta}</b>:<br><br>"
            f"{respostas_extraidas[0]}"
        )
    else:
        resposta_final = (
            "Poxa, tentei procurar direitinho, mas não consegui achar uma resposta clara pra isso. "
            "Quer tentar perguntar de outro jeito?"
        )

    if links:
        resposta_final += "\n\n<b>Fontes:</b><br>" + "<br>".join(
            f'<a href="{x}" target="_blank">{x}</a>' for x in links
        )

    return jsonify({"resposta": resposta_final})

@app.route("/avaliar", methods=["POST"])
def avaliar():
    data = request.get_json()
    print("Feedback:", data)
    return jsonify({"status": "Valeu pelo feedback!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
