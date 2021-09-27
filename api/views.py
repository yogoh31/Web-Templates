from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from posts.models import Post
from tags.models import Tag
from comments.models import Comment

from .serializers import *
from .utils import *


@api_view(['GET'])
def get_routes(request):
    routes = [
        {'GET': '/api/users'},
        {'POST': '/api/users/token/'},
        {'POST': '/api/users/token/refresh/'},
        {'GET': '/api/users/id'},
        {'GET': '/api/users/id/posts'},
        {'POST': '/api/users/id/posts'},
        {'GET': '/api/users/id/posts/id'},
        {'PUT': '/api/users/id/posts/id'},
        {'GET': '/api/users/id/posts/id.comments'},
        {'GET': '/api/users/id/posts/id.comments/id'},
        {'GET': '/api/tags'},
        {'GET': '/api/tags/id'},
    ]
    return Response(routes)


class UsersList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        pass


class UserDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(set, request, user_pk, format=None):
        user = User.objects.get(username=user_pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class PostsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        if 'user_pk' in kwargs:
            user = User.objects.get(username=kwargs['user_pk'])
            posts = Post.objects.filter(author=user)
        else:
            posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):
        if 'user_pk' in kwargs:
            user = User.objects.get(username=kwargs['user_pk'])
        elif request.user.is_authenticated:
            user = User.objects.get(username=request.user.username)
        request.data['author'] = user
        tags = make_dict_from_names(request.data['tags'])
        request.data['tags'] = tags
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None, **kwargs):
        if 'user_pk' in kwargs:
            user = User.objects.get(username=kwargs['user_pk'])
            post = get_object_or_404(Post.objects.filter(
                author=user), pk=kwargs['post_pk'])
        else:
            post = get_object_or_404(Post.objects.all(), pk=kwargs['post_pk'])

        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)

    def put(self, request, format=None, **kwargs):
        instance = get_object_or_404(Post.objects.all(), pk=kwargs['post_pk'])
        user = request.user
        request.data['author'] = user
        serializer = PostSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None, **kwargs):

        post = Post.objects.get(id=kwargs['post_pk'])
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, user_pk, post_pk, comment_pk, format=None, **kwargs):
        if 'post_pk' in kwargs:
            comment = get_object_or_404(Comment.objects.filter(
                author=kwargs['post_pk']), pk=kwargs['comment_pk'])
        else:
            comment = Comment.objects.get(id=kwargs['comment_pk'])
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data)


class TagsList(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class TagDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, **kwargs):
        tag = Tag.objects.get(id=kwargs['tag_pk'])
        serializer = TagSerializer(tag, many=False)
        return Response(serializer.data)
