//var $, scriptUrl, askbotSkin
var mediaUrl = function(resource){
    return scriptUrl + 'm/' + askbotSkin + '/' + resource;
};

var copyAltToTitle = function(sel){
    sel.attr('title', sel.attr('alt'));
};

var getUniqueWords = function(value){
    var words = $.trim(value).split(/\s+/);
    var uniques = new Object();
    var out = new Array();
    $.each(words, function(idx, item){
        if (!(item in uniques)){
            uniques[item] = 1;
            out.push(item);
        };
    });
    return out;
};

var showMessage = function(element, msg, where) {
    var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(' +
    $.i18n._('click to close') + ')</div>');

    div.click(function(event) {
        $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
    });

    var where = where || 'parent';

    if (where == 'parent'){
        element.parent().append(div);
    }
    else {
        element.after(div);
    }

    div.fadeIn("fast");
};

/**
 * kind of like Python's builtin getattr
 * @param {Object} obj
 * @param {string} key
 * @param {*} default_value
 */
var getattr = function(obj, key, default_value){
    if (obj){
        return (key in obj) ? obj[key] : default_value;
    } else {
        return default_value;
    }
};

//outer html hack - https://github.com/brandonaaron/jquery-outerhtml/
(function($){
    var div;
    $.fn.outerHTML = function() {
        var elem = this[0],
        tmp;
        return !elem ? null
        : typeof ( tmp = elem.outerHTML ) === 'string' ? tmp
        : ( div = div || $('<div/>') ).html( this.eq(0).clone() ).html();
    };
})(jQuery);

var makeKeyHandler = function(key, callback){
    return function(e){
        if ((e.which && e.which == key) || (e.keyCode && e.keyCode == key)){
            callback(e);
            e.stopImmediatePropagation();
        }
    };
};


var setupButtonEventHandlers = function(button, callback){
    var wrapped_callback = function(e){
        callback();
        e.stopImmediatePropagation();
    };
    button.keydown(makeKeyHandler(13, wrapped_callback));
    button.click(wrapped_callback);
};

var putCursorAtEnd = function(element){
    var el = element.get()[0];
    if (el.setSelectionRange){
        var len = element.val().length * 2;
        el.setSelectionRange(len, len);
    }
    else{
        element.val(element.val());
    }
    element.scrollTop = 999999;
};

var setCheckBoxesIn = function(selector, value){
    return $(selector + '> input[type=checkbox]').attr('checked', value);
};

var notify = function() {
    var visible = false;
    return {
        show: function(html) {
            if (html) {
                $("body").css("margin-top", "2.2em");
                $(".notify span").html(html);
            }
            $(".notify").fadeIn("slow");
            visible = true;
        },
        close: function(doPostback) {
            if (doPostback) {
               $.post(
                   askbot['urls']['mark_read_message'],
                   { formdata: "required" }
               );
            }
            $(".notify").fadeOut("fast");
            $("body").css("margin-top", "0");
            visible = false;
        },
        isVisible: function() { return visible; }
    };
} ();

/* some google closure-like code for the ui elements */
var inherits = function(childCtor, parentCtor) {
  /** @constructor taken from google closure */
    function tempCtor() {};
    tempCtor.prototype = parentCtor.prototype;
    childCtor.superClass_ = parentCtor.prototype;
    childCtor.prototype = new tempCtor();
    childCtor.prototype.constructor = childCtor;
};

/* wrapper around jQuery object */
var WrappedElement = function(){
    this._element = null;
    /**
     * @private
     * @type {boolean}
     */
    this._in_document = false;
};
WrappedElement.prototype.setElement = function(element){
    this._element = element;
};
WrappedElement.prototype.createDom = function(){
    this._element = $('<div></div>');
    if (this._css_class){
        this.addClass(this._css_class);
    }
};
WrappedElement.prototype.getElement = function(){
    if (this._element === null){
        this.createDom();
    }
    return this._element;
};
WrappedElement.prototype.inDocument = function(){
    return this._in_document;
};
WrappedElement.prototype.enterDocument = function(){
    return this._in_document = true;
};
WrappedElement.prototype.hasElement = function(){
    return (this._element !== null);
};
WrappedElement.prototype.makeElement = function(html_tag){
    //makes jQuery element with tags
    return $('<' + html_tag + '></' + html_tag + '>');
};
WrappedElement.prototype.dispose = function(){
    this._element.remove();
    this._in_document = false;
};


/**
 * @constructor
 * a wrapped jquery element that has state
 */
var Widget = function(){
    WrappedElement.call(this);
    /**
     * @private
     * @type {Object.<string, Function>}
     * "dictionary" of transition state event handlers
     * where keys are names of the states to which 
     * the widget is transitioning
     * and the values are functions are to be called upon
     * the transitions
     */
    this._state_transition_event_handlers = {};
    /** 
     * @private
     * @type {string}
     * internal state of the widget
     */
    this._state = null;
};
inherits(Widget, WrappedElement);

Widget.prototype.getStateTransitionEventHandlers = function(){
    return this._state_transition_event_handlers;
};

/**
 * @param {Widget} other_widget
 * not a careful method, will overwrite all
 */
Widget.prototype.copyStateTransitionEventHandlersFrom = function(other_widget){
    this._state_transition_event_handlers =
        other_widget.getStateTransitionEventHandlers();
};
/**
 * @private
 */
Widget.prototype.backupStateTransitionEventHandlers = function(){
    this._steh_backup = this._state_transition_event_handlers;
};
/**
 * @private
 */
Widget.prototype.restoreStateTransitionEventHandlers = function(){
    this._state_transition_event_handlers = this._steh_backup;
};
/**
 * @param {string} state
 */
Widget.prototype.setState = function(state){
    this._state = state;
};
/**
 * @return {sting} state
 */
Widget.prototype.getState = function(){
    return this._state;
};

/**
 * @param {Object}
 */
Widget.prototype.setStateTransitionEventHandlers = function(handlers){
    this._state_transition_event_handlers = handlers;
};

var SimpleControl = function(){
    WrappedElement.call(this);
    this._handler = null;
    this._title = null;
};
inherits(SimpleControl, WrappedElement);

SimpleControl.prototype.setHandler = function(handler){
    this._handler = handler;
    if (this.hasElement()){
        this.setHandlerInternal();
    }
};

SimpleControl.prototype.setHandlerInternal = function(){
    //default internal setHandler behavior
    setupButtonEventHandlers(this._element, this._handler);
};

SimpleControl.prototype.setTitle = function(title){
    this._title = title;
};

/**
 * A clickable icon
 * @constructor
 * @param {string} icon_class - class name for the icon
 * @param {string} title - to become "title" attribute
 */
var ActionIcon = function(icon_class, title){
    SimpleControl.call(this);
    this._class = icon_class;
    this._title = title
};
inherits(ActionIcon, SimpleControl);
/**
 * @private
 */
ActionIcon.prototype.createDom = function(){
    this._element = this.makeElement('span');
    this.decorate(this._element);
};
/**
 * @param {Object} element
 */
ActionIcon.prototype.decorate = function(element){
    this._element = element;
    this._element.addClass(this._class);
    this._element.attr('title', this._title);
    if (this._handler !== null){
        this.setHandlerInternal();
    }
};
/**
 * destroys the icon thing
 */
ActionIcon.prototype.dispose = function(){
    this._element.remove();
};

var EditLink = function(){
    SimpleControl.call(this)
};
inherits(EditLink, SimpleControl);

