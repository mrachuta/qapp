from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Gate, Comment, CommentFile, Tram, OperationArea
from django.views import generic
from django.conf import settings
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from .forms import GateAddForm, GateFileAddFormSet, CommentAddForm, CommentFileAddForm, CommentFileAddFormSet, GateChangeForm, GateFileChangeFormSet
from django.db import IntegrityError
from django.http import Http404, HttpResponseNotFound
from datetime import datetime
import time
from .filters import GateFilter
import re
from django.core.validators import ValidationError
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator


def generate_log(curr_user, pk, log_dict, gate, category, action, *args):

    if args:
        new_value = args[0]
    else:
        new_value = ''

    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    act_type = {
        'rating': u'zaktualizowano ocenę: {}'.format(new_value),
        'status': u'zaktualizowano status: {}'.format(new_value),
        'comment': u'dodano komentarz',
        'file': u'dodano plik',
        'newgate': u'utworzono bramkę',
        'editgate': u'zmieniono bramkę'
    }

    gate.log_set.create(
        date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        author=curr_user,
        category=category,
        action=act_type[action],
    )

    log_dict[curr_time] = [pk, category, act_type[action]]


def change_rating(gate, value):

    if value == 'OK':
        status = 'A'
        gate.gate_status = status
        gate.gate_rating = value
    else:
        status = 'P'
        gate.gate_status = status
        gate.reject_counter += 1
        gate.gate_rating = ''
    gate.save()


def change_status(gate, value):

    gate.gate_status = value
    gate.gate_rating = ''
    gate.save()


def index(request):
    return render(request, 'qapp/gate/index.html', )


class GateListView(generic.ListView):

    queryset = None
    gate_type = None
    template_name = 'qapp/gate/list.html'
    context_object_name = 'gate_list'
    ordering = ['-tram', 'car', '-bogie', 'bogie_type']
    paginate_by = 20

    def get_queryset(self):
        print(self.gate_type)
        queryset = Gate.objects.filter(type=self.gate_type.upper())
        print(queryset.count())
        self.gate_list = GateFilter(self.request.GET, queryset=queryset)
        return self.gate_list.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(GateListView, self).get_context_data(**kwargs)
        context['gate_type'] = self.gate_type
        context['gate_list_filter'] = self.gate_list
        return context


class BjcView(generic.ListView):

    queryset = Gate.objects.filter(type='BJC')
    template_name = 'qapp/gate/list_bjc.html'
    context_object_name = 'bjc'
    ordering = ['-tram', 'car']
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        self.bjc = GateFilter(self.request.GET, queryset=queryset)
        return self.bjc.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(BjcView, self).get_context_data(**kwargs)
        context['bjc_filter'] = self.bjc
        return context


class DetailView(generic.DetailView):

    model = Gate
    template_name = 'qapp/gate/details.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Gate,
                                 pk=self.kwargs['pk'],
                                 )

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['comment_form'] = CommentAddForm(None)
        context['comment_formset'] = CommentFileAddFormSet(None)
        return context


def gate_update(request, pk):

    log_messages = {}
    gate = get_object_or_404(Gate, pk=pk)
    if request.method == "POST":
        comment_form = CommentAddForm(request.POST)
        comment_formset = CommentFileAddFormSet(request.POST, request.FILES)
        if comment_form.is_valid() and comment_formset.is_valid():
            try:
                change_rating(gate, request.POST['new_rating'])
                generate_log(request.user, pk, log_messages, gate, 'S', 'rating', request.POST['new_rating'])
            except KeyError:
                change_status(gate, request.POST['new_status'])
                generate_log(request.user, pk, log_messages, gate, 'S', 'status', request.POST['new_status'])
            if comment_form.cleaned_data['text'] != '':
                try:
                    comment = comment_form.save(commit=False)
                    comment.id = None
                    comment.author = request.user
                    comment.com_rel_gate = gate
                    comment.save()
                    generate_log(request.user, pk, log_messages, gate, 'S', 'comment')
                    for form in comment_formset:
                        if form.cleaned_data != {}:
                            a = form.save(commit=False)
                            a.id = None
                            a.file_rel_comment = comment
                            a.save()
                            generate_log(request.user, pk, log_messages, gate, 'S', 'file')
                            time.sleep(0.1)
                except IntegrityError:
                    log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = [pk, 'E', u'Bramka nie została zaktualizowana']
            log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = [pk, 'S', u'Bramka została zaktualizowana']
            return render(request, 'qapp/gate/results.html', {
                'log_messages': log_messages,
            }
                          )
        else:
            gate_form = GateAddForm(request.POST)
            gate_formset = GateFileAddFormSet(request.POST)
            return render(request, 'qapp/gate/add.html', {
                'gate_form': gate_form,
                'formset': gate_formset,
            }
                          )
    else:
        gate_form = GateAddForm(None)
        gate_formset = GateFileAddFormSet(None)
        return render(request, 'qapp/gate/add.html', {
            'gate_form': gate_form,
            'formset': gate_formset,
        }
                      )


class LogView(generic.DetailView):

    model = Gate
    template_name = 'qapp/gate/log.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Gate, pk=self.kwargs['pk'])


