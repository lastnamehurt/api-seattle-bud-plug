
import logging

from src.services.bud_finder import BudFinder


def search_deals_task():
    logging.info("Task: Updating Products")
    BudFinder().run()
