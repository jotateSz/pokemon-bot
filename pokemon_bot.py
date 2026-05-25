"""
🎴 POKEMON DROP MONITOR BOT
Monitorea Pokemon Center, Walmart, Target y Costco
Envia email cuando detecta un drop disponible
"""

import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
# CONFIGURACION - EDITA ESTOS VALORES
# ============================================================

EMAIL = "sjosetomas06@gmail.com"
PASSWORD_APP = os.environ.get("EMAIL_PASSWORD", "")  # Ver instrucciones abajo

# Palabras clave a buscar (puedes agregar mas)
KEYWORDS = [
    "booster box",
    "elite trainer box",
    "booster bundle",
    "scarlet violet",
    "prismatic evolutions",
    "surging sparks",
    "151",
]

# Cuanto tiempo esperar entre cada revision (en segundos)
INTERVALO = 60  # 60 = revisar cada 1 minuto

# ============================================================
# URLS A MONITOREAR
# ============================================================

URLS = {
    "Pokemon Center - Cartas": "https://www.pokemoncenter.com/category/trading-card-game",
    "Walmart - Pokemon": "https://www.walmart.com/search?q=pokemon+booster+box",
    "Target - Pokemon": "https://www.target.com/s?searchTerm=pokemon+booster+box",
    "Costco - Pokemon": "https://www.costco.com/CatalogSearch?keyword=pokemon+cards",
}

# ============================================================
# FUNCIONES
# ============================================================

def enviar_email(tienda, url, producto):
    """Envia email de alerta cuando se detecta un drop"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 DROP DETECTADO en {tienda}!"
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        hora = datetime.now().strftime("%H:%M:%S")
        fecha = datetime.now().strftime("%d/%m/%Y")

        html = f"""
        <html>
        <body style="font-family: Arial; background: #1a1a2e; color: white; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #16213e; border-radius: 15px; padding: 30px; border: 2px solid #e3350d;">
                <h1 style="color: #e3350d; text-align: center;">🎴 DROP DETECTADO!</h1>
                <h2 style="color: #f5c518; text-align: center;">{tienda}</h2>
                
                <div style="background: #0f3460; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><b>🏪 Tienda:</b> {tienda}</p>
                    <p><b>📦 Producto:</b> {producto}</p>
                    <p><b>📅 Fecha:</b> {fecha}</p>
                    <p><b>⏰ Hora:</b> {hora}</p>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{url}" 
                       style="background: #e3350d; color: white; padding: 15px 30px; 
                              border-radius: 8px; text-decoration: none; font-size: 18px; font-weight: bold;">
                        🛒 IR A COMPRAR AHORA
                    </a>
                </div>
                
                <p style="color: #888; text-align: center; margin-top: 20px; font-size: 12px;">
                    Bot Pokemon Drop Monitor
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD_APP)
            server.sendmail(EMAIL, EMAIL, msg.as_string())

        print(f"  ✅ Email enviado! Revisa {EMAIL}")

    except Exception as e:
        print(f"  ❌ Error enviando email: {e}")
        print("  → Verifica tu contraseña de aplicación de Gmail")


def revisar_tienda(nombre, url):
    """Revisa una tienda y busca productos disponibles"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        contenido = response.text.lower()

        for keyword in KEYWORDS:
            if keyword.lower() in contenido:
                # Verificar que no diga "out of stock" o "agotado" cerca
                idx = contenido.find(keyword.lower())
                zona = contenido[max(0, idx-100):idx+200]

                palabras_agotado = ["out of stock", "sold out", "agotado", "unavailable", "notify me"]
                agotado = any(p in zona for p in palabras_agotado)

                if not agotado:
                    print(f"  🎯 ENCONTRADO: '{keyword}' en {nombre}")
                    return keyword

        return None

    except Exception as e:
        print(f"  ⚠️  Error revisando {nombre}: {e}")
        return None


def monitorear():
    """Bucle principal de monitoreo"""
    print("=" * 60)
    print("🎴 POKEMON DROP MONITOR BOT")
    print("=" * 60)
    print(f"📧 Alertas a: {EMAIL}")
    print(f"⏱️  Revisando cada {INTERVALO} segundos")
    print(f"🔍 Buscando: {', '.join(KEYWORDS[:3])}...")
    print("=" * 60)
    print("Presiona Ctrl+C para detener\n")

    alertas_enviadas = set()  # Para no enviar el mismo alerta dos veces

    while True:
        hora = datetime.now().strftime("%H:%M:%S")
        print(f"[{hora}] Revisando tiendas...")

        for nombre, url in URLS.items():
            print(f"  → {nombre}...", end=" ")
            resultado = revisar_tienda(nombre, url)

            if resultado:
                clave = f"{nombre}_{resultado}"
                if clave not in alertas_enviadas:
                    print(f"🚨 DROP! Enviando alerta...")
                    enviar_email(nombre, url, resultado)
                    alertas_enviadas.add(clave)
                else:
                    print(f"(alerta ya enviada)")
            else:
                print("sin drops")

            time.sleep(2)  # Espera entre tiendas para no ser bloqueado

        print(f"  Próxima revisión en {INTERVALO} segundos...\n")
        time.sleep(INTERVALO)


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":
    monitorear()
