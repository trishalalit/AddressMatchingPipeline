import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class AddressNormalizer:
    """Normalize address components for better matching."""
    
    STREET_TYPE_MAP = {
        'ST': 'ST',
        'STREET': 'ST',
        'AVE': 'AVE',
        'AVENUE': 'AVE',
        'BLVD': 'BLVD',
        'BOULEVARD': 'BLVD',
        'DR': 'DR',
        'DRIVE': 'DR',
        'RD': 'RD',
        'ROAD': 'RD',
        'LN': 'LN',
        'LANE': 'LN',
        'CT': 'CT',
        'COURT': 'CT',
        'PL': 'PL',
        'PLACE': 'PL',
        'TER': 'TER',
        'TERR': 'TER',
        'TERRACE': 'TER',
        'CIR': 'CIR',
        'CIRCLE': 'CIR',
        'HWY': 'HWY',
        'HIGHWAY': 'HWY',
    }
    
    DIRECTIONAL_MAP = {
        'N': 'N',
        'NORTH': 'N',
        'S': 'S',
        'SOUTH': 'S',
        'E': 'E',
        'EAST': 'E',
        'W': 'W',
        'WEST': 'W',
        'NE': 'NE',
        'NORTHEAST': 'NE',
        'SE': 'SE',
        'SOUTHEAST': 'SE',
        'SW': 'SW',
        'SOUTHWEST': 'SW',
        'NW': 'NW',
        'NORTHWEST': 'NW',
    }
    
    UNIT_TYPE_MAP = {
        'APT': 'APT',
        'APARTMENT': 'APT',
        'UNIT': 'UNIT',
        '#': 'UNIT',
        'STE': 'STE',
        'SUITE': 'STE',
    }
    
    @staticmethod
    def normalize_address_components(components: Dict[str, str]) -> Dict[str, str]:
        """
        Normalize address components for matching.
        
        Args:
            components: Dictionary of parsed address components
            
        Returns:
            Dictionary of normalized address components
        """
        normalized = {}
        
        for key, value in components.items():
            if not value:
                normalized[key] = ''
                continue
            value = value.upper()
            if 'street' in key:
                value = AddressNormalizer._normalize_street_name(value)
            elif 'strtype' in key:
                value = AddressNormalizer.STREET_TYPE_MAP.get(value, value)
            elif 'predir' in key or 'postdir' in key:
                value = AddressNormalizer.DIRECTIONAL_MAP.get(value, value)
            elif 'apttype' in key:
                value = AddressNormalizer.UNIT_TYPE_MAP.get(value, value)
            normalized[key] = value
        return normalized
    
    @staticmethod
    def build_normalized_address(components: Dict[str, str]) -> str:
        parts = []
        if components.get('parsed_house'):
            parts.append(components['parsed_house'])
        if components.get('parsed_predir'):
            parts.append(components['parsed_predir'])
        if components.get('parsed_street'):
            parts.append(components['parsed_street'])
        if components.get('parsed_strtype'):
            parts.append(components['parsed_strtype'])
        if components.get('parsed_postdir'):
            parts.append(components['parsed_postdir'])
        unit_parts = []
        if components.get('parsed_apttype') and components.get('parsed_aptnbr'):
            unit_parts.append(components['parsed_apttype'])
            unit_parts.append(components['parsed_aptnbr'])
        if unit_parts:
            parts.append(' '.join(unit_parts))
        normalized_address = ' '.join(parts).strip()
        normalized_address = re.sub(r'\s+', ' ', normalized_address)
        return normalized_address

    @staticmethod
    def _normalize_street_name(street_name: str) -> str:
        street_name = re.sub(r'(\d+)(ST|ND|RD|TH)\b', r'\1', street_name)
        ordinal_map = {
            'FIRST': '1',
            'SECOND': '2',
            'THIRD': '3',
            'FOURTH': '4',
            'FIFTH': '5',
            'SIXTH': '6',
            'SEVENTH': '7',
            'EIGHTH': '8',
            'NINTH': '9',
            'TENTH': '10'
        }
        for word, number in ordinal_map.items():
            if street_name == word:
                return number
        
        return street_name 