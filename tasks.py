from .app.services import SearchService


def search_deals_task():
    SearchService().run()
