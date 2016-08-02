from dao import Dao

class Customer(Dao.db.Document):
	tagId = Dao.db.StringField()

	firstName = Dao.db.StringField()
	lastName = Dao.db.StringField()
	sex = Dao.db.StringField()

	flyingBlueId = Dao.db.StringField()

	language = Dao.db.StringField()

	phone = Dao.db.StringField()
	email = Dao.db.StringField()

	birthday = Dao.db.DateTimeField()

	flightFrom = Dao.db.StringField()
	flightTo = Dao.db.StringField()
	departureTime = Dao.db.StringField()

	meal = Dao.db.StringField()
	newsPaper = Dao.db.StringField()

	groupId = Dao.db.ListField(Dao.db.StringField())

	tracking = Dao.db.StringField()
	trackingDate = Dao.db.DateTimeField()
