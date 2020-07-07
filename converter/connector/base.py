from typing import Any, Dict, Iterable

from converter.config import Config


class BaseConnector:
    """
    Connects to the the data source

    :param config: The global config for the system
    """

    def __init__(self, config: Config, **options):
        self._options = options
        self.config = config

    def extract(self) -> Iterable[Dict[str, Any]]:
        """
        Extracts the data from the connected source and returns
        an iterable of dictionaries.

        :return: An iterable of the extracted data
        """
        raise NotImplementedError()

    def load(self, data: Iterable[Dict[str, Any]]):
        """
        Loads the data into the connected data object.

        :param data: An iterable of dictionaries representing
            the data to push to the connected source.
        """
        raise NotImplementedError()
