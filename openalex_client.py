from typing import Optional, Dict, Iterable, Union
import requests
import logging
from utils import EntityIdentifierDetector

logging.basicConfig(level=logging.INFO)

class APIRequestHandler:
    """Base class to manage and send API requests."""

    DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    def __init__(self, base_url: str, custom_headers: Optional[Dict[str, str]] = None, timeout: int = 15):
        self.base_url = base_url
        self.headers = self.DEFAULT_HEADERS.copy()
        if custom_headers:
            self.headers.update(custom_headers)
        self.timeout = timeout

    def send_request(self, endpoint: str, request_method: str = 'GET', query_parameters: Optional[Dict[str, any]] = None,
                     request_data: Optional[Union[Dict, str, bytes]] = None) -> Union[Dict, None]:
        """Send a request to the API and handle potential errors."""
        try:
            response = requests.request(
                method=request_method,
                url=f"{self.base_url}/{endpoint}",
                params=query_parameters,
                headers=self.headers,
                timeout=self.timeout,
                json=request_data if isinstance(request_data, Dict) else None,
                data=request_data if not isinstance(request_data, Dict) else None
            )
            response.raise_for_status()

            # Handle responses without content
            return response.json() if response.content else None
        except requests.HTTPError as http_err:
            # Handle HTTP errors here.
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except requests.Timeout:
            logging.error("Request timed out")
            raise
        except Exception as err:
            logging.error(f"An unexpected error occurred: {err}")
            raise


class OpenAlexClient(APIRequestHandler):
    """Client for managing requests to the OpenAlex API."""

    API_BASE_URL = "https://api.openalex.org"
    MAX_ITEMS_RETURNED = 1000
    MAX_ITEMS_PER_REQUEST = 200

    def __init__(self, user_email: Optional[str] = None, timeout_duration: int = 15):
        request_headers = {'Accept': 'application/json'}
        if user_email:
            request_headers['User-Agent'] = f'mailto:{user_email}'
        super().__init__(self.API_BASE_URL, request_headers, timeout_duration)
        
        self.identifier_detector = EntityIdentifierDetector()

    def fetch_single_entity(self, entity_name: str, entity_identifier: str, identifier_type: str = None) -> Dict:
        """Retrieve a specific entity based on its identifier."""
        
        if not entity_name:
            raise ValueError("The 'entity_name' argument cannot be empty or None.")
        if not entity_identifier:
            raise ValueError("The 'entity_identifier' argument cannot be empty or None.")
        if not identifier_type:
            identifier_type = self.identifier_detector.identify(entity_identifier)
            if not identifier_type:
                raise ValueError("The 'identifier_type' argument cannot be empty or None.")

        api_endpoint = f'{entity_name}/{identifier_type}:{entity_identifier}'
        return self.send_request(api_endpoint)

    def fetch_grouped_entities(self, entity_name: str, group_criteria: str, filtering_conditions: Optional[dict] = None,
                               search_term: Optional[str] = None, sorting_order: Optional[dict] = None) -> Dict:
        """Retrieve entities grouped based on a certain criteria."""

        if not entity_name:
            raise ValueError("The 'entity_name' argument cannot be empty.")
        if not group_criteria:
            raise ValueError("The 'group_criteria' argument cannot be empty.")

        parameters = {
            'group_by': group_criteria,
            'filter': self._convert_dict_to_string(filtering_conditions),
            'search': search_term,
            'sort': self._convert_dict_to_string(sorting_order)
        }
        return self.send_request(endpoint=entity_name, query_parameters=parameters)

    def fetch_list_entities(self, entity_name: str, 
                            filtering_conditions: Optional[dict] = None, search_term: Optional[str] = None, sorting_order: Optional[dict] = None, 
                            items_per_page: Optional[int] = None, starting_page: Optional[int] = None, max_pages: Optional[int] = None) -> Iterable:
        """Retrieve data from multiple pages of the API."""
        if not entity_name:
            raise ValueError("The 'entity_name' argument cannot be empty.")
        
        parameters = {
            'filter': self._convert_dict_to_string(filtering_conditions),
            'search': search_term,
            'sort': self._convert_dict_to_string(sorting_order)
        }

        items_per_page = min(max(1, items_per_page or 0), self.MAX_ITEMS_PER_REQUEST)
        parameters['per_page'] = items_per_page
        pages_to_traverse = max_pages or self.MAX_ITEMS_RETURNED // items_per_page

        pagination_type, initial_value = ('page', starting_page) if starting_page is not None else ('cursor', "*")
        yield from self._paginate_through_results(endpoint=entity_name, query_parameters=parameters, 
                                                  pagination_type=pagination_type, starting_value=initial_value, page_limit=pages_to_traverse)

    def _paginate_through_results(self, endpoint: str, query_parameters: Dict[str, any], pagination_type: str, starting_value: str, page_limit: int) -> Iterable:
        """Iteratively fetch data based on either page numbers or cursors."""

        query_parameters[pagination_type] = starting_value
        page_counter = 0
        while page_counter < page_limit:
            current_page_data = self.send_request(endpoint, query_parameters=query_parameters)
            yield current_page_data

            if pagination_type == 'page':
                next_value = query_parameters[pagination_type] + 1
            else:
                next_value = current_page_data['meta'].get('next_cursor')
                if not next_value:
                    break
            
            query_parameters[pagination_type] = next_value
            page_counter += 1

    def _convert_dict_to_string(self, dictionary: dict) -> str:
        if dictionary:
            return ",".join(f"{key}:{value}" for key, value in dictionary.items())
        return None