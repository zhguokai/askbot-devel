#this stuff was removed from views.signin
#instead askbot needs to post the message when the question or answer is posted anonymously
    #todo: this stuff must be executed on some signal
    #because askbot should have nothing to do with the login app
    from askbot.models import AnonymousQuestion as AQ
    session_key = request.session.session_key
    logging.debug('retrieving anonymously posted question associated with session %s' % session_key)
    qlist = AQ.objects.filter(session_key=session_key).order_by('-added_at')
    if len(qlist) > 0:
        question = qlist[0]
    else:
        question = None

    from askbot.models import AnonymousAnswer as AA
    session_key = request.session.session_key
    logging.debug('retrieving posted answer associated with session %s' % session_key)
    alist = AA.objects.filter(session_key=session_key).order_by('-added_at')
    if len(alist) > 0:
        answer = alist[0]
    else:
        answer = None

#and this stuff was ripped out of the template signin.html

    {% if answer %}
        <div class="message">
        {% trans title=answer.question.title, summary=answer.summary %}
        Your answer to {{title}} {{summary}} will be posted once you log in
        {% endtrans %}
        </div>
    {% endif %}
    {% if question %}
        <div class="message">
        {% trans title=question.title, summary=question.summary %}Your question 
        {{title}} {{summary}} will be posted once you log in
        {% endtrans %}
        </div>
    {% endif %}
