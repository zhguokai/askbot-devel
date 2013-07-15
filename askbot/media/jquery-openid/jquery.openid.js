var FederatedLoginMenu = function() {
    WrappedElement.call(this);
    this._parent = undefined;
};
inherits(FederatedLoginMenu, WrappedElement);

FederatedLoginMenu.prototype.setParent = function(parentMenu) {
    this._parent = parentMenu;
};

FederatedLoginMenu.prototype.reset = function() {
    this._openidLoginTokenLabeledInput.reset();
    this._extraInfo.hide();
};

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
    var openidLoginTokenInput = this._openidLoginTokenInput;
    var tokenLabeledInput = this._openidLoginTokenLabeledInput;
    var extraInfo = this._extraInfo;
    return function(providerName, providerNameText) {
        providerInput.val(providerName);
        //@todo: move selectors to the decorator function
        var button = $('button[name="' + providerName + '"]')
        var position = button.position();
        extraInfo.css('position', 'absolute');
        var offsetLeft = position.left - 20;
        extraInfo.css('margin-left', offsetLeft + 'px');
        extraInfo.css('background', 'white');
        extraInfo.css('z-index', 1);
        extraInfo.show();
        //important - his must be after "show"
        tokenLabeledInput.reset();//clear errors if any
        //set the label text; important - must be after "reset"
        if (providerName === 'openid') {
            var labelText = gettext('enter OpenID url');
        } else {
            var formatStr = gettext('enter %s user name');
            var labelText = interpolate(formatStr, [providerNameText]);
        }
        tokenLabeledInput.setLabelText(labelText);
        openidLoginTokenInput.focus();
    };
};

FederatedLoginMenu.prototype.getOpenidLoginWithTokenHandler = function() {
    var tokenInput = this._openidLoginTokenInput;
    var tokenLabeledInput = this._openidLoginTokenLabeledInput;
    var form = this._form;
    return function() {
        if ($.trim(tokenInput.val()) === '') {
            tokenLabeledInput.putLabelInside();
            tokenLabeledInput.setError();
            tokenLabeledInput.focus();
            return false;
        } else {
            form.submit();
        }
    };
};

FederatedLoginMenu.prototype.decorate = function(element) {
    this._element = element;
    this._providerNameElement = element.find('input[name="login-login_provider_name"]');
    this._openidLoginTokenInput = $('input[name="login-openid_login_token"]');
    this._form = element.find('form');
    this._extraInfo = element.find('.extra-openid-info');

    var labeledInput = new LabeledInput();
    labeledInput.decorate(this._openidLoginTokenInput);
    this._openidLoginTokenLabeledInput = labeledInput;


    var buttons = element.find('li > button');
    var me = this;
    var loginWith = this.getLoginHandler();
    var loginWithOpenidUsername = this.getOpenidUsernameLoginHandler();
    $.each(buttons, function(idx, item) {
        var button = $(item);
        var providerName = button.attr('name');
        var providerNameLabel = $('label[for="' + button.attr('id') + '"]');
        if (button.hasClass('openid-username') || button.hasClass('openid-generic')) {
            setupButtonEventHandlers(
                button,
                function() { 
                    loginWithOpenidUsername(providerName, providerNameLabel.html());
                    return false;
                }
            );
        } else {
            setupButtonEventHandlers(
                                button,
                                function() { loginWith(providerName) }
                            );
        }
    });

    //event handlers for the AOL type of openid (with extra token)
    //1) enter key handler for the extra user name popup input
    var openidLoginWithTokenHandler = this.getOpenidLoginWithTokenHandler();
    var submitHandler = makeKeyHandler(13, openidLoginWithTokenHandler);
    this._openidLoginTokenInput.keydown(submitHandler);

    //2) submit button handler for the little popup form
    setupButtonEventHandlers( 
        this._extraInfo.find('input[type="submit"]'),
        openidLoginWithTokenHandler
    )
    //3) prevent menu closure upon click (click on the big menu closes the popup)
    this._extraInfo.click(function(evt){
        evt.stopPropagation();
    });
};

