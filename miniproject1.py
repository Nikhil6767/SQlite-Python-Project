import sqlite3
import sys
import time
from datetime import datetime
# login for both user and editor
def login(c, conn):
	while True:
		print("=====LOGIN/SIGNUP=====")
		id = input("enter your id: ")
		pwd = input("enter your user password: ")
		customer = c.execute("SELECT * FROM customers C WHERE LOWER(C.cid)=?;", (id.lower(),)).fetchone()
		editor = c.execute("SELECT * FROM editors E WHERE LOWER(E.eid)=?;", (id.lower(),)).fetchone()
		if customer:
			# if we entered as a customer
			if customer[2] != pwd:
				print("incorrect password")
				continue
			print("entered as customer")
			return "c", id
		elif editor:
			# if we entered as editor
			if editor[1] != pwd:
				print("incorrect password")
				continue
			print("entered as editor")
			return "e", id
		else:
			# signup if neither customer or editor exists.
			print("no such person found in the database.")
			name = input("if you wish to signup enter your name or nothing to go back to login/signup: ")
			if name == "":
				continue
			c.execute("INSERT INTO customers VALUES (?, ?, ?)", (id, name, pwd))
			print("sign up successful!")
			return "c", id


#-- Customer Functions --#
def start_session(user_id, c, conn):
	current_date = time.strftime("%Y-%m-%d-%H:%M:%S")
	# get the current max_sid, then add 1 to create a unique id
	max_sid = c.execute("SELECT MAX(s.sid) FROM sessions s").fetchone()[0]
	new_sid = max_sid + 1
	# insert the newly made session into the table
	c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)", (new_sid, user_id, current_date, None))
	print("Session started")
	conn.commit()
	return new_sid

def search(user_id, sid, c, conn):
	if sid == None:
		print("Please start a session")
		return
	# get keywords from the user
	keywords = input("Enter in keywords to search seperated by space: ").split()
	results = []
	mov_titles = []
	for word in keywords:
		# search for the keyword anywhere in title, name or role
		word = '%' + word + '%'
		search = c.execute("""
			SELECT m.title, m.year, m.runtime FROM movies m LEFT OUTER JOIN casts c ON c.mid = m.mid LEFT OUTER JOIN moviePeople p ON c.pid = p.pid
			WHERE lower(m.title) LIKE lower(?) OR lower(c.role) LIKE lower(?) OR lower(p.name) LIKE lower(?) ORDER BY (CASE WHEN 
			lower(m.title) LIKE lower(?) AND lower(c.role) LIKE lower(?) AND lower(p.name) LIKE lower(?) THEN 1 WHEN
			lower(m.title) LIKE lower(?) AND lower(c.role) LIKE lower(?) THEN 2 WHEN
			lower(m.title) LIKE lower(?) AND lower(p.name) LIKE lower(?) THEN 2 WHEN
			lower(p.name) LIKE lower(?) AND lower(c.role) LIKE lower(?) THEN 2 ELSE 3 END)""", (word, word, word, word, word, word, word, word, word,
				word, word, word)).fetchall()

		if len(search) == 0:
			print("No matches found")
			return
		# add only unique results to our results list
		for i in range(0, len(search)):
			if search[i] not in results:
				results.append(search[i])
		
	if len(results) > 5:
		print("We found the following matches:")
		i = 0
		for j in range(1,6):
			print(j, "Movie: ", results[i][0], "Year: ", results[i][1], "Duration: ", results[i][2])
			mov_titles.append(results[i][0])
			i += 1
			
		keep_search = True
		while keep_search:
			more_movies = input("See more resutls? (Y for more, N to pick a movie): ")

			if more_movies == 'y' or more_movies == 'Y':
				if i == len(results):
					print("no more movies")
					break

				while (i + 5 <= len(results)):
					mov_titles = []
					for j in range(1,6):
						print(j, "Movie: ", results[i][0], "Year: ", results[i][1], "Duration: ", results[i][2])
						mov_titles.append(results[i][0])
						i += 1
						
					break
				# display remaining movies after exhausting groups of 5
				mov_titles = []
				remaining = len(results) - i
				for j in range(1, remaining + 1):
					print(j, "Movie: ", results[i][0], "Year: ", results[i][1], "Duration: ", results[i][2])
					mov_titles.append(results[i][0])
					i += 1

			elif more_movies == 'n' or more_movies == 'N':
				keep_search = False

			else:
				print("Invalid input")

	else:
		mov_titles = []
		print("We found the following matches:")
		for i in range(1, len(results)+1):
			print(i, "Movie: ", results[i-1][0], "Year: ", results[i-1][1], "Duration: ", results[i-1][2])
			mov_titles.append(results[i-1][0])

	pick_mov = True
	while pick_mov:
		movie_choice = int(input("Select a movie: "))
		try:
			title = mov_titles[movie_choice-1]
		except:
			print("Invalid movie choice, pick again")
			continue
		pick_mov = False
	
	# Retrieve cast information of a movie
	cast_mem = c.execute("SELECT p.name FROM moviePeople p, movies m, casts c WHERE m.title = ? AND m.mid = c.mid AND c.pid = p.pid", (title,)).fetchall()
	print("Cast: ")
	for i in range(len(cast_mem)):
		print(cast_mem[i][0])

	# Retrieve the number of customers who watched the selected movie
	num_watched = c.execute("SELECT count(w.cid) FROM movies m, watch w WHERE m.title = ? AND m.mid = w.mid AND w.duration >= 0.5*m.runtime", (title,)).fetchone()[0]
	print("Number of customers who have watched: ", num_watched)

	mov_screen = True
	while mov_screen:
		print("""
1. Select a cast member to follow
2. Watch the movie\n""")
		options = int(input("How will you proceed: "))
		if options == 1:

			if len(cast_mem) == 0:
				print("No cast members found")
				break

			for i in range(len(cast_mem)):
				print(i+1, cast_mem[i][0])

			follow = int(input("Which cast member would you like to follow? "))
			
			pid = c.execute("SELECT pid from moviePeople where name = ?", (cast_mem[follow-1][0],)).fetchone()[0]
	
			already_follow = c.execute("SELECT cid, pid FROM follows WHERE cid = ? AND pid = ?", (user_id, pid)).fetchall()
	
			if len(already_follow) > 0:
				print("You already follow this person")
				break

			c.execute("INSERT INTO follows VALUES (?, ?)", (user_id, pid))
			print("You are now following ", cast_mem[follow-1][0])
			conn.commit()
			mov_screen = False
			return

		elif options == 2:
			mid = c.execute("SELECT mid FROM movies WHERE title = ?", (title,)).fetchone()[0]
			already_watch = c.execute("SELECT * FROM movies m, watch w WHERE w.mid = ? AND w.cid = ? AND w.sid = ? AND w.duration IS NULL;", (mid, user_id, sid)).fetchall()

			if len(already_watch) > 0:
				print("You are already watching this movie")
				break
			
			c.execute("INSERT INTO watch VALUES (?, ?, ?, ?)", (sid, user_id, mid, None))
			print("Now watching ", title)
			conn.commit()

			current_time = datetime.now()
			current_time = datetime.strptime(current_time.strftime("%H:%M:%S"), "%H:%M:%S")

			mov_screen = False
			return current_time

		else:
			print("Invalid input, pick again")

	return

