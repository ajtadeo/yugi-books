from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import Form, DateField, SelectField, TimeField, IntegerField
from wtforms.validators import InputRequired, ValidationError
from app.birdie_booker.alert import get_alerts, save_alert, delete_alert, set_expired_alert
from app.birdie_booker.location import get_locations

birdie_booker = Blueprint("birdie-booker", __name__, template_folder='templates')

locations = get_locations()
location_dict = {}
location_choices = []
for loc in locations:
  location_dict[loc[0]] = loc[1]
  location_choices.append((loc[0], loc[1]))
location_choices_sorted = sorted(location_choices, key=lambda x: x[1])
  
def validate_date(form, date):
	if date.data < datetime.today().date():
		raise ValidationError("Date must be today or a future date.")

def validate_endTime(form, endTime):
	if endTime.data <= form.startTime.data:
		raise ValidationError("End Time must be after start time.")
 
class AddForm(FlaskForm):
	location = SelectField('Location', [
		InputRequired()
	], choices=location_choices_sorted)

	numPlayers = SelectField('Number of Players', [
		InputRequired()
	], choices=[(1, 1), (2, 2), (3, 3), (4, 4)])

	date = DateField('Date', [
		InputRequired(),
		validate_date
	])

	startTime = TimeField('Start Time', [
		InputRequired()
  ])

	endTime = TimeField('End Time', [
		InputRequired(),
		validate_endTime
  ])

class DeleteForm(FlaskForm):
	id = IntegerField()

@birdie_booker.route("/")
def index():
	alerts = get_alerts()
	add_form = AddForm()
	delete_form = DeleteForm()
	
	return render_template("birdie_booker.html", data=alerts, add_form=add_form, delete_form=delete_form, locations=location_dict)

@birdie_booker.route("/add", methods=['POST'])
def add():
	alerts = get_alerts()
	add_form = AddForm()
	delete_form = DeleteForm()

	# form validation requires date to be un-expired, so isExpired is hardcoded to 0=False
	if add_form.validate_on_submit():
		location = add_form.location.data
		numPlayers = add_form.numPlayers.data
		date = add_form.date.data.strftime("%a %m/%d/%Y")
		startTime = add_form.startTime.data.strftime("%I:%M %p")
		endTime = add_form.endTime.data.strftime("%I:%M %p")
		isExpired = 0

		save_alert(location=location, numPlayers=numPlayers, date=date, startTime=startTime, endTime=endTime, isExpired=isExpired)
		return redirect(url_for("birdie-booker.index"))

	return render_template("birdie_booker.html", data=alerts, add_form=add_form, delete_form=delete_form, locations=location_dict)

@birdie_booker.route("/delete", methods=['POST'])
def delete():
	alerts = get_alerts()
	add_form = AddForm()
	delete_form = DeleteForm()

	if delete_form.is_submitted():
		id = delete_form.id.data
		delete_alert(id)
		return redirect(url_for("birdie-booker.index"))
	
	return render_template("birdie_booker.html", data=alerts, add_form=add_form, delete_form=delete_form, locations=location_dict)