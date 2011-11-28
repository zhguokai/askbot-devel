import sys
from chart.models import Chart

def charts(request):
	def insert_chart(pk, el_id):
		try:
			chart = Chart.objects.get(pk=pk)
		except:
			return '<!-- Error: requested chart not found! -->'
		path = chart.data_provider.rsplit('.', 1)
		data = None
		try:
			__import__(path[0])
			view = getattr(sys.modules[path[0]], path[1])
			data = view(request).content
		except:
			return '<!-- Error: requested chart\'s data provider not found! -->'
		
		return '<script type="text/javascript" language="JavaScript">//<![CDATA[\n$.jqplot("%(id)s", %(data)s);\n//]]></script>' % {
			'id': str(el_id),
			'data': data,
		}
	return {
		'insert_chart': insert_chart,
	}
