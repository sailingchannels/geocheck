from pymongo import MongoClient
import config, sys, time, requests, json
from geopy.geocoders import Nominatim

# open mongodb connection
client = MongoClient(config.mongoDB())
db_name = "sailing-channels"
devMode = False

# init geolocator
geolocator = Nominatim()

# check if dev mode is active
if len(sys.argv) != 2:
	db_name += "-dev"
	devMode = True
	print "*** DEVELOPER MODE ***"

db = client[db_name]

# loop all videos that do not have any geotags and are younger than 1 year
videos = db.videos.find({"geoChecked": {"$exists": False}}, projection=["_id", "title", "description"], limit=10000)
print videos.count()

for vid in videos:

	txt = vid["title"] + " " + vid["description"]

	# try to get some place information
	headers = {
		"X-RosetteAPI-Key": config.apiKey()[2],
		"Content-Type": "application/json",
		"Accept": "application/json"
	}
	payload = {"content": txt}
	r = requests.post("https://api.rosette.com/rest/v1/entities", headers=headers, data=json.dumps(payload))

	result = r.json()

	# find location tags
	locations = []
	if result.has_key("entities"):
		for entity in result["entities"]:
			if entity["type"] == "LOCATION":

				try:
					location = geolocator.geocode(entity["normalized"])
					if location:

						print vid["_id"], entity["normalized"], location.longitude, location.latitude

						locations.append({
							"type": "Point",
							"coordinates": [
								location.longitude,
								location.latitude
							]
						})
				except:
					pass

		if len(locations) > 0:
			db.videos.update_one({"_id": vid["_id"]}, {"$set": {
				"geo": {
					"type": "GeometryCollection",
	  				"geometries": locations
				},
				"geoChecked": True
			}})
		else:
			db.videos.update_one({"_id": vid["_id"]}, {"$set": {
				"geoChecked": True
			}})
