from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Product

DEMO_PRODUCTS = [
    {"title": "Mancuernas ajustables 20kg", "price": "89.99", "description": "Par de mancuernas ajustables con discos intercambiables, de 2 a 20kg cada una."},
    {"title": "Banda de resistencia set x5", "price": "24.99", "description": "Set de 5 bandas elásticas de distinta resistencia, ideales para entrenamiento en casa."},
    {"title": "Colchoneta de yoga premium", "price": "34.50", "description": "Colchoneta antideslizante de 6mm de grosor, incluye correa de transporte."},
    {"title": "Rodillo de espuma para masaje", "price": "19.99", "description": "Foam roller de alta densidad para liberación miofascial y recuperación muscular."},
    {"title": "Guantes de entrenamiento", "price": "15.00", "description": "Guantes acolchados con soporte de muñeca, talle único ajustable."},
    {"title": "Cuerda para saltar con contador", "price": "12.99", "description": "Cuerda de velocidad con rodamientos y contador digital de saltos."},
]


class Command(BaseCommand):
    help = "Crea productos de demo si la tabla de productos está vacía (uso: entornos recién desplegados sin acceso a /admin)."

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write("Ya hay productos cargados, no se crea nada.")
            return

        for data in DEMO_PRODUCTS:
            Product.objects.create(
                title=data["title"],
                slug=slugify(data["title"]),
                description=data["description"],
                price=data["price"],
                active=True,
            )

        self.stdout.write(f"Creados {len(DEMO_PRODUCTS)} productos de demo.")
