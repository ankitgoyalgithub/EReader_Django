from django.conf.urls import patterns, include, url
from login import views
from reader import views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$',views.checkLogin,name='checklogin'),
	url(r'^mylibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyLibrary.as_view()),name='mylibrary'),
    url(r'^centrallibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.CentralLibrary.as_view()),name='centrallibrary'),
    url(r'^myprofile/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyProfile.as_view()),name='myprofile'),
	url(r'^issuebook$',login_required(views.IssueBookView.as_view()),name='issuebook'),
	url(r'^returnbook$',login_required(views.ReturnBookView.as_view()),name='returnbook'),
	url(r'^getbookurl$',login_required(views.getbook),name='getbook'),
    url(r'^getbookmarks$',login_required(views.getbookmarks),name='getbookmarks'),
    url(r'^gethighlights$',login_required(views.getHighlights),name='gethighlights'),
	url(r'^getnotes$',login_required(views.getNotes),name='getNotes'),
	url(r'^savenotes$',login_required(views.saveNotes),name='saveNotes'),
    url(r'^savebookmark$',login_required(views.saveBookmark),name='savebookmark'),
    url(r'^savehighlights$',login_required(views.saveHighlights),name='savehighlights'),
    url(r'^editprofile$',login_required(views.editProfile),name='editprofile'),
    url(r'^searchbook$',login_required(views.searchBook),name='searchbook'),
    url(r'^userissuedbooks$',login_required(views.userIssuedBooks),name='userissuedbooks'),
    url(r'^termsofservice', TemplateView.as_view(template_name='termsofservice.html'), name='termsofservice'),
    url(r'^privacypolicy', TemplateView.as_view(template_name='privacypolicy.html'), name='privacypolicy'),
    url(r'^user_list$',views.UserList.as_view(),name='userlist'),
    url(r'^user_detail/(?P<pk>[0-9]+)$', views.UserDetail.as_view(), name='userdetail'),
    url(r'^books_issued_list$',views.BookIssuedList.as_view(),name='booksissuedlist'),
    url(r'^getuserissuedbooks/(?P<pk>[0-9]+)$', views.issuedBooks, name='getissuedbooks'),
    url(r'^issuebook/(?P<user>[0-9]+)/(?P<book>[\w\-]+)$', views.issueBook, name='issuebook'),
    url(r'^returnbook/(?P<user>[0-9]+)/(?P<book>[\w\-]+)$', views.returnBook, name='returnbook'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
