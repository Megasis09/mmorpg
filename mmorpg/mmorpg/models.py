from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm, get_objects_for_user

class Ad(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ad_detail', kwargs={'pk': self.pk})

class User(AbstractUser):
    email_confirmation_code = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    email_confirmed = models.BooleanField(
        verbose_name=_('E-mail подтверждён'),
        default=False
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    CATEGORY_CHOICES = (
        ('Tank', 'Танки'),
        ('Healer', 'Хилы'),
        ('DD', 'ДД'),
        ('Trader', 'Торговцы'),
        ('GuildMaster', 'Гилдмастеры'),
        ('QuestGiver', 'Квестгиверы'),
        ('BlackSmith', 'Кузнецы'),
        ('LeatherWorker', 'Кожевники'),
        ('Alchemist', 'Зельевары'),
        ('SpellMaster', 'Мастера заклинаний')
    )

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class Image(models.Model):
    file = models.ImageField(upload_to='images/')


class Video(models.Model):
    url = models.TextField()


class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    images = models.ManyToManyField(Image, blank=True)
    videos = models.ManyToManyField(Video, blank=True)

    def __str__(self):
        return self.title


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    def __str__(self):
        return self.subject


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.user, self.newsletter.subject)