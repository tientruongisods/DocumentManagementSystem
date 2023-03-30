from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Category, Document, User
from Document.serialisers import DocumentSerializer, UserSerializer, UserLoginSerializer, CategorySerializer

class CreateCategory(ListCreateAPIView):
    model = Category
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()

    def create_category(self, request, *args, **kwargs):

        serializer = CategorySerializer()
        if serializer.is_valid():
            serializer.save()

            return JsonResponse(serializer.data)({
                'message': 'Create a new Category successful!'
            }, status=status.HTTP_201_CREATED)

        return JsonResponse({
            'message': 'Create a new Document unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)

class ListCreateDocumentView(ListCreateAPIView):
    model = Document
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = DocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse({
                'message': 'Create a new Document successful!'
            }, status=status.HTTP_201_CREATED)

        return JsonResponse({
            'message': 'Create a new Document unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteDocumentView(RetrieveUpdateDestroyAPIView):
    model = Document
    serializer_class = DocumentSerializer

    def put(self, request, *args, **kwargs):
        document = get_object_or_404(Document, id=kwargs.get('pk'))
        serializer = DocumentSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse({
                'message': 'Update Document successful!'
            }, status=status.HTTP_200_OK)

        return JsonResponse({
            'message': 'Update Document unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        document = get_object_or_404(Document, id=kwargs.get('pk'))
        document.delete()

        return JsonResponse({
            'message': 'Delete Document successful!'
        }, status=status.HTTP_200_OK)


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()

            return JsonResponse({
                'message': 'Register successful!'
            }, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({
                'error_message': 'This email has already exist!',
                'errors_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }
                return Response(data, status=status.HTTP_200_OK)

            return Response({
                'error_message': 'Email or password is incorrect!',
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'error_messages': serializer.errors,
            'error_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteCategoryView(RetrieveUpdateDestroyAPIView):
    model = Category
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()

    def delete(self, request, **kwargs):
        category = get_object_or_404(Category, id=kwargs.get('pk'))
        if category.delete():
            return JsonResponse({
                'message': 'Deleted Category Successful!'
            }, status=status.HTTP_200_OK)
        else:

            return JsonResponse({
                'message': 'Deleted Category unsuccessful!'
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateCategoryView(RetrieveUpdateDestroyAPIView):
    model = Document
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.all()

    def put(self, request, **kwargs):
        category = get_object_or_404(Document, id=kwargs.get('pk'))
        serializer = DocumentSerializer(Document, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse({
                'message': 'Update Category successful!'
            }, status=status.HTTP_200_OK)

        return JsonResponse({
            'message': 'Update Category unsuccessful!'
        }, status=status.HTTP_400_BAD_REQUEST)

# Authorization for CRUD User Table
# Requirement:
# Only user with is_admin/is_staff has the authority to perform CRUD on User table
# Approaching: check whether user is_admin/is_staff first, then we allow them to access to this API.

# User view self info (admin - staff)
class UserView(APIView):

    model: User
    serializer_class = UserSerializer

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content ={
            'user': str(request.user),
            'auth': str(User.has_perms(request.user)),
        }
        return Response(content)


# Staff/admin create User --------
# Worked. But unfinished.
class CreateUserView(ListCreateAPIView):
    model: User
    serializer_class = UserSerializer

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        content = {
            'user': str(request.user),
        }

        serializer = UserSerializer(data=request.data)

        staff = User.is_staff
        admin = User.is_superuser
        if serializer.is_valid() and (content.keys() != staff or admin):
            return JsonResponse({
                'message': 'You do not have permission to create a user'
            })
        elif serializer.is_valid() and (content.keys() is staff or admin):
            serializer.save()
            return JsonResponse({
                'message': 'Successfully created a user'
            })


