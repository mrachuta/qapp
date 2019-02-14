import re
import uuid

"""
def validate_operation_no(operation_no):
    if not re.search(r'\D{2}\d{4}', operation_no):
        print('Error')
        return False


text = 'T01-C1-KLE-KL6000'

regex_pattern = re.compile(r'(\D\d{2})-(\D\d)-(\D{3})-(\D{2}\d{4})')
print(regex_pattern.search(text).groups())
"""

"""
errors_list = []

cleaned_data = {'type': 'BJC', 'tram': '1', 'bogie': '', 'car': '1', 'bogie_type': ''}

req_integrity= {
    'BJC': {'tram': True, 'bogie': False, 'car': True, 'bogie_type': False},
    'BJW': {'tram': False, 'bogie': True, 'car': False, 'bogie_type': True},
    'IKS': {'tram': True, 'bogie': False, 'car': True, 'bogie_type': False},
    'IKK': {'tram': True, 'bogie': False, 'car': True, 'bogie_type': False},

}

errors_integrity = {
    'BJC': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pola "wózek" oraz "typ wózka" powinny pozostać puste!',
    'BJW': u'Dla tego typu musisz wskazać "wózek" oraz "typ wózka"; pola "tramwaj" oraz "człon" powinny pozostać puste!',
    'IKS': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pola "wózek" oraz "typ wózka" powinny pozostać puste!',
    'IKK': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pola "wózek" oraz "typ "wózka" powinny pozostać puste!',

}

gate_type = cleaned_data['type']

for key, value in req_integrity[gate_type].items():
    if value is True and cleaned_data[key] != '':
        pass
    elif value is False and cleaned_data[key] == '':
        pass
    else:
        #Raise normalnie
        raise ValueError(errors_integrity[gate_type])

req_unique = {
    'BJC': ['type', 'tram', 'car', 'area', 'operation_no'],
    'BJW': ['type', 'bogie', 'bogie_type', 'operation_no'],
    'IKS': ['type', 'tram', 'name'],
    'IKK': ['type', 'tram', 'name'],
}

for i in self.cleaned_data[req_unique[gate_type][0]]:
    object_params = {}
    for value in req_unique[gate_type]:
        object_params[value] = self.cleaned_data[value]
        if value == req_unique[gate_type][0]:
            object_params[value] = i
            ob = Gate.objects.filter(**object_params)
            if ob.exists():
                errors_list.append(ValidationError('taki obiekt już istnieje na {}!'.format(self.cleaned_data[req_unique[gate_type][0]])))

if errors_list:
    raise ValidationError([err_list])


return self.cleaned_data

def __init__(self, *args, **kwargs):
    super(GateAddForm, self).__init__(*args, **kwargs)
    self.fields['tram'].required = False
    self.fields['car'].required = False
    self.fields['bogie'].required = False
    self.fields['bogie_type'].required = False
"""

jaga = {'Mati': 'Super', 'Kicia': None, 'Hu': ''}

for key, value in jaga.items():
    if not value:
        print('NONE')
    else:
        print('HEHE')
