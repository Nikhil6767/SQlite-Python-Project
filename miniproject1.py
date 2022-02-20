import sqlite3
import sys

def login(c):
	while True:
		print("=====LOGIN/SIGNUP=====")
		id = input("enter your id: ")
		pwd = input("enter your user password: ")
		customer = c.execute("SELECT * FROM customers C WHERE LOWER(C.cid)=?;", (id.lower(),)).fetchone()
		editor = c.execute("SELECT * FROM editors E WHERE LOWER(E.eid)=?;", (id.lower(),)).fetchone()
		if customer:
			if customer[2] != pwd:
				print("incorrect password")
				continue
			print("entered as customer")
			return "c"
		elif editor:
			if editor[1] != pwd:
				print("incorrect password")
				continue
			print("entered as editor")
			return "e"
		else:
			print("no such person found in the database.")
			name = input("if you wish to signup enter your name or nothing to go back to login/signup: ")
			if name == "":
				continue
			c.execute("INSERT INTO customers VALUES (?, ?, ?)", (id, name, pwd))
			print("sign up successful!")
			return "c"


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
	try:
		conn = sqlite3.connect(sys.argv[1])
		c = conn.cursor()
		user = login(c)
		conn.commit()
	except:
		print("You must enter a valid database name as an argument")
		return

	if user == "c":
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
	elif user == "e":
		loop = True
		while loop:
			print(
			'''
1. Add a movie
2. Update a recommendation
3. logout
			''')
			user_choice = int(input("Select an option: "))
			if user_choice == 1:
				add_movies()
			elif user_choice == 2:
				update()
			elif user_choice == 3:
				## logout goes back to login screen ##
				loop = False
			else:
				print("invalid input")
	
	conn.close()	
	return

if __name__ == "__main__":
	'''
	Add login screen first then go to main loop on sucessful login
	'''
	main()