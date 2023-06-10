import phub

client = phub.Client()

v = client.get('https://fr.pornhub.com/view_video.php?viewkey=ph5d2f75ac846d6')

v.download('video.mp4', phub.Quality('worst'))