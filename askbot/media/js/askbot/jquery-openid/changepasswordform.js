/**
 * @constructor
 */
var ChangePasswordForm = function () {
    WrappedElement.call(this);
};
inherits(ChangePasswordForm, WrappedElement);

ChangePasswordForm.prototype.showMessage = function (message, callback) {
    var flash = new FlashAlert('...saved, thanks');
    if (callback) {
        flash.setPostRunHandler(callback);
    }
    this._passwordHeading.append(flash.getElement());
    flash.run();
};

ChangePasswordForm.prototype.clearErrors = function () {
    this._pwInput1Errors.html('');
    this._pwInput2Errors.html('');
};

ChangePasswordForm.prototype.showErrors = function (errors) {
    if (errors.new_password) {
        this._pwInput1Errors.html(errors.new_password[0]);
    }
    if (errors.new_password_retyped) {
        this._pwInput2Errors.html(errors.new_password_retyped[0]);
    }
    if (errors.__all__) {
        this._pwInput2Errors.html(errors.__all__[0]);
    }
};

ChangePasswordForm.prototype.getData = function () {
    return {
        'new_password': this._pwInput1.val(),
        'new_password_retyped': this._pwInput2.val()
    };
};

ChangePasswordForm.prototype.getSubmitHandler = function () {
    var me = this;
    return function () {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: me.getData(),
            url: askbot.urls.changePassword,
            success: function (data) {
                if (data.message) {
                    if (me.inAccountRecovery()) {
                        var callback = function () {
                            window.location.href = askbot.urls.questions;
                        };
                        me.showMessage(data.message, callback);
                    } else {
                        me.showMessage(data.message);
                    }
                    me.clearErrors();
                }
                if (data.errors) {
                    me.clearErrors();
                    me.showErrors(data.errors);
                }
            }
        });
        return false;
    };
};

ChangePasswordForm.prototype.inAccountRecovery = function () {
    return ($('input[name="in_recovery"]').length === 1);
};

ChangePasswordForm.prototype.decorate = function (element) {
    this._element = element;
    this._pwInput1 = element.find('#id_new_password');
    this._pwInput2 = element.find('#id_new_password_retyped');
    this._pwInput1Errors = element.find('.new-password-errors');
    this._pwInput2Errors = element.find('.new-password-retyped-errors');
    this._button = element.find('input[name="change_password"]');
    this._passwordHeading = element.find('#password-heading');
    setupButtonEventHandlers(this._button, this.getSubmitHandler());
};
