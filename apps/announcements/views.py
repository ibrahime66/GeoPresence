from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.mixins import RoleRequiredMixin
from apps.accounts.models import User
from apps.core.views import DEFAULT_PAGE_SIZE, TenantFormMixin, TenantQuerysetMixin

from .forms import AnnouncementForm
from .models import Announcement

ADMIN_ONLY = (User.Role.ADMIN,)


class AnnouncementListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ADMIN_ONLY
    model = Announcement
    template_name = "announcements/announcement_list.html"
    context_object_name = "announcements"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class AnnouncementCreateView(RoleRequiredMixin, TenantFormMixin, CreateView):
    allowed_roles = ADMIN_ONLY
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/announcement_form.html"
    success_url = reverse_lazy("announcements:list")

    def get_initial(self):
        initial = super().get_initial()
        initial["publish_at"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class AnnouncementUpdateView(RoleRequiredMixin, TenantFormMixin, UpdateView):
    allowed_roles = ADMIN_ONLY
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/announcement_form.html"
    success_url = reverse_lazy("announcements:list")


class AnnouncementDeleteView(RoleRequiredMixin, TenantQuerysetMixin, View):
    allowed_roles = ADMIN_ONLY
    model = Announcement

    def post(self, request, *args, **kwargs):
        announcement = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        announcement.delete()
        return redirect("announcements:list")
