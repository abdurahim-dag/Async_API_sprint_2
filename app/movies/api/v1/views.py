""" API views for model FilmWork."""
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import ListView
from movies.models import FilmWork
from typing import Union, List
from django.db.models import QuerySet


class MovieMixin:

    model = FilmWork
    http_method_names = ['get']

    # Default model fields gets
    _fields = (
        'id', 'title', 'description', 'creation_date', 'rating', 'type',
    )
    # Dynamic related fields annotations generates
    _roles = ['writer', 'actor', 'director']

    def get_queryset(self) -> Union[QuerySet, List[FilmWork]]:
        """Modifier queryset with _fields and _roles.

        Returns:
            Union[QuerySet, List[FilmWork]]: Queryset withe all needed fields.
        """
        queryset = super().get_queryset()
        queryset = queryset.values(
            *self._fields,
        ).prefetch_related(
            'genres__name',
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
        )

        for role in self._roles:
            q = Q(personfilmwork__role=role)
            kwargs = {
                '{0}s'.format(role): ArrayAgg(
                    'person__full_name',
                    filter=q,
                    distinct=True,
                ),
            }
            queryset = queryset.annotate(**kwargs)
        return queryset

    def render_to_response(self, context):
        return JsonResponse(context)


class MoviesListApi(MovieMixin, ListView):

    paginate_by = 50
    ordering = '-modified'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Modified context with custom dict structure."""
        context = super().get_context_data()

        try:
            prev = context['page_obj'].previous_page_number()
        except EmptyPage:
            prev = None

        try:
            next = context['page_obj'].next_page_number()
        except EmptyPage:
            next = None

        context = {
            'results': list(context['object_list']),
            'count': context['paginator'].count,
            'total_pages': context['paginator'].num_pages,
            'prev': prev,
            'next': next,
        }
        return context

class MoviesDetailApi(MovieMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        """Insert the single object into the context."""
        context = {}
        if self.object:
            context = self.object
        return context
