from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.accounts.models import User

from . import services as ai_services
from .models import AIConversation
from .providers import AIProviderError


class AIChatView(LoginRequiredMixin, View):
    """Page unique GeoIA : liste des conversations + fil de la conversation
    sélectionnée (ou état vide si aucune). Aucune configuration ici — le
    fournisseur/la clé sont réglés côté serveur (settings.AI_*)."""

    template_name = "ai/chat.html"

    def _tenant(self, request):
        return None if request.user.role == User.Role.SUPER_ADMIN else request.tenant

    def _is_ajax(self, request):
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def get(self, request, pk=None):
        if not ai_services.is_ai_available(request.user):
            messages.error(request, "GeoIA n'est pas disponible pour votre compte.")
            return redirect("core:dashboard")

        tenant = self._tenant(request)
        conversations = AIConversation.objects.filter(tenant=tenant, user=request.user).order_by("-updated_at")
        conversation = None
        if pk:
            conversation = get_object_or_404(conversations, pk=pk)
        return render(request, self.template_name, {
            "conversations": conversations,
            "conversation": conversation,
            # list() plutôt que le queryset : {{ messages_list|last }} dans le
            # template ferait un index négatif, non supporté par un QuerySet.
            "messages_list": list(conversation.messages.all()) if conversation else [],
            "starter_suggestions": ai_services.get_starter_suggestions(request.user),
        })

    def post(self, request, pk=None):
        is_ajax = self._is_ajax(request)

        if not ai_services.is_ai_available(request.user):
            error = "GeoIA n'est pas disponible pour votre compte."
            if is_ajax:
                return JsonResponse({"error": error}, status=403)
            messages.error(request, error)
            return redirect("core:dashboard")

        question = request.POST.get("question", "").strip()
        if not question:
            error = "Veuillez saisir une question."
            if is_ajax:
                return JsonResponse({"error": error}, status=400)
            messages.error(request, error)
            return redirect("ai:chat_detail", pk=pk) if pk else redirect("ai:chat")

        tenant = self._tenant(request)
        if pk:
            conversation = get_object_or_404(AIConversation, pk=pk, tenant=tenant, user=request.user)
        else:
            conversation = AIConversation.objects.create(tenant=tenant, user=request.user)

        try:
            answer = ai_services.ask(request.user, conversation, question, request=request)
        except (ai_services.AIQuotaExceeded, ai_services.AINotAvailable, AIProviderError) as exc:
            error = str(exc) if not isinstance(exc, AIProviderError) else f"GeoIA n'a pas pu répondre : {exc}"
            if is_ajax:
                status = 429 if isinstance(exc, ai_services.AIQuotaExceeded) else 503
                return JsonResponse({
                    "error": error, "conversation_id": str(conversation.pk),
                }, status=status)
            messages.error(request, error)
            return redirect("ai:chat_detail", pk=conversation.pk)

        if is_ajax:
            last_message = conversation.messages.filter(role="ASSISTANT").last()
            return JsonResponse({
                "conversation_id": str(conversation.pk),
                "conversation_title": conversation.title,
                "answer": answer,
                "suggestions": last_message.suggestions if last_message else [],
            })

        return redirect("ai:chat_detail", pk=conversation.pk)
