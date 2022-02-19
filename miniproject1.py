import sqlite3

#-- Customer Functions --#
def start_session():
	return

def search():
	return

def end_movie():
	return

def end_session():
	return

#-- Editor Functions --#
def add_movies():
	return

def update():
	return


def main():
	loop = True
	while loop:
		print(
		'''
1. Start a session
2. Search
3. End watching a movie
4. End session
5. logout
		''')
		user_choice = int(input("Select an option: "))
		if user_choice == 1:
			start_session()
		elif user_choice == 2:
			search()
		elif user_choice == 3:
			end_movie()
		elif user_choice == 4:
			end_session()
		elif user_choice == 5:
			## logout goes back to login screen ##
			loop = False
		else:
			print("invalid input")

	return

if __name__ == "__main__":
	'''
	Add login screen first then go to main loop on sucessful login
	'''
	main()