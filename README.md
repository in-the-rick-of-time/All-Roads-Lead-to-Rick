# All Roads Lead to Rick (Hack and Roll '23)

### Description ###
Inspired by [the Wikipedia Game](https://en.wikipedia.org/wiki/Wikipedia:Wiki_Game) and the zeitgeist of the 21st century, _All Roads Lead to Rick_ is a web app that will find its way from any Youtube URL in the world to our beloved ![Rickroll](https://www.youtube.com/watch?v=dQw4w9WgXcQ), all by traversing through a chain of suggested videos. The web app also provides the ability to create a playlist out of the traversed videos.

### Usage Guide ###
On the home page, you are prompted to enter your _API Key_ and _Youtube URL_. The user's API key is required, as the Youtube provides limited quota for its API usage. More information on setting up a key can be found [below](#setting-up-the-api-key). For our demo, we will use ![Youtube's default TED video by Dr Amy Cuddy](https://www.youtube.com/watch?v=Ks-_Mh1QhMc).

![Home](/demo/home.png)

After the bot does its work, it will generate the suggested videos path it took to find its way to Rick. The videos can be scrolled through on the site, with some cumulative stats on the videos provided below. Users can also generate a youtube playlist out of the traversed videos. In our demo, the bot visited 20 videos (including Rick) to reach Rick.

![Results](/demo/results.png)

Let's generate a playlist!

On clicking on generating a playlist, the site will prompt an Oauth authentication. This is required by Google for the ![playlist insertion function](https://developers.google.com/youtube/v3/docs/playlists/insert).

![Oauth](/demo/oauth.png)

After authentication your Google account, you will be redirected to the _results_ page, where you can click on _My Playlist_ to be redirected to the playlist created in your own Youtube account.

![Results Playlist](/demo/results_playlist.png)
![Youtube Playlist](/demo/yt_playlist.png)

That's it!

### Running the Web App Locally ###
Originally designed to run with Docker on Google Cloud Platform, this project was hosted online over the period of ![Hack and Roll](https://hacknroll.nushackers.org/). However, users can also run this web app locally using Flask. As this project utilises the youtube API, users will need to set up an ![API key](https://developers.google.com/youtube/v3/getting-started) and hosts will need to set up a ![Client Secret File](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid). This can be completed in under 5 minutes.

#### Setting up the API key ####
1. Head over to ![Google Cloud API & Services Dashboard](https://console.cloud.google.com/apis/dashboard).
2. Create a new project and name it whatever you like
3. Under the _Enabled APIs & services_ tab, click on _ENABLE APIS AND SERVICES_. Find the "Youtube Data API v3" API service and enable it.
4. Return to the dashboard and click on the _Credentials_ tab now.
5. Click on _CREATE CREDENTIALS_ and _API key_.
6. Your key has been created and is ready to be used.

#### Setting up the Client Secret File ####
1. Follow steps 1 to 5 above, but instead of choosing _API key_, choose _OAuth client ID_. Note that the API key and Client Secret File can be created on the same project.
2. Under Application type, choose _Web application_. You will be prompted to include origins and redirect URIs. Add `http://127.0.0.1:5000` and `http://127.0.0.1/callback` respectively.
3. Download the JSON file and save it as `client_secret.json` in the root folder.

Now we are ready to deploy the application.

After navigating to the root folder,

```bash
pip install -r requirements.txt
python main.py
```

The web app is now running locally. Enjoy!

### FAQ ###

#### How does the bot work? ####
The application makes use of youtube metadata to make informed decisions on choosing the best suggested video to bring it closer to the Rick Astley video. Our bot scores videos based on `data/tag_data.json` and `data/title.json`, choosing the suggested video with the highest score when navigating to Rick. To create `data/tag_data.json`, we scraped from 900 videos related to the Rick Astley video using `data/rank_tags.py`. Our bot also prioritises videos with the same cateogry ID as Rick.

#### Can this bot be applied for other videos? ####
The Python scripts employed are actually fairly flexible, and the destination video can be changed quite easily. By changing the target video for `main.py` and `data/rank_tags.py`, the bot can be used to find other videos as well. Do note that `title_data.json` was manually curated, and would also require input to change it for use with other videos.
