from datetime import datetime, timedelta, date
from apscheduler.scheduler import Scheduler

class User(object):
	sched = Scheduler()
	sched.start()

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.times = [timedelta(hours=2) for i in range(7)]
		self.today = timedelta(hours=2)
		self.running = False
		self.last_calc = datetime.now()
		self.last_ping = datetime.now()

	def start(self):
		self.ping()
		if not self.last_calc.date() == date.today():
			self.reset_time_left()
		if not self.running:
			self.last_calc = datetime.now()
			self.running = True

	def stop(self):
		self.calc()
		self.running = False

	def get_time_left(self):
		self.calc()
		total_seconds = self.today.seconds
		hours = total_seconds // 3600
		minutes = (total_seconds % 3600) // 60
		seconds = total_seconds % 60
		return {"hours": hours, "minutes": minutes, "seconds": seconds}

	def reset_time_left(self):
		self.today = self.times[datetime.now().weekday()]
		self.last_calc = datetime.now()

	def get_times(self):
		times_list = []
		for allowed_time in self.times:
			total_seconds = allowed_time.seconds
			hours = total_seconds // 3600
			minutes = (total_seconds % 3600) // 60
			seconds = total_seconds % 60
			times_list.append({"hours": hours, "minutes": minutes, "seconds": seconds})
		return times_list

	def calc(self):
		last_calculation = self.last_calc
		now = datetime.now()
		delta = now - last_calculation
		
		if not last_calculation.date() == now.date():
			self.reset_time_left()
		
		if self.running:
			self.today -= delta

			if self.today < timedelta(0):
				self.today = timedelta(0)

			self.last_calc = now

	def ping(self):
		self.last_ping = datetime.now()
		User.sched.add_date_job(self.check_for_timeout, datetime.now() + timedelta(minutes=1), [])

	def check_for_timeout(self):
		if datetime.now() - self.last_ping > timedelta(minutes=1):
			print("Session for " + self.username + " timed out")
			self.stop()