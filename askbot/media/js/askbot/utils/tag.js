var Tag = function () {
    SimpleControl.call(this);
    this._deletable = false;
    this._delete_handler = null;
    this._delete_icon_title = null;
    this._tag_title = null;
    this._name = null;
    this._url_params = null;
    this._inner_html_tag = 'a';
    this._html_tag = 'li';
};
inherits(Tag, SimpleControl);

Tag.prototype.setName = function (name) {
    this._name = name;
};

Tag.prototype.getName = function () {
    return this._name;
};

Tag.prototype.setHtmlTag = function (html_tag) {
    this._html_tag = html_tag;
};

Tag.prototype.setDeletable = function (is_deletable) {
    this._deletable = is_deletable;
};

Tag.prototype.setLinkable = function (is_linkable) {
    if (is_linkable === true) {
        this._inner_html_tag = 'a';
    } else {
        this._inner_html_tag = 'span';
    }
};

Tag.prototype.isLinkable = function () {
    return (this._inner_html_tag === 'a');
};

Tag.prototype.isDeletable = function () {
    return this._deletable;
};

Tag.prototype.isWildcard = function () {
    return (this.getName().substr(-1) === '*');
};

Tag.prototype.setUrlParams = function (url_params) {
    this._url_params = url_params;
};

Tag.prototype.setHandlerInternal = function () {
    setupButtonEventHandlers(this._element.find('.tag'), this._handler);
};

/* delete handler will be specific to the task */
Tag.prototype.setDeleteHandler = function (delete_handler) {
    this._delete_handler = delete_handler;
    if (this.hasElement() && this.isDeletable()) {
        this._delete_icon.setHandler(delete_handler);
    }
};

Tag.prototype.getDeleteHandler = function () {
    return this._delete_handler;
};

Tag.prototype.setDeleteIconTitle = function (title) {
    this._delete_icon_title = title;
};

Tag.prototype.decorate = function (element) {
    this._element = element;
    var del = element.find('.delete-icon');
    if (del.length === 1) {
        this.setDeletable(true);
        this._delete_icon = new DeleteIcon();
        if (this._delete_icon_title !== null) {
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        //do not set the delete handler here
        this._delete_icon.decorate(del);
    }
    this._inner_element = this._element.find('.tag');
    this._name = this.decodeTagName(
        $.trim(this._inner_element.attr('data-tag-name'))
    );
    if (this._title !== null) {
        this._inner_element.attr('title', this._title);
    }
    if (this._handler !== null) {
        this.setHandlerInternal();
    }
};

Tag.prototype.getDisplayTagName = function () {
    //replaces the trailing * symbol with the unicode asterisk
    return this._name.replace(/\*$/, '&#10045;');
};

Tag.prototype.decodeTagName = function (encoded_name) {
    return encoded_name.replace('\u273d', '*');
};

Tag.prototype.createDom = function () {
    this._element = this.makeElement(this._html_tag);
    //render the outer element
    if (this._deletable) {
        this._element.addClass('deletable-tag');
    }
    this._element.addClass('tag-left');

    //render the inner element
    this._inner_element = this.makeElement(this._inner_html_tag);
    if (this.isLinkable()) {
        var url = askbot.urls.questions;
        var flag = false;
        var author = '';
        if (this._url_params) {
            url += QSutils.add_search_tag(this._url_params, this.getName());
        }
        this._inner_element.attr('href', url);
    }
    this._inner_element.addClass('tag tag-right');
    this._inner_element.attr('rel', 'tag');
    if (this._title === null) {
        var name = this.getName();
        this.setTitle(interpolate(gettext('see questions tagged \'%s\''), [name,]));
    }
    this._inner_element.attr('title', this._title);
    this._inner_element.html(this.getDisplayTagName());
    this._inner_element.data('tagName', this.getName());

    this._element.append(this._inner_element);

    if (!this.isLinkable() && this._handler !== null) {
        this.setHandlerInternal();
    }

    if (this._deletable) {
        this._delete_icon = new DeleteIcon();
        this._delete_icon.setHandler(this.getDeleteHandler());
        if (this._delete_icon_title !== null) {
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        var del_icon_elem = this._delete_icon.getElement();
        del_icon_elem.text('x'); // HACK by Tomasz
        this._element.append(del_icon_elem);
    }
};
