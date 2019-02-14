from django import forms
from .models import Gate, Comment, CommentFile, GateFile, Tram, Bogie
from django.forms import inlineformset_factory
from re import search
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist


def validate_op_no(op_no):
    if not search(r'\D{2}\d{4}', op_no):
        raise forms.ValidationError('Operacja musi składać się z dwóch liter i czterech cyfr')


class GateFileAddForm(forms.ModelForm):

    class Meta:
        model = GateFile
        fields = [
            'file',
        ]
        labels = {
            'file': u'Plik'
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera', 'onchange': 'ResizeImage(this)'})
        }


class GateAddForm(forms.ModelForm):

    tram = forms.ModelMultipleChoiceField(queryset=Tram.objects.all(), label=u'Tramwaj')
    bogie = forms.ModelMultipleChoiceField(queryset=Bogie.objects.all(), label=u'Wózek')
    operation_no = forms.CharField(max_length=6, label=u'Numer operacji', validators=[validate_op_no])
    operation_no.widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})

    class Meta:

        model = Gate

        fields = [
            'type',
            #'tram',
            #'bogie',
            'bogie_type',
            'car',
            'area',
            'name',
            'operation_no',
            'content',
            'creation_date',
            'author',
        ]

        labels = {
            'type': u'Typ',
            'tram': u'Tramwaj',
            'bogie': u'Wózek',
            'bogie_type': u'Typ wózka',
            'car': u'Człon',
            'area': u'Obszar',
            'name': u'Nazwa',
            'operation_no': u'Numer operacji',
            'content': u'Zawartość',
            'creation_date': u'Data utworzenia',
            'author': u'Autor'
        }

        widgets = {
            'name': forms.TextInput(attrs={'size': '40px'}),
            'creation_date': forms.TextInput(attrs={'readonly': 'readonly', 'size': '21px'}),
            'author': forms.HiddenInput()
        }

    field_order = [
        'type',
        'tram',
        'car',
        'bogie',
        'bogie_type',
        'area',
        'operation_no',
        'name',
        'content',
        'creation_date',
        'author',

    ]

    def clean(self):

        """Custom validation for form.
        First, validator check the integrity. Depending of Gate.type, some parameters are necessary, other are not
        (see req_integrity dict).
        During iteration, keys and values for specified Gate.type are checked. If parameter is necessary, there is True,
        if not, there is False. (unselected/unfilled fields in form are sended as 'None'). Empty querysets for tram and
        bogie are also send, but empty queryset is not recognized as None.
        So, there is necessary to check, that query/dict value return some results. If not, validated_data is set to
        None. Otherwise, validated_data is set to appropriate dict value.
        If integrity is corrupted, there is no sense to go next steps; ValidationError is raised.

        Next step is to check, that currently added Gate is not a duplicate of other Gate object.

        Due to possibility to add multiple Gate (one Gate for multiple Tram/Bogie), iteration is over the
        cleaned_data['tram'] or cleaned_data['bogie'].
        For each object during iteration, the object_params dict is created.
        Next, starts the iteration over fields that should be unique (see req_unique dict). If iteration found value,
        which has the same name as req_unique[gate_type][1] element ('tram' or 'bogie'), add them also to object_params,
        but with value from first iteration (object Tram or Bogie). Object is called using **kwargs from object_params
        dict. If object exists, error is added to errors_list.

        Due to function save_add_another via form and multiple Gates add in one shot, the list of errors is necessary
        (consider a case, when multiple Gate in on shot are added: some object exists (ValidationError raised),
        and other was added properly)
        """

        errors_list = []

        #print(self.cleaned_data)

        req_integrity = {
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

        gate_type = self.cleaned_data['type']

        for key, value in req_integrity[gate_type].items():

            if not self.cleaned_data[key]:
                validated_data = None
            else:
                validated_data = self.cleaned_data[key]

            if value is True and validated_data is not None:
                pass
            elif value is False and validated_data is None:
                pass
            else:
                raise ValidationError(errors_integrity[gate_type])

        req_unique = {
            'BJC': ['type', 'tram', 'car', 'area', 'operation_no'],
            'BJW': ['type', 'bogie', 'bogie_type', 'operation_no'],
            'IKS': ['type', 'tram', 'name'],
            'IKK': ['type', 'tram', 'name'],
        }

        for i in self.cleaned_data[req_unique[gate_type][1]]:
            object_params = {}
            for value in req_unique[gate_type]:
                print('Iteruje, printuje value')
                print(value)
                object_params[value] = self.cleaned_data[value]
                if value == req_unique[gate_type][1]:
                    object_params[value] = i
            print(object_params)
            ob = Gate.objects.filter(**object_params)
            if ob.exists():
                errors_list.append(ValidationError('taki obiekt już istnieje na {}!'.format(i)))

        if errors_list:
            raise ValidationError([errors_list])

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(GateAddForm, self).__init__(*args, **kwargs)
        self.fields['tram'].required = False
        self.fields['car'].required = False
        self.fields['bogie'].required = False
        self.fields['bogie_type'].required = False


class CommentFileAddForm(forms.ModelForm):

    class Meta:
        model = CommentFile
        fields = [
            'file',
        ]
        labels = {
            'file': u'Plik'
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera', 'onchange': 'ResizeImage(this)'})
        }


class CommentAddForm(forms.ModelForm):

    # gate_rating = forms.RadioSelect(choices=Gate.GATE_GRADES)

    class Meta:
        model = Comment
        fields = [
            'text',
        ]
        labels = {
            'text': u'Komentarz',
        }
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': u'Wpisz opcjonalny komentarz'})
        }


class GateChangeForm(forms.ModelForm):

    #trams_to_apply = forms.ModelMultipleChoiceField(queryset=Tram.objects.all(), label=u'Tramwaje do wprowadzenia zmiany')

    class Meta:

        model = Gate
        fields = [
            'type',
            'tram',
            'bogie',
            'bogie_type',
            'car',
            'area',
            'name',
            'content',
            'operation_no',
            'creation_date',
            'modify_date',
            'author'
        ]
        labels = {
            'type': u'Typ',
            'tram': u'Tramwaj',
            'bogie': u'Wózek',
            'bogie_type': u'Typ wózka',
            'car': u'Człon',
            'area': u'Obszar',
            'name': u'Nazwa',
            'operation_no': u'Numer operacji',
            'content': u'Zawartość',
            'modify_date': u'Data modyfikacji',
            'creation_date': u'Data utworzenia',
            'author': u'Autor'
        }

        widgets = {
            'type': forms.HiddenInput(),
            'tram': forms.HiddenInput(),
            'bogie': forms.HiddenInput(),
            'bogie_type': forms.HiddenInput(),
            'car': forms.HiddenInput(),
            'area': forms.HiddenInput(),
            'creation_date': forms.HiddenInput(),
            'modify_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'author': forms.HiddenInput(),
        }

        field_order = [
            #'type',
            #'tram',
            #'car',
            #'bogie',
            #'bogie_type',
            #'area',
            'operation_no',
            'name',
            'content',
            'modify_date'
            #'creation_date',
            #'author'
        ]

    def __init__(self, *args, **kwargs):
        super(GateChangeForm, self).__init__(*args, **kwargs)
        self.fields['tram'].required = False
        self.fields['car'].required = False
        self.fields['bogie'].required = False
        self.fields['bogie_type'].required = False


GateFileAddFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=False)
CommentFileAddFormSet = forms.inlineformset_factory(Comment, CommentFile, form=CommentFileAddForm, extra=3, can_delete=False)
GateFileChangeFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=True)
