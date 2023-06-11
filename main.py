import phub

phub.debug(False)

client = phub.Client.from_file(open('creds.json'))
