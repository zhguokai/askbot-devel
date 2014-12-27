/**
 * @constructor
 * allows to follow/unfollow users
 */
var FollowUser = function () {
    WrappedElement.call(this);
    this._user_id = null;
    this._user_name = null;
};
inherits(FollowUser, WrappedElement);

/**
 * @param {string} user_name
 */
FollowUser.prototype.setUserName = function (user_name) {
    this._user_name = user_name;
};

FollowUser.prototype.decorate = function (element) {
    this._element = element;
    this._user_id = parseInt(element.attr('id').split('-').pop());
    this._available_action = element.children().hasClass('follow') ? 'follow' : 'unfollow';
    var me = this;
    setupButtonEventHandlers(this._element, function () { me.go(); });
};

FollowUser.prototype.go = function () {
    if (askbot.data.userIsAuthenticated === false) {
        var message = gettext('Please <a href="%(signin_url)s">signin</a> to follow %(username)s');
        var message_data = {
            signin_url: askbot.urls.user_signin + '?next=' + window.location.href,
            username: this._user_name
        };
        message = interpolate(message, message_data, true);
        showMessage(this._element, message);
        return;
    }
    var user_id = this._user_id;
    var url = askbot.urls.unfollow_user;
    if (this._available_action === 'follow') {
        url = askbot.urls.follow_user;
    }
    var me = this;
    $.ajax({
        type: 'POST',
        cache: false,
        dataType: 'json',
        url: url.replace('{{userId}}', user_id),
        success: function () { me.toggleState(); }
    });
};

FollowUser.prototype.toggleState = function () {
    if (this._available_action === 'follow') {
        this._available_action = 'unfollow';
        var unfollow_div = document.createElement('div');
        unfollow_div.setAttribute('class', 'unfollow');
        var red_div = document.createElement('div');
        red_div.setAttribute('class', 'unfollow-red');
        red_div.innerHTML = interpolate(gettext('unfollow %s'), [this._user_name]);
        var green_div = document.createElement('div');
        green_div.setAttribute('class', 'unfollow-green');
        green_div.innerHTML = interpolate(gettext('following %s'), [this._user_name]);
        unfollow_div.appendChild(red_div);
        unfollow_div.appendChild(green_div);
        this._element.html(unfollow_div);
    } else {
        var follow_div = document.createElement('div');
        follow_div.innerHTML = interpolate(gettext('follow %s'), [this._user_name]);
        follow_div.setAttribute('class', 'follow');
        this._available_action = 'follow';
        this._element.html(follow_div);
    }
};
