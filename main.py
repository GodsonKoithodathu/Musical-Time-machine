from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SONGS_URL = "https://www.billboard.com/charts/hot-100"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
USER_ID = os.environ.get("USER_ID")

date = input("Which year do you want to travel to? Type the date in the format of YYYY-MM-DD : ")

response = requests.get(url=f"{SONGS_URL}/{date}")
html_data = response.text

soup = BeautifulSoup(html_data, "html.parser")

top_songs = [title.text.split("\t")[9] for title in soup.find_all(name="h3", class_="lrv-u-font-size-16")]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://open.spotify.com/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
        username=os.environ.get('USERNAME'),
    )
)
user_id = sp.current_user()
year = date.split("-")[0]

song_uris = []

for song in top_songs:
    query = f"track:{song}, year:{year}"
    result = sp.search(q=query, type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

create_playlist = sp.user_playlist_create(user=f"{USER_ID}", name=f"{date} BillBoard 100", public=False,
                                          description="Top Tracks from back in the Days")

album_id = create_playlist['id']

add_songs = sp.playlist_add_items(playlist_id=album_id, items=song_uris)
