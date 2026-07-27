from parsers.xml_parser import XMLParser

parser = XMLParser("../reports/zap/xml/dvwa_scan_01.xml")

report = parser.parse()

print(report)