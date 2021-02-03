# import database
from data_sources.cameron_county import CameronCountyParser
# from data_sources.faa import FAAParser

# fp = FAAParser()
# fp.parse()

ccp = CameronCountyParser()
ccp.parse()
print(ccp.closures)
# database.setup_database()  #reset database
# database.append_cameroncounty(parsed)
