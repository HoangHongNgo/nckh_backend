from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import status
from knox.auth import AuthToken

from .models import Result
from .serializers import RegisterSerializer, ResultSerializer, VideoSerializer


@api_view(['POST'])
def login_api(request):
    if request.method == 'POST':
        serializer = AuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            _, token = AuthToken.objects.create(user)

            return Response({
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_user_data(request):
    user = request.user

    if user.is_authenticated:
        return Response({
            'user_info': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
        })

    return Response({'error': 'not authenticated'}, status=400)


@api_view(['POST'])
def register_api(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            _, token = AuthToken.objects.create(user)

            return Response({
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def execute_model(request):
    if request.method == 'POST':
        try:
            # Extract user_id from the request data
            user_id = request.data.get('user_id')

            # Ensure the user exists
            user = get_object_or_404(User, id=user_id)

            # Attach the user to the request data
            request.data['owner'] = user.id
        except:
            return Response({'detail': 'Input not available'}, status=status.HTTP_400_BAD_REQUEST)

        file_serializer = VideoSerializer(data=request.data)

        if file_serializer.is_valid():
            uploaded_file = request.FILES['video_file']

            if uploaded_file.name.endswith('.avi'):
                # Save the video
                video_instance = file_serializer.save()

                # Process the video and generate a diagnostic and ecg data
                # ecg_data, diagnostic = process_video(video_instance)

                # Create a Result instance and save it to the database
                # result_instance = Result.objects.create(
                #     owner=user,
                #     ecg=ecg_data,
                #     diagnostic=diagnostic
                # )

                return Response(file_serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response({'detail': 'Only AVI videos are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_user_results(request, user_id):
    if request.method == 'POST':
        try:
            results = Result.objects.filter(owner__id=user_id)
            serializer = ResultSerializer(results, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Result.DoesNotExist:
            return Response({'detail': 'User does not exist or has no results.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
