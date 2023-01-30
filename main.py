from flask import Flask, render_template, request, redirect, url_for, session
from search_alg import Search_Alg
import google.oauth2.credentials
import google_auth_oauthlib.flow
from create_playlist import Create_Playlist
import os

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == "GET":
		return render_template('index.html')
	if request.method == 'POST':
		apikey = request.form['APIkey']
		startingvid = request.form['youtubeURL']
		rickbot = Search_Alg(api_key=apikey)
		session.clear()
		try:
			session["videos_data"], session["statistics"] = rickbot.find_rick(starting_vid_url=startingvid)
		except ValueError as e:
			if str(e) == "400": # invalid url
				return render_template("400.html")
			elif str(e) == "403": # ran out of quota or yt api not enabled
				return render_template("403.html")
			elif str(e) == "508":
				return render_template("508.html")
			else: # idk what's going on
				return render_template("500.html")
				
		return redirect(url_for('results'))


@app.route('/index', methods=['GET'])
def index():
	if request.method == 'GET':
		return redirect(url_for('home'))

@app.route('/results', methods=['GET'])
def results():
	if request.method == 'GET':
		if "videos_data" not in session:
			return redirect(url_for('home'))
		return render_template('results.html')


@app.route('/auth', methods=['GET'])
def auth():
	if "credentials" in session:
		return redirect(url_for('createplaylist'))
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		client_secrets_file=CLIENT_SECRETS_FILE,
		scopes=SCOPES,
	)
	flow.redirect_uri = url_for('callback', _external=True)
	authorization_url, state = flow.authorization_url(
		access_type='offline',
		include_granted_scopes='true'
	)
	session['state'] = state
	return redirect(authorization_url)

@app.route('/callback', methods=['GET'])
def callback():
	state = session['state']

	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
	  CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
	flow.redirect_uri = url_for('callback', _external=True)

	authorization_response = request.url
	flow.fetch_token(authorization_response=authorization_response)

	credentials = flow.credentials
	print(credentials)
	session['credentials'] = credentials_to_dict(credentials)

	return redirect(url_for('createplaylist'))

@app.route('/createplaylist', methods=['GET'])
def createplaylist():
	if 'credentials' in session and 'videos_data' in session and 'playlist' not in session:
		credentials = google.oauth2.credentials.Credentials(**session['credentials'])
		vid_ids = [video["id"] for video in session["videos_data"]]
		try:
			playlist_creator = Create_Playlist(API_SERVICE_NAME, API_VERSION, credentials)
		except ValueError as e:
			if str(e) == "403": # we ran out of quota oops
				return render_template('playlist403.html')
			else: # idk what's going on
				return render_template('500.html')
		session['playlist'] = playlist_creator.createPlaylist(vid_ids)
		return redirect(url_for('results'))
	else:
		return redirect(url_for('home'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__ == "__main__":
	app.run(debug=True)
