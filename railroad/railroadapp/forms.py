from django import forms
from .models import Ticket


class reservationForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = [
			"start_station",
			"end_station",
			"start_time",
			"start_date",
			"paying_passenger",
		]