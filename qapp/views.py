from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Gate
from django.views import generic
from .forms import GateAddForm, GateFileAddFormSet, CommentAddForm, CommentFileAddFormSet, GateChangeForm, GateFileChangeFormSet
from django.db import IntegrityError
#from datetime import datetime
#import time
from django.utils import timezone
import pytz
from .filters import GateFilter
from django.core.validators import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin



# Test for decorator
def is_member(user):
    return user.groups.filter(name='dzj').exists()


def log_date_time(**kwargs):
    if kwargs == {'format': 'yes'}:
        return timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return timezone.now()


def generate_log(curr_user, pk, log_dict, gate, category, action, *args):

    """Function generate logs for changes in gate object:

    :param curr_user: user, that make changes in gate object (request.user),
    :param pk: primary key of gate - for printing on screen (identification of gate in 'results.html'),
    :param log_dict: name of dictionary with messages (defined in a view),
    :param gate: gate, for which log was generated,
    :param category: 'S' (sucess) or 'E' (error),
    :param action: type of action to log; value from act_type dictionary,
    :param args: optional argument with for example new value (see act_type dictionary)

    """

    if args:
        new_value = args[0]
    else:
        new_value = ''

    curr_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    act_type = {
        'rating': u'zaktualizowano ocenę: {}'.format(new_value),
        'status': u'zaktualizowano status: {}'.format(new_value),
        'comment': u'dodano komentarz',
        'file': u'dodano plik',
        'newgate': u'utworzono bramkę',
        'editgate': u'zmieniono bramkę'
    }

    gate.log_set.create(
        date_time=log_date_time(),
        author=curr_user,
        category=category,
        action=act_type[action],
    )

    # Add recently added log to view's log dictionary to show them as result (see view's 'redirect' - to 'result.html').
    log_dict[curr_time] = [pk, category, act_type[action]]


def change_rating(gate, value):

    """Function change gate rating (after marking gate.status == 'O').
    If value is 'OK', status will be set to 'A' (gate is closed, so can be moved to archive; prevents from changes)
    and rating to 'OK'.
    If rating is 'NOK', status will be se to 'P', rejection counter (how many times inspection was performed) will
    be increased by 1, and rating will be set to 'NOK' (gate have to be fixed, and inspected once again).

    :param gate: gate object, which will be changed,
    :param value: 'OK' when gate could be accepted, 'P' if gate have to be corrected.

    """

    if value == 'OK':
        status = 'A'
        gate.status = status
        gate.rating = value
    else:
        status = 'P'
        gate.status = status
        gate.reject_counter += 1
        gate.rating = value
    gate.save()


def change_status(gate, value):

    """
    Function change gate status (gate.status can be set as 'O' for receive an rating).
    Allow to change gate status to 'O' (ready to inspection). After set this status, rating is cleaned.

    :param gate: gate object, which will be changed,
    :param value: usually 'O'.

    """

    gate.status = value
    gate.rating = ''
    gate.save()


def index(request):
    return render(request, 'qapp/gate/index.html', )


class GateListView(generic.ListView):

    """
    Universal ListView for all types of Gate object.
    Necessary to specify Gate.type in parameters delivered to class (see urls.py for app).
    For keeping compatibility with django-filter addon, methods get_queryset and get_context_data had to be override.
    (filtered data instead original queryset result have to be delivered to template).
    Due to many Gate.type variants, also ordering should be customized (Gate.type == 'BJW' had no
    tram and car attributes (they are NULL)).
    """

    queryset = None
    gate_type = None
    template_name = 'qapp/gate/list.html'
    context_object_name = 'gate_list'
    paginate_by = 20

    def get_queryset(self):
        # Type is stored in database as big-letter word, so 'bjc' != 'BJC'.
        if self.gate_type.upper() == 'BJW':
            ordering = ['bogie']
        else:
            ordering = ['tram', 'car']
        queryset = Gate.objects.filter(type=self.gate_type.upper()).order_by(*ordering)
        self.gate_list = GateFilter(self.request.GET, queryset=queryset)
        return self.gate_list.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(GateListView, self).get_context_data(**kwargs)
        # Return Gate.type to template.
        context['gate_type'] = self.gate_type
        # Return object (for generating form) to template.
        context['gate_list_filter'] = self.gate_list
        return context


class DetailView(generic.DetailView):

    model = Gate
    template_name = 'qapp/gate/details.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Gate, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['comment_form'] = CommentAddForm(None)
        context['comment_formset'] = CommentFileAddFormSet(None)
        return context

