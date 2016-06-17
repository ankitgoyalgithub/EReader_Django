from django.contrib.auth.models import User, Group
from rest_framework import serializers
from reader.models import BooksIssued, Book


class UserSerializer(serializers.ModelSerializer):
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
    bookEpub = serializers.SerializerMethodField()
    coverImageUrl = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ('id', 'bookName', 'isbn', 'author', 'bookEpub', 'coverImageUrl', 'pub_date')

    def get_bookEpub(self, obj):
        return 'http://52.77.237.94' + str(obj.bookEpub).replace('/home/ubuntu/EReader_Django','')

    def get_coverImageUrl(self, obj):
        return 'http://52.77.237.94' + str(obj.coverImageUrl).replace('/home/ubuntu/EReader_Django','')
