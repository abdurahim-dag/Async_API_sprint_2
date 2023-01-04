import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('Full name'), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):

    class MovieType(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('Tv show')

    title = models.CharField(
        _('Title'),
        max_length=255,
        db_index=True
    )
    description = models.TextField(_('Description'), blank=True, null=True)
    creation_date = models.DateField(
        _('Premiere date'),
        blank=True,
        null=True,
        db_index=True
    )
    rating = models.FloatField(
        _('Rating'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)],
        db_index=True
    )
    type = models.CharField(
        _('Type'),
        max_length=255,
        choices=MovieType.choices,
        default=MovieType.MOVIE,
    )

    genres = models.ManyToManyField(
        Genre,
        through='GenreFilmWork',
    )
    person = models.ManyToManyField(
        Person,
        through='PersonFilmWork',
    )

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _('Film work')
        verbose_name_plural = _('Film works')

    def __str__(self):
        return self.title


class PersonFilmWork(UUIDMixin):
    role = models.TextField(_('Role'))
    created = models.DateTimeField(auto_now_add=True)

    film_work = models.ForeignKey(
        FilmWork,
        verbose_name=_('Film work'),
        on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person,
        verbose_name=_('Person'),
        on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

        constraints = [
            models.UniqueConstraint(fields=['person', 'film_work', 'role'], name='unique_person_film_work')
        ]

    def __str__(self):
        return str(self.person)


class GenreFilmWork(UUIDMixin):
    created = models.DateTimeField(auto_now_add=True)

    film_work = models.ForeignKey(
        FilmWork,
        verbose_name=_('Film work'),
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name=_('Genre'),
        on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='unique_genre_film_work')
        ]

    def __str__(self):
        return str(self.genre)
