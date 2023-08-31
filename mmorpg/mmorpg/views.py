from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import DeleteView, UpdateView

from .models import User, Advertisement, Response, Category, Newsletter, Subscriber
from .forms import SignUpForm, NewsletterForm

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import os

from django.views import generic
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Ad

class AdListView(LoginRequiredMixin, generic.ListView):
    model = Ad
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'ads.view_ad')
        return queryset

class AdDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Ad
    permission_required = 'ads.view_ad'

@login_required
def home(request):
    user = request.user
    categories = Category.objects.all()
    latest_ads = Advertisement.objects.order_by('-id')[:10]
    context = {'user': user, 'categories': categories, 'latest_ads': latest_ads}
    return render(request, 'board/home.html', context)


class AdvertisementListView(LoginRequiredMixin, ListView):
    model = Advertisement
    paginate_by = 10
    template_name = 'board/advertisement_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.request.GET.get('category', '')
        context['query'] = self.request.GET.get('query', '')
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.GET.get('category', '')
        query = self.request.GET.get('query', '')

        if category_name != '':
            queryset = queryset.filter(category__name=category_name)

        if query != '':
            queryset = queryset.filter(Q(title__icontains=query) | Q(text__icontains=query))

        return queryset


class AdvertisementCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    fields = ['category', 'title', 'text', 'images', 'videos']
    template_name = 'board/advertisement_create.html'

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super().form_valid(form)


class AdvertisementUpdateView(LoginRequiredMixin, UpdateView):
    model = Advertisement
    fields = ['category', 'title', 'text', 'images', 'videos']
    template_name = 'board/advertisement_update.html'

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)


class AdvertisementDeleteView(LoginRequiredMixin, DeleteView):
    model = Advertisement
    success_url = '/board/advertisements/'
    template_name = 'board/advertisement_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user)


@login_required
def response_create(request, advertisement_id):
    user = request.user
    advertisement = get_object_or_404(Advertisement, pk=advertisement_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        response = Response(
            user=user,
            advertisement=advertisement,
            text=text
        )
        response.save()

        send_mail(
            'Новый отклик на объявление',
            'У вас новый отклик на объявление "{}".'.format(advertisement.title),
            'noreply@example.com',
            [advertisement.user.email],
        )

        return redirect('response_list', advertisement_id=advertisement_id)

    context = {'user': user, 'advertisement': advertisement}
    return render(request, 'board/response_create.html', context)


class ResponseListView(LoginRequiredMixin, ListView):
    model = Response
    paginate_by = 10
    template_name = 'board/response_list.html'

    def get_queryset(self):
        user = self.request.user
        advertisement_id = self.kwargs['advertisement_id']
        return super().get_queryset().filter(advertisement__user=user, advertisement__id=advertisement_id)


@login_required
def response_delete(request, response_id):
    user = request.user
    response = get_object_or_404(Response, pk=response_id)

    if response.user != user:
        return redirect('home')

    advertisement_id = response.advertisement.id
    response.delete()

    return redirect('response_list', advertisement_id=advertisement_id)


@login_required
def response_accept(request, response_id):
    user = request.user
    response = get_object_or_404(Response, pk=response_id)

    if response.advertisement.user != user:
        return redirect('home')

    response.accepted = True
    response.save()

    send_mail(
        'Отклик на объявление принят',
        'Ваш отклик на объявление "{}" принят.'.format(response.advertisement.title),
        'noreply@example.com',
        [response.user.email],
    )

    return redirect('response_list', advertisement_id=response.advertisement.id)


@login_required
def newsletter_create(request):
    if request.method == 'POST':
        user = request.user
        newsletter_form = NewsletterForm(request.POST)
        if newsletter_form.is_valid():
            newsletter = newsletter_form.save()
            subscribers = Subscriber.objects.filter(user=user)
            for subscriber in subscribers:
                send_mail(
                    newsletter.subject,
                    newsletter.message,
                    'noreply@example.com',
                    [subscriber.user.email],
                )
            return HttpResponseRedirect(reverse('newsletter_list'))
    else:
        newsletter_form = NewsletterForm()
    return render(request, 'board/newsletter_create.html', {'newsletter_form': newsletter_form})


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    # paginate_by = 10
    template_name = 'board/newsletter_list.html'

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(subscriber__user=user).distinct()


@login_required
def subscribe(request, newsletter_id):
    user = request.user
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    subscriber, _ = Subscriber.objects.get_or_create(user=user, newsletter=newsletter)

    return redirect('newsletter_list')


@login_required
def unsubscribe(request, newsletter_id):
    user = request.user
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    subscriber = get_object_or_404(Subscriber, user=user, newsletter=newsletter)
    subscriber.delete()

    return redirect('newsletter_list')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email_confirmation_code = User.objects.make_random_password()
            user.save()

            send_mail(
                'Подтверждение регистрации',
                'Перейдите по ссылке ниже для подтверждения регистрации: http://localhost:8000/board/confirm-email/{}/'.format(user.email_confirmation_code),
                'noreply@example.com',
                [user.email],
            )

            return redirect('signup_done')
    else:
        form = SignUpForm()
    return render(request, 'board/signup.html', {'form': form})


def signup_done(request):
    return render(request, 'board/signup_done.html')


def confirm_email(request, code):
    user = get_object_or_404(User, email_confirmation_code=code)
    user.email_confirmation_code = None
    user.email_confirmed = True
    user.save()

    return render(request, 'board/confirm_email.html')


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
       image = request.FILES['image']
       img = Image.open(image)
       img.save(os.path.join('/path/to/images/', image.name), quality=90)
       return HttpResponse('Image uploaded successfully.')
    return HttpResponse('Image uploading error.')