def end_movie(start_time, user_id, sid, c, conn):
	# check if we are watching movies
	movies_watching = c.execute("SELECT m.title FROM movies m, watch w WHERE w.mid = m.mid AND w.cid = ? AND w.sid = ?;", (user_id,sid)).fetchall()
	if len(movies_watching) == 0:
		print("You are not watching any movies.")
		return

	for i in range(1, len(movies_watching)+1):
		print(i, movies_watching[i-1][0])
	
	if start_time == 0:
		print("cannot stop watching these movies (Can only stop watching movies started in this program)")
		return
		
	# select movie to stop watching
	stop = int(input("Which movie did you want to stop watching? "))
	title = movies_watching[stop-1][0]

	mid = c.execute("SELECT mid FROM movies WHERE title = ?;", (title,)).fetchone()[0]

	end_time = datetime.now()
	end_time = datetime.strptime(end_time.strftime("%H:%M:%S"), "%H:%M:%S")
	
	duration = round((end_time-start_time).total_seconds() / 60, 2)

	movie_runtime = c.execute("SELECT m.runtime FROM movies m, watch w WHERE w.mid = m.mid AND w.cid = ? AND m.title = ?;", (user_id, title)).fetchone()[0]

	# add duration to watch, if the user watched more than the movie runtime, we assume they watched entire movie so we set the runtime as duration watched
	if duration > movie_runtime:
		c.execute("UPDATE watch SET duration = ? WHERE cid = ? AND mid = ?;", (movie_runtime, user_id, mid))
	else:
		c.execute("UPDATE watch SET duration = ? WHERE cid = ? AND mid = ?;", (duration, user_id, mid))

	conn.commit()
	return

def end_session(start_time, sid, user_id, c, conn):
	# see if a session exists
	session = c.execute("SELECT S.sdate FROM sessions S WHERE S.cid=? AND S.sid=? AND S.duration IS NULL", (user_id, sid)).fetchone()
	if (not session):
		print("you must first start a session. exiting...")
		return
	end = input("enter \"end\" if you would like to enter the current session: ")
	if (end.lower() == "end"):
		# end session
		sdate = datetime.strptime(session[0], "%Y-%m-%d-%H:%M:%S")
		edate = datetime.strptime(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), "%Y-%m-%d-%H:%M:%S")
		dur = round((edate - sdate).total_seconds()/ 60, 2)
		c.execute("UPDATE sessions SET duration=? WHERE cid=? AND sid=?;", (dur, user_id, sid))

		# end watching any existing movies
		end_time = datetime.now()
		end_time = datetime.strptime(end_time.strftime("%H:%M:%S"), "%H:%M:%S")
		duration = round((end_time-start_time).total_seconds() / 60, 2)
		c.execute("UPDATE watch SET duration=? WHERE cid=? AND sid=? AND duration IS NULL;", (duration, user_id, sid))
		conn.commit()
		print("ending session...")
		return
	else:
		print("chose not to end session. exiting...")
		return

