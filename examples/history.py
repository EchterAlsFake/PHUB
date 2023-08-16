# Example script that print your PH history

import os
import phub

client = phub.Client(username = 'my-username',
                     password = 'my-password')

# Get optimal title width and table template
display_count = 20
width = os.get_terminal_size()[0]
tf = '| {:>2} | {:<' + str(width - 28) + '} | {:<16} |'

# Print header
print(f'*** {client.account.name}\'s history ***'.center(width))
print('-' * width)
print(tf.format('ID', 'VIDEO TITLE', 'KEY'))
print('=' * width)

# Iterate through videos line by line
for i, video in enumerate(client.account.watched[:display_count]):
    
    # Ensure no weird character in the title
    print(tf.format(i, phub.utils.pathify(video.title), video.key))

# Print footer
print(f' [{display_count} of {len(client.account.watched)}] ==='.rjust(width, '='))