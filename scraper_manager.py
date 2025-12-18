import re
import requests
import logging
import logging_config
from multiprocessing import Pool
from urllib.parse import urlparse
from bs4 import BeautifulSoup, ResultSet, Tag
from utils import get_header


class OlxScraper:
    """Class used to scrape data from OLX Romania."""

    def __init__(self):
        self.headers = get_header()
        self.netloc = "www.olx.ro"
        self.schema = "https"
        self.current_page = 1
        self.last_page = None

    def parse_content(self, target_url: str) -> BeautifulSoup:
        """
        Parse content from a given URL.

        Args:
            target_url (str): A string representing the URL to be processed.

        Returns:
            BeautifulSoup: An object representing the processed content,
            or None in case of error.
        """
        import time
        try:
            # Add delay to avoid 403 errors
            time.sleep(1)
            r = requests.get(target_url, headers=self.headers, timeout=60)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.error(f"Connection error: {error}")
            return None
        else:
            parsed_content = BeautifulSoup(r.text, "html.parser")
            return parsed_content

    def get_ads(self, parsed_content: BeautifulSoup) -> ResultSet[Tag]:
        """
        Returns all ads found on the parsed web page.

        Args:
            parsed_content (BeautifulSoup): a BeautifulSoup object created as
            a result of parsing the web page.

        Returns:
            ResultSet[Tag]: A ResultSet containing all HTML tags that contain ads.
        """
        if parsed_content is None:
            return None
        ads = parsed_content.select("div.css-1sw7q4x")
        if len(ads) == 0:
            logging.warning("No ads found with selector 'div.css-1sw7q4x' - HTML structure may have changed")
        return ads

    def get_last_page(self, parsed_content: BeautifulSoup) -> int:
        """
        Returns the number of the last page available for processing.

        Args:
            parsed_content (BeautifulSoup): a BeautifulSoup object created
            as a result of parsing the web page.

        Returns:
            int: The number of the last page available for parsing. If
            there is no paging or the parsed object is None, it will return None.
        """
        if parsed_content is not None:
            pagination_ul = parsed_content.find("ul", class_="pagination-list")
            if pagination_ul is not None:
                pages = pagination_ul.find_all("li", class_="pagination-item")
                if pages:
                    return int(pages[-1].text)
        return None

    def scrape_ads_urls(self, target_url: str, max_pages: int = 2) -> list:
        """
        Scrapes the URLs of all valid ads present on an OLX page. 
        Only scrapes the first few pages to get the most recent ads.

        Args:
            target_url (str): URL of the OLX page to start the search from.
            max_pages (int): Maximum number of pages to scrape (default: 2 for recent ads only).

        Returns:
            list: a list of relevant URLs of the ads found on the page.

        Raises:
            ValueError: If the URL is invalid or does not belong to the specified domain.
        """
        ads_links = set()
        # Reset page counter for each new scrape
        self.current_page = 1
        self.last_page = None
        
        # Remove query parameters for proper pagination
        clean_url = target_url.split('?')[0] if '?' in target_url else target_url
        # Remove trailing slash to avoid double slashes
        clean_url = clean_url.rstrip('/')
        has_query_params = '?' in target_url
        logging.info(f"Scraping URL: {clean_url} (original had query params: {has_query_params}, max pages: {max_pages})")
        
        if self.netloc != urlparse(clean_url).netloc:
            raise ValueError(
                f"Bad URL! OLXRadar is configured to process {self.netloc} links only.")
        
        while self.current_page <= max_pages:
            url = f"{clean_url}/?page={self.current_page}"
            logging.debug(f"Fetching page {self.current_page}: {url}")
            parsed_content = self.parse_content(url)
            
            if parsed_content is None:
                logging.warning(f"Failed to parse page {self.current_page}, stopping")
                break
                
            ads = self.get_ads(parsed_content)
            
            if ads is None or len(ads) == 0:
                logging.info(f"No ads found on page {self.current_page}, stopping")
                break
                
            logging.info(f"Found {len(ads)} ads on page {self.current_page}")
            
            ads_before_filter = len(ads_links)
            links_found = 0
            links_no_href = 0
            links_not_internal = 0
            links_not_relevant = 0
            links_added = 0
            
            for ad in ads:
                link = ad.find("a", class_="css-rc5s2u")
                if link is None:
                    # Try to find link with any class or without class
                    link = ad.find("a")
                    if link is None:
                        continue
                    else:
                        logging.warning(f"Link found without expected class 'css-rc5s2u' on page {self.current_page}")
                
                if link is not None:
                    links_found += 1
                    if not link.has_attr("href"):
                        links_no_href += 1
                        continue
                        
                    link_href = link["href"]
                    original_href = link_href
                    
                    if not self.is_internal_url(link_href, self.netloc):
                        links_not_internal += 1
                        logging.debug(f"Skipped non-internal URL: {link_href}")
                        continue
                        
                    if not self.is_relevant_url(link_href):
                        links_not_relevant += 1
                        logging.debug(f"Skipped non-relevant URL (has query params): {link_href}")
                        continue
                        
                    if self.is_relative_url(link_href):
                        link_href = f"{self.schema}://{self.netloc}{link_href}"
                    
                    ads_links.add(link_href)
                    links_added += 1
            
            ads_added = len(ads_links) - ads_before_filter
            logging.info(f"Page {self.current_page} stats: {links_found} links found, {links_no_href} without href, {links_not_internal} not internal, {links_not_relevant} not relevant, {links_added} URLs added")
            
            # Stop if we've reached max pages
            if self.current_page >= max_pages:
                logging.info(f"Reached max pages limit ({max_pages}), stopping")
                break
                
            self.current_page += 1
            
        logging.info(f"Total ads scraped from {self.current_page} page(s): {len(ads_links)}")
        return list(ads_links)

    def is_relevant_url(self, url: str) -> bool:
        """
        Determines whether a particular URL is relevant by analyzing the query segment it contains.

        Args:
            url (str): A string representing the URL whose relevance is to be checked.

        Returns:
            bool: True if the URL is relevant, False if not.

        The query (or search) segments, such as "?reason=extended-region", show that the ad
        is added to the search results list by OLX when there are not enough ads
        available for the user's region. Therefore, such a URL is not useful
        (relevant) for monitoring.
        """
        segments = urlparse(url)
        if segments.query != "":
            return False
        return True

    def is_internal_url(self, url: str, domain: str) -> bool:
        """
        Checks if the URL has the same domain as the page it was taken from.

        Args:
            url (str): the URL to check.
            domain (str): Domain of the current page.

        Returns:
            bool: True if the URL is an internal link, False otherwise.
        """
        # URL starts with "/"
        if self.is_relative_url(url):
            return True
        parsed_url = urlparse(url)
        if parsed_url.netloc == domain:
            return True
        return False

    def is_relative_url(self, url: str) -> bool:
        """
        Check if the given url is relative or absolute.

        Args:
            url (str): url to check.

        Returns:
            True if the url is relative, otherwise False.
        """

        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return True
        if re.search(r"^\/[\w.\-\/]+", url):
            return True
        return False

    def get_ad_data(self, ad_url: str) -> dict[str]:
        """
        Extracts data from the HTML page of the ad.

        Args:
            ad_url (str): the URL of the ad.

        Returns:
            dict or None: A dictionary containing the scraped ad data
            or None if the required information is missing.
        """
        logging.debug(f"Processing {ad_url}")
        content = self.parse_content(ad_url)

        if content is None:
            logging.warning(f"Could not parse content for {ad_url}")
            return None

        # Try multiple selectors for title
        title = None
        title_selectors = [
            ("h1", {"class": "css-1soizd2"}),
            ("h1", {}),
            ("h1", {"data-cy": "ad_title"}),
        ]
        for tag, attrs in title_selectors:
            title_elem = content.find(tag, attrs)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # Try multiple selectors for price
        price = None
        price_selectors = [
            ("h3", {"class": "css-ddweki"}),
            ("h3", {}),
            ("p", {"data-testid": "ad-price"}),
            ("span", {"data-testid": "ad-price"}),
        ]
        for tag, attrs in price_selectors:
            price_elem = content.find(tag, attrs)
            if price_elem:
                price = price_elem.get_text(strip=True)
                if price and ("lei" in price.lower() or "ron" in price.lower() or "€" in price or "$" in price):
                    break
        
        # Try multiple selectors for description
        description = None
        desc_selectors = [
            ("div", {"class": "css-bgzo2k"}),
            ("div", {"data-cy": "ad_description"}),
            ("div", {"class": "css-1g5z7m2"}),
        ]
        for tag, attrs in desc_selectors:
            desc_elem = content.find(tag, attrs)
            if desc_elem:
                description = desc_elem.get_text(strip=True, separator="\n")
                if description and len(description) > 10:  # Make sure it's not empty
                    break
        
        seller = None
        if content.find("h4", class_="css-1lcz6o7"):
            seller = content.find(
                "h4", class_="css-1lcz6o7").get_text(strip=True)
        
        if any(item is None for item in [title, price, description]):
            logging.warning(f"Missing data for {ad_url}: title={title is not None}, price={price is not None}, desc={description is not None}")
            return None
        
        ad_data = {
            "title": title,
            "price": price,
            "url": ad_url,
            "description": description
        }
        return ad_data
