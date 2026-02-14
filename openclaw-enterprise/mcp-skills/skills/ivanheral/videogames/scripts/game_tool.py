#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import sys
import argparse
from typing import Optional, Dict, Any, List

# Constants
STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/?term={term}&l=spanish&cc=ES"
STEAM_DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appid}&l=spanish"
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories/?l=spanish&cc=ES"
STEAM_PLAYERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"
STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=3&maxlength=300&format=json"
STEAM_MOST_PLAYED_URL = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
STEAM_ACHIEVEMENTS_URL = "https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}"
STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}?json=1&language=spanish&purchase_type=all&filter=summary"

CHEAPSHARK_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals?title={term}&limit=10"
CHEAPSHARK_STORES_URL = "https://www.cheapshark.com/api/1.0/stores"

def _make_request(url: str) -> Optional[Any]:
    """Helper para realizar peticiones HTTP y devolver JSON."""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error de red al conectar con {url}: {e}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar respuesta JSON de {url}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error inesperado al consultar {url}: {e}", file=sys.stderr)
    return None

def _get_store_map() -> Dict[str, str]:
    """Obtiene un mapa de ID de tienda a Nombre de tienda desde CheapShark."""
    data = _make_request(CHEAPSHARK_STORES_URL)
    store_map = {}
    if data:
        for store in data:
            if store.get('isActive') == 1:
                store_map[store['storeID']] = store['storeName']
    return store_map

# --- CheapShark Functions ---

def search_deals(args: argparse.Namespace) -> None:
    """Busca ofertas en múltiples tiendas usando CheapShark."""
    term = args.term
    encoded_term = urllib.parse.quote(term)
    url = CHEAPSHARK_DEALS_URL.format(term=encoded_term)
    
    data = _make_request(url)
    if not data:
        print(f"No se encontraron ofertas para '{term}'.")
        return

    stores = _get_store_map()

    print(f"--- Mejores Ofertas para '{term}' ---")
    # CheapShark devuelve una lista de ofertas.
    for deal in data:
        title = deal.get('title')
        store_id = deal.get('storeID')
        store_name = stores.get(store_id, f"Tienda {store_id}")
        price = float(deal.get('salePrice', 0))
        normal_price = float(deal.get('normalPrice', 0))
        savings = float(deal.get('savings', 0))
        deal_rating = deal.get('dealRating', '0')
        link = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}"

        if savings > 0:
            price_str = f"{normal_price:.2f} -> {price:.2f} USD (-{savings:.0f}%)"
        else:
            price_str = f"{price:.2f} USD"

        print(f"- {title}")
        print(f"  Tienda: {store_name}")
        print(f"  Precio: {price_str}")
        print(f"  Link: {link}\n")

# --- Steam Functions ---

def search_game(args: argparse.Namespace) -> None:
    """Buscador de juegos en la tienda de Steam."""
    term = args.term
    encoded_term = urllib.parse.quote(term)
    url = STEAM_SEARCH_URL.format(term=encoded_term)
    
    data = _make_request(url)
    
    if not data or 'items' not in data or not data['items']:
        print(f"No se encontraron juegos para '{term}'.")
        return

    print(f"Resultados en Steam para '{term}':")
    for item in data['items']:
        price = "Gratis"
        if item.get('price'):
            price = f"{item['price']['final'] / 100:.2f} {item['price']['currency']}"
        print(f"- {item['name']} (ID: {item['id']}) - {price}")

