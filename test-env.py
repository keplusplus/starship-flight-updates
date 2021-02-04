# import database
# from data_sources.cameron_county import CameronCountyParser
from data_sources.faa import FAAParser

def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))

fp = FAAParser()
tfr_list = fp.parse()
for tfr in tfr_list:
    pretty(tfr, 2)

# ccp = CameronCountyParser()
# ccp.parse()
# print(ccp.closures)
# database.setup_database()  #reset database
# database.append_cameroncounty(parsed)
