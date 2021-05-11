import xml.etree.ElementTree as ET
import argparse
import json

from pathlib import Path

# Layout of Response JSON
res = {
    "flightNumber": "",
    "departureAirport": "",
    "arrivalAirport": "",
    "departureDate": "",
    "cabins": []
}

# Namespaces seatmap1
ns_sm_1 = {
    "soapenc": "http://schemas.xmlsoap.org/soap/encoding/",
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "xsd": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "ns":"http://www.opentravel.org/OTA/2003/05/common/"
}
    
def main():
    parser = argparse.ArgumentParser(description="Convert Seat Map Flight from XML to JSON")
    parser.add_argument("filepath", type=check_dir_path, nargs="+", help="Check 'filepath' for XML File")

    res = {}

    args = parser.parse_args()
    filepath = args.filepath[0]
    path = Path(filepath)

    if (filepath[-5 : ] == "1.xml"):
        res = parse_seatmap1(path)
    else:
        raise argparse.ArgumentTypeError(f"{filepath} is not in checklist")

    new_path = export_new_json(path, res)
    
    print(f"JSON result created of '{filepath}' in new file '{new_path}'")

# EXport JSON file
def export_new_json(filename, res):
    new_path = Path(str(filename.stem) + "_parsed.json")
    with open(new_path, 'w+') as f:
        json.dump(res, f, indent=4)
        return new_path

# XML File Datatype
def check_dir_path(path):
    if (Path(path) and path[-4 : ] == ".xml"):
        return path
    raise argparse.ArgumentTypeError(f"{path} is not a valid path, must be an XML file")  

def parse_xml(path):
    return ET.parse(path) # Parses XML File

def parse_seatmap1(xml):    
    tree = parse_xml(xml) # Parses XML File
    
    # Get Flight Details in Response JSON
    flight = tree.getroot()[0][0][1][0]

    flight_info = flight.find("ns:FlightSegmentInfo", ns_sm_1)
    res["departureDate"] = flight_info.attrib["DepartureDateTime"]
    res["flightNumber"] = flight_info.attrib["FlightNumber"]
    res["departureAirport"] = flight_info.find("ns:DepartureAirport", ns_sm_1).attrib["LocationCode"]
    res["arrivalAirport"] = flight_info.find("ns:ArrivalAirport", ns_sm_1).attrib["LocationCode"]

    for cabin in flight.find("ns:SeatMapDetails", ns_sm_1):
        cabinResult = {
            "type": cabin[0].attrib["CabinType"],
            "layout": cabin.attrib["Layout"],
            "numCols": len(cabin.attrib["Layout"].replace(" ", "")),
            "numRows": 0,
            "seats": []
        }

        # Seat Objects to Cabin
        for row in cabin:
            cabinRowList = []

            for seat in row:
                summary = seat.find("ns:Summary", ns_sm_1)
                service = seat.find("ns:Service", ns_sm_1)
                fee = service.find("ns:Fee", ns_sm_1) if service != None else None
                tags = []
                for feature in seat.findall("ns:Features", ns_sm_1):
                    if feature.attrib == {}:
                        tags.append(feature.text)

                # Seat JSON
                seatResult = {
                    "tags": tags,
                    "number": summary.attrib["SeatNumber"] if summary != None else "N/A",
                    "available": summary.attrib["AvailableInd"] if summary != None else "N/A",
                    "fee": {
                        "amount": fee.attrib["Amount"] if fee != None else "N/A",
                        "currencyCode": fee.attrib["CurrencyCode"] if fee != None else "N/A",
                    }
                }


                cabinRowList.append(seatResult)
            
            cabinResult["seats"].append(cabinRowList)        
            cabinResult["numRows"] += 1

        res["cabins"].append(cabinResult)

    return res

if __name__ == "__main__":
    main()