from pathlib import Path

from parsers.json_parser import JSONParser
from parsers.xml_parser import XMLParser

SUPPORTED_EXTENSIONS = (".xml", ".json")


def get_parser(path):
    """Pick the ZAP report parser from the file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".xml":
        return XMLParser(path)
    if suffix == ".json":
        return JSONParser(path)
    raise ValueError(f"Unsupported report type '{suffix}'. Upload a ZAP .xml or .json report.")


def parse_report(path):
    return get_parser(path).parse()
