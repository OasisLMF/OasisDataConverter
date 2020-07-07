import csv
from io import StringIO, TextIOBase
from itertools import chain
from typing import Dict, Iterable


class BufferedCsvReader(TextIOBase):
    """
    Provides the source as a csv file like object. This helps some data
    processors as they are happier reading files rather than working on
    iterables.

    :param source: The iterable to build the csv from
    :param buffer: The current stored data
    """

    def __init__(self, source):
        self.source: Iterable[Dict[str, any]] = iter(source)
        self.buffer: str = ""
        self._first: bool = True

    def read(self, size=None):
        csv_file = StringIO(self.buffer)
        if size:
            while len(self.buffer) < size:
                try:
                    entry = next(self.source)
                    writer = csv.DictWriter(csv_file, fieldnames=entry.keys())

                    if self._first:
                        self._first = False
                        writer.writeheader()

                    writer.writerow(entry)
                except StopIteration:
                    break

            csv_content = csv_file.getvalue()
            response, self.buffer = csv_content[:size], csv_content[size:]
            return response
        else:
            first_elem = next(self.source)
            writer = csv.DictWriter(csv_file, fieldnames=first_elem.keys())
            writer.writeheader()
            writer.writerows(chain([first_elem], self.source))
            return csv_file.getvalue()
