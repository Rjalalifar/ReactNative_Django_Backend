from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from base.serializer import UserSerializer, userSerializerWithToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
import jwt


def emailSender(data):
    try:
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email='eshop.hamruyesh@gmail.com',
            to=[data['to'], ]
        )

        email.send()
        return True
    except:
        return False


class MyCreatorTokenViewSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = userSerializerWithToken(self.user).data
        for key, val in serializer.items():
            data[key] = val

        data['username'] = self.user.username
        data['email'] = self.user.email
        return data


class MyCreatorTokenView(TokenObtainPairView):
    serializer_class = MyCreatorTokenViewSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    data = request.data

    print(request.data)

    print(request.data['name'])

    user.first_name = data['name'],

    print(user.first_name)

    user.username = data['email'],
    useremail = data['email'],

    if data['password'] != '':

        user.password = make_password(data['password'])
    user.save()

    serializer = userSerializerWithToken(user, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def registerUser(request):
    data = request.data
    username = data['email']
    password = data['password']

    try:
        user = User.objects.create(
            first_name=data['name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
            is_active=False,
        )

        # create token
        token = RefreshToken.for_user(user).access_token

        # send activation email to user
        subject = f"E-Shop Activation email"
        body = f"Hi {user.username} welcome to E-Shop.\n Please use below link for active your account! \n\n" \
            f"http://127.0.0.1:8000/api/v1/users/verify/{str(token)}/"

        data = {
            'subject': subject,
            'body': body,
            'to': user.email,
        }
        result = emailSender(data)

        if result:
            message = {
                'detail': 'Welcome to E-Shop. You should verify your email.Please check your Inbox. We sent an email.'
            }
            return Response(message, status=status.HTTP_201_CREATED)
        else:
            message = {
                'detail': 'There\'s a problem on sending email.'
            }
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:
        user = User.objects.get(username=username)

        # update the user's password
        user.password = make_password(password)
        user.save()

        if user and not user.is_active:

            # create token
            token = RefreshToken.for_user(user).access_token

            # send activation email to user
            subject = f"E-Shop Activation email"
            body = f"Hi {user.username} welcome back to E-Shop.\n Please use below link for active your account! \n\n" \
                f"http://127.0.0.1:8000/api/v1/users/verify/{str(token)}/"

            data = {
                'subject': subject,
                'body': body,
                'to': user.email,
            }
            result = emailSender(data)

            if result:
                message = {
                    'detail': 'User with this email already exists but is not active. You should verify your email.Please check your Inbox. We sent an email.Using new password'
                }
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                message = {
                    'detail': 'There\'s a problem on sending email.'
                }
                return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif user and user.is_active:
            message = {
                'detail': 'User with this email already exists and is active too. Please login.Using new password'
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def verifyEmail(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, ['HS256'])
        user = User.objects.get(id=payload['user_id'])
        user.is_active = True
        user.save()
        return HttpResponseRedirect('http://localhost:3000/login?tokne=success')
    except:
        return HttpResponseRedirect('http://localhost:3000/login?token=fail')
