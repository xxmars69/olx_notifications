import os
import logging
import logging_config
from multiprocessing import Pool
from scraper_manager import OlxScraper
from database_manager import DatabaseManager
from notification_manager import Messenger
from utils import BASE_DIR


scraper = OlxScraper()
db = DatabaseManager()


def load_target_urls() -> list:
    """
    Fetch the list of URLs to monitor from the file 'target_urls.txt',
    which is located in the same directory as the script.

    Returns:
        list: list of URLs from which to collect data. If the
        file does not exist, it creates it and returns an empty list.

    """
    file_path = os.path.join(BASE_DIR, "target_urls.txt")
    user_message = f"The file 'target_urls.txt' has been created. Add " \
        + f"in it at least one URL to monitor for new ads. Add 1 URL per line."
    try:
        with open(file_path) as f:
            target_urls = [line.strip() for line in f]
    except FileNotFoundError:
        logging.info(user_message)
        open(file_path, "w").close()
        target_urls = []
    if not target_urls:
        logging.info(user_message)
    return target_urls


def get_new_ads_urls(all_urls: list) -> list:
    """
    Returns a list of new ad URLs (not found in the database). 

    Args:
        all_urls (list): list of URLs to be matched against the database.

    Returns:
        new_urls (list): List of URLs not found in the database.
    """
    new_urls = []
    if all_urls:
        for url in all_urls:
            if not db.url_exists(url):
                new_urls.append(url)
    return new_urls


def get_new_ads_urls_for_url(target_url: str) -> list:
    """
    Extracts ads for a specific URL and filters out previously processed ads.

    Args:
        target_url (str): A string representing the URL for which new ads should be retrieved.

    Returns:
        List[str]: A list of URLs representing new ads retrieved from the monitored URL.
    """

    try:
        ads_urls = scraper.scrape_ads_urls(target_url)
        logging.info(f"Scraper found {len(ads_urls)} total ads from {target_url}")
    except ValueError as error:
        logging.error(error)
        return []
    except Exception as e:
        logging.error(f"Unexpected error scraping {target_url}: {e}")
        return []
    
    new_urls = get_new_ads_urls(ads_urls)
    logging.info(f"Found {len(new_urls)} new ads (out of {len(ads_urls)} total)")
    return new_urls


def main() -> None:
    """
    Main function. Collects and processes ads
    and sends notifications via Telegram.
    """

    target_urls = load_target_urls()
    if not target_urls:
        logging.warning("No target URLs found in target_urls.txt")
        return
    
    logging.info(f"Starting scraper for {len(target_urls)} URL(s)")
    
    for target_url in target_urls:
        logging.info(f"Processing URL: {target_url}")
        # get_new_ads_urls_for_url already filters new ads, no need to filter again
        new_ads_urls = get_new_ads_urls_for_url(target_url)
        
        if not new_ads_urls:
            logging.info(f"No new ads found for {target_url}")
            continue

        logging.info(f"Found {len(new_ads_urls)} new ad URLs, processing...")

        # Process ads in parallel, for increased speed
        with Pool(10) as pool:
            new_ads = pool.map(scraper.get_ad_data, new_ads_urls)
        new_ads = list(filter(None, new_ads))

        if new_ads:
            logging.info(f"Successfully extracted {len(new_ads)} ads, sending notification...")
            message_subject, message_body = Messenger.generate_email_content(
                target_url, new_ads)
            Messenger.send_telegram_message(message_subject, message_body)
        else:
            logging.warning(f"Found {len(new_ads_urls)} new URLs but couldn't extract data from them")

        # Add the processed ads to database
        for url in new_ads_urls:
            db.add_url(url)
        
        logging.info(f"Completed processing for {target_url}")


if __name__ == "__main__":
    main()
