
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

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
        cls.user2 = User.objects.create_user(username='leos')

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user2)

    def test_urls_uses_correct_template(self):

        templates_url_names = {
            '/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.FOUND.value,
            '/follow/': HTTPStatus.FOUND.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/comment/': HTTPStatus.FOUND.value,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user2}/': HTTPStatus.OK.value,
            f'/profile/{self.user2}/follow/': HTTPStatus.FOUND.value,
            f'/profile/{self.user2}/unfollow/': HTTPStatus.FOUND.value,
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
