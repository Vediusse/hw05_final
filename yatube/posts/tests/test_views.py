
import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, Follow
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username="Bazz")
        cls.user = User.objects.get(username="Bazz")

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
        )
        post_objs = [
            Post(
                text=f"Пост №{i+1}",
                author=User.objects.get(username="Bazz"),
                group=Group.objects.get(slug="test-slug"),
                image=SimpleUploadedFile(name='image.gif',
                                         content=small_gif,
                                         content_type='image/gif')
            )
            for i in range(settings.POST_PAGE_AMOUNT)
        ]
        Post.objects.bulk_create(post_objs)

        cls.last_post_id = Post.objects.latest("created").id

        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse("posts:create"): "posts/create_post.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/post_details.html",
            reverse(
                "posts:edit",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": "Bazz"},
            ): "posts/profile.html",
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(slug="test-slug")

    def test_pages_uses_correct_template(self):
        for (
            reverse_name,
            template,
        ) in PostPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_and_sorting_by_pubdate(self):
        FIELDS = (
            PostPagesTests.last_post_id,
            f"Пост №{PostPagesTests.last_post_id}",
            self.user,
            self.group,
        )
        view_funcs = {
            reverse("posts:index"): "?page=2",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): "?page=2",
            reverse(
                "posts:profile", kwargs={"username": self.user}
            ): "?page=2",
        }

        for reverse_name, page_number in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.PAGE_AMOUNT)
                response = self.client.get(reverse_name + page_number)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.POST_PAGE_AMOUNT
                                 - settings.PAGE_AMOUNT)
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.id, FIELDS[0])
                self.assertEqual(first_object.text, FIELDS[1])
                self.assertEqual(first_object.author, FIELDS[2])
                self.assertEqual(first_object.group, FIELDS[3])

    def test_forms_pages(self):
        view_funcs = {
            reverse("posts:create"): forms.ModelForm,
            reverse(
                "posts:edit", kwargs={"post_id": settings.TEST_PAGE_NUMBER}
            ): forms.ModelForm,
        }
        for reverse_name, clss in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                form_obj = response.context["form"]
                self.assertIsInstance(form_obj, clss)

    def test_post_detail(self):
        response = self.client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            )
        )
        obj = response.context["post"]
        fields = {
            obj.id: PostPagesTests.last_post_id,
            obj.text: f"Пост №{PostPagesTests.last_post_id}",
            obj.author: self.user,
            obj.group: self.group,
        }
        for field, correct_field in fields.items():
            self.assertEqual(field, correct_field)

    def test_form_post_creation(self):
        fields = [
            "Test post creation",
            self.user,
            self.group,
        ]
        Post.objects.create(text=fields[0], author=fields[1], group=fields[2])
        view_funcs = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for reverse_name in view_funcs:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.text, fields[0])
                self.assertEqual(first_object.author, fields[1])
                self.assertEqual(first_object.group, fields[2])

    def test_cache_on_page(self):
        response_one = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(text='Cache check', author=self.user)
        response_two = self.authorized_client.get(reverse('posts:index'))
        cache.clear()
        response_three = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_one.content, response_two.content,
                         'Кэширование не работает')
        self.assertNotEqual(response_two.content, response_three.content,
                            'Не кэшируются страница')

    def test_img_on_pages(self):
        cache.clear()
        templates_pages_name = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.user}
            ): "posts/group_list.html",
        }
        for urls in templates_pages_name:
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                post = Post.objects.get(id=self.last_post_id)
                self.assertEqual(response.context['page_obj'][0].image,
                                 post.image)
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.last_post_id}))
        object = response.context['post']
        self.assertEqual(object.image, post.image)


class FollowingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='neo')
        cls.user2 = User.objects.create_user(username='leo')
        cls.user3 = User.objects.create_user(username='areo')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client3 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        self.authorized_client3.force_login(self.user3)

    def test_following_user_by_yourself(self):
        self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user}))
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, 1)

    def test_following_task(self):
        self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user2}))
        self.assertEqual(Follow.objects.get().author, self.user2)
        self.authorized_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user2}))
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, 0)

    def test_following_correct_task(self):
        self.authorized_client2.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user}))
        self.authorized_client.post(
            reverse('posts:create'),
            {
                'text': 'Тестовый пост 2222',
                'author': self.user,
            }
        )
        response = self.authorized_client2.get(reverse(
            'posts:index_follow'))
        object = response.context['page_obj']
        self.assertEqual(len(object), 2)
        response = self.authorized_client3.get(reverse(
            'posts:index_follow'))
        object = response.context['page_obj']
        self.assertEqual(len(object), 0)
