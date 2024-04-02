from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()

class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )

    def test_note_in_list_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

