/**
 * A button on which user can click
 * and become added to some group (followers, group members, etc.)
 * or toggle some state on/off
 * The button has four states on-prompt, off-prompt, on-state and off-state
 * on-prompt is activated on mouseover, when user is not part of group
 * off-prompt - on mouseover, when user is part of group
 * on-state - when user is part of group and mouse is not over the button
 * off-state - same as above, but when user is not part of the group
 */
var TwoStateToggle = function () {
    SimpleControl.call(this);
    this._state = null;
    this._state_messages = {};
    this._states = [
        'on-state',
        'off-state',
        'on-prompt',
        'off-prompt'
    ];
    this._handler = this.getDefaultHandler();
    this._post_data = {};
    this.toggleUrl = '';//public property
};
inherits(TwoStateToggle, SimpleControl);

TwoStateToggle.prototype.setPostData = function (data) {
    this._post_data = data;
};

TwoStateToggle.prototype.getPostData = function () {
    return this._post_data;
};

TwoStateToggle.prototype.resetStyles = function () {
    var element = this._element;
    var states = this._states;
    $.each(states, function (idx, state) {
        element.removeClass(state);
    });
    this._element.html('');
};

TwoStateToggle.prototype.isOn = function () {
    return this._element.hasClass('on');
};

TwoStateToggle.prototype.getDefaultHandler = function () {
    var me = this;
    return function () {
        var data = me.getPostData();
        data.disable = me.isOn();
        $.ajax({
            type: 'POST',
            dataType: 'json',
            cache: false,
            url: me.toggleUrl,
            data: data,
            success: function (data) {
                if (data.success) {
                    if ( data.is_enabled ) {
                        me.setState('on-state');
                    } else {
                        me.setState('off-state');
                    }
                } else {
                    showMessage(me.getElement(), data.message);
                }
            }
        });
    };
};

TwoStateToggle.prototype.isCheckBox = function () {
    var element = this._element;
    return element.attr('type') === 'checkbox';
};

TwoStateToggle.prototype.setState = function (state) {
    var element = this._element;
    this._state = state;
    if (element) {
        this.resetStyles();
        element.addClass(state);
        if (state === 'on-state') {
            element.addClass('on');
        } else if (state === 'off-state') {
            element.removeClass('on');
        }
        if ( this.isCheckBox() ) {
            if (state === 'on-state') {
                element.attr('checked', true);
            } else if (state === 'off-state') {
                element.attr('checked', false);
            }
        } else {
            this._element.html(this._state_messages[state]);
        }
    }
};

TwoStateToggle.prototype.decorate = function (element) {
    this._element = element;
    //read messages for all states
    var messages = {};
    messages['on-state'] =
        element.attr('data-on-state-text') || gettext('enabled');
    messages['off-state'] =
        element.attr('data-off-state-text') || gettext('disabled');
    messages['on-prompt'] =
        element.attr('data-on-prompt-text') || messages['on-state'];
    messages['off-prompt'] =
        element.attr('data-off-prompt-text') || messages['off-state'];
    this._state_messages = messages;

    this.toggleUrl = element.attr('data-toggle-url');

    //detect state and save it
    if (this.isCheckBox()) {
        this._state = element.attr('checked') ? 'state-on' : 'state-off';
    } else {
        var text = $.trim(element.html());
        for (var i = 0; i < this._states.length; i++) {
            var state = this._states[i];
            if (text === messages[state]) {
                this._state = state;
                break;
            }
        }
    }

    //set mouseover handler only for non-checkbox version
    if (this.isCheckBox() === false) {
        var me = this;
        element.mouseover(function () {
            var is_on = me.isOn();
            if (is_on) {
                me.setState('off-prompt');
            } else {
                me.setState('on-prompt');
            }
            //element.css('background-color', 'red');
            return false;
        });
        element.mouseout(function () {
            var is_on = me.isOn();
            if (is_on) {
                me.setState('on-state');
            } else {
                me.setState('off-state');
            }
            //element.css('background-color', 'white');
            return false;
        });
    }

    setupButtonEventHandlers(element, this.getHandler());
};
