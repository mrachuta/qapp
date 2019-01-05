from django import forms
from .models import Gate, Comment, CommentFile, GateFile, Tram
from django.forms import inlineformset_factory
from re import search


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


class GateAddForm(forms.ModelForm):

    # tram = forms.ModelMultipleChoiceField(queryset=Tram.objects.all(), label=u'Tramwaj')
    operation_no = forms.CharField(max_length=6, label=u'Numer operacji', validators=[validate_op_no])
    operation_no.widget = forms.TextInput(attrs={'size': '8px', 'maxlength': '6'})

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
            'creation_date': u'Data utworzenia',
            'author': u'Autor'
        }

        widgets = {
            # 'tram': forms.CheckboxSelectMultiple(),
            'name': forms.TextInput(attrs={'size': '52px'}),
            'creation_date': forms.TextInput(attrs={'readonly': 'readonly', 'size': '28px'}),
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
        'name', 'content',
        'creation_date',
        'author'
    ]

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
            'file': forms.FileInput(attrs={'accept': 'image/*;capture-camera'})
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

    trams_to_apply = forms.ModelMultipleChoiceField(
        queryset=Tram.objects.all(),
        label=u'Tramwaje do wprowadzenia zmiany'
    )

    class Meta:

        model = Gate
        fields = [
            'tram',
            'car',
            'area',
            'name',
            'content',
            'operation_no',
            'modify_date'
        ]
        labels = {
            'tram': u'Tramwaj źródłowy',
            'car': u'Człon',
            'area': u'Obszar',
            'name': u'Nazwa',
            'operation_no': u'Numer operacji',
            'content': u'Zawartość',
            'modify_date': 'Data modyfikacji',
        }

        widgets = {
            'tram': forms.TextInput(attrs={'readonly': 'readonly'}),
            'car': forms.TextInput(attrs={'readonly': 'readonly'}),
            'area': forms.TextInput(attrs={'readonly': 'readonly'}),
            'modify_date': forms.TextInput(attrs={'readonly': 'readonly'})
        }

    field_order = [
        'tram',
        'car',
        'area',
        'operation_no',
        'name',
        'content',
        'modify_date',
        'trams_to_apply'
    ]


GateFileAddFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=False)
CommentFileAddFormSet = forms.inlineformset_factory(Comment, CommentFile, form=CommentFileAddForm, extra=5, can_delete=False)
GateFileChangeFormSet = forms.inlineformset_factory(Gate, GateFile, form=GateFileAddForm, extra=3, can_delete=True)