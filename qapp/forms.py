from django import forms
from .models import Gate, Comment, CommentFile, GateFile, Tram, Bogie, OperationArea
from django.forms import inlineformset_factory
from re import search
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


def validate_op_no(op_no):
    if not search(r'\D{2}\d{4}', op_no):
        raise forms.ValidationError({'operation_no': ['Operacja musi składać się z dwóch wielkich liter i czterech cyfr',]})


class GateFileAddForm(forms.ModelForm):

    class Meta:
        model = GateFile
        fields = [
            'file',
        ]
        labels = {
            'file': u'Plik',
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera', 'onchange': 'ResizeImage(this)'}),
        }


class GateAddForm(forms.ModelForm):

    tram = forms.ModelMultipleChoiceField(queryset=Tram.objects.all(), label=u'Tramwaj')
    bogie = forms.ModelMultipleChoiceField(queryset=Bogie.objects.all(), label=u'Wózek')
    #operation_no = forms.CharField(max_length=6, min_length=6, label=u'Numer operacji')
    #operation_no.widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})

    class Meta:

        model = Gate

        fields = [
            'type',
            'car',
            'area',
            'responsible',
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
            'car': u'Człon',
            'area': u'Obszar',
            'responsible': u'Odpowiedzialny',
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
        'area',
        'responsible',
        'operation_no',
        'name',
        'content',
        'creation_date',
        'author',

    ]

    def __init__(self, *args, **kwargs):
        super(GateAddForm, self).__init__(*args, **kwargs)
        self.fields['tram'].required = False
        self.fields['car'].required = False
        self.fields['bogie'].required = False
        self.fields['operation_no'].max_length = 6
        self.fields['operation_no'].min_length = 6
        self.fields['operation_no'].label = u'Numer operacji'
        self.fields['operation_no'].widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})
        self.fields['responsible'].choices = [
            (user.pk, '{} {} ({})'.format(user.last_name, user.first_name, user.username))
            for user in User.objects.all().order_by('last_name')
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

        validate_op_no(self.cleaned_data['operation_no'])

        # If responsible person is not selected, add foreman as responsible

        if not self.cleaned_data['responsible']:
            foreman = OperationArea.objects.get(area=self.cleaned_data['area']).foreman
            self.cleaned_data['responsible'] = foreman

        errors_list = []

        req_integrity = {
            'BJC': {'tram': True, 'bogie': False, 'car': True, },
            'BJW': {'tram': False, 'bogie': True, 'car': False, },
            'IKS': {'tram': True, 'bogie': False, 'car': True, },
            'IKK': {'tram': True, 'bogie': False, 'car': True, },

        }

        errors_integrity = {
            'BJC': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pole "wózek" powinno pozostać puste!',
            'BJW': u'Dla tego typu musisz wskazać "wózek"; pola "tramwaj" oraz "człon" powinny pozostać puste!',
            'IKS': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pole "wózek" powinno pozostać puste!',
            'IKK': u'Dla tego typu musisz wskazać "tramwaj" i "człon"; pola "wózek" powinno pozostać puste!',
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
            'BJW': ['type', 'bogie', 'operation_no'],
            'IKS': ['type', 'tram', 'name'],
            'IKK': ['type', 'tram', 'name'],
        }

        for i in self.cleaned_data[req_unique[gate_type][1]]:
            object_params = {}
            for value in req_unique[gate_type]:
                object_params[value] = self.cleaned_data[value]
                if value == req_unique[gate_type][1]:
                    object_params[value] = i
            ob = Gate.objects.filter(**object_params)
            if ob.exists():
                errors_list.append(ValidationError('taki obiekt już istnieje na {}!'.format(i)))

        if errors_list:
            raise ValidationError([errors_list])

        return self.cleaned_data


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
            'file': forms.FileInput(attrs={'class': 'upload-file', 'accept': 'image/*;capture-camera', 'onchange': 'CatchFile(this)'})
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
            'text': forms.Textarea(attrs={'placeholder': u'Wpisz opcjonalny komentarz', 'style': 'margin: 0px; width: 500px; height: 210px;'})
        }


class GateChangeForm(forms.ModelForm):

    class Meta:

        model = Gate
        fields = [
            'type',
            'tram',
            'bogie',
            'car',
            'area',
            'responsible',
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
            'car': u'Człon',
            'area': u'Obszar',
            'responsible': u'Odpowiedzialny',
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
            'car': forms.HiddenInput(),
            'area': forms.HiddenInput(),
            'creation_date': forms.HiddenInput(),
            'modify_date': forms.TextInput(attrs={'readonly': 'readonly'}),
            'author': forms.HiddenInput(),
        }

        field_order = [
            'responsible',
            'operation_no',
            'name',
            'content',
            'modify_date'
        ]

    def __init__(self, *args, **kwargs):
        super(GateChangeForm, self).__init__(*args, **kwargs)
        self.fields['tram'].required = False
        self.fields['car'].required = False
        self.fields['bogie'].required = False
        self.fields['responsible'].choices = [
            (user.pk, '{} {} ({})'.format(user.last_name, user.first_name, user.username))
            for user in User.objects.all().order_by('last_name')
        ]

    def clean(self):

        validate_op_no(self.cleaned_data['operation_no'])

        if not self.cleaned_data['responsible']:
            foreman = OperationArea.objects.get(area=self.cleaned_data['area']).foreman
            self.cleaned_data['responsible'] = foreman

        curr_ob = Gate.objects.get(pk=self.instance.pk)

        req_unique = {
            'BJC': ['type', 'tram', 'car', 'area', 'operation_no'],
            'BJW': ['type', 'bogie', 'operation_no'],
            'IKS': ['type', 'tram', 'name'],
            'IKK': ['type', 'tram', 'name'],
        }

        ob_params = {}

        for i in req_unique[self.cleaned_data['type']]:
            if getattr(curr_ob, i) != self.cleaned_data[i]:
                for i in req_unique[self.cleaned_data['type']]:
                    ob_params[i] = self.cleaned_data[i]
                break
            else:
                pass

        if ob_params and Gate.objects.filter(**ob_params).exists():
            message = '{} {}, obszar {}'.format(
                self.cleaned_data.get('tram', self.cleaned_data['bogie']),
                self.cleaned_data.get('car', ''),
                self.cleaned_data.get('area', ''))

            raise ValidationError(
                'Taki obiekt już istnieje na {}'.format(message))

        return self.cleaned_data


GateFileAddFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=False)
CommentFileAddFormSet = forms.inlineformset_factory(Comment, CommentFile, form=CommentFileAddForm, extra=3, can_delete=False)
GateFileChangeFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=True)
