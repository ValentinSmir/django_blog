from django.shortcuts import get_object_or_404, redirect

from blog.models import Post, Category, Profile, Comment

from django.views.generic import (ListView, DetailView, UpdateView, CreateView,
                                  DeleteView)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.models import User

from django.urls import reverse_lazy

from .forms import ProfileForm, CommentForm, PostForm

from datetime import datetime as dt

from django.db.models import Count

from django.utils import timezone


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        fil = Post.objects.annotate(comment_count=Count('comments')).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()).order_by('-pub_date')
        return fil


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(Post.objects.filter(
                is_published=True,
                pub_date__date__lte=dt.now()), category__is_published=True,
                pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10
    slug_url_kwarg = 'category_slug'

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=category, is_published=True,
                                   pub_date__lte=timezone.now())

    def get_context_data(self):
        context = super().get_context_data()
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        context['category'] = category
        return context


class ShowProfileView(ListView):
    model = Profile
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        posts = Post.objects.annotate(
            comment_count=Count('comments')).filter(
                author=user).order_by('-pub_date')
        if self.request.user != user:
            posts = Post.published.all().annotate(
                comment_count=Count('comments')).filter(
                    author=user).order_by('-pub_date')
        return posts

    def get_context_data(self, *args, **kwargs):
        user = get_object_or_404(User, username=self.kwargs['username'])
        context = super().get_context_data(*args, **kwargs)
        context['user'] = user
        return context


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object.author})


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'pk'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs[self.pk_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs[self.pk_url_kwarg]})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'pk'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.comment = get_object_or_404(Post,
                                                  pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.kwargs.get('pk')})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.kwargs.get('pk')})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.kwargs.get('pk')})
