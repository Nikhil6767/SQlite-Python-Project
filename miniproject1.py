import sqlite3
import sys
import time
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
			return "c", id
		elif editor:
			if editor[1] != pwd:
				print("incorrect password")
				continue
			print("entered as editor")
			return "e", id
		else:
			print("no such person found in the database.")
			'''
			do we need to check if new user cid already exists? also do we need to c.commit after excecuting
			the insert values?
			'''
			name = input("if you wish to signup enter your name or nothing to go back to login/signup: ")
			if name == "":
				continue
			c.execute("INSERT INTO customers VALUES (?, ?, ?)", (id, name, pwd))
			print("sign up successful!")
			return "c", id


#-- Customer Functions --#
def start_session(user_id, c, conn):
	current_date = time.strftime("%Y-%m-%d")
	print(current_date)
	max_sid = c.execute("SELECT MAX(s.sid) FROM sessions s").fetchone()[0]
	new_sid = max_sid + 1
	c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", (new_sid, user_id, current_date, None))
	conn.commit()
	return

def search():
	return

def end_movie():
	return

def end_session():
	return

#-- Editor Functions --#
def add_movies(c, conn):
	mid = input("enter movie id: ")
	movies = c.execute("SELECT * FROM movies M WHERE M.mid=?;", (mid,)).fetchone()
	if not movies:
		title = input("enter movie title: ")
		year = input("enter movie year: ")
		runtime = input("enter movie runtime: ")
		casts = input("enter space seperated cast members id: ").split()
		c.execute("INSERT INTO movies VALUES (?, ?, ?, ?)", (mid, title, year, runtime))
		for cast in casts:
			person = c.execute("SELECT * FROM moviePeople MP WHERE MP.pid=?;", (cast,)).fetchone()
			name = person[1] if person else ""
			birth_year = person[2] if person else ""
			if not person:
				print("this cast member does not yet exist")
				name = input("enter cast name: ")
				birth_year = input("enter birth year of cast: ")
				c.execute("INSERT INTO moviePeople VALUES (?, ?, ?)", (cast, name, birth_year))
			print(str(name) + " " + str(birth_year))
			confirm = input("to reject this cast enter nothing, otherwise enter that cast members role: ")
			if confirm == "":
				print("rejected " + name)
				continue
			else:
				c.execute("INSERT INTO casts VALUES (?, ?, ?)", (mid, cast, confirm))
		conn.commit()
		return
	else:
		print("movie id is not unique")
		return


def update():
	return


def main(user, user_id, login_loop, c, conn):
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
6. End Program
			''')
			user_choice = int(input("Select an option: "))
			if user_choice == 1:
				start_session(user_id, c, conn)
			elif user_choice == 2:
				search()
			elif user_choice == 3:
				end_movie()
			elif user_choice == 4:
				end_session()
			elif user_choice == 5:
				## logout goes back to login screen ##
				loop = False
			elif user_choice == 6:
				loop = False
				login_loop = False
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
4. End Program
			''')
			user_choice = int(input("Select an option: "))
			if user_choice == 1:
				add_movies(c, conn)
			elif user_choice == 2:
				update()
			elif user_choice == 3:
				## logout goes back to login screen ##
				loop = False
			elif user_choice == 4:
				loop = False
				login_loop = False
			else:
				print("invalid input")
	
	return login_loop

if __name__ == "__main__":

	login_loop = True
	try:
		conn = sqlite3.connect(sys.argv[1])
		c = conn.cursor()
		conn.commit()
		
	except:
		print("You must enter a valid database name as an argument")
		exit()

	while login_loop:
		user, user_id = login(c)
		login_loop = main(user, user_id, login_loop, c, conn)

	conn.close()