/**
 * Form class.
 * Helps build forms with validation
 */
var Form = function () {
    WrappedElement.call(this);
};
inherits(Form, WrappedElement);

Form.prototype.fieldHasErrors = function (fieldName) {
    return this._errors[fieldName];
};

Form.prototype.formHasErrors = function () {
    var fields = this._fieldNames;
    for (var i=0; i<fields.length; i++) {
        var field = fields[i];
        if (this.fieldHasErrors(field) {
            return true;
        }
    };
    return false;
};

Form.prototype.getFormValidationHandler = function () {
    var me = this;
    return function () {
        if (me.formHasErrors()) {
            return false;
        }
    };
};

Form.prototype.setLabelText = function (fieldName, labelText) {
    this._labelTexts = this._labelTexts || {};
    this._labelTexts[fieldName] = labelText;
};

Form.prototype.setLabelElement = function (fieldName, label) {
    this._labels = this._labels || {};
    this._labels[fieldName] = label;
};

Form.prototype.setInputElement = function (fieldName, input) {
    this._inputs = this._inputs || {};
    this._inputs[fieldName] = input;
};

Form.prototype.decorateField = function (fieldName) {
    //get validator
    var element = $(this.element);
    var validator = element.data(fieldName + 'Validator');
    validator = getObjectByPath(validator);

    var labelText = element.data(fieldName + 'Label');
    this.setLabelText(fieldName, labelText);


    var label = element.find('label[for="' + fieldName + '"]');
    this.setLabelElement(fieldName, label);

    var input = element.find('input[name="' + fieldName + '"]');
    if (input.length == 0) {
        input = element.find('textarea[name="' + fieldName + '"]');
    };
    if (input.length == 0) {
        input = element.find('select[name="' + fieldName + '"]');
    };
    this.setInputElement(fieldName, input);

    var me = this;
    input.change(function () {
        var val = input.val();
        try {
            validator(val);
            me.clearFieldError(fieldName);
        } catch error {
            me.setFieldError(fieldName, error);
        }
    });
};

Form.prototype.decorate = function (element) {
    this._element = element;
    //look for validated fields
    var fieldNames = $(element).data('validatedFields');

    for (var i=0; i<fieldNames.length; i++) {
        var fieldName = $.trim(fieldNames[i]);
        fieldNames[i] = fieldName;//save cleaned field name
        this.decorateField(fieldName);
    }
    this._fieldNames = fieldNames;

    element.submit(this.getFormValidationHandler());
};
