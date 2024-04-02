from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogicCreate(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User Author')
        cls.note_data = {
          'title': 'Заголовок',
          'text': 'Текст',
          'author': cls.author,
          'slug': 'slug'
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'), self.note_data)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, 'Заголовок')
        self.assertEqual(new_note.text, 'Текст')
        self.assertEqual(new_note.author, self.author)
        self.assertEqual(new_note.slug, 'slug')

    def test_anonymous_user_cant_create_note(self):
        count_before = Note.objects.count()
        self.client.post(reverse('notes:add'), self.note_data)
        count_after = Note.objects.count()
        self.assertEqual(count_after, count_before)

    def test_empty_slug(self):
        self.note_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), self.note_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note_slug = Note.objects.get().slug
        assert Note.objects.count() == 1
        expected_slug = slugify(self.note_data['title'])
        self.assertEqual(expected_slug, new_note_slug)       


class TestLogicSlugEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User Author')
        cls.reader = User.objects.create(username='User Reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )
        cls.new_note_data = {
          'title': 'Заголовок',
          'text': 'Новый текст',
          'author': cls.author,
          'slug': 'slug'
        }

    def test_not_unique_slug(self):        
        self.client.force_login(self.author)
        self.client.post(reverse('notes:add'), self.new_note_data)
        assert Note.objects.count() == 1

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.new_note_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_note_data['title'])
        self.assertEqual(self.note.text, self.new_note_data['text'])
        self.assertEqual(self.note.slug, self.new_note_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.new_note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.note.title)
        self.assertEqual(self.note.text, self.note.text)
        self.assertEqual(self.note.slug, self.note.slug)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        assert Note.objects.count() == 1
