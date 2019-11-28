from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import MovieSerializer, GenreSerializer, ReviewSerializer, ReviewCreateSerializer, SortSerializer
from .models import Movie, Genre, HashTag, Review, Sort
from accounts.models import User
from accounts.serializers import UserSerializer2
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import random

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny,])
def index(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def top10(request):
    movies = Movie.objects.all().order_by('-score')[:10]
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def recommended(request, id):
    user = get_object_or_404(User, id=id)
    genres = user.like_genres.all()
    reviews = Review.objects.filter(user=user)
    # 1.평점 8 이상 영화의 해시태그들
    hashtagList = []
    watchMovie = []
    for review in reviews:
        if review.star >= 8:
            movie = get_object_or_404(Movie, title=review.movie)
            watchMovie.append(movie)
            for hashtag in movie.hashtags.all():
                hashtagList.append(hashtag)
    # 2.선호장르의 영화의 해시태그들
    movieList = []
    movieList2 = []
    for genre in genres:
        genre2 = get_object_or_404(Genre, name=genre)
        movies = Movie.objects.filter(genres=genre2).order_by('-score')
        # print(movies)

        for movie in movies:
            for hashtag in movie.hashtags.all():
                for h in hashtagList:
                    if hashtag == h:
                        # 사용자가 이미 평점을 남긴 영화는 제외
                        if movie not in watchMovie:
                            movieList.append(movie)
                # 사용자가 이미 평점을 남긴 영화는 제외
                if movie not in watchMovie:
                    movieList2.append(movie)
                break

    if movieList:
        movie = movieList[random.randrange(0, len(movieList)-1)]
    else:
        movie = movieList2[random.randrange(0, len(movieList2)-1)]
    serializer = MovieSerializer(movie)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def detail(request, id):
    movie = get_object_or_404(Movie, id=id)
    serializer = MovieSerializer(movie)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def hashtags(request, id):
    hashtags = HashTag.objects.filter(tagged_movie=id)
    # print(hashtags)
    movie2 = []
    # 1.각 해시태그가 있는 영화들을 value만 추출해서 movie2 한곳에 담아준다.
    for hashtag in hashtags:
        # temp = Movie.objects.filter(hashtags=hashtag)
        temp = hashtag.tagged_movie.all()
        for i in temp.values():
            if i not in movie2:
                movie2.append(i)
    # print(movie2)
    # 2.여러개 보낼 때는 serializer사용하지 않고 보내준다(리스트형태).
    return JsonResponse(movie2, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def get_movies(request, id):
    hashtag = get_object_or_404(HashTag, id=id)
    movies = hashtag.tagged_movie.all()
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def get_genres(request):
    genres = Genre.objects.all()
    # print(genres)
    serializer = GenreSerializer(genres, many=True)
    return JsonResponse(serializer.data, safe=False)
    
@api_view(['GET'])
@permission_classes([AllowAny,])
def genre(request, id):
    genre = get_object_or_404(Genre, id=id)
    movies = genre.movies.all().order_by('-score')
    serializer = MovieSerializer(movies, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def like(request, id):
    movie = get_object_or_404(Movie, id=id)
    user = request.user
    
    if user not in movie.users.all():
        movie.users.add(user)
        is_ok = True
    else:
        movie.users.remove(user)
        is_ok = False
    context = {
        'likes_cnt': movie.users.all().count(),
        'is_ok': is_ok
    }
    return JsonResponse(context)

@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def review(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            review = serializer.save(user=request.user, movie=movie)
            serializer = ReviewSerializer(review)
            return JsonResponse(serializer.data, safe=False)
        return HttpResponse(status=400)
    elif request.method == 'DELETE':
        review = get_object_or_404(Review, id=id)
        review.delete()
        return

@api_view(['GET'])
@permission_classes([AllowAny,])
def get_reviews(request, id):
    movie = get_object_or_404(Movie, id=id)
    reviews = movie.review_set.all()
    serializer = ReviewSerializer(reviews, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def sorts(request):
    sorts = Sort.objects.filter(sort=1)
    serializer = SortSerializer(sorts, many=True)
    sorts = Sort.objects.filter(sort=2)
    serializer2 = SortSerializer(sorts, many=True)
    context = {
        'sort1': serializer.data,
        'sort2': serializer2.data
    }
    return JsonResponse(context, safe=False)

@api_view(['GET'])
@permission_classes([AllowAny,])
def sort(request, sort, id):
    sorts = Sort.objects.filter(sort=sort, id=id)
    serializer = SortSerializer(sorts, many=True)
    return JsonResponse(serializer.data, safe=False)