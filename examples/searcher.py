# Example searching script

import phub

client = phub.Client()

while 1:
    
    query = input('[*] Enter query: ')
    
    record = client.search(query)
    
    print('[+] Found results:')
    
    for i in range(10):
        try: print(f'* {i} -- {record[i].title}')
        except IndexError: break

# EOF