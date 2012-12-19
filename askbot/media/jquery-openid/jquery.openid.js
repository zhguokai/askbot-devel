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

FederatedLoginMenu.prototype.decorate = function(element) {
    this._element = element;
    this._providerNameElement = element.find('input[name="login_provider_name"]');
    this._form = element.find('form');
    var buttons = element.find('li > button');
    var me = this;
    var loginWith = this.getLoginHandler();
    $.each(buttons, function(idx, item) {
        var button = $(item);
        var providerName = button.attr('name');
        setupButtonEventHandlers(button, function() { loginWith(providerName) });
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
    }

    this._button = element.find('input[type="submit"]');
    this._url = this._button.data('url');
    setupButtonEventHandlers(this._button, this.getSubmitHandler());
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
    askbot['vars']['modalDialog'].hide();//@note: using global variable
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

    //@todo: make sure to include account recovery field, hidden by default
    var inputs = element.find('input[type="text"], input[type="password"]');
    $.each(inputs, function(idx, item) {
        var inputElement = $(item);
        var input = new LabeledInput();
        input.decorate(inputElement);
    });
};


$.fn.authenticator = function() {
    var signin_page = $(this);
    var signin_form = $('#signin-form');
    var openid_login_token_input = $('input[name=openid_login_token]');
    var openid_login_token_input_fields = $('#openid-fs');
    var provider_name_input = $('input[name=login_provider_name]');
    var email_input_fields = $('#email-input-fs');
    var account_recovery_heading = $('#account-recovery-heading');
    var account_recovery_hint = $('#account-recovery-form>.hint');
    var account_recovery_link = $('#account-recovery-form>.hint>span.link'); 
    var account_recovery_text_span = $('#account-recovery-form>.hint>span.text');
    var accountRecoveryForm = $('#account-recovery-form');
    var password_input_fields = $('#password-fs');
    var existing_login_methods_div = $('#existing-login-methods');
    var openid_submit_button = $('input[name=openid_login_with_extra_token]');
    var existing_login_methods = {};

    var account_recovery_question_text = account_recovery_heading.html();
    var account_recovery_prompt_text = account_recovery_text_span.html();

    var setup_click_handler = function(elements, handler_function){
        elements.unbind('click').click(handler_function); 
    };

    var setup_enter_key_handler = function(elements, handler_function){
        elements.each(
            function(index, element){
                $(element).unbind('keypress').keypress(
                    function(e){
                        if ((e.which && e.which == 13)||(e.keyCode && e.keyCode == 13)){
                            if (handler_function){
                                return handler_function();
                            }
                            else {
                                element.click();
                                return false;
                            }
                        }
                    }
                );
            }
        );
    };

    var setup_event_handlers = function(elements, handler_function){
        setup_click_handler(elements, handler_function);
        setup_enter_key_handler(elements);
    };

    var get_provider_name = function(row_el){
        var row = $(row_el);
        var name_span = row.find('.ab-provider-name');
        return provider_name = $.trim(name_span.html());
    };

    var read_existing_login_methods = function(){
        $('.ab-provider-row').each(
            function(i, provider_row){
                var provider_name = get_provider_name(provider_row);
                existing_login_methods[provider_name] = true;
            }
        );
    };

    var setup_login_method_deleters = function(){
        $('.ab-provider-row').each(
            function(i, provider_row){
                var provider_name = get_provider_name(provider_row);
                var remove_button = $(
                                    provider_row
                                ).find('button');
                remove_button.click(
                    function(){
                        var message = interpolate(gettext('Are you sure you want to remove your %s login?'), [provider_name]);
                        if (confirm(message)){
                            $.ajax({
                                type: 'POST',
                                url: authUrl + 'delete_login_method/',//url!!!
                                data: {provider_name: provider_name},
                                success: function(data, text_status, xhr){
                                    $(provider_row).remove();
                                    delete existing_login_methods[provider_name];
                                    provider_count -=1;
                                    if (provider_count < 0){
                                        provider_count === 0;
                                    }
                                    if (provider_count === 0){
                                        $('#ab-existing-login-methods').remove();
                                        $('#ab-show-login-methods').remove();
                                        $('h1').html(
                                            gettext("Please add one or more login methods.")
                                        );
                                        $('#login-intro').html(
                                            gettext("You don\'t have a method to log in right now, please add one or more by clicking any of the icons below.")
                                        );
                                        existing_login_methods = null;
                                    }
                                }
                            });
                        }
                    }
                );
            }
        );
    }

    var submit_login_with_password = function(){
        var username = $('#id_username');
        var password = $('#id_password');

        if (username.val().length < 1){
            username.focus();
            return false;
        }
        if (password.val().length < 1){
            password.focus();
            return false;
        }
        return true;
    };

    var submit_change_password = function(){
        var newpass = $('#id_new_password');
        var newpass_retyped = $('#id_new_password_retyped');
        if (newpass.val().length < 1){
            newpass.focus();
            return false
        }
        if (newpass_retyped.val().length < 1){
            newpass_retyped.focus();
            return false;
        }
        if (newpass.val() !== newpass_retyped.val()){
            newpass_retyped.after(
                    '<span class="error">' +
                    gettext('passwords do not match') + 
                    '</span>'
                );
            newpass.val('').focus();
            newpass_retyped.val('');
            return false;
        }
        return true;
    };

    //validator, may be extended to check url for openid
    var submit_with_extra_openid_token = function() {
        if (openid_login_token_input.val().length < 1) {
            openid_login_token_input.focus();
            return false;
        }
        return true;
    };

    var insert_login_list_enabler = function(){
        var enabler = $('#login-list-enabler');
        if (enabler.is('p#login-list-enabler')){
            enabler.show();
        }
        else {
            enabler = $(
                    '<p id="login-list-enabler"><a href="#">' +
                    gettext('Show/change current login methods') +
                    '</a></p>');
            setup_event_handlers(
                enabler,
                function(){
                    if (askbot['settings']['signin_always_show_local_login'] === false){
                        password_input_fields.hide();
                    }
                    openid_login_token_input_fields.hide();
                    enabler.hide();
                    existing_login_methods_div.show();
                }
            );
            existing_login_methods_div.after(enabler);
        }
    };

    var reset_password_input_fields = function(){
        if (userIsAuthenticated){
            $('#id_new_password').val('');
            $('#id_new_password_retyped').val('');
        }
        else {
            $('#id_username').val('');
            $('#id_password').val('');
        }
    };

    var reset_form = function(){
        openid_login_token_input_fields.hide();
        if (askbot['settings']['signin_always_show_local_login'] === false){
            password_input_fields.hide();
        }
        reset_password_input_fields();
        if (userIsAuthenticated === false){
            email_input_fields.hide();
            account_recovery_heading.hide();
            account_recovery_link.show();
            account_recovery_hint.show();
            $('#account-recovery-form>p.hint').css('margin-top','10px');
            account_recovery_text_span.html(account_recovery_question_text).show();
        }
        else {
            if (existing_login_methods !== null){
                existing_login_methods_div.hide();
                insert_login_list_enabler();
            }
        }
    };

    var reset_form_and_errors = function(){
        reset_form();
        $('.error').remove();
    }

    var set_provider_name = function(element){
        var provider_name = element.attr('name');
        provider_name_input.val(provider_name);
    };

    var show_openid_input_fields = function(provider_name){
        reset_form_and_errors();
        var token_name = extra_token_name[provider_name]
        if (userIsAuthenticated){
            $('#openid-heading').html(
                interpolate(gettext('Please enter your %s, then proceed'), [token_name])
            );
            var button_text = gettext('Connect your %(provider_name)s account to %(site)s');
			var data = {
				provider_name: provider_name,
				site: siteName
			}
			button_text = interpolate(button_text, data, true);
            openid_submit_button.val(button_text);
        } 
        else {
            $('#openid-heading>span').html(token_name);
        }
        openid_login_token_input_fields.show();
        openid_login_token_input.focus();
    };

    var start_simple_login = function() {
        //$('#openid_form .providers td').removeClass('highlight');
        //$li.addClass('highlight');
        set_provider_name($(this));
        signin_form.submit();
        return true;
    };

    var start_login_with_extra_openid_token = function() {
        show_openid_input_fields($(this).attr('name'));
        set_provider_name($(this));
        
        setup_enter_key_handler(
            openid_login_token_input,
            function(){
                openid_submit_button.click();
                return false;
            }
        );

        setup_event_handlers(
            openid_submit_button,
            function(){
                signin_form.unbind(
                                'submit'
                            ).submit(
                                submit_with_extra_openid_token
                            );
            }
        );
        return false;
    };

    var start_facebook_login = function(){
        set_provider_name($(this));
        if (typeof FB != 'undefined'){
            FB.getLoginStatus(function(response){
                if (response.authResponse){
                    signin_form.submit();
                }
                else {
                    if (FB.getAuthResponse()){
                      signin_form.submit();
                    }
                    FB.login();
                }
            });
        }
        return false;
    };

    var start_password_login_or_change = function(){
        //called upon clicking on one of the password login buttons 
        reset_form_and_errors();
        set_provider_name($(this));
        var provider_name = $(this).attr('name');
        return setup_password_login_or_change(provider_name);
    };

    var init_always_visible_password_login = function(){
        reset_form();
        //will break wordpress and ldap
        provider_name_input.val('local');
        setup_password_login_or_change('local');
    };

    var setup_password_login_or_change = function(provider_name){
        var token_name = extra_token_name[provider_name]
        var password_action_input = $('input[name=password_action]');
        if (userIsAuthenticated === true){
            var password_button = $('input[name=change_password]');
            var submit_action = submit_change_password;
            if (provider_name === 'local'){
                var provider_cleaned_name = siteName;
            }
            else {
                var provider_cleaned_name = provider_name;
            }
            if (existing_login_methods && existing_login_methods[provider_name]){
                var password_heading_text = interpolate(gettext('Change your %s password'), [provider_cleaned_name])
                var password_button_text = gettext('Change password')
            }
            else {
                var password_heading_text = interpolate(gettext('Create a password for %s'), [provider_cleaned_name])
                var password_button_text = gettext('Create password')
            }
            $('#password-heading').html(
                password_heading_text
            )
            password_button.val(password_button_text);
            password_action_input.val('change_password');
            var focus_input = $('#id_new_password');
            var submittable_input = $('#id_new_password_retyped');
        }
        else{
            $('#password-heading>span').html(token_name);
            var password_button = $('input[name=login_with_password]');
            var submit_action = submit_login_with_password;
            var create_pw_link = $('a.create-password-account')
            if (create_pw_link.length > 0){
                create_pw_link.html(gettext('Create a password-protected account'));
                var url = create_pw_link.attr('href');
                if (url.indexOf('?') !== -1){
                    url = url.replace(/\?.*$/,'?login_provider=' + provider_name);
                }
                else{
                    url += '?login_provider=' + provider_name;
                }
                create_pw_link.attr('href', url);
            }
            password_action_input.val('login');
            var focus_input = $('#id_username');
            var submittable_input = $('#id_password');
        }
        password_input_fields.show();
        focus_input.focus();

        var submit_password_login = function(){
            signin_form.unbind('submit').submit(submit_action);
        };

        setup_enter_key_handler(
            submittable_input,
            function() {
                password_button.click();
                return false;
            }
        );
        setup_event_handlers(password_button, submit_password_login);
        return false;
    };

    var start_account_recovery = function(){
        reset_form_and_errors();
        account_recovery_hint.hide(); 
        account_recovery_heading.css('margin-bottom', '0px');
        account_recovery_heading.html(account_recovery_prompt_text).show();
        email_input_fields.show();
        $('#id_email').focus();
    };

    var clear_password_fields = function(){
        $('#id_password').val('');
        $('#id_new_password').val('');
        $('#id_new_password_retyped').val('');
    };

    var setup_default_handlers = function(){
        setup_event_handlers(
            signin_page.find('input.openid-direct'),
            start_simple_login
        );

        setup_event_handlers(
            signin_page.find('input.openid-username'),
            start_login_with_extra_openid_token
        );

        setup_event_handlers(
            signin_page.find('input.openid-generic'),
            start_login_with_extra_openid_token
        );

        setup_event_handlers(
            signin_page.find('input.facebook'),
            start_facebook_login
        );

        setup_event_handlers(
            signin_page.find('input.oauth'),
            start_simple_login
        );

        setup_event_handlers( 
            signin_page.find('input.password'),
            start_password_login_or_change
        );
        setup_event_handlers( 
            signin_page.find('input.wordpress_site'),
            start_password_login_or_change
        );

        setup_event_handlers(account_recovery_link, start_account_recovery);

        if (userIsAuthenticated){
            read_existing_login_methods();
            setup_login_method_deleters();
        }
    };

    setup_default_handlers();
    if (askbot['settings']['signin_always_show_local_login'] === true){
        init_always_visible_password_login();
    }
    clear_password_fields();
    return this;
};
//@ sourceURL=jquery.openid.js
