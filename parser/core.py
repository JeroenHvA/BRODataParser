# -*- coding: utf-8 -*-
from typing import Dict, List
import xml.etree.ElementTree as ET

from filter import wellFilter

class Well:

    def __init__(self, bro_id: str, well_surface_level: float, x_position: float, y_position: float):
        self.bro_id = bro_id
        self.well_filter: Dict[int, wellFilter] = {}
        self.well_surface_level = well_surface_level
        self.x_position = x_position
        self.y_position = y_position

    def add_filters(self, well_number, well_filter: wellFilter) -> None:
        """ This function adds a wellFilter object to the well object.

        Args:
            well_number (_type_): Number of the filter, used to identify the filter in the well (tubeNumber)
            well_filter (wellFilter): wellFilter object containing the filter data
        """
        self.well_filter[well_number] = well_filter

    def get_filters(self, well_number: int) -> wellFilter:
        """Get the filter object for a given well number.

        Args:
            well_number (int): number of the filter in the well (tubeNumber)

        Returns:
            wellFilter: returns the wellFilter object for the given well number
        """
        if well_number in self.well_filter.keys():
            return self.well_filter[well_number]
        else:
            print(f"well number {well_number} not found in observations.")
            return None
    def get_well_profile(self) -> dict:
        """Returns a profile of all the filters in the well.

        Returns:
            dict: Dictionary with the well profile (top position and bottom position) of the filter
        """
        return {f"{i} --> {v.well_bro_id}": {"top position": v.screen_top_position, 
                                "bottom position": v.screen_bottom_position} 
                                for i, v in self.well_filter.items()}

    def __str__(self):
        for well_number, observation in self.well_filter.items():
            print(observation)

    def __len__(self):
        return len(self.well_filter)
    


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
    """Append a well observation to an existing Well object from an XML file.
    This function reads an XML file containing well observations and extracts the relevant data
    Warning: if Well is empty and if it lacks the well number, it will create a new well observation.

    Args:
        file_path (str): path to the XML file containing well data
        well (Well): An existing Well object with filter, to which data will be added

    Returns:
        Well: Well object with filter data added from the XML file
    """
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
    tree = ET.parse(file_path)
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
