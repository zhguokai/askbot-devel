var setup_inbox = function () {
    var page = $('.inbox-forum');
    if (page.length) {
        var clearNotifs = $('.js-manage-messages');
        if (clearNotifs.length) {
            var inbox = new ResponseNotifs();
            inbox.decorate(clearNotifs);
        }
    }
};

var setup_badge_details_toggle = function () {
    $('.badge-context-toggle').each(function (idx, elem) {
        var context_list = $(elem).parent().next('ul');
        if (context_list.children().length > 0) {
            $(elem).addClass('active');
            var toggle_display = function () {
                if (context_list.css('display') === 'none') {
                    $('.badge-context-list').hide();
                    context_list.show();
                } else {
                    context_list.hide();
                }
            };
            $(elem).click(toggle_display);
        }
    });
};

(function () {
    var fbtn = $('.follow-user-toggle');
    if (fbtn.length === 1) {
        var follow_user = new FollowUser();
        follow_user.decorate(fbtn);
        follow_user.setUserName(askbot.data.viewUserName);
    }
    if (askbot.data.userId !== askbot.data.viewUserId) {
        if (askbot.data.userIsAdminOrMod) {
            var group_editor = new UserGroupsEditor();
            group_editor.decorate($('#user-groups'));
        } else {
            $('#add-group').remove();
        }
    } else {
        $('#add-group').remove();
    }

    var tweeting = $('.auto-tweeting');
    if (tweeting.length) {
        var tweetingControl = new Tweeting();
        tweetingControl.decorate(tweeting);
    }

    var qPager = $('.user-questions-pager');
    if (qPager.length) {
        var qPaginator = new UserQuestionsPaginator();
        qPaginator.decorate(qPager);
    }

    var aPager = $('.user-answers-pager');
    if (aPager.length) {
        var aPaginator = new UserAnswersPaginator();
        aPaginator.decorate(aPager);
    }

})();
