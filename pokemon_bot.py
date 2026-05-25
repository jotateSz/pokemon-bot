"""
🎴 POKEMON DROP MONITOR BOT
Para GitHub Actions - revisa una vez y termina
"""
 
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
 
EMAIL = "sjosetomas06@gmail.com"
PASSWORD_APP = os.environ.get("EMAIL_PASSWORD", "")
 
KEYWORDS = [
    "booster box",
    "elite trainer box",
    "booster bundle",
    "scarlet violet",
    "prismatic evolutions",
    "surging sparks",
    "151",
]
 
URLS = {
    "Pokemon Center": "https://www.pokemoncenter.com/category/trading-card-game",
    "Walmart": "https://www.walmart.com/search?q=pokemon+booster+box",
    "Target": "https://www.target.com/s?searchTerm=pokemon+booster+box",
    "Costco": "https://www.costco.com/CatalogSearch?keyword=pokemon+cards",
}
 
def enviar_email(tienda, url, producto):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"DROP POKEMON en {tienda}!"
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        hora = datetime.now().strftime("%H:%M:%S")
        fecha = datetime.now().strftime("%d/%m/%Y")
        html = f"""
        <html><body style="font-family:Arial;background:#1a1a2e;color:white;padding:20px;">
        <div style="max-width:600px;margin:auto;background:#16213e;border-radius:15px;padding:30px;border:2px solid #e3350d;">
        <h1 style="color:#e3350d;text-align:center;">DROP DETECTADO!</h1>
        <h2 style="color:#f5c518;text-align:center;">{tienda}</h2>
        <div style="background:#0f3460;padding:20px;border-radius:10px;margin:20px 0;">
        <p><b>Tienda:</b> {tienda}</p>
        <p><b>Producto:</b> {producto}</p>
        <p><b>Fecha:</b> {fecha} {hora}</p>
        </div>
        <div style="text-align:center;">
        <a href="{url}" style="background:#e3350d;color:white;padding:15px 30px;border-radius:8px;text-decoration:none;font-size:18px;font-weight:bold;">IR A COMPRAR AHORA</a>
        </div></div></body></html>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD_APP)
            server.sendmail(EMAIL, EMAIL, msg.as_string())
        print(f"  Email enviado a {EMAIL}")
    except Exception as e:
        print(f"  Error enviando email: {e}")
 
def revisar_tienda(nombre, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        contenido = response.text.lower()
        for keyword in KEYWORDS:
            if keyword.lower() in contenido:
                idx = contenido.find(keyword.lower())
                zona = contenido[max(0, idx-100):idx+200]
                agotado = any(p in zona for p in ["out of stock", "sold out", "agotado", "unavailable", "notify me"])
                if not agotado:
                    return keyword
        return None
    except Exception as e:
        print(f"  Error en {nombre}: {e}")
        return None
 
def main():
    print("POKEMON DROP MONITOR")
    drops = []
    for nombre, url in URLS.items():
        print(f"Revisando {nombre}...", end=" ")
        resultado = revisar_tienda(nombre, url)
        if resultado:
            print(f"DROP: {resultado}")
            drops.append((nombre, url, resultado))
        else:
            print("sin drops")
    if drops:
        for nombre, url, producto in drops:
            enviar_email(nombre, url, producto)
    else:
        print("Sin drops esta vez.")
 
if __name__ == "__main__":
    main()
 