def get_game_details(args: argparse.Namespace) -> None:
    """Obtiene detalles de un juego por su AppID."""
    appid = args.appid
    url = STEAM_DETAILS_URL.format(appid=appid)
    
    data = _make_request(url)
    
    if not data or str(appid) not in data or not data[str(appid)]['success']:
        print(f"No se pudieron obtener detalles para el AppID {appid}.")
        return

    game_data = data[str(appid)]['data']
    name = game_data.get('name', 'Desconocido')
    desc = game_data.get('short_description', 'Sin descripción.')
    devs = ", ".join(game_data.get('developers', []))
    publishers = ", ".join(game_data.get('publishers', []))
    
    price_overview = game_data.get('price_overview')
    price = "Gratis/Desconocido"
    if price_overview:
        price = price_overview.get('final_formatted', 'N/A')
    elif game_data.get('is_free'):
        price = "Gratis"

    metacritic = "N/A"
    if 'metacritic' in game_data:
        metacritic = game_data['metacritic'].get('score', 'N/A')

    release_date_data = game_data.get('release_date', {})
    release_date = release_date_data.get('date', 'Desconocida')
    coming_soon = release_date_data.get('coming_soon', False)
    status = " (Próximamente)" if coming_soon else ""

    print(f"--- Detalles de {name} ---")
    print(f"ID: {appid}")
    print(f"Precio: {price}")
    print(f"Lanzamiento: {release_date}{status}")
    print(f"Metacritic: {metacritic}")
    print(f"Desarrolladores: {devs}")
    print(f"Publishers: {publishers}")
    print(f"Descripción: {desc}")

def get_specials(args: argparse.Namespace) -> None:
    """Obtiene las ofertas destacadas de la tienda de Steam."""
    url = STEAM_FEATURED_URL
    
    data = _make_request(url)
    
    if not data or 'specials' not in data or 'items' not in data['specials']:
        print("No se pudieron obtener ofertas especiales en este momento.")
        return

    print("--- Ofertas Destacadas en Steam ---")
    for item in data['specials']['items']:
        discount = item.get('discount_percent', 0)
        orig_price = item.get('original_price')
        final_price = item.get('final_price')
        currency = item.get('currency', 'EUR')
        
        price_str = ""
        if orig_price and final_price:
            price_str = f"{orig_price/100:.2f} -> {final_price/100:.2f} {currency} (-{discount}%)"
        else:
            price_str = "Gratis/Desconocido"
            
        print(f"- {item['name']} (ID: {item['id']}) - {price_str}")

def get_player_count(args: argparse.Namespace) -> None:
    """Obtiene el número de jugadores actuales para un AppID."""
    appid = args.appid
    url = STEAM_PLAYERS_URL.format(appid=appid)
    
    data = _make_request(url)
    
    if not data or 'response' not in data or data['response'].get('result') != 1:
        print(f"No se pudo obtener el conteo de jugadores para el ID {appid}.")
        return

    count = data['response'].get('player_count', 0)
    print(f"Jugadores actuales para ID {appid}: {count:,}")

def get_news(args: argparse.Namespace) -> None:
    """Obtiene las noticias más recientes de un juego."""
    appid = args.appid
    url = STEAM_NEWS_URL.format(appid=appid)
    
    data = _make_request(url)
    
    if not data or 'appnews' not in data or not data['appnews'].get('newsitems'):
        print(f"No hay noticias disponibles para el ID {appid}.")
        return

    print(f"--- Últimas Noticias para ID {appid} ---")
    for item in data['appnews']['newsitems']:
        print(f"- {item['title']}")
        print(f"  URL: {item['url']}\n")

def get_trends(args: argparse.Namespace) -> None:
    """Obtiene tendencias (más vendidos y novedades)."""
    url = STEAM_FEATURED_URL
    
    data = _make_request(url)
    
    if not data:
        print("No se pudieron obtener tendencias.")
        return

    if 'top_sellers' in data:
        print("--- Lo más vendido en Steam ---")
        for item in data['top_sellers']['items'][:5]:
            print(f"- {item['name']} (ID: {item['id']})")
    
    print("\n--- Nuevos Lanzamientos ---")
    if 'new_releases' in data:
        for item in data['new_releases']['items'][:5]:
            print(f"- {item['name']} (ID: {item['id']})")

def get_most_played(args: argparse.Namespace) -> None:
    """Obtiene los juegos con más jugadores concurrentes actualmente."""
    url = STEAM_MOST_PLAYED_URL
    
    data = _make_request(url)
    
    if not data or 'response' not in data or 'ranks' not in data['response']:
        print("No se pudieron obtener los juegos más jugados.")
        return

    print("--- Top Juegos por Jugadores Online ---")
    for rank in data['response']['ranks'][:10]:
        appid = rank['appid']
        peak = rank.get('peak_in_game', 0)
        print(f"Posición {rank['rank']}: AppID {appid} - Pico de jugadores: {peak:,}")
    
    print("\n(Usa 'details <ID>' para saber el nombre de un juego específico)")

