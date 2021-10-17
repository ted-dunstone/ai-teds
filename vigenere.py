import sys

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main():

	if len(sys.argv) == 2:
		with open(sys.argv[1], 'r') as f:
			message = f.read()
	else:
		message = raw_input("Enter your message here: ")

	key = raw_input("Please enter your key: ")
	mode = raw_input("Enter 0 for Encrypt, 1 for Decrypt: ")

	# Decrypt
	if mode == '1':
		translated = translate(message, key, 1)
	# Encrypt
	else:
		translated = translate(message, key, 0)

	if len(sys.argv) == 2:
		if mode == '1':
			newFile = "dec." + sys.argv[1]
		else:
			newFile = "enc." + sys.argv[1]

		with open(newFile, 'w') as f:
			f.write(translated)
		print('%s was sucessfully written.' % (newFile))
	else:
		print('Translated message: %s' % (translated))

# 0 for encrypt, 1 for decrypt
def translate(message, key, mode):

	translated = []

	keyIndex = 0
	key = key.upper()

	# Iterate each character in the message.
	for symbol in message:
		num = LETTERS.find(symbol.upper())

		if num != -1: # If it is a letter
			# Add if encrypting, subtract if decrypting.
			if mode == 0:
				num += LETTERS.find(key[keyIndex])
			elif mode == 1:
				num -= LETTERS.find(key[keyIndex])

			num %= len(LETTERS) # Potential wrap-around

			if symbol.isupper():
				translated.append(LETTERS[num])
			elif symbol.islower():
				translated.append(LETTERS[num].lower())

			keyIndex += 1
			if keyIndex == len(key):
				keyIndex = 0

		# Not found in LETTERS
		else:
			translated.append(symbol)

	return ''.join(translated)