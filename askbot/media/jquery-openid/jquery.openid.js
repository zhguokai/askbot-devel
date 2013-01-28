var FederatedLoginMenu = function() {
    WrappedElement.call(this);
};
inherits(FederatedLoginMenu, WrappedElement);

FederatedLoginMenu.prototype.getLoginHandler = function() {
    var providerInput = this._providerNameElement;
    return function(providerName) {
        providerInput.val(providerName);
    };
};

/**
 * displays a field where user can enter username
 * and a button activating the signing with the openid provier
 */
FederatedLoginMenu.prototype.getOpenidUsernameLoginHandler = function() {
    var providerInput = this._providerNameElement;
    return function(providerName) {
        providerInput.val(providerName);
        //@todo: move selectors to the decorator function
        var extraInfo = $('.extra-openid-info');
        var button = $('button[name="' + providerName + '"]')
        var position = button.position();
        extraInfo.css('position', 'absolute');
        var offsetLeft = position.left - 20;
        extraInfo.css('margin-left', offsetLeft + 'px');
        extraInfo.css('margin-top', '25px');
        extraInfo.css('background', 'white');
        extraInfo.show();
        $('input[name="openid_login_token"]').focus();
    };
};

FederatedLoginMenu.prototype.decorate = function(element) {
    this._element = element;
    this._providerNameElement = element.find('input[name="login-login_provider_name"]');
    this._form = element.find('form');
    var buttons = element.find('li > button');
    var me = this;
    var loginWith = this.getLoginHandler();
    var loginWithOpenidUsername = this.getOpenidUsernameLoginHandler();
    $.each(buttons, function(idx, item) {
        var button = $(item);
        var providerName = button.attr('name');
        if (button.hasClass('openid-username')) {
            setupButtonEventHandlers(
                button,
                function() { 
                    loginWithOpenidUsername(providerName);
                    return false;
                }
            );
        } else {
            setupButtonEventHandlers(button, function() { loginWith(providerName) });
        }
    });
};

var AjaxForm = function() {
    WrappedElement.call(this);
    this._fieldNames = [];//define fields in subclasses
    this._inputs = {};//all keyed by field name
    this._labels = {};
    this._labelDefaultTexts = {};
    this._formPrefix = undefined;//set to string (folowed by dash in django)
};
inherits(AjaxForm, WrappedElement);

AjaxForm.prototype.getSubmitHandler = function() {
    var me = this;
    var inputs = this._inputs;
    var fieldNames = this._fieldNames;
    var url = this._url;
    return function () {
        var data = {};
        $.each(fieldNames, function(idx, fieldName) {
            data[fieldName] = inputs[fieldName].val() || '';
        });
        $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(data) {
                if (data['success']) {
                    if (data['errors']) {
                        me.setErrors(data['errors']);
                    } else {
                        me.handleSuccess(data);
                    }
                }
            }
        });
    };
};

AjaxForm.prototype.setErrors = function(errors) {
    for (var i = 0; i < this._fieldNames.length; i++) {
        var fieldName = this._fieldNames[i];

        var label = this._labels[fieldName];
        if (errors[fieldName]) {
            label.html(errors[fieldName][0]);
            label.addClass('error');
        } else {
            var defaultText = this._labelDefaultTexts[fieldName];
            label.html(defaultText);
            label.removeClass('error');
        }
    };
};

AjaxForm.prototype.decorate = function(element) {
    this._element = element;

    //init labels, inputs and default texts
    var formPrefix = this._formPrefix;
    for (var i = 0; i < this._fieldNames.length; i++) {
        var fieldName = this._fieldNames[i];
        var domFieldName = fieldName;
        if (formPrefix) {
            domFieldName = formPrefix + fieldName;
        }
        var input = element.find('input[name="' + domFieldName + '"]');
        var label = element.find('label[for="' + input.attr('id') + '"]');
        this._inputs[fieldName] = input;
        this._labels[fieldName] = label;
        this._labelDefaultTexts[fieldName] = label.html();
        var activeLabel = new LabeledInput();
        activeLabel.decorate(input);
    }

    this._button = element.find('input[type="submit"]');
    this._url = this._button.data('url');

    var submitHandler = this.getSubmitHandler();
    var enterKeyHandler = makeKeyHandler(13, submitHandler);

    $.each(this._inputs, function(idx, inputItem) {
        $(inputItem).keyup(enterKeyHandler);
    });

    setupButtonEventHandlers(this._button, submitHandler);
};

