from xml.dom import ValidationErr
from django.forms import ValidationError
from rest_framework import serializers
from accounts.models import User
from accounts.utils import Util



# for sending email with encoding and token generation
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator




class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','name','password','password2','tc',]
        extra_kwargs = {
            'password':{'write_only':True}
        }

#Validating Password and Confirm Password
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password Doesnot Match..!')
        return attrs

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

#Login
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name','email']

class UserChangePasswordSerializer(serializers.Serializer):
    password =serializers.CharField(max_length= 255,style={'input_type':'password'},write_only=True)
    password2 =serializers.CharField(max_length= 255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields = ['password','password2']
        
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError('Password Doesnot Match..!')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID',uid)
            print('-------------------------------------------')
            token = PasswordResetTokenGenerator().make_token(user)
            print('password reset token', token)
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            print('password reset link', link)

            #Send Email
            body = 'click following link to reset your password'+link
            data = {
                'subject':'Reset your password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)

            return attrs
        else:
           raise ValidationErr('You Are not a Registered User Please register')


class UserPasswordResetSerializer(serializers.Serializer):
    password =serializers.CharField(max_length= 255,style={'input_type':'password'},write_only=True)
    password2 =serializers.CharField(max_length= 255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields = ['password','password2']
        
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')        
            if password != password2:
                raise serializers.ValidationError('Password Doesnot Match..!')
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationError('Token is not valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise ValidationError('Token is not valid or Expired')
