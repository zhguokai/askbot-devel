var AskForm = function () {
    Form.call(this);
};
inherits(AskForm, Form);

AskForm.prototype.decorate = function (element) {
    getSuperClass(AskForm).decorate.call(this, element);
    var bodyTriggerLink = element.find('.question-body-trigger');
    var editorElement = element.find('.folded-editor');
    if (bodyTriggerLink.length && editorElement.length) {
        var foldedEditor = new FoldedEditor();
        foldedEditor.setExternalTrigger(bodyTriggerLink);
        foldedEditor.decorate(editorElement);
    }
};