/**
 * @constructor
 * expects a specific response from the server
 */
var LoginOrRegisterForm = function() {
    AjaxForm.call(this);
};
inherits(LoginOrRegisterForm, AjaxForm);

LoginOrRegisterForm.prototype.handleSuccess = function(data) {
    this._userToolsNav.html(data['userToolsNavHTML']);
    //askbot['vars']['modalDialog'].hide();//@note: using global variable
    $('.modal').hide();
    $('.modal-backdrop').hide();
    if (data['redirectUrl']) {
        window.location.href = data['redirectUrl'];
    }
};

LoginOrRegisterForm.prototype.decorate = function(element) {
    LoginOrRegisterForm.superClass_.decorate.call(this, element);
    this._userToolsNav = $('#userToolsNav');
};

/**
 * @constructor
 */
var PasswordLoginForm = function() {
    LoginOrRegisterForm.call(this);
    this._fieldNames = ['username', 'password'];
    this._formPrefix = 'login-'
};
inherits(PasswordLoginForm, LoginOrRegisterForm);

/**
 * @contstructor
 */
var PasswordRegisterForm = function() {
    LoginOrRegisterForm.call(this);
    this._fieldNames = ['username', 'email', 'password1', 'password2'];
    this._formPrefix = 'register-';
};
inherits(PasswordRegisterForm, LoginOrRegisterForm);

/**
 * @constructor
 */
var CompleteRegistrationForm = function() {
    LoginOrRegisterForm.call(this);
    this._fieldNames = ['username', 'email'];
};
inherits(CompleteRegistrationForm, LoginOrRegisterForm);

/**
 * @constructor
 */
var AccountRecoveryForm = function() {
    AjaxForm.call(this);
    this._fieldNames = ['email'];
    this._formPrefix = 'recover-';
};
inherits(AccountRecoveryForm, AjaxForm);

AccountRecoveryForm.prototype.show = function() {
    this._prompt.hide();
    this._form.show();
    this._inputs['email'].focus();
};

AccountRecoveryForm.prototype.hide = function() {
    this._prompt.show();
    this._form.hide();
    this._inputs['email'].blur();
};

AccountRecoveryForm.prototype.handleSuccess = function() {
    this._prompt.html(gettext('Email sent. Please follow the enclosed recovery link'));
    this.hide();
};

AccountRecoveryForm.prototype.decorate = function(element) {
    this._prompt = element.find('.prompt');
    this._form = element.find('.form');
    //this.show();
    AccountRecoveryForm.superClass_.decorate.call(this, element);
    this.hide();
    var me = this;
    setupButtonEventHandlers(this._prompt, function() { me.show() });
};

/**
 * @constructor
 */
var AuthMenu = function() {
    WrappedElement.call(this);
};
inherits(AuthMenu, WrappedElement);

AuthMenu.prototype.decorate = function(element) {
    this._element = element;

    var federatedLogins = new FederatedLoginMenu();
    federatedLogins.decorate($('.federated-login-methods'));
    this._federatedLogins = federatedLogins;

    var passwordLogin = new PasswordLoginForm();
    passwordLogin.decorate($('.password-login'));
    this._passwordLogin = passwordLogin;

    var passwordRegister = new PasswordRegisterForm();
    passwordRegister.decorate($('.password-registration'));
    this._passwordRegister = passwordRegister;

    var recoveryForm = new AccountRecoveryForm();
    recoveryForm.decorate($('.account-recovery'));
    this._accountRecoveryForm = recoveryForm;

    //@todo: make sure to include account recovery field, hidden by default
};
//@ sourceURL=jquery.openid.js
