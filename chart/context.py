import sys
from django.core.urlresolvers import reverse
from chart.models import Chart
from chart.views import chart_data
from django.http import HttpResponseForbidden

def charts(request):
	def insert_chart(pk, el_id, ajax=False):
		try:
			chart = Chart.objects.get(pk=pk)
		except:
			return '<!-- Error: requested chart not found! -->'
		def script(script_text):
			return '<script type="text/javascript" language="JavaScript">//<![CDATA[\n%s\n//]]></script>' \
				% script_text
		if ajax:
			return script('ajaxChart("%(id)s", "%(path)s", %(options)s);'
				% {
					'id': unicode(el_id),
					'path': reverse('chart_data', kwargs={'chart_pk': pk}),
					'options': any(chart.options) and chart.options or 'null',})
		else:
			data_response = chart_data(request, pk)
			if isinstance(data_response, HttpResponseForbidden):
				return '<!-- Error: authorisation required -->'
			return script('$.jqplot("%(id)s", %(data)s, %(options)s);'
				% {
					'id': unicode(el_id),
					'data': data_response.content,
					'options': any(chart.options) and chart.options or 'null',})
	return {
		'insert_chart': insert_chart,
	}
