from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import F
import datetime
import time
from .models import Trips, Trains, Segments, Stations, FareTypes, Reservations, StopsAt, SeatsFree, Passengers
#from railroadapp.models import Stations
from railroadapp.forms import reservationForm

def index(request):
    return render(request, "railroadapp/index.html")


def newIndex(request):
	return render(request, "railroadapp/index2.html")

def station(request):
	curr_station = Stations.objects.all();
	context = {
	"now": curr_station
	}
	return render(request, "railroadapp/station.html",context)

def errorPage(request):
	return render(request, "railroadapp/errorPage.html")
def trains(request):
	now = datetime.datetime.now().time()
	print(now)
	itr = StopsAt.objects.all()
	currTrain = [];
	for s in itr:
		#print("this went thru")
		if s.time_in < now and now < s.time_out:

			currTrain.append([s.train_id,s.station.station_name,s.time_in, s.time_out]);

			print("Curr train is ", s.train_id, " it is at station ", s.station.station_name, " at time ", s.time_in, " it will leave at ", s.time_out)

	context = {
		"trains": currTrain
	}
	return render(request, "railroadapp/trains.html",context);

def reserve(request):
	if request.method == "POST":
		form = reservationForm(request.POST)
		if form.is_valid():
			reserv = form.save(commit = False)
			reserv.save()

			#Getting the data we need from the form that user filled out
			t_date = request.POST.get("start_date")
			trip_start = request.POST.get("start_station")
			trip_end = request.POST.get("end_station")
			start_time = request.POST.get("start_time")
			curr_date = request.POST.get("start_date")
			passenger = request.POST.get("paying_passenger")
			firstSlice = Segments.objects.values_list('seg_n_end', flat = True)[int(trip_start)-1]
			endSlice = Segments.objects.values_list('seg_s_end', flat = True)[int(trip_end) -2]
			#End getting useful data

			#Start calculating the fare for the segments
			itr = Segments.objects.all()[firstSlice:endSlice]
			total_fare = 0
			for s in itr:
				total_fare += s.seg_fare
			print("trip_start = ", trip_start, " trip_end = ", trip_end, "first slice = ", firstSlice, " second slice = ", endSlice, ' total fare = ', total_fare)
			#End calculating fare, now we have it

			#Check if user is entering a valid time and a train will stop at that time
			doesStop = StopsAt.objects.filter(station = trip_start);
			print(doesStop);
			trainExists = False;
			start_time = datetime.datetime.strptime(start_time, '%H:%M')
			for train in doesStop:
				if train.time_in < start_time.time() and start_time.time() < train.time_out:
					stoppingTrain = train.train_id
					trainExists = True;
			if(not trainExists):
				return redirect('errorpage')
			#Now we know there is a valid train and we have its train id

			#Now we have the fare, and the train they will be at. Now we must decrement seats free
			seatsTable = SeatsFree.objects.filter(seat_free_date = curr_date, train_id = stoppingTrain, segment_id__gte = firstSlice, segment_id__lte = endSlice);
			seatsTable.update(freeseat = F('freeseat')-1)
			#Seats free has been decremented
			date_entered = datetime.datetime.strptime(curr_date, '%Y-%m-%d').date()
			newReserv = Reservations(reservation_date = datetime.datetime.combine(date_entered, start_time.time()),
				paying_passenger = Passengers.objects.get(pk = passenger),
				card_number = Passengers.objects.get(passenger_id = passenger).preferred_card_number, 
				billing_address = Passengers.objects.get(passenger_id = passenger).preferred_billing_address, 
				)
			newReserv.save()

			newTrip = Trips(trip_date = t_date, 
				trip_seg_start = Segments.objects.get(seg_n_end = trip_start), 
				trip_seg_ends = Segments.objects.get(seg_s_end = trip_end), 
				fare_type = FareTypes.objects.get(pk = 1), 
				fare = total_fare, 
				trip_train = Trains.objects.get(pk = stoppingTrain), 
				reservation = newReserv
				)

			print('created the trip ', newTrip.trip_seg_start, " ", newTrip.fare)

			newTrip.save()
			print(' done creating')
			return redirect('index')

	else:
		form = reservationForm()
	context = {'form': form}
	return render(request, 'railroadapp/reserve.html', context)

def stationTimes(request, id):
	
	stops = StopsAt.objects.filter(station = id).order_by('time_in')
	print(stops)
	context = {
		"stop": stops
	} 
	for times in stops:
		print(times.time_in)
	return render(request, 'railroadapp/station_id.html',context)


def myReserv(request, id):

	myReservs = Reservations.objects.filter(paying_passenger = id)


	context = {
		"passenger": myReservs
	}
	return render(request, 'railroadapp/myreservation.html', context)


