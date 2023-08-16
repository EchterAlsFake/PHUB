# Example searching script

import phub

client = phub.Client()

query = input('Enter query: ')
result = client.search(query)

print(f'Found results for "{query}":')

for i, video in enumerate(result):
    
    print(f'{i: <2} - {video.title}')

print('...')