def get_achievements(args: argparse.Namespace) -> None:
    """Obtiene los porcentajes globales de logros para un juego."""
    appid = args.appid
    url = STEAM_ACHIEVEMENTS_URL.format(appid=appid)
    
    data = _make_request(url)
    
    if not data or 'achievementpercentages' not in data:
        print(f"No hay datos de logros para el ID {appid}.")
        return

    achievements = data['achievementpercentages']['achievements']
    print(f"--- Logros más raros para ID {appid} ---")
    sorted_ach = sorted(achievements, key=lambda x: x['percent'])
    for ach in sorted_ach[:5]:
        percent_val = float(ach['percent'])
        print(f"- {ach['name']}: {percent_val:.2f}% de los jugadores")

def get_reviews(args: argparse.Namespace) -> None:
    """Obtiene un resumen de las reseñas de los usuarios."""
    appid = args.appid
    url = STEAM_REVIEWS_URL.format(appid=appid)
    
    data = _make_request(url)
    
    if not data or 'query_summary' not in data:
        print(f"No se pudo obtener el resumen de reseñas para el ID {appid}.")
        return

    summary = data['query_summary']
    score_desc = summary.get('review_score_desc', 'N/A')
    total_pos = summary.get('total_positive', 0)
    total_rev = summary.get('total_reviews', 0)
    
    percent = (total_pos / total_rev * 100) if total_rev > 0 else 0
    
    print(f"--- Resumen de Reseñas para ID {appid} ---")
    print(f"Calificación: {score_desc}")
    print(f"Porcentaje Positivo: {percent:.1f}%")
    print(f"Total de reseñas: {total_rev:,}")

def main():
    parser = argparse.ArgumentParser(description="Herramienta unificada para videojuegos (Steam y CheapShark)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Steam Commands ---
    
    search_parser = subparsers.add_parser("search", help="Buscar un juego en Steam")
    search_parser.add_argument("term", type=str, help="Término de búsqueda")
    search_parser.set_defaults(func=search_game)

    details_parser = subparsers.add_parser("details", help="Obtener detalles de Steam por ID")
    details_parser.add_argument("appid", type=int, help="AppID del juego")
    details_parser.set_defaults(func=get_game_details)

    offers_parser = subparsers.add_parser("offers", help="Ver ofertas destacadas de Steam")
    offers_parser.set_defaults(func=get_specials)

    players_parser = subparsers.add_parser("players", help="Ver jugadores actuales (Steam)")
    players_parser.add_argument("appid", type=int, help="AppID del juego")
    players_parser.set_defaults(func=get_player_count)

    news_parser = subparsers.add_parser("news", help="Ver noticias de un juego (Steam)")
    news_parser.add_argument("appid", type=int, help="AppID del juego")
    news_parser.set_defaults(func=get_news)

    trends_parser = subparsers.add_parser("trends", help="Ver tendencias de Steam")
    trends_parser.set_defaults(func=get_trends)

    top_parser = subparsers.add_parser("top", help="Ver juegos con más jugadores en Steam")
    top_parser.set_defaults(func=get_most_played)

    ach_parser = subparsers.add_parser("achievements", help="Ver logros globales (Steam)")
    ach_parser.add_argument("appid", type=int, help="AppID del juego")
    ach_parser.set_defaults(func=get_achievements)

    rev_parser = subparsers.add_parser("reviews", help="Ver resumen de reseñas (Steam)")
    rev_parser.add_argument("appid", type=int, help="AppID del juego")
    rev_parser.set_defaults(func=get_reviews)

    # --- CheapShark Commands ---

    deal_parser = subparsers.add_parser("deals", help="Buscar mejores ofertas en todas las tiendas (CheapShark)")
    deal_parser.add_argument("term", type=str, help="Nombre del juego")
    deal_parser.set_defaults(func=search_deals)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
