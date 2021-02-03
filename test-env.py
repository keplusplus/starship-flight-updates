import database
from data_sources.cameron_county import CameronCountyParser
from data_sources.faa import FAAParser

fp = FAAParser()
fp.parse()

ccp = CameronCountyParser()
parsed = ccp.parse()
print(parsed)
#database.setup_database()  #reset database
database.append_cameroncounty(parsed)
