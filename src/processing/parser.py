import usaddress
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AddressParser:
    @staticmethod
    def parse(address_line_1: str, address_line_2: Optional[str] = None) -> Dict[str, str]:
        full_address = address_line_1
        if address_line_2 and len(address_line_2.strip()) > 0:
            full_address = f"{full_address} {address_line_2}"            
        components = {
            'parsed_house': '',
            'parsed_predir': '',
            'parsed_street': '',
            'parsed_strtype': '',
            'parsed_postdir': '',
            'parsed_apttype': '',
            'parsed_aptnbr': ''
        }
        if not full_address or full_address.strip() == '':
            return components
        try:
            tagged_address, address_type = usaddress.tag(full_address)
            components['parsed_house'] = tagged_address.get('AddressNumber', '')
            components['parsed_predir'] = tagged_address.get('StreetNamePreDirectional', '')
            components['parsed_street'] = tagged_address.get('StreetName', '')
            components['parsed_strtype'] = tagged_address.get('StreetNamePostType', '')
            components['parsed_postdir'] = tagged_address.get('StreetNamePostDirectional', '')
            components['parsed_apttype'] = tagged_address.get('OccupancyType', '')
            components['parsed_aptnbr'] = tagged_address.get('OccupancyIdentifier', '')
            if address_line_2 and address_line_2.strip().lower().startswith('unit'):
                unit_parts = address_line_2.strip().split(None, 1)
                if len(unit_parts) > 1:
                    components['parsed_apttype'] = 'UNIT'
                    components['parsed_aptnbr'] = unit_parts[1]
        except (usaddress.RepeatedLabelError, usaddress.ParsingError) as e:
            logger.warning(f"usaddress parsing error: {e} for '{full_address}'. Using fallback.")
            components = AddressParser._fallback_parsing(full_address, address_line_2)
        return AddressParser._clean_components(components)
    
    @staticmethod
    def _fallback_parsing(address: str, address_line_2: Optional[str] = None) -> Dict[str, str]:
        components = {
            'parsed_house': '',
            'parsed_predir': '',
            'parsed_street': '',
            'parsed_strtype': '',
            'parsed_postdir': '',
            'parsed_apttype': '',
            'parsed_aptnbr': ''
        }
        house_match = re.match(r'^(\d+[A-Za-z]?)', address)
        if house_match:
            components['parsed_house'] = house_match.group(1)
        street_types = ['ST', 'AVE', 'BLVD', 'DR', 'LN', 'RD', 'CT', 'PL', 'TER', 'TERR', 'WAY', 'CIR']
        for st in street_types:
            pattern = r'(?i)\s+' + st + r'\b'
            if re.search(pattern, address):
                components['parsed_strtype'] = st
                break
        if components['parsed_house'] and components['parsed_strtype']:
            street_pattern = f"{components['parsed_house']}(.*?){components['parsed_strtype']}"
            street_match = re.search(street_pattern, address, re.IGNORECASE)
            if street_match:
                components['parsed_street'] = street_match.group(1).strip()
        if address_line_2:
            unit_match = re.match(r'(?i)(UNIT|APT|#)\s*(.+)', address_line_2)
            if unit_match:
                components['parsed_apttype'] = unit_match.group(1).upper()
                components['parsed_aptnbr'] = unit_match.group(2)
            else:
                components['parsed_apttype'] = 'UNIT'
                components['parsed_aptnbr'] = address_line_2.strip()
        
        return components
    
    @staticmethod
    def _clean_components(components: Dict[str, str]) -> Dict[str, str]:
        for key in components:
            if components[key] is None:
                components[key] = ''
            else:
                components[key] = str(components[key]).strip()
        
        street_type_map = {
            'STREET': 'ST',
            'AVENUE': 'AVE',
            'BOULEVARD': 'BLVD',
            'DRIVE': 'DR',
            'LANE': 'LN',
            'ROAD': 'RD',
            'COURT': 'CT',
            'PLACE': 'PL',
            'TERRACE': 'TER',
            'CIRCLE': 'CIR'
        }
        
        if components['parsed_strtype'].upper() in street_type_map:
            components['parsed_strtype'] = street_type_map[components['parsed_strtype'].upper()]
        
        unit_type_map = {
            'APARTMENT': 'APT',
            'NUMBER': '#',
            'SUITE': 'STE',
            'UNIT': 'UNIT'
        }
        
        if components['parsed_apttype'].upper() in unit_type_map:
            components['parsed_apttype'] = unit_type_map[components['parsed_apttype'].upper()]
        
        return components 