@login_required
def gate_update(request, pk):

    log_messages = {}
    gate = get_object_or_404(Gate, pk=pk)
    if request.method == "POST":
        comment_form = CommentAddForm(request.POST)
        comment_formset = CommentFileAddFormSet(request.POST, request.FILES)
        if comment_form.is_valid() and comment_formset.is_valid():
            try:
                # Check, does it is change of Gate.rating or Gate.status?
                change_rating(gate, request.POST['new_rating'])
                generate_log(request.user, pk, log_messages, gate, 'S', 'rating', request.POST['new_rating'])
            except KeyError:
                change_status(gate, request.POST['new_status'])
                generate_log(request.user, pk, log_messages, gate, 'S', 'status', request.POST['new_status'])
            if comment_form.has_changed():
                # If comment-text is not empty, add Comment object.
                try:
                    comment = comment_form.save(commit=False)
                    comment.id = None
                    comment.author = request.user
                    comment.com_rel_gate = gate
                    comment.date_time = log_date_time()
                    comment.save()
                    generate_log(request.user, pk, log_messages, gate, 'S', 'comment')
                    # Try to iterate over files attached to Comment object and add every file as CommentFile object.
                    # Adding empty comment-text with files is prevented, using JS (see details.html template).
                    for form in comment_formset:
                        if form.is_valid():
                            if form.has_changed():
                                a = form.save(commit=False)
                                a.id = None
                                a.file_rel_comment = comment
                                a.save()
                                generate_log(request.user, pk, log_messages, gate, 'S', 'file')
                                # Sleep for a moment, to generate log with different time for each file.
                                # Without this, every file have the same time of adding in log.
                                #time.sleep(0.1)
                except IntegrityError:
                    log_messages[log_date_time(format='yes')] = [pk, 'E', u'Bramka nie została zaktualizowana']
            log_messages[log_date_time(format='yes')] = [pk, 'S', u'Bramka została zaktualizowana']
            # If all jobs finished, go to result page and show the changes stored in log_messages dict
            return render(request, 'qapp/gate/results.html', {
                'log_messages': log_messages,
            }
                          )
        else:
            # If there some errors in form, allow user to correct data (render pre-filled form with error messages).
            gate_form = GateAddForm(request.POST)
            gate_formset = GateFileAddFormSet(request.POST)
            return render(request, 'qapp/gate/add.html', {
                'gate_form': gate_form,
                'formset': gate_formset,
            }
                          )
    else:
        # If request was not made by POST method, render blank form.
        gate_form = GateAddForm(None)
        gate_formset = GateFileAddFormSet(None)
        return render(request, 'qapp/gate/add.html', {
            'gate_form': gate_form,
            'formset': gate_formset,
        }
                      )



class LogView(LoginRequiredMixin, generic.DetailView):

    model = Gate
    template_name = 'qapp/gate/log.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Gate, pk=self.kwargs['pk'])


@login_required
@user_passes_test(is_member)
def gate_add(request):

    log_messages = {}
    if request.method == "POST":
        gate_form = GateAddForm(request.POST)
        gate_formset = GateFileAddFormSet(request.POST, request.FILES)
        if gate_form.is_valid() and gate_formset.is_valid():
            if gate_form.cleaned_data['type'] == 'BJW':
                # Gate.type is declared by user as 'BJW' (because for this type tram and car attributes are NULL's).
                for bogie in gate_form.cleaned_data['bogie']:
                    try:
                        gate = gate_form.save(commit=False)
                        gate.id = None
                        gate.bogie = bogie
                        gate.modify_date = None
                        gate.save()
                        for form in gate_formset:
                            if form.is_valid():
                                if form.has_changed():
                                    a = form.save(commit=False)
                                    a.id = None
                                    a.file_rel_gate = gate
                                    a.save()
                        generate_log(request.user, gate.pk, log_messages, gate, 'S', 'newgate')
                    except (IntegrityError, ValidationError):
                        log_messages[log_date_time(format='yes')] = ['', 'E', u'Bramka nie została dodana']
                    else:
                        log_messages[log_date_time(format='yes')] = ['', 'S', u'Bramka została dodana']
            else:
                # Gate.type is other than 'BJW', because rest of types have bogie and bogie_type attributes as NULL's.
                for tram in gate_form.cleaned_data['tram']:
                    try:
                        gate = gate_form.save(commit=False)
                        gate.id = None
                        gate.tram = tram
                        gate.modify_date = None
                        gate.save()
                        for form in gate_formset:
                                if form.is_valid():
                                    if form.has_changed():
                                        a = form.save(commit=False)
                                        a.id = None
                                        a.file_rel_gate = gate
                                        a.save()
                        generate_log(request.user, gate.pk, log_messages, gate, 'S', 'newgate')
                    except (IntegrityError, ValidationError):
                        log_messages[log_date_time(format='yes')] = ['', 'E', u'Bramka nie została dodana']
                    else:
                        log_messages[log_date_time(format='yes')] = ['', 'S', u'Bramka została dodana']
            if 'save_add_another' in request.POST:
                # To speed-up multiple Gate adding, generating results via results.html are skipped.
                # Pre-filled form with important data from previous request is generated; the results of previous
                # request are showed below the form.
                init_params = {
                    'type': request.POST['type'],
                    'tram': request.POST.get('tram', ''),
                    'car': request.POST.get('car', ''),
                    'bogie': request.POST.get('bogie', ''),
                    'bogie_type': request.POST.get('bogie_type', ''),
                    'area': request.POST['area'],
                    'creation_date': timezone.now(),
                    'author': request.POST['author']
                }
                gate_form = GateAddForm(None, initial=init_params)
                gate_formset = GateFileAddFormSet(None)
                return render(request, 'qapp/gate/add.html', {
                    'gate_form': gate_form,
                    'gate_formset': gate_formset,
                    'log_messages': log_messages,
                }
                              )
            else:
                # If all jobs finished, go to result page and show the changes stored in log_messages dict.
                return render(request, 'qapp/gate/results.html', {
                    'log_messages': log_messages,
                }
                              )
        else:
            # If there some errors in form, allow user to correct data (render pre-filled form with error messages).
            gate_form = GateAddForm(request.POST)
            gate_formset = GateFileAddFormSet(request.POST)
            return render(request, 'qapp/gate/add.html', {
                'gate_form': gate_form,
                'gate_formset': gate_formset
            }
                          )
    else:
        # If request was not made by POST method, render blank form.
        gate_form = GateAddForm(None, initial={
            'author': request.user,
            'creation_date': timezone.now()
        }
                                )
        gate_formset = GateFileAddFormSet(None)
        return render(request, 'qapp/gate/add.html', {
            'gate_form': gate_form,
            'gate_formset': gate_formset
        }
                      )


