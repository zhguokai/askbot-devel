/**
 * triggers showing the "data-target" element
 * and destroys itself on activation
 */
var ShowTrigger = function () {
    WrappedElement.call(this);
};
inherits(ShowTrigger, WrappedElement);

ShowTrigger.prototype.decorate = function(element) {
    this._element = element;
    var target = $($(element).data('target'));
    var me = this;
    var onTrigger = function () {
        target.show();
        me.dispose();
    }
    setupButtonEventHandlers(element, onTrigger);
};
