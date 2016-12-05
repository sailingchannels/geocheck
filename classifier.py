from pymongo import MongoClient
import config, sys, time, requests, json

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

# loop all videos that do not have any geotags and are younger than 1 year
for vid in db.videos.find({"geoChecked": {"$exists": False}}, projection=["_id", "title", "description"]

	if not vid:
		continue

	txt = vid["title"] + " " + vid["description"]

	# try to get some place information
	headers = {
		"X-RosetteAPI-Key": config.apiKey()[6],
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

				place = entity["normalized"].encode("utf-8")

				try:
					l = requests.get("http://api.mapbox.com/geocoding/v5/mapbox.places/" + place + ".json?access_token=pk.eyJ1Ijoic2FpbGluZ2NoYW5uZWxzIiwiYSI6ImNpbHp5MngxczAwaHp2OW00Y2szOG1oM2wifQ.4w_KaRlbtjBf9_TNQL6SXw")
					locs = l.json()

					if locs and locs.has_key("features") and len(locs["features"]) > 0:

						location = locs["features"][0]
						print vid["_id"], place, location["geometry"]["coordinates"]

						locations.append(location["geometry"])
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
	else:
		db.videos.update_one({"_id": vid["_id"]}, {"$set": {
			"geoChecked": True
		}})
