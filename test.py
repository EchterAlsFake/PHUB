import phub

client = phub.Client()

video = client.get('ph5c584b2c0fe50')

print(video.like)