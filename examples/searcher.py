# Example searching script

import phub

client = phub.Client()

while 1:
    
    query = input('[*] Enter query: ')
    
    record = client.search(query)
    
    print('[+] Found results:')
    
    for video in record.range(0, 10):
        print(video.title)

# EOF