def gate_add(request):

    log_messages = {}
    if request.method == "POST":
        gate_form = GateAddForm(request.POST)
        gate_formset = GateFileAddFormSet(request.POST, request.FILES)
        print('request.POST')
        print(request.POST)
        if gate_form.is_valid() and gate_formset.is_valid():
            print('cleaned_data')
            print(gate_form.cleaned_data)
            if gate_form.cleaned_data['bogie']:
                try:
                    gate = gate_form.save(commit=False)
                    gate.id = None
                    gate.modify_date = None
                    gate.save()
                    for form in gate_formset:
                        if form.cleaned_data != {}:
                            a = form.save(commit=False)
                            a.id = None
                            a.file_rel_gate = gate
                            a.save()
                    generate_log(request.user, gate.pk, log_messages, gate, 'S', 'newgate')
                except (IntegrityError, ValidationError):
                    log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'E', u'Bramka nie została dodana']
                else:
                    log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'S', u'Bramka została dodana']
                    print('Final')
            else:
                for tram in gate_form.cleaned_data['tram']:
                    try:
                        gate = gate_form.save(commit=False)
                        gate.id = None
                        gate.tram = tram
                        gate.modify_date = None
                        gate.save()
                        for form in gate_formset:
                            if form.cleaned_data != {}:
                                a = form.save(commit=False)
                                a.id = None
                                a.file_rel_gate = gate
                                a.save()
                        generate_log(request.user, gate.pk, log_messages, gate, 'S', 'newgate')
                    except (IntegrityError, ValidationError):
                        log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'E', u'Bramka nie została dodana']
                    else:
                        log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'S', u'Bramka została dodana']
            if 'save_add_another' in request.POST:

                init_params = {
                    'type': request.POST['type'],
                    'tram': request.POST.get('tram', ''),
                    'car': request.POST.get('car', ''),
                    'bogie': request.POST.get('bogie', ''),
                    'bogie_type': request.POST.get('bogie_type', ''),
                    'area': request.POST['area'],
                    'creation_date': datetime.now(),
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
                return render(request, 'qapp/gate/results.html', {
                    'log_messages': log_messages,
                }
                              )
        else:
            gate_form = GateAddForm(request.POST)
            gate_formset = GateFileAddFormSet(request.POST)
            return render(request, 'qapp/gate/add.html', {
                'gate_form': gate_form,
                'gate_formset': gate_formset
            }
                          )
    else:
        gate_form = GateAddForm(None, initial={
            'author': request.user,
            'creation_date': datetime.now()
        }
                                )
        gate_formset = GateFileAddFormSet(None)
        return render(request, 'qapp/gate/add.html', {
            'gate_form': gate_form,
            'gate_formset': gate_formset
        }
                      )


class MyGates(generic.ListView):

    template_name = 'qapp/gate/mygates.html'
    context_object_name = 'user_gates'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.groups.filter(name='dzj').exists():
            self.user_gates = GateFilter(self.request.GET, queryset=Gate.objects.all().filter(author=self.request.user).order_by('gate_rating', 'tram'))
        else:
            self.user_gates = GateFilter(self.request.GET, queryset=Gate.objects.all().filter(area__responsible=self.request.user).order_by('gate_rating', 'tram'))
        return self.user_gates.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super(MyGates, self).get_context_data(**kwargs)
        context['user_gates_filter'] = self.user_gates
        return context


def gate_edit(request, pk):
    log_messages = {}
    gate = get_object_or_404(Gate, pk=pk)
    fields_to_show = ['operation_no', 'name', 'content', 'modify_date']
    if request.method == "POST":
        print('request.POST')
        print(request.POST)
        gate_form = GateChangeForm(request.POST, instance=gate)
        gate_formset = GateFileChangeFormSet(request.POST, request.FILES, instance=gate)
        if gate_form.is_valid() and gate_formset.is_valid():
            try:
                gate.save()
                for form in gate_formset:
                    if form.cleaned_data != {}:
                        a = form.save(commit=False)
                        a.save()
                generate_log(request.user, gate.pk, log_messages, gate, 'S', 'editgate')
            except (IntegrityError, ValidationError):
                log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'E', u'Bramka nie została zmieniona']
            else:
                log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'S', u'Bramka została zmieniona']
            return render(request, 'qapp/gate/results.html', {'log_messages': log_messages, })
    else:
        gate_form = GateChangeForm(instance=gate, initial={'modify_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        gate_formset = GateFileChangeFormSet(instance=gate)
    return render(request, 'qapp/gate/edit.html', {'gate_form': gate_form, 'gate_formset': gate_formset, 'fields_to_show': fields_to_show})


def mass_update(request):

    log_messages = {}
    if request.method == "POST":
        # regex_pattern = re.compile(r'(\D\d{2})-(\D\d)-(\D{3})-(\D{2}\d{4})')
        print(request.POST)
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken' and key != 'new_rating':
                gate = get_object_or_404(Gate, pk=key)
                if gate.gate_status == 'O':
                    change_rating(gate, request.POST['new_rating'])
                    generate_log(request.user, gate.pk, log_messages, gate, 'S', 'rating', request.POST['new_rating'])
                    log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'S', u'Bramka została zaktualizowana']
                else:
                    log_messages[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = ['', 'E', u'Bramka nie została zaktualizowana']
        return render(request, 'qapp/gate/results.html', {
            'log_messages': log_messages,
        }
                      )
    else:
        return redirect('qapp:gate_list')
