import database
from data_sources.cameron_county import CameronCountyParser
from parser.faa import FAAParser

fp = FAAParser()
fp.parse()

ccp = CameronCountyParser()
parsed = ccp.parse()
print(parsed)
database.append_cameroncounty(parsed)
