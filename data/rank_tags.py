import os
import json
import googleapiclient.discovery
import googleapiclient.errors

output_dict = dict()
seen_vids = set()

def main():
	API_KEY = "{INPUT YOUR API KEY HERE}"

	# Disable OAuthlib's HTTPS verification when running locally.
	# *DO NOT* leave this option enabled in production.
	os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

	api_service_name = "youtube"
	api_version = "v3"

	youtube = googleapiclient.discovery.build(
		api_service_name, api_version, developerKey=API_KEY)

	add_my_tags(youtube, "dQw4w9WgXcQ", 5)
	add_related_tags(youtube, "dQw4w9WgXcQ", 3)

	with open('json_data.json', 'w') as outfile:
		json.dump(output_dict, outfile)

	return

def add_related_tags(youtube, vid_id, max_depth, depth=1):
	if depth < max_depth:
		request = youtube.search().list(
			part="snippet",
			relatedToVideoId=vid_id,
			type="video",
			maxResults=30
		)
		response = request.execute()
		for video in response["items"]:
			vid_id = video["id"]["videoId"]
			add_my_tags(youtube, vid_id, max_depth-depth)
			add_related_tags(youtube, vid_id, max_depth, depth+1)
	else:
		return

def add_my_tags(youtube, vid_id, points):
	if vid_id in seen_vids:
		return
	request = youtube.videos().list(
		part="snippet",
		id=vid_id
	)
	response = request.execute()

	try:
		for tag in response["items"][0]["snippet"]["tags"]:
			if tag.lower() not in output_dict:
				output_dict[tag.lower()] = points
	except:
		pass # if no tags, then just ignore

	seen_vids.add(vid_id)
	return


if __name__ == "__main__":
	main()