class MyGates(LoginRequiredMixin, generic.ListView):

    template_name = 'qapp/gate/mygates.html'
    context_object_name = 'user_gates'
    paginate_by = 20

    """
    Customized get_context_data method is connected with django-filter addon.
    See class GateListView(generic.ListView) comment for more informations.
    """

    def get_queryset(self):
        # Return context_object_name for dzj-group member or for non-members
        if self.request.user.groups.filter(name='dzj').exists():
            self.user_gates = GateFilter(self.request.GET, queryset=Gate.objects.all().
                                         filter(author=self.request.user).
                                         order_by('rating', 'tram')
                                         )
        else:
            self.user_gates = GateFilter(self.request.GET, queryset=Gate.objects.all().
                                         filter(responsible=self.request.user).
                                         order_by('rating', 'tram')
                                         )
        return self.user_gates.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(MyGates, self).get_context_data(**kwargs)
        context['user_gates_filter'] = self.user_gates
        return context


@login_required
@user_passes_test(is_member)
def gate_edit(request, pk):
    log_messages = {}
    gate = get_object_or_404(Gate, pk=pk)
    # Fields below could be changed on existing model via POST request; rest of model fields are generated as static
    if request.method == "POST":
        gate_form = GateChangeForm(request.POST, instance=gate)
        gate_formset = GateFileChangeFormSet(request.POST, request.FILES, instance=gate)
        if gate_form.is_valid() and gate_formset.is_valid():
            try:
                gate.save()
                gate_formset.save()
                generate_log(request.user, gate.pk, log_messages, gate, 'S', 'editgate')
            except (IntegrityError, ValidationError):
                log_messages[log_date_time(format='yes')] = ['', 'E', u'Bramka nie została zmieniona']
            else:
                log_messages[log_date_time(format='yes')] = ['', 'S', u'Bramka została zmieniona']
            return render(request, 'qapp/gate/results.html', {
                'log_messages': log_messages,
            }
                          )
        else:
            # If there some errors in form, allow user to correct data (render pre-filled form with error messages).
            gate_form = GateChangeForm(request.POST, instance=gate, initial={'modify_date': log_date_time()})
            gate_formset = GateFileChangeFormSet(request.POST, request.FILES, instance=gate)
            return render(request, 'qapp/gate/edit.html', {
                'gate_form': gate_form,
                'gate_formset': gate_formset,
                'gate.pk': pk,
            }
                          )
    else:
        # If request was not made by POST method, render blank form.
        gate_form = GateChangeForm(instance=gate, initial={'modify_date': log_date_time()})
        gate_formset = GateFileChangeFormSet(instance=gate)
        return render(request, 'qapp/gate/edit.html', {
            'gate_form': gate_form,
            'gate_formset': gate_formset,
            'gate.pk': pk,
        }
                      )

@login_required
@user_passes_test(is_member)
def mass_update(request):
    log_messages = {}
    if request.method == "POST":
        for key, value in request.POST.items():
            # Skip unecessary values received via POST.
            if key != 'csrfmiddlewaretoken' and key != 'new_rating':
                gate = get_object_or_404(Gate, pk=key)
                # Make changes in gate, only if gate.status == 'O'
                if gate.status == 'O':
                    change_rating(gate, request.POST['new_rating'])
                    generate_log(request.user, gate.pk, log_messages, gate, 'S', 'rating', request.POST['new_rating'])
                    log_messages[log_date_time(format='yes')] = ['', 'S', u'Bramka została zaktualizowana']
                else:
                    log_messages[log_date_time(format='yes')] = ['', 'E', u'Bramka nie została zaktualizowana']
        return render(request, 'qapp/gate/results.html', {
            'log_messages': log_messages,
        }
                      )
    else:
        return redirect('qapp:gate_list')
