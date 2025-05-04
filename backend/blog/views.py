from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from blog.models import Discussion, Blog, ViewedBlog


def blog(request):
    blogs = Blog.objects.all()

    if request.method == 'POST':
        image = request.FILES.get('image')
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        description = request.POST.get('description')

        if not (image and title and summary and description):
            messages.info(request, 'Empty fields are not allowed!')
            return redirect('blog')

        Blog.objects.create(
            author=request.user,
            image=image,
            title=title,
            summary=summary,
            description=description
        ).save()
        messages.success(request, 'Article details sent to the moderator successfully!')
        return redirect('blog')

    context = {
        'blogs': blogs
    }

    return render(request, 'blog/blog.html', context)


def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    discussions = Discussion.objects.filter(blog=blog)

    user = request.user.id
    if user is not None:
        if not ViewedBlog.objects.filter(user=request.user, blog=blog).exists():
            ViewedBlog.objects.create(user=request.user, blog=blog)

    if request.method == 'POST':
        comment = request.POST['comment']
        is_anonymous = request.POST.getlist('anonymous')

        if comment:
            discussion = Discussion.objects.create(
                author=request.user,
                blog=blog,
                comment=comment,
                is_anonymous=False
            )

            if is_anonymous:
                discussion.is_anonymous = True

            discussion.save()
            return HttpResponseRedirect(reverse('blog-detail', kwargs={'blog_id': blog.pk}))

    count_of_views = ViewedBlog.objects.filter(blog=blog).count()

    context = {
        'blog': blog,
        'discussions': discussions,
        'count_of_views': count_of_views
    }

    for discussion in discussions:
        discussion.liked = discussion.like.filter(id=request.user.id).exists()

    for discussion in discussions:
        discussion.disliked = discussion.dislike.filter(id=request.user.id).exists()

    for discussion in discussions:
        discussion.complained = discussion.complain.filter(id=request.user.id).exists()

    return render(request, 'blog/blog_detail.html', context)


def LikeComment(request, pk):
    user = request.user
    comment_like = get_object_or_404(Discussion, id=request.POST.get('comment_like'))
    liked_comment = False
    if user in comment_like.like.all():
        comment_like.like.remove(user)
        liked_comment = False
    else:
        comment_like.like.add(user)
        if user in comment_like.dislike.all():
            comment_like.dislike.remove(user)
        liked_comment = True
    return redirect('blog-detail', blog_id=comment_like.blog.id)


def DislikeComment(request, pk):
    user = request.user
    comment_dislike = get_object_or_404(Discussion, id=request.POST.get('comment_dislike'))
    disliked_comment = False
    if user in comment_dislike.dislike.all():
        comment_dislike.dislike.remove(user)
        disliked_comment = False
    else:
        comment_dislike.dislike.add(user)
        if user in comment_dislike.like.all():
            comment_dislike.like.remove(user)
        disliked_comment = True
    return redirect('blog-detail', blog_id=comment_dislike.blog.id)


def ComplainComment(request, pk):
    user = request.user
    complain_comment = get_object_or_404(Discussion, id=request.POST.get('comment_complain'))
    comment = get_object_or_404(Discussion, id=pk)

    complained = False
    if user in complain_comment.complain.all():
        complain_comment.complain.remove(user)
        complained = False
    else:
        complain_comment.complain.add(user)
        complained = True

        subject = 'Warning: Comment violation'
        message = f'Your comment on <{comment.blog.title}> has been reported by other users and may violate our ' \
                  f'community guidelines. Please review our guidelines and ensure your comments are respectful ' \
                  f'and ' \
                  f'constructive. Thank you. '
        from_email = 'womenssdiary@gmail.com'
        to_email = [comment.author.email]
        EmailMessage(subject, message, from_email, to_email).send()

    return redirect('blog-detail', blog_id=complain_comment.blog.id)
