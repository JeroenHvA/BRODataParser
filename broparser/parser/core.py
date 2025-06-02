# -*- coding: utf-8 -*-
from typing import Dict, List
import xml.etree.ElementTree as ET
from datetime import datetime

from well_filter import wellFilter, wellFilterData

class Well:

    def __init__(self, bro_id: str, well_surface_level: float, x_position: float, y_position: float):
        self.bro_id = bro_id
        self.well_observations: Dict[int, wellFilterData] = {}
        self.well_surface_level = well_surface_level
        self.x_position = x_position
        self.y_position = y_position

    def add_filters(self, well_number, wellobservation: wellFilterData) -> None:
        """ Add a well observation to the well."""
        self.well_observations[well_number] = wellobservation

    def get_filters(self, well_number: int) -> Dict[int, wellFilterData]:
        if well_number in self.well_observations.keys():
            return self.well_observations[well_number]
        else:
            print(f"well number {well_number} not found in observations.")
            return None
    def get_well_profile(self) -> List:
            return {f"{i} --> {v.well_bro_id}": {"top position": v.screen_top_position, 
                                    "bottom position": v.screen_bottom_position} 
                                    for i, v in self.well_observations.items()}

    def __str__(self):
        for well_number, observation in self.well_observations.items():
            print(observation)

    def __len__(self):
        return len(self.well_observations)
    


def parse_gmw_wells(file_path: str) -> Well:
    """Function to parse xml IMBRO or IMBRO/A data downloaded from DinoLoket as IMBRO-XML files

    Args:
        xml_root (ET.Element): the source of the Well data (starting with GMW)

    Returns:
        Well: a Well object containing the parsed data 
    """
    namespace = {
        "brocom": "http://www.broservices.nl/xsd/brocommon/3.0",
        "gmwcommon": "http://www.broservices.nl/xsd/gmwcommon/1.1",
        "gml": "http://www.opengis.net/gml/3.2",
        "": "http://www.broservices.nl/xsd/dsgmw/1.1",
    }
    tree = ET.parse(file_path)
    root = tree.getroot()
    gmw = root.find(".//{http://www.broservices.nl/xsd/dsgmw/1.1}GMW_PPO")
    bro_id = gmw.findtext("brocom:broId", namespaces=namespace)

    # Extract X, Y
    pos_text = gmw.find(".//gmwcommon:location/gml:pos", namespaces=namespace).text
    x, y = map(float, pos_text.strip().split())

    # Extract surface level
    surface_level = float(gmw.find(".//gmwcommon:groundLevelPosition", namespaces=namespace).text)

    _well = Well(bro_id=bro_id, well_surface_level=surface_level, x_position=x, y_position=y)

    for well in gmw.findall("monitoringTube", namespaces=namespace):
        well_number = int(well.findtext("tubeNumber", namespaces=namespace))
        screen = well.find("screen", namespaces=namespace)
        screen_length = float(screen.findtext("screenLength", namespaces=namespace))
        screen_top = float(screen.findtext("screenTopPosition", namespaces=namespace))
        screen_bottom = float(screen.findtext("screenBottomPosition", namespaces=namespace))

        well_observation = wellFilter(
            gld_bro_id=bro_id,
            well_number=well_number,
            well_bro_id=well.findtext("brocom:broId", namespaces=namespace)
        )
        well_observation.add_metadata(
            screen_length=screen_length,
            screen_top_position=screen_top,
            screen_bottom_position=screen_bottom
        )
        _well.add_filters(
            int(well_number), well_observation
        )
        
    return _well

def xml_append_well_observations(file_path: str, well: Well) -> Well:
    # Register namespaces with prefixes
    namespaces = {
        'dsgld': 'http://www.broservices.nl/xsd/dsgld/1.0',
        'gldcommon': 'http://www.broservices.nl/xsd/gldcommon/1.0',
        'brocom': 'http://www.broservices.nl/xsd/brocommon/3.0',
        'gml': 'http://www.opengis.net/gml/3.2',
        'om': 'http://www.opengis.net/om/2.0',
        'waterml': 'http://www.opengis.net/waterml/2.0',
    }

    # Load and parse the XML file
    tree = ET.parse(file_path)  # replace with actual file path
    root = tree.getroot()

    # Extract broId and wellNumber
    common_bro_id = root.find('.//gldcommon:broId', namespaces).text
    well_number = root.find('.//gldcommon:tubeNumber', namespaces).text
    well_bro_id = [f for f in file_path.split('\\')][-1][:-4]

    # Create instance
    if not int(well_number) in well.well_observations.keys():
        wellobservation = wellFilter(common_bro_id, well_number, well_bro_id)
    else:
        wellobservation = well.get_filters(int(well_number))
        wellobservation.well_bro_id = well_bro_id

    # Loop over all observations
    observations = root.findall('.//om:OM_Observation', namespaces)
    for obs in observations:
        # Loop over all MeasurementTVP points
        tvps = obs.findall('.//waterml:MeasurementTVP', namespaces)
        for tvp in tvps:
            time_el = tvp.find('waterml:time', namespaces)
            value_el = tvp.find('waterml:value', namespaces)
            if time_el.text is not None:
                value = value_el.text
                if value is None:
                    value = (-9999)
                v = [float(value), ""]
                e = wellobservation.dataset.add_observation(time_el.text, v, None, True)
                if e != None:
                    print(e)
                #print("added observation:", time_el.text, value_el.text)
    wellobservation.dataset.add_columns(
            columns=["dateTime", "GWS+NAP", "Toelichting"]
        )
    wellobservation.dataset.order()
    well.add_filters(int(well_number), wellobservation)
    # Save the updated XML file
    return well
