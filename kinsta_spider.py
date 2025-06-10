import scrapy
import requests
import json

class KinstaSpider(scrapy.Spider):
    name = "kinsta"
    allowed_domains = []  # Initialize as empty list
    # start_urls = ["http://example.com"]  # Dummy URL, not actually used
    start_urls = [] # Initialize as empty list

    def __init__(self, kinsta_api_key=None, site_id=None, *args, **kwargs):
        super(KinstaSpider, self).__init__(*args, **kwargs)
        self.kinsta_api_key = kinsta_api_key
        self.site_id = site_id
        if not self.kinsta_api_key or not self.site_id:
            raise ValueError("Kinsta API key and Site ID must be provided.")
        self.headers = {
            "Authorization": f"Bearer {self.kinsta_api_key}",
            "Content-Type": "application/json"
        }

        # Load domains from domains.json
        with open("domains.json", "r") as f:
            self.domains_data = json.load(f)
            self.start_urls = [item["url"] for item in self.domains_data]
            self.allowed_domains = [item["domain"] for item in self.domains_data]

    def start_requests(self):
        # Start by clearing the cache
        for url in self.start_urls:
            yield scrapy.Request(
                url=f"https://api.kinsta.com/v2/sites/{self.site_id}/cache/clear",
                method="POST",
                headers=self.headers,
                callback=self.parse_clear_cache
            )

    def parse_clear_cache(self, response):
        if response.status == 204:
            self.log("Cache cleared successfully!")
            # Now, fetch plugins
            yield scrapy.Request(
                url=f"https://api.kinsta.com/v2/sites/{self.site_id}/plugins",
                headers=self.headers,
                callback=self.parse_plugins
            )
        else:
            self.log(f"Error clearing cache: {response.status} - {response.text}")

    def parse_plugins(self, response):
        try:
            data = json.loads(response.text)
            plugins = data.get("plugins", [])
            for plugin in plugins:
                yield {
                    "type": "plugin",
                    "name": plugin.get("name"),
                    "status": plugin.get("status")
                }

            # Now, fetch themes
            yield scrapy.Request(
                url=f"https://api.kinsta.com/v2/sites/{self.site_id}/themes",
                headers=self.headers,
                callback=self.parse_themes
            )

        except json.JSONDecodeError:
            self.log(f"Error decoding JSON: {response.text}")

    def parse_themes(self, response):
        try:
            data = json.loads(response.text)
            themes = data.get("themes", [])
            for theme in themes:
                yield {
                    "type": "theme",
                    "name": theme.get("name"),
                    "status": theme.get("status")
                }
        except json.JSONDecodeError:
            self.log(f"Error decoding JSON: {response.text}")