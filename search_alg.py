import json
from collections import namedtuple
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import re
import sys

class Search_Alg():

	RICKROLL_ID = "dQw4w9WgXcQ"
	MUSIC_CATEGORY_ID = 10
	TAGS_JSON_FILENAME = "data/tag_data.json"
	TITLE_JSON_FILENAME = "data/title_data.json"
	MAX_RESULTS = 100

	def __init__(self, api_key):
		self.visited_channels = set() # get list of visited channels and categories. We do not revisit them
		self.visited_vid_details = list()
		self.statistics = {"duration":0, "viewcount":0, "count":0}
		
		with open(self.TAGS_JSON_FILENAME) as tags_file:
			self.scored_tags = json.load(tags_file)
		with open(self.TITLE_JSON_FILENAME) as title_file:
			self.scored_titles = json.load(title_file)

		api_service_name = "youtube"
		api_version = "v3"
		self.youtube = googleapiclient.discovery.build(
		    api_service_name, api_version, developerKey=api_key)

	def find_rick(self, starting_vid_url): # main function to call
		starting_id = self.id_from_url(starting_vid_url)
		curr_vid_id = starting_id
		self.update_details_and_stats_lsts(starting_id)
		while curr_vid_id != self.RICKROLL_ID:
			request = self.youtube.search().list( # get list of related videos to current video
			part="snippet",
			relatedToVideoId=curr_vid_id,
			type="video",
			maxResults=self.MAX_RESULTS
			)
			response = self.handle_request(request)

			curr_vid_details = self.get_best_related(response) # choose the best suggested video
			self.update_details_and_stats_lsts(curr_vid_details.vid_id, curr_vid_details.vid_title, curr_vid_details.channel_title)
			curr_vid_id = curr_vid_details.vid_id

		else:
			return self.visited_vid_details, self.statistics

	def handle_request(self, request): # wrapper to handle request and error
		try:
			response = request.execute()
		except HttpError as e:
			error_response = json.loads(e.content)
			error_code = error_response['error']['code']
			raise ValueError(error_code)
		return response

	def id_from_url(self, url):
		regex = r"(?<=\?v=)[a-zA-Z0-9_-]+(?=&)?" # extract id from url (nested between "v=" and "&" if channel name included in url)
		return re.search(regex, url).group()

	def update_details_and_stats_lsts(self, vid_id, vid_title=None, channel_title=None): # update global lists of visited vid_details and stats
		if vid_title == None or channel_title == None: # account for starting video which has not been searched
			vid_title, channel_title, duration, viewcount = self.get_stats_and_details(vid_id)
			self.update_total_stats(vid_id, duration, viewcount)
		else:
			self.update_total_stats(vid_id)
		self.visited_vid_details.append({'id':vid_id, 'title':vid_title, 'publisher':channel_title})
	
	def get_stats_and_details(self, vid_id): # specifically designed for first video. Get stats and details at once.
		request = self.youtube.videos().list(
			part="snippet,contentDetails,statistics",
			id=vid_id
		)
		response = self.handle_request(request)
		
		video = response["items"][0]
		snippet = video["snippet"]
		vid_title = snippet["title"]
		channel_title = snippet["channelTitle"]
		duration = self.get_duration(video["contentDetails"]["duration"])
		viewcount = int(video["statistics"]["viewCount"])

		return vid_title, channel_title, duration, viewcount

	def update_total_stats(self, vid_id, duration=None, viewcount=None): # add visited video data and stats to global lists
		if duration == None or viewcount == None: # starting video will have been searched earlier. No need to get duration and viewcount again
			duration, viewcount = self.get_stats(vid_id)
		self.statistics["duration"] += duration
		self.statistics["viewcount"] += viewcount
		self.statistics["count"] += 1

	def get_stats(self,vid_id):
		request = self.youtube.videos().list(
				part="contentDetails,statistics",
				id=vid_id
			)
		response = self.handle_request(request)
		duration = self.get_duration(response["items"][0]["contentDetails"]["duration"])
		viewcount = int(response["items"][0]["statistics"]["viewCount"])

		return duration, viewcount

	def get_duration(self,duration_str): # get video duration for compiled stats
		LIVESTREAM_CODE = "P0D" # livestream has no timing. Just ignore
		regex = r"P(?!$)(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T(?=\d+[HMS])(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$"
		if duration_str != LIVESTREAM_CODE:
			duration_tuple = re.match(regex, duration_str).groups(default="0")
			duration_secs = self.add_seconds(duration_tuple)
			return duration_secs
		else:
			return 0

	def add_seconds(self, tuple):
		YR_COEFF = 31536000
		MTH_COEFF = 2628000
		DAY_COEFF = 86400
		HR_COEFF = 3600
		MIN_COEFF = 60
		seconds = YR_COEFF*int(tuple[0]) + MTH_COEFF*int(tuple[1]) + DAY_COEFF*int(tuple[2]) + HR_COEFF*int(tuple[3]) + MIN_COEFF*int(tuple[4]) + int(tuple[5])
		return seconds

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
	
	def get_best_related(self, response):
		videoDetails = namedtuple("videoDetails", ["vid_id", "vid_title", "channel_title", "cat_id", "score"])
		best_video = videoDetails("vid_id", "vid_title", "channel_title", -1, -1) # placeholder best vid. score is -1 so it is replaced immediately
		has_music_video = False # check if music video has been found in the related vids. If found, only look at music vids

		related_vids_lst = self.get_related_data(self.get_related_ids_lst(response))

		for video in related_vids_lst:
			first_music_video = False
			vid_id = video["id"]
			snippet = video["snippet"]
			channel_title = snippet["channelTitle"]
			vid_title = snippet["title"]
			cat_id = int(snippet["categoryId"])

			if vid_id == self.RICKROLL_ID: # ladies and gentlemen, we got him!
				return videoDetails(vid_id, vid_title, channel_title, cat_id, None) # actually don't need cat_id or score, but include by convention

			if channel_title in self.visited_channels: # if channel has already been visited, don't even bother looking up the metadata
				continue

			if cat_id != self.MUSIC_CATEGORY_ID and has_music_video: # if this is not a music vid, and we alr have music vids in the related or it is a category we have visited, ignore this vid
				continue
			elif not has_music_video and cat_id == self.MUSIC_CATEGORY_ID: # if this is our first music vid, set a has_music_vid to true
				has_music_video = True
				first_music_video = True # if this is the first music video encountered

			score = self.calc_tag_score(snippet) + self.calc_title_score(vid_title)

			if score > best_video.score or first_music_video: # if is the only music video or has the highest score so far
				best_video = videoDetails(vid_id, vid_title, channel_title, cat_id, score)

		self.visited_channels.add(best_video.channel_title) # Adds channel of best video into visited channels. Let's not go back

		return best_video

	def get_related_ids_lst(self, response):
		related_ids = []
		for video in response["items"]: # iterate through list of related videos
			vid_id = video["id"]["videoId"]
			related_ids.append(vid_id) # append into a list
		return related_ids

	def get_related_data(self, vid_ids):
		MAX_LIST_RESULTS = 50 # only able to list 5o videos at a time
		total_vids = len(vid_ids)
		n_vids_left = total_vids # num of vids that have still not been searched
		related_vids_lst = list()
		while n_vids_left > 0:
			if n_vids_left < MAX_LIST_RESULTS:
				ids_comma_sep = ','.join(vid_ids[0:n_vids_left]) # Change from python list to a comma-separated string for API
				n_vids_left = 0
			else:
				ids_comma_sep = ','.join(vid_ids[n_vids_left - MAX_LIST_RESULTS:n_vids_left])
				n_vids_left -= MAX_LIST_RESULTS
	
			request = self.youtube.videos().list(
				part="snippet",
				id=ids_comma_sep
			)
			response = self.handle_request(request)
			related_vids_lst += response["items"] # combine the list of related vids for all searches
		return related_vids_lst