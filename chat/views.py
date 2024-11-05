from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services.llm_service import LLMService
import logging
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync
import asyncio

logger = logging.getLogger(__name__)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            logger.info(f"Login successful for user: {user.username}")
            
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            })
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_400_BAD_REQUEST)

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        try:
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
            history = list(conversation.messages.order_by('created_at').values('content', 'role'))
            
            # Use async_to_sync to properly handle the async LLM response
            try:
                ai_response = async_to_sync(llm_service.get_response)(message_content, history)
                
                # Create AI message
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=ai_response,
                    role='assistant'
                )

                return Response({
                    'message': ai_response,
                    'user_message': MessageSerializer(user_message).data,
                    'ai_message': MessageSerializer(ai_message).data
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error getting LLM response: {str(e)}")
                return Response({
                    'error': 'Failed to generate AI response',
                    'detail': str(e) if settings.DEBUG else 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}")
            return Response({
                'error': 'Failed to process message',
                'detail': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)