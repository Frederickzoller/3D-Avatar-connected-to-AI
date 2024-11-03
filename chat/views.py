from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services.llm_service import LLMService

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    llm_service = LLMService()

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    async def send_message(self, request, pk=None):
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
        user_message = request.data.get('message')
        
        if not user_message:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save user message
        Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )

        # Get conversation context
        context = [
            {"role": "system", "content": "You are a helpful assistant."},
            *[{"role": "user" if msg.is_user else "assistant", "content": msg.content} 
              for msg in conversation.messages.all()]
        ]

        # Get AI response
        ai_response = await self.llm_service.get_response(user_message, context)

        # Save AI response
        Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )

        return Response({
            'message': ai_response
        }, status=status.HTTP_200_OK) 