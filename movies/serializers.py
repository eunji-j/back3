from rest_framework import serializers
from .models import Genre, Movie, HashTag
from accounts.models import User

class HashTagSerializer(serializers.ModelSerializer):
    # movies = MovieSerializer(many=True)
    class Meta:
        model = HashTag
        fields = '__all__'
        
class GenreSerializer(serializers.ModelSerializer):
    # movies = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all(), many=True)
    class Meta:
        model = Genre
        fields = ('id', 'name', 'movies')

class MovieSerializer(serializers.ModelSerializer):
    # genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)
    # hashtag = serializers.PrimaryKeyRelatedField(queryset=HashTag.objects.all(), many=True)
    # like_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    genres = GenreSerializer(many=True)
    hashtags = HashTagSerializer(many=True)
    
    class Meta:
        model = Movie
        fields = ('id', 'title', 'image', 'director', 'actor', 'score', 'rating', 'audience', 'genres', 'hashtags')

