from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from optparse import make_option
from askbot import models

base_report_dir = "/ala-windfeedback1/qa/web/reports/tag"

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--full',
            action = 'store_true',
            dest = 'show_details',
            default = False,
            help = 'Show details for each question.'
        ),
        make_option('--file',
            action = 'store_true',
            dest = 'save_file',
            default = False,
            help = 'Save results to file.'
        ),
    )
    help = 'Print report about questions labeled with any of the provided tags'

    def handle(self, *args, **kwargs):
      tag_list =  models.Tag.objects.all().filter(deleted=False)
      for tag in tag_list:
        print tag

        questions = models.Question.objects.filter(tags = tag).distinct()
        question_content_type = ContentType.objects.get_for_model(models.Question)
        answer_content_type = ContentType.objects.get_for_model(models.Answer)
        summary_str = 'Report: %s \n\n' % (tag)

        detail_str = ''
        data = {
                'title': 'Title',
                'upvotes': 'Up Votes',
                'downvotes': 'Down Votes',
                'answers': 'Answers',
                'comments': 'Comments'
            }
        summary_str += '%(title)-32s %(upvotes)7s %(downvotes)9s %(answers)7s %(comments)8s\n' % data
        for question in questions:
            question_votes = models.Vote.objects.filter(
                                        object_id = question.id,
                                        content_type = question_content_type
                                    )
            downvote_count = question_votes.filter(vote = models.Vote.VOTE_DOWN).count()
            upvote_count = question_votes.filter(vote = models.Vote.VOTE_UP).count()
            data = {
                'title': question.title[:30],
                'full_title': question.title,
                'upvotes': upvote_count,
                'downvotes': downvote_count,
                'answers': question.answer_count,
                'comments': question.comments.all().count()
            }
            summary_str += '%(title)-32s %(upvotes)7d %(downvotes)9d %(answers)7d %(comments)8s\n' % data
            detail_str += 60*"=" + '\n'
            detail_str += '%(full_title)s - upvotes: %(upvotes)3d, downvotes: %(downvotes)3d\n\n' % data
            detail_str += question.text + '\n'
            if True:
                for comment in question.comments.all():
                    detail_str += 'Comment by %s\n' % comment.user.username
                    detail_str += comment.comment + '\n'
                for answer in question.answers.all():
                    detail_str += '------------------\n'
                    answer_votes = models.Vote.objects.filter(
                                                    content_type = answer_content_type,
                                                    object_id = answer.id
                                                )
                    data = {
                        'author': answer.author,
                        'downvotes': answer_votes.filter(vote = models.Vote.VOTE_DOWN).count(),
                        'upvotes': answer_votes.filter(vote = models.Vote.VOTE_UP).count(),
                    }
                    detail_str +=  'Answer by %(author)s - upvotes %(upvotes)d downvotes %(downvotes)d\n' % data
                    detail_str += answer.text + '\n'
                    for comment in answer.comments.all():
                        detail_str += 'Comment by %s\n' % comment.user.username
                        detail_str += comment.comment + '\n'
        if kwargs['save_file'] == True:
           fd = open("%s/%s.txt" % (base_report_dir , tag), 'w')
           fd.write(summary_str.encode("iso-8859-15", "replace"))
           if kwargs['show_details'] == True:
               fd.write(detail_str.encode("iso-8859-15","replace"))
           fd.close()
        else:
           print summary_str
           if kwargs['show_details'] == True:
               print detail_str

