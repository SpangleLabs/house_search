import json

from scraper import RightMoveScraper, ZooplaScraper

with open("config.json") as f:
    config = json.load(f)


scrapers = [
    RightMoveScraper(),
    ZooplaScraper(config["zoopla_key"])
]

if __name__ == '__main__':
    location = "Cambridge"
    rentals = []
    for scraper in scrapers:
        rentals += scraper.get_cambridge_rentals()
    rentals = sorted(rentals, key=lambda x: x.price)
    print(rentals)
