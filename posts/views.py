import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Post, Comment
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, PostSerializer, CommentSerializer

def validate_username(username):
    if not username or len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")
    if User.objects.filter(username=username).exists():
        raise ValidationError("Username already exists")

def validate_user_input(data):
    required_fields = ['username', 'email']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"{field} is required")
    
    validate_username(data['username'])
    validate_email(data['email'])

def validate_post_input(data):
    if 'content' not in data:
        raise ValidationError("Content is required")
    if 'author' not in data:
        raise ValidationError("Author ID is required")
    if not data['content'].strip():
        raise ValidationError("Content cannot be empty")
    if not str(data['author']).isdigit():
        raise ValidationError("Author ID must be a number")

def get_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        validate_user_input(data)
        
        user = User.objects.create(
            username=data['username'], 
            email=data['email']
        )
        return JsonResponse({
            'id': user.id, 
            'username': user.username,
            'email': user.email,
            'message': 'User created successfully'
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def update_user(request, id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        user = User.objects.filter(id=id).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        data = json.loads(request.body)
        if 'email' not in data:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        validate_email(data['email'])
        user.email = data['email']
        user.save()
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'User updated successfully'
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def delete_user(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        user = User.objects.filter(id=id).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_posts(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        validate_post_input(data)
        
        author = User.objects.filter(id=data['author']).first()
        if not author:
            return JsonResponse({'error': 'Author not found'}, status=404)

        post = Post.objects.create(
            content=data['content'],
            author=author
        )
        return JsonResponse({
            'id': post.id,
            'content': post.content,
            'author_id': post.author.id,
            'message': 'Post created successfully'
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
