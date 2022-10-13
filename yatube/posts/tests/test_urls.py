from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from random import randint

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='leo',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.user = User.objects.create_user(username='Vedius')

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):

        templates_url_names = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.FOUND.value,
            f'/posts/{self.post.id}/comment/': HTTPStatus.FOUND.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):

                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_404(self):
        id404 = 0
        response = self.authorized_client.get(
            reverse('posts:edit', args=[id404])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
