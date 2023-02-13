from django.urls import path
from core import views

urlpatterns = [
    # реализация через классы
    path('', views.HomeListView.as_view(), name='home'),
    path('detail/<int:pk>', views.HomeDetailView.as_view(), name='detail_page'),
    path('edit-page', views.ArticleCreateView.as_view(), name='edit_page'),
    path('update-page/<int:pk>', views.ArticleUpdateView.as_view(), name='update_page'),
    path('delete-page/<int:pk>', views.ArticleDeleteView.as_view(), name='delete_page'),
    path('login', views.MyprojectLoginView.as_view(), name='login_page'),
    path('register', views.RegisterUserView.as_view(), name='register_page'),
    path('logout', views.MyProjectLogout.as_view(), name='logout_page'),
    #ajax
    path('update_comment_status/<int:pk>/<slug:type>', views.update_comment_status, name='update_comment_status'),

    # реализация через функции
    # path('', views.home, name='home'),
    # path('detail/<int:id>', views.detail_page, name='detail_page'),
    # path('edit-page', views.edit_page, name='edit_page'),
    # path('update-page/<int:pk>', views.update_page, name='update_page'),
    # path('delete-page/<int:pk>', views.delete_page, name='delete_page'),

]