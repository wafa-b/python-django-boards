from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse, Http404
from .models import Board , Topic,Post
from django.contrib.auth.models import User
from .forms import NewTopicForm ,PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse


# Create your views here.

def index(request):
    boards = Board.objects.all()

    # boards_name =list()
    # for board in boards:
    #     boards_name.append(board.name)
    #     res_response = '<br>'.join(boards_name)
    # return HttpResponse(res_response)

    return render(request,'home.html',{'boards':boards})


# def boards_topic(request,id):
#     board = get_object_or_404(Board,pk=id)
#     queryset = board.topics.order_by('-created_date').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#     paginator = Paginator(queryset, 20)
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         topics = paginator.page(1)
#     except EmptyPage:
#         topics = paginator.page(paginator.num_pages)
#     return render(request, 'topics.html', {'board': board, 'topics': topics})
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('id'))
        queryset = self.board.topics.order_by('-created_date').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def new_topic(request,id):
    board = get_object_or_404(Board,pk=id)
    user = request.user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.created_by = user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect('boards_topic',id=board.pk)
    else:
        form = NewTopicForm()

    return render(request,'new_topic.html',{'board':board,'form':form})


# def topic_posts(request,id,topic_id):
#     topic = get_object_or_404(Topic,board__pk =id,pk=topic_id)
#     topic.views +=1
#     topic.save()
#     return render(request,'topic_posts.html',{'topic':topic})
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)


    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('id'), pk=self.kwargs.get('topic_id'))
        queryset = self.topic.posts.order_by('created_date')
        return queryset

@login_required
def reply_topic(request,id,topic_id):
    topic = get_object_or_404(Topic,board__pk =id,pk=topic_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.created_date = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'id':id, 'topic_id': topic_id})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)

            # return redirect('topic_posts',id=id,topic_id=topic.pk)
    else:
        form = PostForm()
    return render(request,'reply_topic.html',{'topic':topic,'form':form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.created_by = self.request.user
        post.save()
        return redirect('topic_posts', id=post.topic.board.pk, topic_id=post.topic.pk)

