import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Лев Толстой',
            slug='tolstoy',
            description='Группа Льва Толстого',
        )

        cls.author = User.objects.create_user(
            username='test_user',
            first_name='test',
            last_name='test',
            email='testuser@yatube.ru'
        )

        cls.user = User.objects.create_user(username='Vedius')

        cls.post = Post.objects.create(
            author=cls.user,
            text='text',
        )

        cls.form = PostForm()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.gif_name = 'small.gif'
        cls.comment = 'Текстовый коммент'
        cls.image_post = 'texts'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Send',
        }
        response = self.authorized_client.post(reverse('posts:create'),
                                               data=form_data,
                                               follow=True)

        self.assertRedirects(response, reverse('posts:profile',
                                               args=[self.user.username]))
        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=TestCreateForm.group).exists())

    def test_form_update(self):
        post = Post.objects.create(
            group=TestCreateForm.group,
            text="text",
            author=User.objects.get(username='Vedius'),
        )

        self.authorized_client.force_login(self.author)
        url = reverse('posts:edit', args=[post.id])
        self.authorized_client.get(url)
        form_data = {
            'group': self.group.id,
            'text': 'text',
        }
        self.authorized_client.post(
            reverse('posts:edit', args=[post.id]),
            data=form_data, follow=True)
        post.refresh_from_db()
        self.assertEqual(str(post), form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

    def test_post_form_with_image(self):
        uploaded = SimpleUploadedFile(name=self.gif_name,
                                      content=self.small_gif,
                                      content_type='image/gif')
        form_data = {
            'group': self.group.id,
            'text': self.image_post,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:create'), data=form_data, follow=True
        )
        post_image = Post.objects.filter(text=self.image_post).get().image.name
        self.assertIn(uploaded.name, post_image)

    def test_comment_post(self):
        form_data = {
            'group': self.group.id,
            'text': self.comment,
            'author': self.user
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        comment = response.context['comments'][0].text
        self.assertEqual('Текстовый коммент', comment)