EditLink.prototype.createDom = function(){
    var element = $('<a></a>');
    element.addClass('edit');
    this.decorate(element);
};

EditLink.prototype.decorate = function(element){
    this._element = element;
    this._element.attr('title', $.i18n._('click to edit this comment'));
    this._element.html($.i18n._('edit'));
    this.setHandlerInternal();
};

/**
 * @constructor
 * @param {string} title
 */
var DeleteIcon = function(title){
    ActionIcon.call(this, 'delete-icon', title);
};
inherits(DeleteIcon, ActionIcon);

var AdderIcon = function(title){
    ActionIcon.call(this, 'adder-icon', title);
};
inherits(AdderIcon, ActionIcon);

var Tag = function(){
    SimpleControl.call(this);
    this._deletable = false;
    this._delete_handler = null;
    this._delete_icon_title = null;
    this._tag_title = null;
    this._name = null;
    this._url_params = null;
    this._inner_html_tag = 'a';
    this._html_tag = 'li';
}
inherits(Tag, SimpleControl);

Tag.prototype.setName = function(name){
    this._name = name;
};

Tag.prototype.getName = function(){
    return this._name;
};

Tag.prototype.setHtmlTag = function(html_tag){
    this._html_tag = html_tag;
};

Tag.prototype.setDeletable = function(is_deletable){
    this._deletable = is_deletable;
};

Tag.prototype.setLinkable = function(is_linkable){
    if (is_linkable === true){
        this._inner_html_tag = 'a';
    } else {
        this._inner_html_tag = 'span';
    }
};

Tag.prototype.isLinkable = function(){
    return (this._inner_html_tag === 'a');
};

Tag.prototype.isDeletable = function(){
    return this._deletable;
};

Tag.prototype.isWildcard = function(){
    return (this.getName().substr(-1) === '*');
};

Tag.prototype.setUrlParams = function(url_params){
    this._url_params = url_params;
};

Tag.prototype.setHandlerInternal = function(){
    setupButtonEventHandlers(this._element.find('.tag'), this._handler);
};

/* delete handler will be specific to the task */
Tag.prototype.setDeleteHandler = function(delete_handler){
    this._delete_handler = delete_handler;
    if (this.hasElement() && this.isDeletable()){
        this._delete_icon.setHandler(delete_handler);
    }
};

Tag.prototype.getDeleteHandler = function(){
    return this._delete_handler;
};

Tag.prototype.setDeleteIconTitle = function(title){
    this._delete_icon_title = title;
};

