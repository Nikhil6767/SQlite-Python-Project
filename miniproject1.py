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
	movies = c.execute("SELECT * FROM movies M WHERE LOWER(M.mid)=?;", (mid.lower(),)).fetchone()
	if not movies:
		title = input("enter movie title: ")
		year = input("enter movie year: ")
		runtime = input("enter movie runtime: ")
		casts = input("enter space seperated cast members id: ").split()
		c.execute("INSERT INTO movies VALUES (?, ?, ?, ?)", (mid, title, year, runtime))
		for cast in casts:
			person = c.execute("SELECT * FROM moviePeople MP WHERE LOWER(MP.pid)=?;", (cast.lower(),)).fetchone()
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


def update(c, conn):
	print(
		'''
1. monthly report
2. annual report
3. all-time report
		''')
	report = input("Select a report: ")
	if report == "1":
		movie_pairs = c.execute("""SELECT M1.mid, M2.mid, COUNT(DISTINCT W1.cid) AS customerCount 
								   FROM movies M1, movies M2, watch W1 INNER JOIN sessions S1 ON LOWER(W1.sid) = LOWER(S1.sid), watch W2 INNER JOIN sessions S2 ON LOWER(W2.sid) = LOWER(S2.sid)
								   WHERE LOWER(M1.mid) = LOWER(W1.mid) AND LOWER(M2.mid) = LOWER(W2.mid) AND LOWER(M1.mid) != LOWER(M2.mid) AND LOWER(W1.cid) = LOWER(W2.cid)
								   AND S1.sdate <= date(S2.sdate, "+1 months") AND S1.sdate >= date(S2.sdate, "-1 months") AND W1.duration >= M1.runtime * 0.5 AND W2.duration >= M2.runtime * 0.5
								   GROUP BY M1.mid, M2.mid
								   ORDER BY customerCount DESC;""", ()).fetchall()
	elif report == "2":
		movie_pairs = c.execute("""SELECT M1.mid, M2.mid, COUNT(DISTINCT W1.cid) AS customerCount 
								   FROM movies M1, movies M2, watch W1 INNER JOIN sessions S1 ON LOWER(W1.sid) = LOWER(S1.sid), watch W2 INNER JOIN sessions S2 ON LOWER(W2.sid) = LOWER(S2.sid)
								   WHERE LOWER(M1.mid) = LOWER(W1.mid) AND LOWER(M2.mid) = LOWER(W2.mid) AND LOWER(M1.mid) != LOWER(M2.mid) AND LOWER(W1.cid) = LOWER(W2.cid)
								   AND S1.sdate <= date(S2.sdate, "+1 years") AND S1.sdate >= date(S2.sdate, "-1 years") AND W1.duration >= M1.runtime * 0.5 AND W2.duration >= M2.runtime * 0.5
								   GROUP BY M1.mid, M2.mid
								   ORDER BY customerCount DESC;""", ()).fetchall()
	elif report == "3":
		movie_pairs = c.execute("""SELECT M1.mid, M2.mid, COUNT(DISTINCT W1.cid) AS customerCount 
								   FROM movies M1, movies M2, watch W1 INNER JOIN sessions S1 ON LOWER(W1.sid) = LOWER(S1.sid), watch W2 INNER JOIN sessions S2 ON LOWER(W2.sid) = LOWER(S2.sid)
								   WHERE LOWER(M1.mid) = LOWER(W1.mid) AND LOWER(M2.mid) = LOWER(W2.mid) AND LOWER(M1.mid) != LOWER(M2.mid) AND LOWER(W1.cid) = LOWER(W2.cid)
								   AND W1.duration >= M1.runtime * 0.5 AND W2.duration >= M2.runtime * 0.5
								   GROUP BY M1.mid, M2.mid
								   ORDER BY customerCount DESC;""", ()).fetchall()
		
	else:
		print("did not select report...exiting")
		return	
	i = 0
	while i < len(movie_pairs):
		recommended = c.execute("SELECT * FROM recommendations R WHERE LOWER(R.watched)=? AND LOWER(R.recommended)=?;", (str(movie_pairs[i][0]), str(movie_pairs[i][1]))).fetchone()
		if not recommended:
			print(str(i + 1) + ". " + str(movie_pairs[i][0]) + ", " + str(movie_pairs[i][1]) + ", number who watched: " + str(movie_pairs[i][2]) + ", in recommended: no")
		else:
			print(str(i + 1) + ". " + str(movie_pairs[i][0]) + ", " + str(movie_pairs[i][1]) + ", number who watched: " + str(movie_pairs[i][2]) + ", in recommended: yes, score: " + str(recommended[2]))
		i += 1

	while True:
		index = input("select an index to update a movie or enter nothing to exit: ")
		if index == "":
			print("exiting")
			return
		try:
			movie_pair = movie_pairs[int(index) - 1]
			recommended = c.execute("SELECT * FROM recommendations R WHERE LOWER(R.watched)=? AND LOWER(R.recommended)=?;", (str(movie_pair[0]), str(movie_pair[1]))).fetchone()
			if not recommended:
				score = input("this movie pair is not yet recommended, enter a score to add it, otherwise nothing: ")
				if score == "":
					print("not added")
					continue
				else:
					c.execute("INSERT INTO recommendations VALUES (?, ?, ?)", (movie_pair[0], movie_pair[1], score))
			else:
				score = input("this movie pair is recommended, enter a score to change it, \"del\" to delete it or nothing otherwise: ")
				if score == "":
					print("nothing changed")
				elif score == "del":
					c.execute("DELETE FROM recommendations WHERE LOWER(watched)=? AND LOWER(recommended)=?;", (str(movie_pair[0]), str(movie_pair[1])))
				else:
					c.execute("UPDATE recommendations SET score=? WHERE LOWER(watched)=? AND LOWER(recommended)=?;", (float(score), str(movie_pair[0]), str(movie_pair[1])))
		except:
			print("not a valid index...try again")
	conn.commit()
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
			user_choice = input("Select an option: ")
			if user_choice == "1":
				start_session(user_id, c, conn)
			elif user_choice == "2":
				search()
			elif user_choice == "3":
				end_movie()
			elif user_choice == "4":
				end_session()
			elif user_choice == "5":
				## logout goes back to login screen ##
				loop = False
			elif user_choice == "6":
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
			user_choice = input("Select an option: ")
			if user_choice == "1":
				add_movies(c, conn)
			elif user_choice == "2":
				update(c, conn)
			elif user_choice == "3":
				## logout goes back to login screen ##
				loop = False
			elif user_choice == "4":
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