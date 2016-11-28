from pymongo import MongoClient
import config, sys, geograpy2

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
for vid in db.videos.find({"geo": {"$exists": False}}, projection=["_id", "title", "description"]):

	txt = vid["title"] + " " + vid["description"]
	print txt

	# try to get some place information
	r = requests.post("http://httpbin.org/post", data=payload)

	print vid["_id"]
	print "- - -"
	break
