from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.urls import reverse
import ntpath
import uuid
import os
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToPathAndRename(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        comm_pk = instance.file_rel_comment.pk
        org_filename = filename.split('.')[:-1]
        ext = filename.split('.')[-1]
        filename = '{}_{}.{}'.format(comm_pk, org_filename, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)


class Tram(models.Model):
    number = models.CharField(max_length=3)
    manufactured_date = models.IntegerField(default=date.today().year, validators=[
        MinValueValidator(2017),
        MaxValueValidator(date.today().year)
    ]
                                           )
    objects = models.Manager

    class Meta:
        ordering = ('-number',)

    def __str__(self):
        return self.number


class Bogie(models.Model):
    number = models.CharField(max_length=11)
    manufactured_date = models.IntegerField(default=date.today().year, validators=[
        MinValueValidator(2017),
        MaxValueValidator(date.today().year)
    ]
                                           )
    objects = models.Manager

    class Meta:
        ordering = ('-number',)

    def __str__(self):
        return self.number


class OperationArea(models.Model):

    AREAS = (
        ('KLE', u'Klejownia'),
        ('KAB', u'Kablownia'),
        ('PDM', u'Podmontaż dachów - mechanika'),
        ('PDE', u'Podmontaż dachów - elektryka'),
        ('MGM', u'Montaż główny - mechanika'),
        ('MGE', u'Montaż główny - elektryka'),
        ('MKM', u'Montaż końcowy - mechanika'),
        ('MKE', u'Montaż końcowy - elektryka'),
        ('MWM', u'Montaż wózków - mechanika'),
        ('MWE', u'Montaż wózków - elektryka'),
        ('MKA', u'Montaż kabin'),
        ('TES', u'Testing'),
        ('MWM', u'Montaż wózków - mechanika'),
        ('MWE', u'Montaż wózków - elektryka'),
        ('ISD', u'Inspekcja końcowa Solaris - dach'),
        ('ISP', u'Inspekcja końcowa Solaris - podwozie'),
        ('ISW', u'Inspekcja końcowa Solaris - wnętrzne'),
        ('ISZ', u'Inspekcja końcowa Solaris - zewnątrz'),
        ('ISL', u'Inspekcja końcowa Solaris - lakier'),
        ('IKT', u'Inspekcja końcowa klienta - tramwaj')
    )

    area = models.CharField(choices=AREAS, max_length=3)
    responsible = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    objects = models.Manager

    def __str__(self):
        return self.area


class Gate(models.Model):

    GATE_TYPE = (
        ('BJC', u'Bramka jakościowa - człon'),
        ('BJW', u'Bramka jakościowa - wózek'),
        ('IKS', u'Inspekcja końcowa - Solaris'),
        ('IKK', u'Inspekcja końcowa - klient')
    )

    CAR_SYMBOLS = (
        ('C1', u'C1'),
        ('C2', u'C2'),
        ('C3', u'C3'),
        ('C4', u'C4')
    )

    BOGIE_TYPES = (
        ('WN1', u'Wózek napędowy 1'),
        ('WN2', u'Wózek napędowy 2'),
        ('WT', u'Wózek toczny'),
        ('WN3', u'Wózek napędowy 3'),
        ('WN4', u'Wózek napędowy 4'),
    )

    GATE_STATUSES = (
        ('R', u'Realizacja'),
        ('O', u'Ocena DZJ'),
        ('P', u'Ponowna realizacja'),
        ('A', u'Archiwum')
    )

    GATE_GRADES = (
        ('OK', u'Zaakceptowany'),
        ('NOK', u'Odrzucony')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(choices=GATE_TYPE, default='BJC', max_length=3)
    tram = models.ForeignKey(Tram, null=True, on_delete=models.CASCADE)
    bogie = models.ForeignKey(Bogie, null=True, on_delete=models.CASCADE)
    bogie_type = models.CharField(choices=BOGIE_TYPES, null=True, max_length=3)
    car = models.CharField(choices=CAR_SYMBOLS, max_length=2, null=True)
    area = models.ForeignKey(OperationArea, null=True, on_delete=models.CASCADE)
    operation_no = models.CharField(max_length=6, null=True)
    name = models.CharField(max_length=200)
    content = models.TextField()
    gate_status = models.CharField(choices=GATE_STATUSES, default='R', max_length=1)
    gate_rating = models.CharField(choices=GATE_GRADES, blank=True, max_length=3)
    reject_counter = models.IntegerField(default='0')
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='author')
    creation_date = models.DateTimeField(default=datetime.now(), blank=True)
    modify_date = models.DateTimeField(default='', blank=True, null=True)
    objects = models.Manager

    class Meta:
        ordering = ('-tram',)
        permissions = (
            ('can_change_gate_status', u'Może zmenić status bramki'),
            ('can_change_gate_rating', u'Może zmienić ocenę bramki'),
            ('can_add_new_gate', u'Może dodać nową bramkę')
        )

        #unique_together = ('type', 'tram', 'car', 'area', 'operation_no')

    def validate_unique(self, exclude=None):

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
                if key == self.type:
                    if not none_test(self.tram, value['conditions'][0]) \
                            or not none_test(self.car, value['conditions'][1]) \
                            or not none_test(self.bogie, value['conditions'][2]) \
                            or not none_test(self.bogie_type, value['conditions'][3]):
                                raise ValidationError(value['err_msg'])

        #print(vars(self))
        requirements_unique = (
            {
                'BJC': {
                    'type': self.type,
                    'tram': self.tram,
                    'car': self.car,
                    'area': self.area,
                    'operation_no': self.operation_no
                }
            },
            {
                'BJW': {
                    'type': self.type,
                    'bogie': self.bogie,
                    'bogie_type': self.bogie_type,
                    'operation_no': self.operation_no
                }
            },
            {
                'IKS': {
                    'type': self.type,
                    'tram': self.tram,
                    'name': self.name
                }
            },
            {
                'IKK':
                    {'type': self.type,
                     'tram': self.tram,
                     'name': self.name
                     }
            },
        )
        for requirement in requirements_unique:
            for key, value in requirement.items():
                if key == self.type:
                    ob = Gate.objects.filter(**value)
                    if ob.exists():
                        raise ValidationError('Taki obiekt już istnieje!')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('qapp:gate_details', args=[
            self.pk,
        ])


class GateFile(models.Model):
    file_rel_gate = models.ForeignKey(Gate, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads_g', blank=True, null=True)

    def filename(self):
        return ntpath.basename(self.file.name)

    def __str__(self):
        return u'Załącznik do bramki: {}'.format(self.file)



class Comment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    com_rel_gate = models.ForeignKey(Gate, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000, blank=True, null=True)
    #file = models.FileField(upload_to='uploads_c', blank=True, null=True)
    date_time = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return 'Komentarz, autor: {}'.format(self.author)


class CommentFile(models.Model):
    file_rel_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    file = models.FileField(upload_to=UploadToPathAndRename(os.path.join('uploads_c')), blank=True, null=True)

    def filename(self):
        return ntpath.basename(self.file.name)

    def __str__(self):
        return 'Załącznik do komentarza: {}'.format(self.file)



class Log(models.Model):

    log_rel_gate = models.ForeignKey(Gate, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now())
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    category = models.CharField(max_length=1, blank=True)
    action = models.CharField(max_length=30)

    def __str__(self):
        return 'Log z {}'.format(self.date_time)