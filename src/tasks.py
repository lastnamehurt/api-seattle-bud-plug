from src.services import SearchService
import logging


def search_deals_task():
    logging.info("Task: Updating Products")
    SearchService().run()
