from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from optparse import make_option
from askbot import models

class Command(BaseCommand):
    args = '<tag1 tag2 ...>'
    option_list = BaseCommand.option_list + (
        make_option('--full',
            action = 'store_true',
            dest = 'show_details',
            default = False,
            help = 'Show details for each question.'
        ),
    )
    help = 'Print report about questions labeled with any of the provided tags'

    def handle(self, *args, **kwargs):
        simple_tag_names = set()
        wildcard_tag_names = set()
        for tag_name in args:
            if tag_name.endswith('*'):
                wildcard_tag_names.add(tag_name)
            else:
                simple_tag_names.add(tag_name)

        wk_tags = models.Tag.objects.get_by_wildcards(wildcards = wildcard_tag_names)
        tags = models.Tag.objects.filter(name__in = simple_tag_names)

        questions = models.Question.objects.filter(tags__in = wk_tags | tags).distinct()
        question_content_type = ContentType.objects.get_for_model(models.Question)
        answer_content_type = ContentType.objects.get_for_model(models.Answer)
        print ''
        if kwargs['show_details'] == False:
            data = {
                'title': 'Title',
                'upvotes': 'Up Votes',
                'downvotes': 'Down Votes',
                'answers': 'Answers',
                'comments': 'Comments'
            }
            print '%(title)-32s %(upvotes)7s %(downvotes)9s %(answers)7s %(comments)8s' % data
        for question in questions:
            question_votes = models.Vote.objects.filter(
                                        object_id = question.id,
                                        content_type = question_content_type
                                    )
            downvote_count = question_votes.filter(vote = models.Vote.VOTE_DOWN).count()
            upvote_count = question_votes.filter(vote = models.Vote.VOTE_UP).count()
            data = {
                'title': question.title[:30],
                'upvotes': upvote_count,
                'downvotes': downvote_count,
                'answers': question.answer_count,
                'comments': question.comments.all().count()
            }
            if kwargs['show_details'] == False:
                print '%(title)-32s %(upvotes)7d %(downvotes)9d %(answers)7d %(comments)8s' % data
            else:
                print 60*"="
                print '%(title)-32s - upvotes: %(upvotes)3d, downvotes: %(downvotes)3d\n' % data
                print question.text, '\n'
                for comment in question.comments.all():
                    print 'Comment by %s' % comment.user.username
                    print comment.comment
                for answer in question.answers.all():
                    print '------------------'
                    answer_votes = models.Vote.objects.filter(
                                                    content_type = answer_content_type,
                                                    object_id = answer.id
                                                )
                    data = {
                        'author': answer.author,
                        'downvotes': answer_votes.filter(vote = models.Vote.VOTE_DOWN).count(),
                        'upvotes': answer_votes.filter(vote = models.Vote.VOTE_UP).count(),
                    }
                    print 'Answer by %(author)s - upvotes %(upvotes)d downvotes %(downvotes)d' % data
                    print answer.text, '\n'
                    for comment in answer.comments.all():
                        print 'Comment by %s' % comment.user.username
                        print comment.comment
