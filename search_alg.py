import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import re
import requests

class Search_Alg():

	RICKROLL_ID = "dQw4w9WgXcQ"
	RICKROLL_DICT = {
		'url':"https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
		'thumbnail_url':"https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg", 
		'title':"Rick Astley - Never Gonna Give You Up (Official Music Video)", 
		'publisher':"Rick Astley"
		}
	MUSIC_CATEGORY_ID = 10
	TAGS_JSON_FILENAME = "data/tag_data.json"
	TITLE_JSON_FILENAME = "data/title_data.json"
	MAXIMUM_RESULTS = 100

	def __init__(self, api_key):
		self.visited_channels = set()
		self.visited_cats = set()
		self.output_list = list() 
		self.visited_ids = list()
		self.statistics = {"duration":0, "viewcount":0, "count":0} 
		
		with open(self.TAGS_JSON_FILENAME) as tags_file:
			self.scored_tags = json.load(tags_file)
		with open(self.TITLE_JSON_FILENAME) as title_file:
			self.scored_titles = json.load(title_file)

		os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
		api_service_name = "youtube"
		api_version = "v3"
		self.youtube = googleapiclient.discovery.build(
		    api_service_name, api_version, developerKey=api_key)

	def find_rick(self, starting_vid_url):
		starting_id = self.id_from_url(starting_vid_url)
		current_vid = starting_id
		duration, viewcount, count = self.starting_stats(starting_id)
		self.statistics["duration"] += int(duration)
		self.statistics["viewcount"] += int(viewcount)
		self.statistics["count"] += 1
		self.visited_ids.append(starting_id)
		while True:
			if self.check_if_found_rick(current_vid):
				self.visited_ids.append(self.RICKROLL_ID)
				self.output_list.append(self.RICKROLL_DICT)
				ids = self.visited_ids
				videos_data = self.output_list
				statistics = self.statistics
				return ids, videos_data, statistics

			request = self.youtube.search().list( # get list of related videos to current video
			part="snippet",
			relatedToVideoId=current_vid,
			type="video",
			maxResults=self.MAXIMUM_RESULTS
			)
			
			try:
				response = request.execute()
			except HttpError as e:
				error_response = json.loads(e.content)
				error_code = error_response['error']['code']
				raise ValueError(error_code)

			current_vid = self.get_best_related(response)

	def id_from_url(self, url):
		regex = r"(?<=\?v=)[A-Za-z0-9]+(?=&)?"
		return re.search(regex, url).group()

	def get_duration(self,response,index=0):
		raw_duration = response["items"][index]["contentDetails"]["duration"]
		regex = r"P(?!$)(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T(?=\d+[HMS])(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$"
		if raw_duration != "P0D":
			duration_tuple = re.match(regex, raw_duration).groups(default="0")
			duration_secs = self.add_seconds(duration_tuple)
			return duration_secs
		else:
			return 0

	def starting_stats(self,starting_id):
		request = self.youtube.videos().list(
				part="snippet,contentDetails,statistics",
				id=starting_id
			)
		try:
			response = request.execute()
		except HttpError as e:
			error_response = json.loads(e.content)
			error_code = error_response['error']['code']
			raise ValueError(error_code)
		
		start_duration = self.get_duration(response)
		start_viewcount = response["items"][0]["statistics"]["viewCount"]
		start_count = 0
		return start_duration, start_viewcount, start_count

	def calc_tag_score(self, snippet):
		score = 0
		if "tags" in snippet:
			tags = snippet["tags"]
			for tag in tags:
				if tag.lower() in self.scored_tags: # if tag in data list, add points accordingly
					score += self.scored_tags[tag.lower()]
		return score

	def calc_title_score(self, title):
		title = title.lower()
		score = 0
		for keyword in self.scored_titles:
			if keyword in title:
				score += self.scored_titles[keyword]
		return score

	def find_index(self, list, value):
		for i, item in enumerate(list):
			if item == value:
				return i
		return -1
	
	def add_seconds(self, tuple):
		seconds = 31536000*int(tuple[0]) + 2628000*int(tuple[1]) + 86400*int(tuple[2]) + 3600*int(tuple[3]) + 60*int(tuple[4]) + int(tuple[5])
		return seconds

	def get_best_related(self, response):
		best_video = ("id", "url", "thumbnail_url", "title", "publisher", "cat", "duration", "viewcount", "channel_name", -1) # create tuple to store best related vid (score = -1 because it should be replaced immediately)
		has_music_video = False # check if music video has been found in the related vids. If found, only look at music vids
		rel_ids = []

		for video in response["items"]: # iterate through list of related videos
			vid_id = video["id"]["videoId"]
			rel_ids.append(vid_id) # append into a list
		
		half_length = 50
		rel_string_1 = ','.join(rel_ids[:half_length]) # Change from python list to a string of all values separated by a comma, format that the API wants
		rel_string_2 = ','.join(rel_ids[half_length:])
		

		rel_request_1 = self.youtube.videos().list(
			part="snippet,contentDetails,statistics",
			id=rel_string_1
		)
		rel_request_2 = self.youtube.videos().list(
			part="snippet,contentDetails,statistics",
			id=rel_string_2
		)

		try:
			rel_response_1 = rel_request_1.execute()
			rel_response_2 = rel_request_2.execute()
		except HttpError as e:
			error_response = json.loads(e.content)
			error_code = error_response['error']['code']
			raise ValueError(error_code)

		for video in response["items"]:
			first_music_video = False
			vid_id = video["id"]["videoId"]
			channel_id = video["snippet"]["channelId"]
			vid_title = video["snippet"]["title"]

			if self.check_if_found_rick(vid_id):
				return vid_id

			if channel_id not in self.visited_channels: # if channel has already been visited, don't even bother looking up the metadata
				vid_index = self.find_index(rel_ids,vid_id)
				if vid_index < 50:
					duration_secs = self.get_duration(rel_response_1,vid_index)
					data = rel_response_1["items"][vid_index]
				else:
					duration_secs = self.get_duration(rel_response_2,vid_index - 50)
					data = rel_response_2["items"][vid_index - 50]

				snippet = data["snippet"] # index 50-99 will be in response 2, indexed from 0, hence -50
				channel_name = snippet["channelTitle"]
				vid_viewcount = data["statistics"]["viewCount"]
				cat_id = int(snippet["categoryId"])

				if cat_id in self.visited_cats:
					continue
				if cat_id != self.MUSIC_CATEGORY_ID and has_music_video: # if this is not a music vid, and we alr have music vids in the related or it is a category we have visited, ignore this vid
					continue
				elif not has_music_video and cat_id == self.MUSIC_CATEGORY_ID: # if this is our first music vid, set a has_music_vid to true
					has_music_video = True
					first_music_video = True # if this is the first music video encountered

				score = self.calc_tag_score(snippet) + self.calc_title_score(vid_title)

				if score > best_video[-1] or first_music_video: # if is the only music video or has the highest score so far
					url = "https://www.youtube.com/watch?v=" + vid_id
					thumbnail_url = "https://img.youtube.com/vi/" + vid_id + "/hqdefault.jpg"
					best_video = (vid_id, url, thumbnail_url, vid_title, channel_id, cat_id, duration_secs, vid_viewcount, channel_name, score)

		self.output_list.append({'url':best_video[1], 'thumbnail_url':best_video[2], 'title':best_video[3], 'publisher':best_video[8]})
		self.statistics['viewcount'] += int(best_video[7]) # add viewcount
		self.statistics['count'] += 1 # add into count of iterations
		self.statistics['duration'] += best_video[6]

		self.visited_channels.add(best_video[4]) # Adds channel of best video into visited channels
		self.visited_ids.append(best_video[0]) 
		

		if best_video[5] != self.MUSIC_CATEGORY_ID:
			self.visited_cats.add(best_video[5]) # only add into visited if its not music

		return best_video[0]

	def check_if_found_rick(self, vid_id):
		if vid_id == self.RICKROLL_ID:
			return True