/**
 * @constructor
 * expects a specific response from the server
 */
var LoginOrRegisterForm = function() {
    AjaxForm.call(this);
    this._parent = undefined;
};
inherits(LoginOrRegisterForm, AjaxForm);

LoginOrRegisterForm.prototype.setParent = function(parentMenu) {
    this._parent = parentMenu;
};

/*
 * @note: this function is a hack and has no access to the modal
 * menu object itself.
 */
LoginOrRegisterForm.prototype.closeModalMenu = function() {
    $('.modal').remove();
    $('.modal-backdrop').remove();
};


LoginOrRegisterForm.prototype.isModal = function() {
    return ($('.modal').length > 0);
};

LoginOrRegisterForm.prototype.handleSuccess = function(data) {
    if (data['redirectUrl']) {
        window.location.href = data['redirectUrl'];
    }
    if (this._parent) {
        if (this._parent.isModal()) {
            //stay on the page
            this._parent.reset();
        } else {
            //go to the next page
            window.location.href = getNextUrl();
            return;
        }
    } else if (this.isModal() === false) {
        //go to the next page
        window.location.href = getNextUrl();
        return;
    }
    this._userToolsNav.html(data['userToolsNavHTML']);
    /* if login form is not part of the modal menu, then
     * redirect either based on the query part of the url
     * or to the default post-login redirect page */
    var logoutBtn = $('a.logout');
    if (logoutBtn.length === 1) {
        var logoutLink = new LogoutLink();
        logoutLink.decorate(logoutBtn);
    }

    if (this.isModal()) {
        this.closeModalMenu();
    };
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

CompleteRegistrationForm.prototype.decorate = function(element) {
    CompleteRegistrationForm.superClass_.decorate.call(this, element);
    //a hack that makes registration menu closable
    var me = this;
    $('#id_username').focus();
    $('.modal .close').click(function() {
        me.closeModalMenu();
        me.dispose();
    });
    //todo: move this to the html template
    var modal = $('.modal');
    modal.find('h3').html(gettext('Finish registration'));
    modal.find('.modal-footer').remove();
};

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

AccountRecoveryForm.prototype.reset = function() {
    this._inputs['email'].val('');
    this.hide();
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

AuthMenu.prototype.isModal = function() {
    var count = $('.modal').length;
    if (count > 1) {
        throw 'too many modal menues open!!!';
    } else {
        return count === 1;
    }
};

AuthMenu.prototype.closeModalMenu = function() {
    $('.modal').modal('hide');
    $('.modal').hide();
    $('.modal-backdrop').hide();
};

AuthMenu.prototype.reset = function() {
    this._federatedLogins.reset();
    this._passwordLogin.reset();
    this._passwordRegister.reset();
    this._accountRecoveryForm.reset();
    if (this.isModal()) {
        this.closeModalMenu();
    }
};

AuthMenu.prototype.decorate = function(element) {
    this._element = element;

    var federatedLogins = new FederatedLoginMenu();
    federatedLogins.setParent(this);
    federatedLogins.decorate($('.federated-login-methods'));
    this._federatedLogins = federatedLogins;

    var passwordLogin = new PasswordLoginForm();
    passwordLogin.setParent(this);
    passwordLogin.decorate($('.password-login'));
    this._passwordLogin = passwordLogin;

    var passwordRegister = new PasswordRegisterForm();
    passwordRegister.setParent(this);
    passwordRegister.decorate($('.password-registration'));
    this._passwordRegister = passwordRegister;

    var recoveryForm = new AccountRecoveryForm();
    recoveryForm.decorate($('.account-recovery'));
    //this one does not need setParent(), b/c it does not close on success
    this._accountRecoveryForm = recoveryForm;

    //need this to close the extra username popup
    element.click(function(){ federatedLogins.reset(); });
};
//@ sourceURL=jquery.openid.js
