from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from chart.models import Chart
import json
from django.contrib.auth.models import User


def user_registrations(request):
	DATE_FORMAT = '%d.%m'
	users = User.objects.filter(date_joined__gte=datetime.now() - timedelta(31)) \
		.only('date_joined')[:]
	regs_by_date = {}
	for user in users:
		date_joined = user.date_joined.strftime(DATE_FORMAT)
		if date_joined in regs_by_date:
			regs_by_date[date_joined] += 1
		else:
			regs_by_date[date_joined] = 1
	today = date.today()
	past_date = today - timedelta(30)
	values = []
	while past_date <= today:
		date_key = past_date.strftime(DATE_FORMAT)
		values.append([
			date_key,
			date_key in regs_by_date and regs_by_date[date_key] or 0])
		past_date += timedelta(1)
	return HttpResponse(json.dumps([values]))

def test(request):
	return HttpResponse('[[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,-219.9]]]')
