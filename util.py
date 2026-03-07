#
# Some general utility and constants
#

from loxi.of13.const import ofp_type_map

# remove the ugly prefix thing
of_type_map = {type_number: type_string.replace('OFPT_', '') for type_number, type_string in ofp_type_map.items()}