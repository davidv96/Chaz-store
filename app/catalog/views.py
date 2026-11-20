from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from orders.mixins import StaffRequiredMixin

from .forms import ServiceForm
from .models import Service, Tag



class HomeView(TemplateView):
    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_services"] = Service.objects.filter(is_active=True, is_featured=True).prefetch_related("tags")[:4]
        return context


class ServiceListView(ListView):
    model = Service
    template_name = "catalog/service_list.html"
    context_object_name = "services"
    paginate_by = 12

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).prefetch_related("tags")

        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug).distinct()

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["current_tag"] = self.request.GET.get("tag", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["catalog/_service_list_partial.html"]
        return [self.template_name]


class ServiceDetailView(DetailView):
    model = Service
    template_name = "catalog/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(is_active=True).prefetch_related("tags")


def service_list_partial(request):
    """FBV that returns the service list partial for HTMX filtering."""
    queryset = Service.objects.filter(is_active=True).prefetch_related("tags")

    tag_slug = request.GET.get("tag")
    if tag_slug:
        queryset = queryset.filter(tags__slug=tag_slug).distinct()

    query = request.GET.get("q")
    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, "catalog/_service_list_partial.html", {"services": queryset})


# ── Staff Views ──────────────────────────────────────────────────────────────


class ServiceAdminListView(StaffRequiredMixin, ListView):
    """Full products table for staff — includes inactive/draft services."""

    model = Service
    template_name = "catalog/service_admin_list.html"
    context_object_name = "services"
    paginate_by = 25

    def get_queryset(self):
        queryset = Service.objects.all().prefetch_related("tags")

        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug).distinct()

        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "draft":
            queryset = queryset.filter(is_active=False)

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(slug__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context["current_tag"] = self.request.GET.get("tag", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["search_query"] = self.request.GET.get("q", "")
        all_services = Service.objects.all()
        total_count = all_services.count()
        active_count = all_services.filter(is_active=True).count()
        context["total_count"] = total_count
        context["active_count"] = active_count
        context["draft_count"] = total_count - active_count
        return context

    def get_template_names(self):
        if self.request.htmx:
            return ["catalog/_service_admin_table_partial.html"]
        return [self.template_name]


class ServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "catalog/service_form.html"
    success_url = reverse_lazy("catalog:service_admin_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx["form"]
        if form.is_bound:
            selected_ids = form.data.getlist("tags")
            ctx["initial_tags"] = list(Tag.objects.filter(pk__in=selected_ids).values("id", "name"))
        else:
            ctx["initial_tags"] = []
        return ctx


class ServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "catalog/service_form.html"
    success_url = reverse_lazy("catalog:service_admin_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx["form"]
        if form.is_bound:
            selected_ids = form.data.getlist("tags")
            ctx["initial_tags"] = list(Tag.objects.filter(pk__in=selected_ids).values("id", "name"))
        else:
            ctx["initial_tags"] = list(form.instance.tags.values("id", "name"))
        return ctx


class TagListView(StaffRequiredMixin, ListView):
    model = Tag
    template_name = "catalog/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.annotate(service_count=Count("services")).order_by("-service_count", "name")


@require_http_methods(["POST"])
def tag_delete(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    messages.success(request, f'Tag "{tag.name}" deleted.')
    return redirect("catalog:tag_list")


@require_http_methods(["GET"])
def tag_search(request):
    """Return tags matching the query as JSON."""
    q = request.GET.get("q", "").strip()
    qs = Tag.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    data = [{"id": t.id, "name": t.name} for t in qs[:20]]
    return JsonResponse({"tags": data})


@require_http_methods(["POST"])
def tag_get_or_create(request):
    """Get or create a tag by name. Staff only."""
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"error": "Name required"}, status=400)
    try:
        tag = Tag.objects.get(name__iexact=name)
        created = False
    except Tag.DoesNotExist:
        base_slug = slugify(name)
        slug = base_slug
        i = 1
        while Tag.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        tag = Tag.objects.create(name=name, slug=slug)
        created = True
    return JsonResponse({"id": tag.id, "name": tag.name, "created": created})
