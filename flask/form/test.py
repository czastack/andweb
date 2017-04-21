from __init__ import Form
import fields

class TestForm(Form):
	common_class = 'form-control'
	common_attrs = {'required': True}
	name = fields.Input('Name')
	age = fields.YesNo('Age')
	submit = fields.Submit('Name')

form = TestForm({'name': 666})
for field in form:
	print(field)