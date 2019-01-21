from django import forms
from .models import Gate, Comment, CommentFile, GateFile, Tram
from django.forms import inlineformset_factory
from re import search
from django.core.validators import ValidationError


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
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera', 'onchange': 'change(this)'})
        }


class GateAddForm(forms.ModelForm):

    tram = forms.ModelMultipleChoiceField(queryset=Tram.objects.all(), label=u'Tramwaj')
    operation_no = forms.CharField(max_length=6, label=u'Numer operacji', validators=[validate_op_no])
    operation_no.widget = forms.TextInput(attrs={'size': '5px', 'maxlength': '6'})

    class Meta:

        model = Gate

        fields = [
            'type',
            #'tram',
            'bogie',
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

        err_list = []
        print('test')
        def none_test(arg, condition):

            if condition is True and arg is not None:
                return True
            elif condition is False and arg is None:
                return True
            else:
                return False

        requirements_integrity = (
            {
                'BJC': {
                    'conditions': [True, True, False, False],
                    'err_msg': u'Dla tego typu musisz wskazać \'Tramwaj\', \'Człon\' oraz \'Numer operacji\'; '
                               u'pola \'Wózek\' oraz \'Typ wózka\' powinny pozostać puste!'
                }
            },
            {
                'BJW': {
                    'conditions': [False, False, True, True],
                    'err_msg': 'Dla tego typu musisz wskazać \'Wózek\', \'Typ wózka\' oraz \'Numer operacji\'; '
                               'pole \'Tramwaj\' oraz \'Człon\' powinny pozostać puste!'
                }
            },
            {
                'IKS': {
                    'conditions': [True, True, False, False],
                    'err_msg': u'Dla tego typu musisz wskazać \'Tramwaj\' oraz \'Człon\'; '
                               u''u'pola \'Wózek\', \'Typ wózka\' oraz \'Numer operacji\' powinny pozostać puste!'
                }
            },
            {
                'IKK': {
                    'conditions': [True, True, False, False],
                    'err_msg': u'Dla tego typu musisz wskazać \'Tramwaj\' oraz \'Człon\'; '
                               u'pola \'Wózek\', \'Typ wózka\' oraz \'Numer operacji\' powinny pozostać puste!'
                }
            },
        )

        for requirement in requirements_integrity:
            for key, value in requirement.items():
                if key == self.cleaned_data['type']:
                    if not none_test(self.cleaned_data['tram'][0], value['conditions'][0]) \
                            or not none_test(self.cleaned_data['car'], value['conditions'][1]) \
                            or not none_test(self.cleaned_data['bogie'], value['conditions'][2]) \
                            or not none_test(self.cleaned_data['bogie_type'], value['conditions'][3]):
                                raise ValidationError(value['err_msg'])
        print('test2')
        for tram in self.cleaned_data['tram']:
            requirements_unique = (
                {
                    'BJC': {
                        'type': self.cleaned_data['type'],
                        'tram': tram,
                        'car': self.cleaned_data['car'],
                        'area': self.cleaned_data['area'],
                        'operation_no': self.cleaned_data['operation_no']
                    }
                },
                {
                    'BJW': {
                        'type': self.cleaned_data['type'],
                        'bogie': self.cleaned_data['bogie'],
                        'bogie_type': self.cleaned_data['bogie_type'],
                        'operation_no': self.cleaned_data['operation_no']
                    }
                },
                {
                    'IKS': {
                        'type': self.cleaned_data['type'],
                        'tram': tram,
                        'name': self.cleaned_data['name']
                    }
                },
                {
                    'IKK':
                        {'type': self.cleaned_data['type'],
                         'tram': tram,
                         'name': self.cleaned_data['name']
                         }
                },
            )

            for requirement in requirements_unique:
                for key, value in requirement.items():
                    if key == self.cleaned_data['type']:
                        ob = Gate.objects.filter(**value)
                        if ob.exists():
                            err_list.append(ValidationError('taki obiekt już istnieje na {}!'.format(
                                value.get('tram', '{}'.format(value.get('bogie', ''))))))
        print('test3')
        print(err_list)
        if err_list:
            raise ValidationError([err_list])

        print('test4')
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
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera', 'onchange': 'change(this)'})
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
