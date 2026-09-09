from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

SELENIUM_URL = "http://selenium:4444/wd/hub"
SEARCH_URL = (
    "https://www.amazon.com.mx/s?k=gym&__mk_es_MX=%C3%85M%C3%85%C5%BD%C3%95%C3%91"
    "&crid=1OW69KRQM1IVO&sprefix=gym%2Caps%2C190&ref=nb_sb_noss_1"
)


class Command(BaseCommand):
    help = "Scrapea el listado de productos de una búsqueda de Amazon usando Selenium + BeautifulSoup."

    def handle(self, *args, **options):
        options_ = Options()
        driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options_)

        try:
            driver.get(SEARCH_URL)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            cards = soup.select('div[data-component-type="s-search-result"]')
            self.stdout.write(f"Encontradas {len(cards)} tarjetas de producto\n")

            for card in cards:
                link_tag = card.find("a", class_=lambda c: c and "a-text-normal" in c)
                price_tag = card.select_one("span.a-price > span.a-offscreen")
                if not link_tag:
                    continue
                titulo = link_tag.get_text(strip=True)
                if not titulo:
                    continue
                self.stdout.write(f"título: {titulo}")
                self.stdout.write(f"link: {link_tag.get('href')}")
                self.stdout.write(f"precio: {price_tag.get_text(strip=True) if price_tag else 'N/A'}")
                self.stdout.write("")
        finally:
            driver.quit()
