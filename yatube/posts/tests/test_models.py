from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_methods(self):
        post_text = PostModelTest.post
        expected_len_text = PostModelTest.post.text[:13]
        self.assertEqual(expected_len_text, str(post_text))
        group = PostModelTest.group
        expected_obj_name = group.title
        self.assertEqual(expected_obj_name, str(group))
