from django.shortcuts import render, redirect
from .models import Articles, Comments
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ArticleForm, AuthUserForm, RegisterUserForm, CommentForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.edit import FormMixin
from django.template import Context, Template


# класс для уведомлений об успехе
class CustomSuccessMessageMixin:
    @property
    def success_msg(self):
        return False

    # если форма валидна, то добавлены request и текущ сообщение
    def form_valid(self, form):
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)

    # вводен доп параметр id статьи в url
    def get_success_url(self):
        return '%s?id=%s' % (self.success_url, self.object.id)


class HomeListView(ListView):
    model = Articles
    template_name = 'core/index.html'
    context_object_name = 'list_articles'


# в классе DetailView нет form для комментариев
# поэтому доп наследуем от FormMixin из файла django edit.py
class HomeDetailView(CustomSuccessMessageMixin, FormMixin, DetailView):
    model = Articles
    template_name = 'core/detail.html'
    context_object_name = 'get_article'
    # форма для комментариев
    form_class = CommentForm
    success_msg = 'Комментарий создан и отправлен на модерацию'

    # переопределен метод класса CustomSuccessMessageMixin
    def get_success_url(self, **kwargs):
        return reverse_lazy('detail_page', kwargs={'pk': self.get_object().id})

    # переопределен метод post для формы комментария
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # для сохранения переопределен метод проверки валидности
    def form_valid(self, form):
        # создаем self.object, но commit=False запись еще не сохранена в БД
        self.object = form.save(commit=False)
        # добавлен доп параметр article и автор к self.object
        self.object.article = self.get_object()
        self.object.author = self.request.user
        # сохраняет в БД
        self.object.save()
        return super().form_valid(form)


# LoginRequiredMixin - доступ только для авторизованных пользователей
# CustomSuccessMessageMixin - уведомление об успехе
class ArticleCreateView(LoginRequiredMixin, CustomSuccessMessageMixin, CreateView):
    model = Articles
    template_name = 'core/edit_page.html'
    form_class = ArticleForm
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись создана'

    # добавлены данные к get_context_data
    def get_context_data(self, **kwargs):
        kwargs['list_articles'] = Articles.objects.all().order_by('-id')
        return super().get_context_data(**kwargs)

    # переопределен метод form_valid
    # к данным формы автоматически добавляет
    # имя авторизованного Автора при создании статьи
    def form_valid(self, form):
        # создан self.object но commit=False без сохранения в БД
        self.object = form.save(commit=False)
        # добавлен параметр author к self.object = имя user
        self.object.author = self.request.user
        # сохраняет в БД
        self.object.save()
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, CustomSuccessMessageMixin, UpdateView):
    model = Articles
    template_name = 'core/edit_page.html'
    form_class = ArticleForm
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись обновлена'

    # добавлен параметр update = True
    def get_context_data(self, **kwargs):
        kwargs['update'] = True
        return super().get_context_data(**kwargs)

    # переопределен метод для блокировки редактирования чужих статей
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs['instance'].author # имя автора статьи
        # self.request.user # имя авторизованного пользователя
        # если user не автор статьи, то отказ доступа (403 Forbidden)
        if self.request.user != kwargs['instance'].author and str(self.request.user) != 'admin':
            return self.handle_no_permission()
        return kwargs


# класс использует метод post, в шаблоне edit page использована форма
class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Articles
    template_name = 'core/edit_page.html'
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись удалена'

    # тк метод post то не применить класс mixin для уведомелния
    # переопределен метод post
    def post(self, request, *args, **kwargs):
        messages.success(self.request, self.success_msg)
        return super().post(request)

    # переопределен метод для блокировки удаления чужих статей
    def form_valid(self, request):
        self.object = self.get_object()
        # если User не Автор статьи, то доступ к url удаления закрыт 403
        if self.request.user != self.object.author and str(self.request.user) != 'admin':
            return self.handle_no_permission()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class MyprojectLoginView(LoginView):
    template_name = 'core/login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('edit_page')

    # переопределен url при успешной авторизации
    # вместо стандартного значения http://127.0.0.1:8000/accounts/profile/
    def get_success_url(self):
        return self.success_url


class RegisterUserView(CreateView):
    model = User
    template_name = 'core/register_page.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('edit_page')

    # если форма регистрации валидна, то пользователь авторизуется автоматически
    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        # authenticate, login - функция django
        aut_user = authenticate(username=username, password=password)
        login(self.request, aut_user)
        return form_valid


class MyProjectLogout(LogoutView):
    next_page = reverse_lazy('home')


# изменяет статус комментария
def update_comment_status(request, pk, type):
    comment = Comments.objects.get(pk=pk)
    if request.user != comment.article.author and str(request.user) != 'admin':
        return HttpResponse('Denied. Нет доступа')
    if type == 'public':
        # для инвертирования статуса comment.status = True / False
        # operator меняет значение на обратное при каждом обращении
        import operator
        comment.status = operator.not_(comment.status)
        comment.save()
        template = 'core/comment_item.html'
        context = {'comment': comment, 'status_comment': 'Статус публикации изменен'}
        return render(request, template, context)
    elif type == 'delete':
        comment.delete()
        # эта часть может быть переписана аналогично предыдущему
        # через шаблон, но добавив проверку на существование comment
        return HttpResponse('''
            <div class="alert alert-success">
            Комментарий удален
            </div>
            ''')
    return HttpResponse('1')