#-- Editor Functions --#
def add_movies(c, conn):
	# find movie
	mid = input("enter movie id: ")
	movies = c.execute("SELECT * FROM movies M WHERE LOWER(M.mid)=?;", (mid.lower(),)).fetchone()
	if not movies:
		# get and insert movie info
		title = input("enter movie title: ")
		year = input("enter movie year: ")
		runtime = input("enter movie runtime: ")
		casts = input("enter space seperated cast members id: ").split()
		c.execute("INSERT INTO movies VALUES (?, ?, ?, ?)", (mid, title, year, runtime))
		for cast in casts:
			# insert cast members
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
		# if movies already exists
		print("movie id is not unique")
		return


def update(c, conn):
	# select report
	print(
		'''
1. monthly report
2. annual report
3. all-time report
		''')
	report = input("Select a report: ")
	# find report depending on selected
	if report == "1":
		movie_pairs = c.execute("""SELECT M1.mid, M2.mid, COUNT(DISTINCT W1.cid) AS customerCount 
								   FROM movies M1, movies M2, watch W1 INNER JOIN sessions S1 ON LOWER(W1.sid) = LOWER(S1.sid), watch W2 INNER JOIN sessions S2 ON LOWER(W2.sid) = LOWER(S2.sid)
								   WHERE LOWER(M1.mid) = LOWER(W1.mid) AND LOWER(M2.mid) = LOWER(W2.mid) AND LOWER(M1.mid) != LOWER(M2.mid) AND LOWER(W1.cid) = LOWER(W2.cid)
								   AND S1.sdate <= date(S2.sdate, "+1 months") AND S1.sdate >= date(S2.sdate, "-30 days") AND W1.duration >= M1.runtime * 0.5 AND W2.duration >= M2.runtime * 0.5
								   GROUP BY M1.mid, M2.mid
								   ORDER BY customerCount DESC;""", ()).fetchall()
	elif report == "2":
		movie_pairs = c.execute("""SELECT M1.mid, M2.mid, COUNT(DISTINCT W1.cid) AS customerCount 
								   FROM movies M1, movies M2, watch W1 INNER JOIN sessions S1 ON LOWER(W1.sid) = LOWER(S1.sid), watch W2 INNER JOIN sessions S2 ON LOWER(W2.sid) = LOWER(S2.sid)
								   WHERE LOWER(M1.mid) = LOWER(W1.mid) AND LOWER(M2.mid) = LOWER(W2.mid) AND LOWER(M1.mid) != LOWER(M2.mid) AND LOWER(W1.cid) = LOWER(W2.cid)
								   AND S1.sdate <= date(S2.sdate, "+1 years") AND S1.sdate >= date(S2.sdate, "-365 days") AND W1.duration >= M1.runtime * 0.5 AND W2.duration >= M2.runtime * 0.5
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
		# if invalid report selected
		print("did not select report...exiting")
		return	
	i = 0
	while i < len(movie_pairs):
		# display report information
		recommended = c.execute("SELECT * FROM recommendations R WHERE LOWER(R.watched)=? AND LOWER(R.recommended)=?;", (str(movie_pairs[i][0]), str(movie_pairs[i][1]))).fetchone()
		if not recommended:
			print(str(i + 1) + ". " + str(movie_pairs[i][0]) + ", " + str(movie_pairs[i][1]) + ", number who watched: " + str(movie_pairs[i][2]) + ", in recommended: no")
		else:
			print(str(i + 1) + ". " + str(movie_pairs[i][0]) + ", " + str(movie_pairs[i][1]) + ", number who watched: " + str(movie_pairs[i][2]) + ", in recommended: yes, score: " + str(recommended[2]))
		i += 1

	while True:
		index = input("select an index to update a movie or enter nothing to exit: ")
		if index == "":
			conn.commit()
			print("exiting")
			return
		try:
			# recommend a movie pair or change score
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
			# if invalid movie pair
			print("not a valid index...try again")


def main(user, user_id, login_loop, c, conn):
	sid = None
	start_time = 0
	# customer options
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
				sid = start_session(user_id, c, conn)
			elif user_choice == "2":
				start_time = search(user_id, sid, c, conn)
			elif user_choice == "3":
				end_movie(start_time, user_id, sid, c, conn)
			elif user_choice == "4":
				end_session(start_time, sid, user_id, c, conn)
			elif user_choice == "5":
				loop = False
			elif user_choice == "6":
				loop = False
				login_loop = False
			else:
				print("invalid input")
	# editor options
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
		# connect to sqlite3 
		conn = sqlite3.connect(sys.argv[1])
		c = conn.cursor()
		conn.commit()

	except:
		print("You must enter a valid database name as an argument")
		exit()

	while login_loop:
		# login then go into main functions	
		user, user_id = login(c, conn)
		conn.commit()
		login_loop = main(user, user_id, login_loop, c, conn)

	conn.close()