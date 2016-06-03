from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.views import generic
from reader.models import BooksIssued, Note, Highlight, BookMark, Book
from reader.serializers import UserSerializer
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound
from login.models import ExtendedUser
import sys, os, re
import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from reader.serializers import UserSerializer, BooksIssuedSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework import generics

# Create your views here.

class MyProfile(generic.ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'profile.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		request = self.request
		user = request.user
		context = {}
		issuedBooks = []
		userIssuedBooks = BooksIssued.objects.filter(user=user)
		for booking in userIssuedBooks:
			book = Book.objects.get(id=booking.book_id)
			issuedBooks.append(book)
		context['issuedBooks'] = issuedBooks
		return context

class MyLibrary(generic.ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'my_library.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		request = self.request
		user = request.user
		if hasattr(request.user,'extendeduser'):
			pass
		elif user.socialaccount_set.all():
			social_set = user.socialaccount_set.all()[0]
			if not (ExtendedUser.objects.filter(user_id = user.id)):
				if social_set.provider == 'facebook':
					facebook_data = social_set.extra_data
					print('****************************')
					print(facebook_data)
					print('****************************')
					img_url =  "https://graph.facebook.com/{}/picture?width=140&&height=140".format(facebook_data.get('id',''))
					extendedUser = ExtendedUser(user=user, imageUrl = img_url)
					extendedUser.save()
		context = {}
		issuedBooks = []
		userIssuedBooks = BooksIssued.objects.filter(user=user)
		for booking in userIssuedBooks:
			book = Book.objects.get(id=booking.book_id)
			issuedBooks.append(book)
		context['issuedBooks'] = issuedBooks
		return context

# Create your views here.
class CentralLibrary(generic.ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'central_library.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		request = self.request
		user = request.user
		context = {}
		issuedBooks = []
		bookList = Book.objects.all()
		context['books'] = [book for book in bookList]
		return context

class IssueBookView(generic.ListView):
	template_name = 'central_library.html'
	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		try:
			message = {}
			request = self.request
			user = request.user
			alreadyIssuedBooksCount = BooksIssued.objects.filter(user=user).count()
			if(alreadyIssuedBooksCount == 3):
				message['success'] = 'You already have 3 books issued. First return a book from MyLibrary to continue'
				return HttpResponse(json.dumps(message), content_type='application/json')

			bookId = int(request.POST.get('bookId',''))
			bookToIssue = Book.objects.get(pk=bookId)

			if bookToIssue:
				issuedBooks, created = BooksIssued.objects.get_or_create(user=user, book=bookToIssue)
			else:
				message['success'] = 'Error occured while issuing book'
				return HttpResponse(json.dumps(message), content_type='application/json')

			if created:
				message['success'] = 'Book is successfully issued'
				return HttpResponse(json.dumps(message), content_type='application/json')
			else:
				message['success'] = 'This book is already issued to you.'
				return HttpResponse(json.dumps(message), content_type='application/json')
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			message['success'] = 'Some error occured'
			return HttpResponse(json.dumps(message), content_type='application/json')

class ReturnBookView(generic.ListView):
	template_name = 'my_library.html'
	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		try:
			message = {}
			request = self.request
			user = request.user
			bookId = int(request.POST.get('bookId',''))
			issuedBook = BooksIssued.objects.filter(user=user, book=bookId)

			if issuedBook:
				issuedBook.delete();
				message['success'] = 'Book returned successfully'
				return HttpResponse(json.dumps(message), content_type='application/json')
			else:
				message['success'] = 'Error in returning book'
				return HttpResponse(json.dumps(message), content_type='application/json')
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			message['success'] = 'Some error occured'
			return HttpResponse(json.dumps(message), content_type='application/json')

def getbook(request):
	message = {}
	try:
		bookId = int(request.POST.get('bookId',''))
		if bookId:
			bookToRead = Book.objects.get(pk=bookId)
			bookUrl = str(bookToRead.bookEpub)
			bookUrl = '/media/books/'+bookUrl.split('/')[-1]
			message['bookUrl'] = bookUrl
			message['bookName'] = str(bookToRead.bookName)
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['error'] = 'Error retrieving book info.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def getbookmarks(request):
	message = {}
	bookMarks = []
	try:
		user = request.user
		bookId = int(request.POST.get('bookId',''))
		if bookId and user:
			book = Book.objects.get(pk=bookId)
			userBookmarks = BookMark.objects.filter(user=user, book=book)
			for bookmark in userBookmarks:
				bookMarks.append({'bookMarkName':bookmark.bookmarkName, 'chapterHref':bookmark.chapterHref, 'pageCfi':bookmark.pageCfi})
			message['bookmarkList'] = bookMarks
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['error'] = 'Error in retrieving Bookmarks.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def getNotes(request):
	message = {}
	notes = []
	try:
		user = request.user
		bookId = int(request.POST.get('bookId',''))
		if bookId and user:
			book = Book.objects.get(pk=bookId)
			userNotes = Note.objects.filter(user=user, book=book)
			for note in userNotes:
				notes.append({'noteText':note.text, 'chapterHref':note.chapterHref, 'pageCfi':note.pageCfi, 'wordRange':note.wordRange})
			message['noteList'] = notes
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['error'] = 'Error in retrieving Notes.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def getHighlights(request):
	message = {}
	highlights = []
	try:
		user = request.user
		bookId = int(request.POST.get('bookId',''))
		if bookId and user:
			book = Book.objects.get(pk=bookId)
			userHighlights = Highlight.objects.filter(user=user, book=book)
			for highlight in userHighlights:
				highlights.append({'highlightText':highlight.text, 'chapterHref':highlight.chapterHref, 'pageCfi':highlight.pageCfi, 'wordRange':highlight.wordRange})
			message['highlightList'] = highlights
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['error'] = 'Error in retrieving Highlights.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def saveNotes(request):
	message = {}
	try:
		user = request.user
		bookId = int(request.POST.get('bookId',''))
		wordRange = request.POST.get('wordRange','')
		pageCfi = request.POST.get('pageCfi','')
		chapterHref = request.POST.get('chapterHref','')
		noteText = request.POST.get('noteText','')
		book = Book.objects.get(pk=bookId)

		if book and wordRange and pageCfi and chapterHref and noteText:
			newNote = Note(user=user, book=book, text=noteText, wordRange=wordRange, chapterHref=chapterHref, pageCfi=pageCfi)
			newNote.save()
			message['message'] = 'Notes saved successfully.'
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['message'] = 'Error occured while saving Note.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def saveBookmark(request):
	message = {}
	try:
		user = request.user
		bookmarkName = request.POST.get('bookmarkName','')
		bookId = int(request.POST.get('bookId',''))
		pageCfi = request.POST.get('pageCfi','')
		chapterHref = request.POST.get('chapterHref','')
		book = Book.objects.get(pk=bookId)

		if book and pageCfi and chapterHref and bookmarkName:
			newBookmark = BookMark(user=user, book=book, bookmarkName=bookmarkName, chapterHref=chapterHref, pageCfi=pageCfi)
			newBookmark.save()
			message['message'] = 'Bookmark saved successfully'
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['message'] = 'Error occured while saving Bookmark.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def saveHighlights(request):
	message = {}
	try:
		user = request.user
		bookId = int(request.POST.get('bookId',''))
		wordRange = request.POST.get('wordRange','')
		pageCfi = request.POST.get('pageCfi','')
		chapterHref = request.POST.get('chapterHref','')
		text = request.POST.get('text','')
		book = Book.objects.get(pk=bookId)

		if book and pageCfi and chapterHref and text and wordRange:
			newHighlight = Highlight(user=user, book=book, wordRange=wordRange, text=text, chapterHref=chapterHref, pageCfi=pageCfi)
			newHighlight.save()
			message['message'] = 'Highlight saved successfully'
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['message'] = 'Error occured while saving Highlight'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def editProfile(request):
	message = {}
	try:
		user = request.user
		fieldToEdit = request.POST.get('field','')
		newValue = request.POST.get('value')

		if fieldToEdit == 'first_name':
			user.first_name = newValue
		elif fieldToEdit == 'last_name':
			user.last_name = newValue
		elif fieldToEdit == 'address':
			user.extendeduser.address = newValue
		elif fieldToEdit == 'city':
			user.extendeduser.city = newValue
		elif fieldToEdit == 'country':
			user.extendeduser.country = newValue
		else:
			message['message'] = fieldToEdit+' is not editable.'
			return HttpResponse(json.dumps(message), content_type='application/json')
		user.extendeduser.save()
		user.save()
		message['message'] = 'Profile updated'
		return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def searchBook(request):
	bookList = []
	bookFound = False
	message = {}
	currBookFound = False
	try:
		user = request.user
		searchKey = request.POST.get('searchKey','')

		if searchKey:
			allBooks = Book.objects.all()
			print(allBooks)
			for book in allBooks:
				if re.search(searchKey, book.bookName, re.IGNORECASE):
					currBookFound = True
					bookFound = True
				elif re.search(searchKey, book.author, re.IGNORECASE):
					currBookFound = True
					bookFound = True
				elif re.search(searchKey, book.isbn, re.IGNORECASE):
					currBookFound = True
					bookList.append(book)
					bookFound = True

				if currBookFound:
					currBookFound = False
					tempBook = {}
					tempBook['id'] = book.id
					tempBook['bookName'] = book.bookName
					tempBook['coverImageUrl'] = '/media'+str(book.coverImageUrl).split('media')[1]
					tempBook['author'] = book.author
					bookList.append(tempBook)

			if not bookFound:
				message['message'] = 'Book not found'
				return HttpResponse(json.dumps(message), content_type='application/json')
			else:
				message['bookList'] = bookList
				return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['message'] = 'Provide a valid search key.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def userIssuedBooks(request):
	user = request.user
	message = {}
	issuedBookList = []
	try:
		userIssuedBooks = BooksIssued.objects.filter(user=user)
		if userIssuedBooks:
			for book in userIssuedBooks:
				issuedBookList.append(book.book.id)
			message['issuedBookList'] = issuedBookList
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['issuedBookList'] = []
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['message'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def checkLogin(request):
	user = request.user
	if user is None or not user.is_authenticated or user.is_anonymous():
		url = reverse('account_login')
	else:
		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
	return HttpResponseRedirect(url)

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
		
		
"""
REST API functions
"""

class UserList(generics.ListCreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	
class BookIssuedList(generics.ListCreateAPIView):
	queryset = BooksIssued.objects.all()
	serializer_class = BooksIssuedSerializer


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))		
@csrf_exempt
def issuedBooks(request, pk, format=None):
	if request.method == 'GET':
		response_dict = {}
		issuedBooksList = BooksIssued.objects.filter(user_id=pk)
		if issuedBooksList:
			response_dict["user"] = pk
			response_dict["books"] = []
			for books in issuedBooksList:
				temp = {}
				temp["id"] = books.book.id
				temp["author"] = books.book.author
				temp["isbn"] = books.book.isbn
				temp["bookName"] = books.book.bookName
				temp["bookEpub"] = str(books.book.bookEpub)
				temp["coverImageUrl"] = str(books.book.coverImageUrl)
				temp["pub_date"] =  books.book.pub_date.isoformat()
				response_dict["books"].append(temp)
		else:
			response_dict["error"] = "No Books Issued by the User or Invalid User/Book Id provided"
			return JSONResponse(json.dumps(response_dict), status=400)
		return JSONResponse(json.dumps(response_dict))

@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))		
@csrf_exempt
def issueBook(request, user, book, format=None):
	if request.method == 'POST':
		response = {}
		try:
			user = User.objects.get(pk=user)
		except User.DoesNotExist:
			response['error'] = 'User Id is invalid.'
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
		
		try:
			bookToIssue = Book.objects.get(pk=book)
		except Book.DoesNotExist:
			response['error'] = 'Book Id is invalid.'
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
		
		if user and bookToIssue:
			issuedBooks, created = BooksIssued.objects.get_or_create(user=user, book=bookToIssue)
			if issuedBooks:
				response['success'] = "Book already issued"
			else:
				response['success'] = "Book Issued Successfully"
			return Response(json.dumps(response), status=status.HTTP_201_CREATED)
		else:
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
			
@api_view(['DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))		
@csrf_exempt
def returnBook(request, user, book, format=None):
	if request.method == 'DELETE':
		response = {}
		try:
			user = User.objects.get(pk=user)
		except User.DoesNotExist:
			response['error'] = 'User Id is invalid.'
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
		
		try:
			bookToIssue = Book.objects.get(pk=book)
		except Book.DoesNotExist:
			response['error'] = 'Book Id is invalid.'
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
			
		if user and bookToIssue:
			issuedRecord = BooksIssued.objects.get(user=user, book=bookToIssue)
			if issuedRecord:
				issuedRecord.delete()
				response['success'] = "Book Issued Successfully"
				return Response(status=status.HTTP_204_NO_CONTENT)
			else:
				response['error'] = "The mentioned book is not issued by the user"
				return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
			
		else:
			return Response(json.dumps(response), status=status.HTTP_400_BAD_REQUEST)
			
	