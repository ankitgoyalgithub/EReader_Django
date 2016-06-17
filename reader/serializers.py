from django.contrib.auth.models import User, Group
from rest_framework import serializers
from reader.models import BooksIssued, Book
from login.models import ExtendedUser

class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ('imageUrl', 'city', 'state', 'country', 'address')

class UserSerializer(serializers.ModelSerializer):
    extendedUser = ExtendedUserSerializer()
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
        
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
        
class BooksIssuedSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = BooksIssued
        fields = ('id','user', 'book')

class BookSerializer(serializers.ModelSerializer):
    bookEpub = serializers.SerializerMethodField('get_bookEpub')
    coverImageUrl = serializers.SerializerMethodField('get_coverImageUrl')
    class Meta:
        model = Book
        fields = ('id', 'bookName', 'isbn', 'author', 'bookEpub', 'coverImageUrl', 'pub_date')

    def get_bookEpub(self, obj):
        return obj.bookEpub.replace('/home/ubuntu/EReader_Django','')

    def get_coverImageUrl(self, obj):
        return obj.coverImageUrl.replace('/home/ubuntu/EReader_Django','')