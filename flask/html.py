
def html_params(data, keys = None):
	"""生成html属性字符串"""
	if data is None:
		return ''
	params = []
	for k in keys or data:
		v = data[k]
		if k.startswith('data_'):
			k = k.replace('_', '-', 1)
		if v is True:
			params.append(k)
		elif v is False or v is None:
			pass
		else:
			params.append('%s="%s"' % (k, v))
	return ' '.join(params)

def html_tag(tag, attrs = None, text = '', closed = True):
	"""生成html标签"""
	if text is None:
		text = ''
	attrs = ' ' + html_params(attrs) if attrs else ''
	if closed:
		return "<{0}{1}>{2}</{0}>".format(tag, attrs, text)
	else:
		return "<{0}{1}>".format(tag, attrs)