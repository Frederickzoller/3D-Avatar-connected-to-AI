from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services.llm_service import LLMService
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async, async_to_sync

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Associate the current user with the conversation
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = get_object_or_404(Conversation, pk=pk)
        message_content = request.data.get('message', '')
        
        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            role='user'
        )

        # Initialize LLM service
        llm_service = LLMService()
        
        # Get conversation history
        conversation_history = list(conversation.messages.all().values('role', 'content'))
        
        # Use async_to_sync to handle the async get_response
        try:
            ai_response = async_to_sync(llm_service.get_response)(message_content, conversation_history)
            
            # Create AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                content=ai_response,
                role='assistant'
            )

            return Response({
                'user_message': MessageSerializer(user_message).data,
                'ai_message': MessageSerializer(ai_message).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Add debug logging
        print(f"Login attempt for username: {request.data.get('username')}")
        
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            })
        except Exception as e:
            # Try manual authentication to get more details
            user = authenticate(
                username=request.data.get('username'),
                password=request.data.get('password')
            )
            if user is None:
                return Response({
                    'error': 'Authentication failed',
                    'detail': 'Please check your username and password.',
                    'debug_info': {
                        'username_exists': bool(User.objects.filter(username=request.data.get('username')).exists()),
                        'password_provided': bool(request.data.get('password')),
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)