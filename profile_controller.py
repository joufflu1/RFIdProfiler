from flask import Flask,url_for,jsonify,render_template
from flask_socketio import SocketIO
from datetime import datetime
from customer import Customer
from dao import Dao


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'rfid',
    'host': '127.0.0.1',
    'port': 27017
}


Dao.db.init_app(app)

socketio = SocketIO(app)


@app.route('/loung', methods=['GET', 'POST'])
def loung():
	return render_template('loung.html')


@app.route('/car', methods=['GET', 'POST'])
def car():
	return render_template('rent.html')

@app.route('/add')
def add():
	Customer.objects.delete()
	now = datetime.now()

	Customer(
		tagId         = 'FD0E1516', 
		firstName     = 'William',
		lastName      = 'Pikachu',
		tracking      = '?',
		trackingDate  = now,
		sex           = 'Homme',
		flyingBlueId  = '123456',
		language      = 'Francais',
		phone         = '0011223344', 
		email         = 'william@af.fr',
		birthday      = datetime(1975, 1, 1),
		flightFrom    = 'NCE',
		flightTo      = 'CDG',
		departureTime = '0815',
		meal          = 'Vegetarien',
		newsPaper     = 'Les Echos',
		groupId       = {''}
	).save()

	Customer(
		tagId         = '721BF0AF',
		firstName     = 'David',
		lastName      = 'Bulbizarre',
		tracking      = '?',
		trackingDate  = now,
		sex           = 'Homme',
		flyingBlueId  = '234567',
		language      = 'Anglais',
		phone         = '1122334455',
		email         = 'david@caramail.fr',
		birthday      = datetime(1978, 6, 12),
		flightFrom    = 'CDG',
		flightTo      = 'JFK',
		departureTime = '1355',
		meal          = '',
		newsPaper     = 'Le Monde, New York Times',
		groupId       = {''}
	).save()

	Customer(
		tagId         = '3A6C9DB7',
		firstName     = 'Fabrice',
		lastName      = 'Rondoudou',
		tracking      = '?',
		trackingDate  = now,
		sex           = 'Homme',
		flyingBlueId  = '345678',
		language      = 'Italien',
		phone         = '2233445566',
		email         = 'fabrice@lycos.fr',
		birthday      = datetime(1980, 8, 18),
		flightFrom    = 'CDG',
		flightTo      = 'JFK',
		departureTime = '1420',
		meal          = 'Sans gluten',
		newsPaper     = '',
		groupId       = {''}
	).save()

	Customer(
		tagId         = '0x3d1e5e77',
		firstName     = 'Philippe',
		lastName      = 'Ronflex',
		tracking      = '?',
		trackingDate  = now,
		sex           = 'Homme',
		flyingBlueId  = '456789',
		language      = 'Francais',
		phone         = '3344556677',
		email         = 'philippe@hotmail.fr',
		birthday      = datetime(1975, 10, 22),
		flightFrom    = 'CDG',
		flightTo      = 'AMS',
		departureTime = '1600',
		meal          = '',
		newsPaper     = 'L Equipe',
		groupId       = {''}
	).save()

	Customer(
		tagId         = '4C16E2A1',
		firstName     = 'Cyprien',
		lastName      = 'Semoun',
		tracking      = '?',
		trackingDate  = now,
		sex           = 'Indetermine',
		flyingBlueId  = '567890',
		language      = 'Francais',
		phone         = '4455667788',
		email         = 'cypriensemoun@jesaispas.com',
		birthday      = datetime(2000, 12, 25),
		flightFrom    = 'BKK',
		flightTo      = 'AUK',
		departureTime = '2330',
		meal          = '',
		newsPaper     = '',
		groupId       = {''}
	).save()

	str = ""
	for customer in Customer.objects:
		str += customer.tagId + ' ' + customer.firstName + ' ' + customer.lastName + ' ' + customer.email + '<br>'

	return str


@app.route("/profile/<tag>")
def getProfile(tag):
	result = Customer.objects(tagId=tag)
	return result[0].tagId + ' ' + result[0].firstName + ' ' + result[0].lastName + ' ' + result[0].email


@socketio.on('getCustomerListInLoung')
def handle_messageGetAll_event(json):
	broadcastCustomerListInLoung()


@socketio.on('sendTagId')
def handle_message_event(json):
	tagId = json['data']
	result = Customer.objects(tagId=tagId);
	try:
		customer = result[0]
		oldTracking = customer.tracking
		currentTracking = 'loung'
		newTracking = '?'
		now =  datetime.now()
		if oldTracking != currentTracking:
			customer.update(tracking=currentTracking,trackingDate = now)
			newTracking = currentTracking
		else: 
			customer.update(tracking=newTracking,trackingDate = now)
			newTracking = '?'
		broadcastSelectedCustomer(customer.tagId)
		broadcastCustomerListInLoung()
	except IndexError:
		print('Customer ?')


def broadcastCustomerListInLoung():
	result = Customer.objects(tracking='loung').order_by('-trackingDate')
	customerList = []
	for customer in result:
		customerList.append({
			'tagId':customer.tagId,
			'firstName':customer.firstName,
			'lastName':customer.lastName,
			'sex':customer.sex,
			'tracking':customer.tracking,
			'trackingDate':customer.trackingDate.strftime("%Y-%m-%d %H:%M:%S"),
			'flyingBlueId':customer.flyingBlueId,
			'language':customer.language,
			'phone':customer.phone,
			'email':customer.email,
			'birthday':customer.birthday.strftime("%Y-%m-%d"),
			'flightFrom':customer.flightFrom,
			'flightTo':customer.flightTo,
			'departureTime':customer.departureTime,
			'meal':customer.meal,
			'newsPaper':customer.newsPaper})
	socketio.emit('customerListInLoung', customerList, broadcast=True)


def broadcastSelectedCustomer(tagId):
	result = Customer.objects(tagId=tagId)
	singleCustomerList = []
	for customer in result:
		singleCustomerList.append({
			'tagId':customer.tagId,
			'firstName':customer.firstName,
			'lastName':customer.lastName,
			'sex':customer.sex,
			'tracking':customer.tracking,
			'trackingDate':customer.trackingDate.strftime("%Y-%m-%d %H:%M:%S"),
			'flyingBlueId':customer.flyingBlueId,
			'language':customer.language,
			'phone':customer.phone,
			'email':customer.email,
			'birthday':customer.birthday.strftime("%Y-%m-%d"),
			'flightFrom':customer.flightFrom,
			'flightTo':customer.flightTo,
			'departureTime':customer.departureTime,
			'meal':customer.meal,
			'newsPaper':customer.newsPaper})
	if len(singleCustomerList):
		socketio.emit('selectedCustomer', singleCustomerList, broadcast=True)


if __name__ == "__main__":
	socketio.run(app, host='192.168.42.1', port=5000)