Tag.prototype.decorate = function(element){
    this._element = element;
    var del = element.find('.delete-icon');
    if (del.length === 1){
        this.setDeletable(true);
        this._delete_icon = new DeleteIcon();
        if (this._delete_icon_title != null){
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        //do not set the delete handler here
        this._delete_icon.decorate(del);
    }
    this._inner_element = this._element.find('.tag');
    this._name = this.decodeTagName($.trim(this._inner_element.html()));
    if (this._title !== null){
        this._inner_element.attr('title', this._title);
    }
    if (this._handler !== null){
        this.setHandlerInternal();
    }
};

Tag.prototype.getDisplayTagName = function(){
    //replaces the trailing * symbol with the unicode asterisk
    return this._name.replace(/\*$/, '&#10045;');
};

Tag.prototype.decodeTagName = function(encoded_name){
    return encoded_name.replace('\u273d', '*');
};

Tag.prototype.createDom = function(){
    this._element = this.makeElement(this._html_tag);
    //render the outer element
    if (this._deletable){
        this._element.addClass('deletable-tag');
    }
    this._element.addClass('tag-left');

    //render the inner element
    this._inner_element = this.makeElement(this._inner_html_tag);
    if (this.isLinkable()){
        var url = askbot['urls']['questions'];
        url += '?tags=' + escape(this.getName());
        if (this._url_params !== null){
            url += escape('&' + this._url_params);
        }
        this._inner_element.attr('href', url);
    }
    this._inner_element.addClass('tag tag-right');
    this._inner_element.attr('rel', 'tag');
    if (this._title === null){
        this.setTitle(
            $.i18n._(
                "see questions tagged '{tag}'"
            ).replace(
                '{tag}',
                this.getName()
            )
        );
    }
    this._inner_element.attr('title', this._title);
    this._inner_element.html(this.getDisplayTagName());

    this._element.append(this._inner_element);

    if (!this.isLinkable() && this._handler !== null){
        this.setHandlerInternal();
    }

    if (this._deletable){
        this._delete_icon = new DeleteIcon();
        this._delete_icon.setHandler(this.getDeleteHandler());
        if (this._delete_icon_title !== null){
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        this._element.append(this._delete_icon.getElement());
    }
};

//Search Engine Keyword Highlight with Javascript
//http://scott.yang.id.au/code/se-hilite/
Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["local","q"],["cnprog\\.","q"],["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function(d){var g=null;var e=new RegExp("");for(var c=0;c<Hilite.search_engines.length;c++){var f=Hilite.search_engines[c];e.compile("^http://(www\\.)?"+f[0],"i");var b=d.match(e);if(b){var a;if(isNaN(f[1])){a=Hilite.decodeReferrerQS(d,f[1])}else{a=b[f[1]+1]}if(a){a=decodeURIComponent(a);if(f.length>2&&f[2]){a=decodeURIComponent(a)}a=a.replace(/\'|"/g,"");a=a.split(/[\s,\+\.]+/);return a}break}}return null};Hilite.decodeReferrerQS=function(f,d){var b=f.indexOf("?");var c;if(b>=0){var a=new String(f.substring(b+1));b=0;c=0;while((b>=0)&&((c=a.indexOf("=",b))>=0)){var e,g;e=a.substring(b,c);b=a.indexOf("&",c)+1;if(e==d){if(b<=0){return a.substring(c+1)}else{return a.substring(c+1,b-1)}}else{if(b<=0){return null}}}}return null};Hilite.hiliteElement=function(f,e){if(!e||f.childNodes.length==0){return}var c=new Array();for(var b=0;b<e.length;b++){e[b]=e[b].toLowerCase();if(Hilite.exact){c.push("\\b"+e[b]+"\\b")}else{c.push(e[b])}}c=new RegExp(c.join("|"),"i");var a={};for(var b=0;b<e.length;b++){if(Hilite.style_name_suffix){a[e[b]]=Hilite.style_name+(b+1)}else{a[e[b]]=Hilite.style_name}}var d=function(m){var j=c.exec(m.data);if(j){var n=j[0];var i="";var h=m.splitText(j.index);var g=h.splitText(n.length);var l=m.ownerDocument.createElement("SPAN");m.parentNode.replaceChild(l,h);l.className=a[n.toLowerCase()];l.appendChild(h);return l}else{return m}};Hilite.walkElements(f.childNodes[0],1,d)};Hilite.hilite=function(){var a=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var b=null;a=Hilite.decodeReferrer(a);if(a&&((Hilite.elementid&&(b=document.getElementById(Hilite.elementid)))||(b=document.body))){Hilite.hiliteElement(b,a)}};Hilite.walkElements=function(d,f,e){var a=/^(script|style|textarea)/i;var c=0;while(d&&f>0){c++;if(c>=Hilite.max_nodes){var b=function(){Hilite.walkElements(d,f,e)};setTimeout(b,50);return}if(d.nodeType==1){if(!a.test(d.tagName)&&d.childNodes.length>0){d=d.childNodes[0];f++;continue}}else{if(d.nodeType==3){d=e(d)}}if(d.nextSibling){d=d.nextSibling}else{while(f>0){d=d.parentNode;f--;if(d.nextSibling){d=d.nextSibling;break}}}}};if(Hilite.onload){if(window.attachEvent){window.attachEvent("onload",Hilite.hilite)}else{if(window.addEventListener){window.addEventListener("load",Hilite.hilite,false)}else{var __onload=window.onload;window.onload=function(){Hilite.hilite();__onload()}}}};
/* json2.js by D. Crockford */
if(!this.JSON){this.JSON={}}(function(){function f(n){return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(key){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf()}}var cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,gap,indent,meta={"\b":"\\b","\t":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==="string"?c:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+string+'"'}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function"){value=value.toJSON(key)}if(typeof rep==="function"){value=rep.call(holder,key,value)}switch(typeof value){case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value){return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]"){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object"){length=rep.length;for(i=0;i<length;i+=1){k=rep[i];if(typeof k==="string"){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value){if(Object.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function"){JSON.stringify=function(value,replacer,space){var i;gap="";indent="";if(typeof space==="number"){for(i=0;i<space;i+=1){indent+=" "}}else{if(typeof space==="string"){indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function"){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==="object"){for(k in value){if(Object.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());
//jquery fieldselection
(function(){var a={getSelection:function(){var b=this.jquery?this[0]:this;return(("selectionStart" in b&&function(){var c=b.selectionEnd-b.selectionStart;return{start:b.selectionStart,end:b.selectionEnd,length:c,text:b.value.substr(b.selectionStart,c)}})||(document.selection&&function(){b.focus();var d=document.selection.createRange();if(d==null){return{start:0,end:b.value.length,length:0}}var c=b.createTextRange();var e=c.duplicate();c.moveToBookmark(d.getBookmark());e.setEndPoint("EndToStart",c);return{start:e.text.length,end:e.text.length+d.text.length,length:d.text.length,text:d.text}})||function(){return{start:0,end:b.value.length,length:0}})()},replaceSelection:function(){var b=this.jquery?this[0]:this;var c=arguments[0]||"";return(("selectionStart" in b&&function(){b.value=b.value.substr(0,b.selectionStart)+c+b.value.substr(b.selectionEnd,b.value.length);return this})||(document.selection&&function(){b.focus();document.selection.createRange().text=c;return this})||function(){b.value+=c;return this})()}};jQuery.each(a,function(b){jQuery.fn[b]=this})})();
//our custom autocompleter
var AutoCompleter=function(a){var b={autocompleteMultiple:true,multipleSeparator:" ",inputClass:"acInput",loadingClass:"acLoading",resultsClass:"acResults",selectClass:"acSelect",queryParamName:"q",limitParamName:"limit",extraParams:{},lineSeparator:"\n",cellSeparator:"|",minChars:2,maxItemsToShow:10,delay:400,useCache:true,maxCacheLength:10,matchSubset:true,matchCase:false,matchInside:true,mustMatch:false,preloadData:false,selectFirst:false,stopCharRegex:/\s+/,selectOnly:false,formatItem:null,onItemSelect:false,autoFill:false,filterResults:true,sortResults:true,sortFunction:false,onNoMatch:false};this.options=$.extend({},b,a);this.cacheData_={};this.cacheLength_=0;this.selectClass_="jquery-autocomplete-selected-item";this.keyTimeout_=null;this.lastKeyPressed_=null;this.lastProcessedValue_=null;this.lastSelectedValue_=null;this.active_=false;this.finishOnBlur_=true;this.options.minChars=parseInt(this.options.minChars,10);if(isNaN(this.options.minChars)||this.options.minChars<1){this.options.minChars=2}this.options.maxItemsToShow=parseInt(this.options.maxItemsToShow,10);if(isNaN(this.options.maxItemsToShow)||this.options.maxItemsToShow<1){this.options.maxItemsToShow=10}this.options.maxCacheLength=parseInt(this.options.maxCacheLength,10);if(isNaN(this.options.maxCacheLength)||this.options.maxCacheLength<1){this.options.maxCacheLength=10}if(this.options.preloadData===true){this.fetchRemoteData("",function(){})}};inherits(AutoCompleter,WrappedElement);AutoCompleter.prototype.decorate=function(a){this._element=a;this._element.attr("autocomplete","off");this._results=$("<div></div>").hide();if(this.options.resultsClass){this._results.addClass(this.options.resultsClass)}this._results.css({position:"absolute"});$("body").append(this._results);this.setEventHandlers()};AutoCompleter.prototype.setEventHandlers=function(){var a=this;a._element.keydown(function(b){a.lastKeyPressed_=b.keyCode;switch(a.lastKeyPressed_){case 38:b.preventDefault();if(a.active_){a.focusPrev()}else{a.activate()}return false;break;case 40:b.preventDefault();if(a.active_){a.focusNext()}else{a.activate()}return false;break;case 9:case 13:if(a.active_){b.preventDefault();a.selectCurrent();return false}break;case 27:if(a.active_){b.preventDefault();a.finish();return false}break;default:a.activate()}});a._element.blur(function(){if(a.finishOnBlur_){setTimeout(function(){a.finish()},200)}})};AutoCompleter.prototype.position=function(){var a=this._element.offset();this._results.css({top:a.top+this._element.outerHeight(),left:a.left})};AutoCompleter.prototype.cacheRead=function(d){var f,c,b,a,e;if(this.options.useCache){d=String(d);f=d.length;if(this.options.matchSubset){c=1}else{c=f}while(c<=f){if(this.options.matchInside){a=f-c}else{a=0}e=0;while(e<=a){b=d.substr(0,c);if(this.cacheData_[b]!==undefined){return this.cacheData_[b]}e++}c++}}return false};AutoCompleter.prototype.cacheWrite=function(a,b){if(this.options.useCache){if(this.cacheLength_>=this.options.maxCacheLength){this.cacheFlush()}a=String(a);if(this.cacheData_[a]!==undefined){this.cacheLength_++}return this.cacheData_[a]=b}return false};AutoCompleter.prototype.cacheFlush=function(){this.cacheData_={};this.cacheLength_=0};AutoCompleter.prototype.callHook=function(c,b){var a=this.options[c];if(a&&$.isFunction(a)){return a(b,this)}return false};AutoCompleter.prototype.activate=function(){var b=this;var a=function(){b.activateNow()};var c=parseInt(this.options.delay,10);if(isNaN(c)||c<=0){c=250}if(this.keyTimeout_){clearTimeout(this.keyTimeout_)}this.keyTimeout_=setTimeout(a,c)};AutoCompleter.prototype.activateNow=function(){var a=this.getValue();if(a!==this.lastProcessedValue_&&a!==this.lastSelectedValue_){if(a.length>=this.options.minChars){this.active_=true;this.lastProcessedValue_=a;this.fetchData(a)}}};AutoCompleter.prototype.fetchData=function(b){if(this.options.data){this.filterAndShowResults(this.options.data,b)}else{var a=this;this.fetchRemoteData(b,function(c){a.filterAndShowResults(c,b)})}};AutoCompleter.prototype.fetchRemoteData=function(c,e){var d=this.cacheRead(c);if(d){e(d)}else{var a=this;if(this._element){this._element.addClass(this.options.loadingClass)}var b=function(g){var f=false;if(g!==false){f=a.parseRemoteData(g);a.options.data=f;a.cacheWrite(c,f)}if(a._element){a._element.removeClass(a.options.loadingClass)}e(f)};$.ajax({url:this.makeUrl(c),success:b,error:function(){b(false)}})}};AutoCompleter.prototype.setOption=function(a,b){this.options[a]=b};AutoCompleter.prototype.setExtraParam=function(b,c){var a=$.trim(String(b));if(a){if(!this.options.extraParams){this.options.extraParams={}}if(this.options.extraParams[a]!==c){this.options.extraParams[a]=c;this.cacheFlush()}}};AutoCompleter.prototype.makeUrl=function(e){var a=this;var b=this.options.url;var d=$.extend({},this.options.extraParams);if(this.options.queryParamName===false){b+=encodeURIComponent(e)}else{d[this.options.queryParamName]=e}if(this.options.limitParamName&&this.options.maxItemsToShow){d[this.options.limitParamName]=this.options.maxItemsToShow}var c=[];$.each(d,function(f,g){c.push(a.makeUrlParam(f,g))});if(c.length){b+=b.indexOf("?")==-1?"?":"&";b+=c.join("&")}return b};AutoCompleter.prototype.makeUrlParam=function(a,b){return String(a)+"="+encodeURIComponent(b)};AutoCompleter.prototype.splitText=function(a){return String(a).replace(/(\r\n|\r|\n)/g,"\n").split(this.options.lineSeparator)};AutoCompleter.prototype.parseRemoteData=function(c){var h,b,f,d,g;var e=[];var b=this.splitText(c);for(f=0;f<b.length;f++){var a=b[f].split(this.options.cellSeparator);g=[];for(d=0;d<a.length;d++){g.push(unescape(a[d]))}h=g.shift();e.push({value:unescape(h),data:g})}return e};AutoCompleter.prototype.filterAndShowResults=function(a,b){this.showResults(this.filterResults(a,b),b)};AutoCompleter.prototype.filterResults=function(d,b){var f=[];var l,c,e,m,j,a;var k,h,g;for(e=0;e<d.length;e++){m=d[e];j=typeof m;if(j==="string"){l=m;c={}}else{if($.isArray(m)){l=m[0];c=m.slice(1)}else{if(j==="object"){l=m.value;c=m.data}}}l=String(l);if(l>""){if(typeof c!=="object"){c={}}if(this.options.filterResults){h=String(b);g=String(l);if(!this.options.matchCase){h=h.toLowerCase();g=g.toLowerCase()}a=g.indexOf(h);if(this.options.matchInside){a=a>-1}else{a=a===0}}else{a=true}if(a){f.push({value:l,data:c})}}}if(this.options.sortResults){f=this.sortResults(f,b)}if(this.options.maxItemsToShow>0&&this.options.maxItemsToShow<f.length){f.length=this.options.maxItemsToShow}return f};AutoCompleter.prototype.sortResults=function(c,d){var b=this;var a=this.options.sortFunction;if(!$.isFunction(a)){a=function(g,e,h){return b.sortValueAlpha(g,e,h)}}c.sort(function(f,e){return a(f,e,d)});return c};AutoCompleter.prototype.sortValueAlpha=function(d,c,e){d=String(d.value);c=String(c.value);if(!this.options.matchCase){d=d.toLowerCase();c=c.toLowerCase()}if(d>c){return 1}if(d<c){return -1}return 0};AutoCompleter.prototype.showResults=function(e,b){var k=this;var g=$("<ul></ul>");var f,l,j,a,h=false,d=false;var c=e.length;for(f=0;f<c;f++){l=e[f];j=$("<li>"+this.showResult(l.value,l.data)+"</li>");j.data("value",l.value);j.data("data",l.data);j.click(function(){var i=$(this);k.selectItem(i)}).mousedown(function(){k.finishOnBlur_=false}).mouseup(function(){k.finishOnBlur_=true});g.append(j);if(h===false){h=String(l.value);d=j;j.addClass(this.options.firstItemClass)}if(f==c-1){j.addClass(this.options.lastItemClass)}}this.position();this._results.html(g).show();a=this._results.outerWidth()-this._results.width();this._results.width(this._element.outerWidth()-a);$("li",this._results).hover(function(){k.focusItem(this)},function(){});if(this.autoFill(h,b)){this.focusItem(d)}};AutoCompleter.prototype.showResult=function(b,a){if($.isFunction(this.options.showResult)){return this.options.showResult(b,a)}else{return b}};AutoCompleter.prototype.autoFill=function(e,c){var b,a,d,f;if(this.options.autoFill&&this.lastKeyPressed_!=8){b=String(e).toLowerCase();a=String(c).toLowerCase();d=e.length;f=c.length;if(b.substr(0,f)===a){this._element.val(e);this.selectRange(f,d);return true}}return false};AutoCompleter.prototype.focusNext=function(){this.focusMove(+1)};AutoCompleter.prototype.focusPrev=function(){this.focusMove(-1)};AutoCompleter.prototype.focusMove=function(a){var b,c=$("li",this._results);a=parseInt(a,10);for(var b=0;b<c.length;b++){if($(c[b]).hasClass(this.selectClass_)){this.focusItem(b+a);return}}this.focusItem(0)};AutoCompleter.prototype.focusItem=function(b){var a,c=$("li",this._results);if(c.length){c.removeClass(this.selectClass_).removeClass(this.options.selectClass);if(typeof b==="number"){b=parseInt(b,10);if(b<0){b=0}else{if(b>=c.length){b=c.length-1}}a=$(c[b])}else{a=$(b)}if(a){a.addClass(this.selectClass_).addClass(this.options.selectClass)}}};AutoCompleter.prototype.selectCurrent=function(){var a=$("li."+this.selectClass_,this._results);if(a.length==1){this.selectItem(a)}else{this.finish()}};AutoCompleter.prototype.selectItem=function(d){var c=d.data("value");var b=d.data("data");var a=this.displayValue(c,b);this.lastProcessedValue_=a;this.lastSelectedValue_=a;this.setValue(a);this.setCaret(a.length);this.callHook("onItemSelect",{value:c,data:b});this.finish()};AutoCompleter.prototype.isContentChar=function(a){if(a.match(this.options.stopCharRegex)){return false}else{if(a===this.options.multipleSeparator){return false}else{return true}}};AutoCompleter.prototype.getValue=function(){var c=this._element.getSelection();var d=this._element.val();var f=c.start;var e=f;for(cpos=f;cpos>=0;cpos=cpos-1){if(cpos===d.length){continue}var b=d.charAt(cpos);if(!this.isContentChar(b)){break}e=cpos}var a=f;for(cpos=f;cpos<d.length;cpos=cpos+1){if(cpos===0){continue}var b=d.charAt(cpos);if(!this.isContentChar(b)){break}a=cpos}this._selection_start=e;this._selection_end=a;return d.substring(e,a)};AutoCompleter.prototype.setValue=function(b){var a=this._element.val().substring(0,this._selection_start);var c=this._element.val().substring(this._selection_end+1);this._element.val(a+b+c)};AutoCompleter.prototype.displayValue=function(b,a){if($.isFunction(this.options.displayValue)){return this.options.displayValue(b,a)}else{return b}};AutoCompleter.prototype.finish=function(){if(this.keyTimeout_){clearTimeout(this.keyTimeout_)}if(this._element.val()!==this.lastSelectedValue_){if(this.options.mustMatch){this._element.val("")}this.callHook("onNoMatch")}this._results.hide();this.lastKeyPressed_=null;this.lastProcessedValue_=null;if(this.active_){this.callHook("onFinish")}this.active_=false};AutoCompleter.prototype.selectRange=function(d,a){var c=this._element.get(0);if(c.setSelectionRange){c.focus();c.setSelectionRange(d,a)}else{if(this.createTextRange){var b=this.createTextRange();b.collapse(true);b.moveEnd("character",a);b.moveStart("character",d);b.select()}}};AutoCompleter.prototype.setCaret=function(a){this.selectRange(a,a)};

/**
 * A text element with an "edit" prompt
 * showing on mouseover
 * the widget has two states: DISPLAY and "EDIT"
 * when user hits "edit", widget state changes to
 * EDIT, when user hits "enter" state goes to "DISPLAY
 * replaced with an input box and the "edit" link
 * hides
 * when user hits "enter", 
 */
var EditableString = function(){
    Widget.call(this);
    /**
     * @private
     * @type {string}
     * text string that is to be shown 
     * to the user
     */
    this._text = '';

    /**
     * @private
     * @type {boolean}
     */
    this._is_editable = true;
    /**
     * @private
     * @type {string}
     * supported states are 'DISPLAY' and 'EDIT'
     * 'DISPLAY' is default
     */
    this._state = 'DISPLAY';
};
inherits(EditableString, Widget);

/**
 * @param {boolean} is_editable
 */
EditableString.prototype.setEditable = function(is_editable){
    this._is_editable = is_editable;
};

/**
 * @param {boolean}
 */
EditableString.prototype.isEditable = function(){
    return this._is_editable;
};

/**
 * @return {Object}
 */
EditableString.prototype.getDisplayBlock = function(){
    return this._display_block;
};
/**
 * @return {Object}
 */
EditableString.prototype.getEditBlock = function(){
    return this._edit_block;
};

EditableString.prototype.setState = function(state){
    if (state === 'EDIT' && this.isEditable() === false){
        throw 'cannot edit this instance of EditableString';
    }

    this._state = state;

    //run transition event handler, if exists
    var handlers = this.getStateTransitionEventHandlers();
    if (handlers.hasOwnProperty(state)){
        handlers[state].call();
    }

    if (! (this._display_block && this._edit_block) ){
        //a case when createDom has not yet been called
        return;
    }

    //hide and show things
    if (state === 'EDIT'){
        this._edit_block.show();
        this._input_box.focus();
        this._display_block.hide();
    } else if (state === 'DISPLAY'){
        this._edit_block.hide();
        this._display_block.show();
        if (this.isEditable()){
            this._edit_link.show();
        }
    }
};

/**
 * @param {string} text - string text
 */
EditableString.prototype.setText = function(text){
    this._text = text;
    if (this._text_element){
        this._text_element.html(text);
    };
};

/**
 * @return {string} text of the string
 */
EditableString.prototype.getText = function(){
    if (this._text_element){
        var text = $.trim(this._text_element.html());
        this._text = text;
        return text;
    } else {
        return $.trim(this._text);
    }
};

/**
 * @return {string}
 */
EditableString.prototype.getInputBoxText = function(){
    return $.trim(this._input_box.val());
};

EditableString.prototype.getSaveEditHandler = function(){
    var me = this;
    return function(){
        me.setText(me.getInputBoxText());
        me.setState('DISPLAY');
    };
};

EditableString.prototype.getStartEditHandler = function(){
    var me = this;
    return function(){
        me.setState('EDIT');
        me._input_box.val(me._text_element.html());
        me._input_box.focus();
    };
};

/**
 * takes an jQuery element, assumes (no error checking)
 * that the element
 * has a single text node and replaces its content with
 * <div><span>text</span><a>edit</a><div>
 * <div><input /></div>
 * and enters the DISPLAY state
 */
EditableString.prototype.decorate = function(element){
    this.setText(element.html());//no error checking
    //build dom for the display block
    var real_element = this.getElement();
    this._element = element;
    this._element.empty();
    this._element.append(real_element);
};

EditableString.prototype.createDom = function(){

    this._element = this.makeElement('div');

    this._display_block = this.makeElement('div');
    this._element.append(this._display_block);
    this._text_element = this.makeElement('span');
    this._display_block.append(this._text_element);
    //set the value of text
    this._text_element.html(this._text);
    //set the display state

    //it is assumed that _is_editable is set once at the beginning
    this._edit_block = this.makeElement('div');
    this._element.append(this._edit_block);

    this._input_box = this.makeElement('input');
    this._input_box.attr('type', 'text');
    this._edit_block.append(this._input_box);

    var edit_link = new EditLink();
    edit_link.setHandler(
        this.getStartEditHandler()
    );

    var edit_element = edit_link.getElement();
    if (!this.isEditable()){
        edit_element.hide();
    }
    this._display_block.append(edit_element);
    //build dom for the edit block

    this._edit_link = edit_link.getElement();

    this._input_box.keydown(
        makeKeyHandler(13, this.getSaveEditHandler())
    );
    this.setState(this.getState());
};

/**
 * @constructor
 * @inherits {EditableString}
 */
var Category = function(){
    EditableString.call(this);
    /** 
     * @private
     * @type {?number}
     */
    this._category_id = null;
    /**
     * @private
     * @type {?Category}
     * parent category, if any
     */
    this._parent = null;
}
inherits(Category, EditableString);

/**
 * @param {number} id
 * set caterory id
 */
Category.prototype.setId = function(id){
    this._category_id = id;
};
/**
 * @return {number}
 */
Category.prototype.getId = function(){
    return this._category_id;
};
/**
 * @return boolean
 */
Category.prototype.hasId = function(){
    return (this._category_id !== null);
};
/**
 * @param {Category} parent_category
 */
Category.prototype.setParent = function(parent_category){
    this._parent = parent_category;
};
/**
 * @returns {?Category}
 */
Category.prototype.getParent = function(){
    return this._parent;
};

/**
 * @param {string} name
 * set category name
 */
Category.prototype.setName = function(name){
    this.setText(name);
};

/**
 * @return {?string}
 */
Category.prototype.getName = function(){
    return this.getText();
};

/**
 * override of the parent classes getter
 * @return {Function}
 */
Category.prototype.getSaveEditHandler = function(){
    var me = this;
    if (this.hasId()){
        return function(){
            me.startRenaming();
        }
    } else {
        return function(){
            me.startAddingToDatabase();
        };
    }
};

/**
 * @private
 */
Category.prototype.startRenaming = function(){
    var new_name = this.getInputBoxText();
    var old_name = this.getText();
    if (new_name !== '' && new_name !== old_name){
        var me = this;
        var success_handler = function(){
            me.setText(new_name);
            me.setState('DISPLAY');
        };
        $.ajax({
            type: 'POST',
            cache: false,
            dataType: 'json',
            url: askbot['urls']['rename_category'],
            data: {id: me.getId(), name: new_name},
            success: success_handler
        });
    }
};
/**
 * starts deleting a category from the database
 * @param {Function} on_delete - to be called after delete succeeds
 */
Category.prototype.startDeleting = function(on_delete){
    $.ajax({
        type: 'POST',
        cache: false,
        dataType: 'json',
        url: askbot['urls']['delete_category'],
        data: {id: this.getId()},
    });
};

/**
 * @private
 */
Category.prototype.startAddingToDatabase = function(){
    var new_category_name = this.getInputBoxText();
    var data = {
        'parent': this.getParent().getId(),
        name: new_category_name 
    };
    var me = this;
    var success_handler = function(){
        me.setText(new_category_name);
        me.setState('DISPLAY');
        me.becomeBonaFide();
    };
    $.ajax({
        type: 'POST',
        cache: false,
        dataType: 'json',
        url: askbot['urls']['add_category'],
        data: data,
        success: success_handler
    });
};

/**
 * @private
 * called when category becomes "real" after saving
 * in the database
 */
Category.prototype.becomeBonaFide = function(){
    this.restoreStateTransitionEventHandlers();
};

/**
 * @constructor
 * @param {MenuItem} parent_item
 */
var MenuAdder = function(parent_item){
    AdderIcon.call(this, gettext('Add subcategory'));
    /**
     * @private
     * @type {MenuItem}
     */
    this._parent_menu_item = parent_item;
};
inherits(MenuAdder, AdderIcon);
/**
 * @return {MenuItem}
 */
MenuAdder.prototype.getParentMenuItem = function(){
    return this._parent_menu_item;
};
/**
 * @private
 */
MenuAdder.prototype.setHanderInternal = function(){
    var me = this;
    this._handler = function(){
        //build an empty subtree on the current menu item
        var new_menu = me.getParentMenuItem().buildSubtree();
        //activate the menu item adder on the new menu
        new_menu.getMenuItemAdder().activate();
    }
    MenuAdder.superClass_.setHandlerInternal.call(this);
};

/** 
 * the data structure used to construct the MenuItem
 * @typedef {{id: number, name: string, children: Array.<MenuData>}}
 */
var MenuItemData;

/**
 * the data structure for the entire menu
 * @typedef {{Array.<MenuItemData>}}
 */
var MenuData;


/**
 * MenuItem widget
 * @constructor
 * @param {Menu} parent_menu - the parent menu
 * @param {MenuItemData} data
 */
var MenuItem = function(parent_menu, data){
    Widget.call(this);
    /** 
     * MenuItem id
     * @type {integer}
     */
    this.id = getattr(data, 'id', null);
    /**
     * MenuItem name
     * @type {string}
     */
    this.name = getattr(data, 'id', null);
    /**
     * source data for the children
     * @private
     * @type {Object} 
     */
    this._children_data = getattr(data, 'children', null);
    /**
     * @private
     * @type {Menu}
     */
    this._parent_menu = parent_menu;
    /**
     * child menu item
     * @private
     * @type {Menu}
     */
    this._child_menu = null;
    /**
     * content element of the menu
     * @private
     * @type {Object} any class,
     * but method getText() is required
     */
    this._content = null;

};
inherits(MenuItem, WrappedElement);

/**
 * @param {Object} content - content object
 * any object with a method getText()
 */
MenuItem.prototype.setContent = function(content){
    this._content = content;
};

/**
 * @returns {Object}
 */
MenuItem.prototype.getContent = function(){
    return this._content;
};

/**
 * @returns {Menu}
 */
MenuItem.prototype.getParentMenu = function(){
    return this._parent_menu;
}

/**
 * @private
 * @param {state} string
 * supported states are DISPLAY and EDIT
 */
MenuItem.prototype.setState = function(state){
    this._content.setState(state);
}

/**
 * @type {boolean}
 */
MenuItem.prototype.isEditable = function(){
    return this._parent_menu.isEditable();
};

/**
 * @return {boolean}
 */
MenuItem.prototype.hasChildren = function(){
    return (this._children_data.length > 0);
};

/**
 * @param {boolean} is_childless
 * changes the display in accordance with the new status
 */
MenuItem.prototype.setChildless = function(is_childless){
    var more_icon = this._more_icon;
    var menu_adder = this._menu_adder.getElement();
    if (is_childless){
        more_icon.hide();
        menu_adder.show();
    } else {
        more_icon.show();
        menu_adder.hide();
    }
};

/**
 * @param {boolean} is_deletable
 * changes the display
 */
MenuItem.prototype.setDeletable = function(is_deletable){
    if (is_deletable){
        this._delete_icon.getElement().show();
    } else {
        this._delete_icon.getElement().hide();
    }
};

/**
 * @private
 */
MenuItem.prototype.hideControls = function(){
    this._more_icon.hide();
    this._delete_icon.getElement().hide();
    this._menu_adder.getElement().hide();
};


/**
 * creates dom for a single MenuItem
 * does not build subcategories
 */
MenuItem.prototype.createDom = function(){
    //create the text element for MenuItem
    this._element = this.makeElement('li');
    this._element.addClass('ab-menu-item');
    this._element.append(this.getContent().getElement());

    var disp_block = this.getContent().getDisplayBlock();

    //todo: may become a widget
    var more_icon = this.makeElement('span');
    more_icon.addClass('ab-more-icon');
    disp_block.append(more_icon);
    this._more_icon = more_icon;
    var deleter = new DeleteIcon();
    this._delete_icon = deleter;
    var me = this;
    var on_delete = function(){
        me.finishDeleting();
    }
    deleter.setHandler(function(){
        me.startDeleting(on_delete);
    });
    disp_block.append(deleter.getElement());

    /* todo: add check on the current menu level
     * if it is maxed out - do not add the MenuAdder
     */
    var menu_adder = new MenuAdder(this);
    this._menu_adder = menu_adder;
    disp_block.append(menu_adder.getElement());

    this.hideControls();

    if (this.hasChildren()){
        this.setChildless(false);
    } else {
        if (this.isEditable()){
            this.setDeletable(true);
            this.setChildless(true);
        }
    }

    //todo: copy state transition event handlers to the EditableText
    //add delete handler and button - if user has privilege to delete
    var me = this;
    this._element.mouseover(function(e){me.focusOnMe(e)});
    this._element.mouseout(function(e){me.startLosingFocusOnMe(e)});
    this.getContent().getElement().mouseover(function(e){me.stopLosingFocusOnMe(e)});
};

/**
 * @private
 * @param {Function} on_delete callback
 * starts deleting the menu item with attempting to
 * remove content - potentially entailing an ajax request
 */
MenuItem.prototype.startDeleting = function(on_delete){
    this.getContent().startDeleting(on_delete);
};

/**
 * @private
 * finalizes deletion of the menu item
 * if the item was last on the menu and the menu is not top-level
 * the parent menu item will need to be adjusted to allow
 * creation of a subtree and the parent menu is destroyed
 */
MenuItem.prototype.finishDeleting = function(){
    var menu = this._parent_menu;
    parent_menu.removeMenuItem(me);
    if (menu.isEmpty() && menu.getLevel() > 0){
        var parent_item = this.getParentItem();
        parent_item.setChildless(true);
        menu.dispose();
    }
    me.dispose();
};

/**
 * destroys the menu item
 */
MenuItem.prototype.dispose = function(){
    this.getContent().dispose();
    this._element.remove();
    if (this._more_icon){
        this._more_icon.remove();
    }
    if (this._delete_icon){
        this._delete_icon.dispose();
    }
    if (this._menu_adder){
        this._menu_adder.dispose();
    }
    if (this._child_menu){
        this._child_menu.dispose();
    }
};

/**
 * stops closing of the parent menu, if closure is scheduled
 * closes all child menues of the parent menu
 * opens own child menu, if exists
 */
MenuItem.prototype.focusOnMe = function(e){
    var parent_menu = this._parent_menu;
    parent_menu.stopClosingAll();
    parent_menu.closeChildren();
    parent_menu.setActiveItem(this);
    this.openChildMenu();
    e.stopImmediatePropagation();
};

/** sets the timer to close child menues */
MenuItem.prototype.startLosingFocusOnMe = function(e){
    this._parent_menu.startClosing();
    this.deactivate();
    e.stopImmediatePropagation();
};

/** cancels the timer for closing the child menues */
MenuItem.prototype.stopLosingFocusOnMe = function(e){
    this._parent_menu.stopClosingAll();
};

/** opens the child menu if it is there */
MenuItem.prototype.openChildMenu = function(){
    if (this._child_menu){
        this._child_menu.open();
    }
};

/** closes child menu, if exists */
MenuItem.prototype.closeChildMenu = function(){
    if (this._child_menu){
        this._child_menu.close();
    }
}

MenuItem.prototype.activate = function(){
    this._element.addClass('ab-active-menu-item');
};

MenuItem.prototype.deactivate = function(){
    this._element.removeClass('ab-active-menu-item');
};

/**
 * Initializes child_menus and treir DOM's
 * @return {?Menu}
 */
MenuItem.prototype.buildSubtree = function(){
    var child_menu = this._parent_menu.createChild();
    child_menu.setData(this._children_data);
    this.getElement().append(child_menu.getElement());

    child_menu.setParentContentItem(this.getContent());

    this._child_menu = child_menu;
    return child_menu;
};

/**
 * @constructor
 * @param {Menu} parent_menu - owner of the adder instance
 * creates a menu item widget
 */
var MenuItemAdder = function(parent_menu){
    Widget.call(this);
    /**
     * @private
     * @type {string}
     * the link message
     */
    this._text = gettext('Add new item');
    /**
     * @private
     * @type {Menu}
     */
    this._parent_menu = parent_menu;
};
inherits(MenuItemAdder, Widget);
/**
 * @param {Function} func the content item creator function
 */
MenuItemAdder.prototype.setContentItemCreator = function(func){
    this._content_item_creator = func;
};
/**
 * @param {string} text - link text
 */
MenuItemAdder.prototype.setText = function(text){
    this._text = text;
};
/** @private */
MenuItemAdder.prototype.createDom = function(){
    var li = this.makeElement('li');
    var link = this.makeElement('a');
    link.html(this._text);
    this._button = link;

    var me = this;
    setupButtonEventHandlers(link, function(){ me.startAddingItem() });

    li.append(link);
    this._element = li;

    /* similar event handlers to MenuItem - to prevent
    premature closing of the menu */
    this._element.mouseover(function(e){ me.focusOnMe(e) });
    this._element.mouseout(function(e){ me.startLosingFocusOnMe(e) });
    link.mouseover(function(e){ me.stopLosingFocusOnMe(e) });
};
/**
 * stops closing of the parent menu, if closure is scheduled
 * closes all child menues of the parent menu
 * opens own child menu, if exists
 */
MenuItemAdder.prototype.focusOnMe = function(e){
    var parent_menu = this._parent_menu;
    parent_menu.stopClosingAll();
    //parent_menu.setActiveItem(this);//should be null
    e.stopImmediatePropagation();
};

/** sets the timer to close child menues */
MenuItemAdder.prototype.startLosingFocusOnMe = function(e){
    this._parent_menu.startClosing();
    e.stopImmediatePropagation();
};

/** cancels the timer for closing the child menues */
MenuItemAdder.prototype.stopLosingFocusOnMe = function(e){
    this._parent_menu.stopClosingAll();
};

MenuItemAdder.prototype.activate = function(){
    this._link.click();
};
/**
 * @private
 */
MenuItemAdder.prototype.startAddingItem = function(){
    if (this.getState() === 'WORKING'){
        return;
    }
    //create the item
    var menu_item = new MenuItem(this._parent_menu);
    var content = this._content_item_creator();
    var me = this;
    content.backupStateTransitionEventHandlers();
    content.setStateTransitionEventHandlers({
        DISPLAY: function(){ me.setState('IDLE'); }
    });
    menu_item.setContent(content);

    this._parent_menu.addMenuItem(menu_item);

    this.setState('WORKING');
};

/**
 * @constructor
 * a menu widget, which may be nested
 * elements of the menu are instances of
 * ``MenuItem``
 * the menu may be editable in place
 */
var Menu = function(){
    Widget.call(this);
    /**
     * @private
     * @type {?MenuItem}
     */
    this._active_item = null;
    /**
     * @private
     * @type {MenuData} menu items
     */
    this._children = [];
    /**
     * @private
     * @type {?MenuItemAdder}
     */
    this._menu_item_adder = null;
    /**
     * @private
     * @type {Function}
     */
    this._content_item_constructor = null;
    /**
     * @private
     * @type {number}
     */
    this._close_delay = 350;//ms before the menues close
    /**
     * @private
     * @type {?Menu}
     */
    this._parent_menu = null;
    /** 
     * @private
     * @type {Array.<Menu>}
     * stack of open menues, with leaf being the last item
     * and root - the first item
     */
    this._menu_stack = [];

    /**
     * @private
     * @type {boolean}
     */
    this._is_editable = true;

    /**
     * @private
     * @type {boolean}
     */
    this._is_frozen = false;
};
inherits(Menu, Widget);

/**
 * @private
 * @return {boolean}
 */
Menu.prototype.isRoot = function(){
    return (this._parent_menu === null);
};

/**
 * @param {boolean} is_editable
 */
Menu.prototype.setEditable = function(is_editable){
    this._is_editable = is_editable;
};
/**
 * @return {boolean}
 */
Menu.prototype.isEditable = function(){
    return this._is_editable;
};

/**
 * @param {MenuData} data the category tree data
 */
Menu.prototype.setData = function(data){
    /**
     * @private
     * @type {MenuData}
     */
    this._data = data;
};

/**
 * @param {Function} creator
 */
Menu.prototype.setContentItemCreator = function(creator){
    this._content_item_creator = creator;
};

/**
 * @param {MenuData}
 * @return {Object} menu item content object
 */
Menu.prototype.createContentItem = function(data){
    return this._content_item_creator(data);
};

/**
 * creates the menu item,
 * sets its content and builds the child_menu
 * if there any child elements 
 * in the data
 * @param {MenuItemData} data
 * @return {MenuItem}
 */
Menu.prototype.createMenuItem = function(data){
    var menu_item = new MenuItem(this, data);

    //set menu item content
    var item_content = this.createContentItem(data);
    item_content.setEditable(this.isEditable());
    item_content.copyStateTransitionEventHandlersFrom(this);

    menu_item.setContent(item_content);

    //build child menu
    if (data['children'].length > 0){
        var child_menu = menu_item.buildSubtree();
    }
    return menu_item;
};

/**
 * @param {Object} parent_content
 */
Menu.prototype.setParentContentItem = function(parent_content){
    this._parent_content_item = parent_content;
    $.each(this._children, function(idx, menu_item){
        menu_item.getContent().setParent(parent_content);
    });
};
/**
 * @return {Object}
 */
Menu.prototype.getParentContentItem = function(){
    return this._parent_content_item;
};

/**
 * @return {MenuItemAdder}
 */
Menu.prototype.getMenuItemAdder = function(){
    return this._menu_item_adder;
};

/**
 * adds "content" item to the menu
 * @param {MenuItem} menu_item
 */
Menu.prototype.addMenuItem = function(menu_item){
    var item_element = menu_item.getElement();
    if (this._menu_item_adder){
        this._menu_item_adder.getElement().before(item_element);
    } else {
        this._element.append(item_element);
    }
    this._children.push(menu_item);
};

/**
 * @param {MenuItem} menu_item
 * removes menu item from the menu
 */
Menu.prototype.removeMenuItem = function(menu_item){
    for (var i = 0; i<this._children_length; i--){
        if (menu_item === this._children[i]){
            this._children.splice(i, 1);
            return;
        }
    }
};

Menu.prototype.createMenuItemAdder = function(){
    var item_adder = new MenuItemAdder(this);
    var me = this;
    item_adder.setContentItemCreator(function(){
        var item = me.createContentItem();
        item.setEditable(true);//we do not call this otherwise
        item.setState('EDIT')
        item.setParent(me.getParentContentItem());
        return item;
    });
    return item_adder;
};

/**
 * decorates any element by replacing its content
 * with the nested <ul> HTML code representing the 
 * category tree
 * @param {Object} element - parent jQuery object
 * @param {boolean?} is_root - true if it must be root menu
 * root menu opens right below the element, others - to the right
 */
Menu.prototype.decorate = function(element, is_root){
    if (this._data === null){
        return;
    }
    this._is_root = is_root;
    this._root_element = element;//the button which opens the menu
    this._root_element.after(this.getElement());//calls this.createDom()
    var me = this;
    this._root_element.mouseover(function(){
        me.open()
    });
    this._root_element.mouseout(function(){
        me.startClosing();
    });
};

/**
 * @private
 * called before an item starts to become edited
 */
Menu.prototype.stopEditingAllItems = function(){
    var menu_stack = this.getMenuStack();
    $.each(menu_stack, function(idx, open_menu){
        $.each(open_menu._children, function(idx, menu_item){
            menu_item.setState('DISPLAY');
        });
    });
};

/**
 * @private
 * sets transition event handlers to the menu
 * supported states are EDIT, DISPLAY and ADD
 */
Menu.prototype.initStateTransitionEventHandlers = function(){
    var me = this;
    //need to prevent editing more than one entry at a time
    this.setStateTransitionEventHandlers({
        EDIT: function(){
            me.stopEditingAllItems();
            me.freeze();
        },
        DISPLAY: function(){
            me.unfreeze();
        }
    });
};

/**
 * freezes the menu - so it does not collapse
 * until "unfrozen"
 */
Menu.prototype.freeze = function(){
    //use a private attribute...
    this.getRootMenu()._is_frozen = true;
};
Menu.prototype.unfreeze = function(){
    this.getRootMenu()._is_frozen = false;
};

/**
 * @private
 * a hack allowing top level content elements
 * have parent
 */
Menu.prototype.createRootContentElement = function(){
}

/**
 * @return {boolean}
 */
Menu.prototype.isFrozen = function(){
    return this.getRootMenu()._is_frozen;
};

/**
 * creates the nested HTML <ul> which represents
 * the category tree. 
 */
Menu.prototype.createDom = function(){
    this._element = this.makeElement('ul');
    this._element.css('position', 'absolute').hide();

    this.initStateTransitionEventHandlers();

    var me = this;
    $.each(this._data, function(idx, child_node){
        //create the category (and any children within) and add it to the tree
        var menu_item = me.createMenuItem(child_node);
        me.addMenuItem(menu_item);
    });
    if (this.isEditable()){
        var item_adder = this.createMenuItemAdder();
        this._element.append(item_adder.getElement());
        this._menu_item_adder = item_adder;
    }
    this.createRootContentElement();
};

/**
 * Opens the menu
 */
Menu.prototype.open = function(){
    if (this.isFrozen()){
        return;
    }
    var position = {my: 'left top'};
    if (this.isRoot()){
        position['at'] = 'left bottom';
        position['of'] = this._root_element;
    } else {
        position['at'] = 'right top';
        position['of'] = this._parent_menu.getActiveItem().getElement();
    }
    this._element.show();
    this._element.position(position);
    var menu_stack = this.getMenuStack();
    menu_stack.push(this);

};

/**
 * @return {MenuItem} 
 * currently active menu item
 */
Menu.prototype.getActiveItem = function(){
    return this._active_item;
};

/**
 * @param {MenuItem} menu_item
 */
Menu.prototype.setActiveItem = function(menu_item){
    if (this.isFrozen()){
        return;
    }
    this._active_item = menu_item;
    menu_item.activate();
};

/**
 * starts a timer to close all the menues
 * in the tree
 */
Menu.prototype.startClosing = function(){
    if (this.isFrozen()){
        return;
    }
    var me = this;
    var timer = setTimeout(
                    function(){me.closeAll()},
                    me._close_delay
                );
    this.setGlobalCloseTimer(timer);
};

/**
 * @return {Array.<Menu>}
 * returns the stack of open menues
 */
Menu.prototype.getMenuStack = function(){
    var root = this.getRootMenu();
    return root._menu_stack;
};

/**
 * @private
 * @param {number} timer
 * sets the global menu close timer
 */
Menu.prototype.setGlobalCloseTimer = function(timer){
    var root = this.getRootMenu();
    root.setCloseTimer(timer);
};

/**
 * @private
 * @return {number} the timer
 */
Menu.prototype.getGlobalCloseTimer = function(){
    return this.getRootMenu().getCloseTimer();
};

/**
 * @private
 * @return {Menu}
 * returns the top level menu
 */
Menu.prototype.getRootMenu = function(){
    if (this.isRoot()){
        return this;
    } else {
        return this.getParentMenu().getRootMenu();
    }
};

/**
 * @private
 * @return {Menu}
 */
Menu.prototype.getParentMenu = function(){
    return this._parent_menu;
};

/**
 * @private
 * @param {number} timer
 */
Menu.prototype.setCloseTimer = function(timer){
    this._close_timer = timer;
};

/**
 * @private
 * @return {number} timer
 */
Menu.prototype.getCloseTimer = function(){
    return this._close_timer;
};

/**
 * closes all menues immediately
 */
Menu.prototype.closeAll = function(){
    if (this.isFrozen()){
        return;
    }
    var menu_stack = this.getMenuStack();
    for (var i = menu_stack.length - 1; i >= 0; i--){
        menu_stack[i].close();
        menu_stack.pop();
    }
};

/**
 * cancels closure of all menues
 */
Menu.prototype.stopClosingAll = function(){
    var timer = this.getGlobalCloseTimer();
    clearTimeout(timer);
};

/**
 * closes any open child menues
 */
Menu.prototype.closeChildren = function(){
    if (this.isFrozen()){
        return;
    }
    var menu_stack = this.getMenuStack();
    for (var i = menu_stack.length - 1; i >= 0; i--){
        if (menu_stack[i] === this){
            break;
        }
        menu_stack[i].close();
        menu_stack.pop();
    }
};

/**
 * @param {Menu} parent_menu
 */
Menu.prototype.setParent = function(parent_menu){
    this._parent_menu = parent_menu;
};

/**
 * @return {Menu}
 * "bear a child to its own likeness"
 */
Menu.prototype.createChild = function(){
    var child = new Menu();
    child.setContentItemCreator(this._content_item_creator);
    child.setParent(this);
    child.setEditable(this.isEditable());
    return child;
};

/**
 * closes current menu
 * and if menu is editable, sets the state to DISPLAY
 * on all child items
 */
Menu.prototype.close = function(){
    if (this.isFrozen()){
        return;
    }
    this.getElement().hide();
    $.each(this._children, function(idx, menu_item){
        menu_item.setState('DISPLAY');
    });
};
