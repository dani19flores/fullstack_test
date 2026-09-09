from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

SELENIUM_URL = "http://selenium:4444/wd/hub"
BASE_URL = "https://www.amazon.com.mx"
SEARCH_URL = (
    "https://www.amazon.com.mx/s?k=gym&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91"
    "&crid=1OW69KRQM1IVO&sprefix=gym%2Caps%2C190&ref=nb_sb_noss_1"
)
MAX_PRODUCTS = 5


class Command(BaseCommand):
    help = (
        "Scraper de dos pasos: recorre el listado de una búsqueda de Amazon "
        "para sacar los links a cada producto, y luego entra a cada vista de "
        "detalle para extraer título, precio, calificación, disponibilidad, "
        "descripción e imagen."
    )

    def handle(self, *args, **options):
        options_ = Options()
        driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options_)

        try:
            links = self.get_product_links(driver)
            self.stdout.write(f"Encontrados {len(links)} links de producto en el listado\n")

            for link in links[:MAX_PRODUCTS]:
                data = self.get_product_detail(driver, link)
                self.print_product(data)
        finally:
            driver.quit()

    def get_product_links(self, driver):
        """Vista de listado: junta los links a cada vista de detalle."""
        driver.get(SEARCH_URL)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        cards = soup.select('div[data-component-type="s-search-result"]')
        links = []
        for card in cards:
            link_tag = card.find("a", class_=lambda c: c and "a-text-normal" in c)
            if not link_tag or not link_tag.get("href"):
                continue
            links.append(urljoin(BASE_URL, link_tag["href"]))
        return links

    def get_product_detail(self, driver, url):
        """Vista de detalle: extrae los datos relevantes de un producto puntual."""
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title = soup.select_one("#productTitle")
        price = soup.select_one("span.a-price > span.a-offscreen")
        rating = soup.select_one("span.a-icon-alt")
        availability = soup.select_one("#availability span")
        bullets = soup.select("#feature-bullets li span.a-list-item")
        image = soup.select_one("#landingImage")

        return {
            "url": url,
            "title": title.get_text(strip=True) if title else None,
            "price": price.get_text(strip=True) if price else None,
            "rating": rating.get_text(strip=True) if rating else None,
            "availability": availability.get_text(strip=True) if availability else None,
            "description": [b.get_text(strip=True) for b in bullets],
            "image": image.get("src") if image else None,
        }

    def print_product(self, data):
        self.stdout.write(f"título: {data['title']}")
        self.stdout.write(f"precio: {data['price']}")
        self.stdout.write(f"calificación: {data['rating']}")
        self.stdout.write(f"disponibilidad: {data['availability']}")
        self.stdout.write(f"imagen: {data['image']}")
        self.stdout.write("descripción:")
        for bullet in data["description"]:
            self.stdout.write(f"  - {bullet}")
        self.stdout.write(f"url: {data['url']}")
        self.stdout.write("")
