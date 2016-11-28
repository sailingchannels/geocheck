from pymongo import MongoClient

# open mongodb connection
client = MongoClient(config.mongoDB())
db_name = "sailing-channels"
devMode = False

# check if dev mode is active
if len(sys.argv) != 2:
	db_name += "-dev"
	devMode = True
	print "*** DEVELOPER MODE ***"

db = client[db_name]

# loop all videos that do not have any geotags
for vid in db.videos.find({"$exists": {"geo": False}}, projection=["_id", "title", "description"]):
	print vid["_id"], vid["title"]
