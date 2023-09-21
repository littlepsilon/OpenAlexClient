# OpenAlexClient

A Python client for managing requests to the OpenAlex API.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/littlepsilon/OpenAlexClient.git
```

2. Navigate to the directory:

```bash
cd OpenAlexClient
```

## Usage

### Initialization

```python
from openalex_client import OpenAlexClient

# Initialize the client. You can provide a user email if you have one.
client = OpenAlexClient(user_email="your_email@example.com")
```

### Fetching a Single Entity

```python
entity_name = "works"
entity_identifier = "your_identifier_here"  # Replace with a DOI, PMID, etc.
result = client.fetch_single_entity(entity_name, entity_identifier)
print(result)
```

### Fetching Entities Grouped by Criteria

```python
group_criteria = "your_grouping_criteria_here"
filtering_conditions = {"key1": "value1", "key2": "value2"}
search_term = "your_search_term_here"
sorting_order = {"key": "asc"}  
grouped_results = client.fetch_grouped_entities(entity_name, group_criteria, filtering_conditions, search_term, sorting_order)
print(grouped_results)
```

### Fetching a List of Entities

```python
filtering_conditions = {"key1": "value1", "key2": "value2"}
search_term = "your_search_term_here"
sorting_order = {"key": "asc"}
items_per_page = 100
starting_page = 1
max_pages = 5
list_results = client.fetch_list_entities(entity_name, filtering_conditions, search_term, sorting_order, items_per_page, starting_page, max_pages)
print(list(list_results))
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
