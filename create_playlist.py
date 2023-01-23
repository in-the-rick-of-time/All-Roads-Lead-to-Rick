import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import HttpError
import json

class Create_Playlist():
	PLAYLIST_TITLE = "Road to Rick"
	PLAYLIST_DESC = "Lovingly curated by o.intherickoftime!"
	PLAYLIST_PRIVACY = "private"

	def __init__(self, api_service_name, api_version, credentials):
		self.youtube = googleapiclient.discovery.build(
			api_service_name, api_version, credentials=credentials)

	def createPlaylist(self, vid_ids):
		playlist_id = self.newEmptyPlaylist()
		self.insertVideos(playlist_id, vid_ids)
		return playlist_id

	def insertVideos(self, playlist_id, vid_ids):
		batch = self.youtube.new_batch_http_request()
		for videoId in vid_ids:
			request = self.youtube.playlistItems().insert(
				part="snippet",
				body={
					"snippet": {
						"playlistId": playlist_id,
						"resourceId": {
							"kind": "youtube#video",
							"videoId": videoId
						}
					}
				}
			)
			try:
				request.execute()
			except HttpError as e:
				error_response = json.loads(e.content)
				error_code = error_response['error']['code']
				raise ValueError(error_code)

	def newEmptyPlaylist(self):
		request = self.youtube.playlists().insert(
			part="snippet,status",
			body={
				"snippet": {
					"title": self.PLAYLIST_TITLE,
					"description": self.PLAYLIST_DESC,
					"defaultLanguage": "en"
				},
				"status": {
					"privacyStatus": self.PLAYLIST_PRIVACY
				}
			}
		)
		response = request.execute()
		return response['id']