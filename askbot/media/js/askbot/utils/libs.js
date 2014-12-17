//Search Engine Keyword Highlight with Javascript
//http://scott.yang.id.au/code/se-hilite/
Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["local","q"],["cnprog\\.","q"],["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function (d) {var g=null;var e=new RegExp("");for(var c=0;c<Hilite.search_engines.length;c++) {var f=Hilite.search_engines[c];e.compile("^http://(www\\.)?"+f[0],"i");var b=d.match(e);if(b) {var a;if(isNaN(f[1])) {a=Hilite.decodeReferrerQS(d,f[1])}else{a=b[f[1]+1]}if(a) {a=decodeURIComponent(a);if(f.length>2&&f[2]) {a=decodeURIComponent(a)}a=a.replace(/\'|"/g,"");a=a.split(/[\s,\+\.]+/);return a}break}}return null};Hilite.decodeReferrerQS=function (f,d) {var b=f.indexOf("?");var c;if(b>=0) {var a=new String(f.substring(b+1));b=0;c=0;while((b>=0)&&((c=a.indexOf("=",b))>=0)) {var e,g;e=a.substring(b,c);b=a.indexOf("&",c)+1;if(e==d) {if(b<=0) {return a.substring(c+1)}else{return a.substring(c+1,b-1)}}else{if(b<=0) {return null}}}}return null};Hilite.hiliteElement=function (f,e) {if(!e||f.childNodes.length==0) {return}var c=new Array();for(var b=0;b<e.length;b++) {e[b]=e[b].toLowerCase();if(Hilite.exact) {c.push("\\b"+e[b]+"\\b")}else{c.push(e[b])}}c=new RegExp(c.join("|"),"i");var a={};for(var b=0;b<e.length;b++) {if(Hilite.style_name_suffix) {a[e[b]]=Hilite.style_name+(b+1)}else{a[e[b]]=Hilite.style_name}}var d=function (m) {var j=c.exec(m.data);if(j) {var n=j[0];var i="";var h=m.splitText(j.index);var g=h.splitText(n.length);var l=m.ownerDocument.createElement("SPAN");m.parentNode.replaceChild(l,h);l.className=a[n.toLowerCase()];l.appendChild(h);return l}else{return m}};Hilite.walkElements(f.childNodes[0],1,d)};Hilite.hilite=function () {var a=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var b=null;a=Hilite.decodeReferrer(a);if(a&&((Hilite.elementid&&(b=document.getElementById(Hilite.elementid)))||(b=document.body))) {Hilite.hiliteElement(b,a)}};Hilite.walkElements=function (d,f,e) {var a=/^(script|style|textarea)/i;var c=0;while(d&&f>0) {c++;if(c>=Hilite.max_nodes) {var b=function () {Hilite.walkElements(d,f,e)};setTimeout(b,50);return}if(d.nodeType==1) {if(!a.test(d.tagName)&&d.childNodes.length>0) {d=d.childNodes[0];f++;continue}}else{if(d.nodeType==3) {d=e(d)}}if(d.nextSibling) {d=d.nextSibling}else{while(f>0) {d=d.parentNode;f--;if(d.nextSibling) {d=d.nextSibling;break}}}}};if(Hilite.onload) {if(window.attachEvent) {window.attachEvent("onload",Hilite.hilite)}else{if(window.addEventListener) {window.addEventListener("load",Hilite.hilite,false)}else{var __onload=window.onload;window.onload=function () {Hilite.hilite();__onload()}}}};

if(!this.JSON) {this.JSON={}}(function () {function f(n) {return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function") {Date.prototype.toJSON=function (key) {return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function (key) {return this.valueOf()}}var cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,gap,indent,meta={"\b":"\\b","\t":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},rep;function quote(string) {escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function (a) {var c=meta[a];return typeof c==="string"?c:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+string+'"'}function str(key,holder) {var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function") {value=value.toJSON(key)}if(typeof rep==="function") {value=rep.call(holder,key,value)}switch(typeof value) {case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value) {return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]") {length=value.length;for(i=0;i<length;i+=1) {partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object") {length=rep.length;for(i=0;i<length;i+=1) {k=rep[i];if(typeof k==="string") {v=str(k,value);if(v) {partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value) {if(Object.hasOwnProperty.call(value,k)) {v=str(k,value);if(v) {partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function") {JSON.stringify=function (value,replacer,space) {var i;gap="";indent="";if(typeof space==="number") {for(i=0;i<space;i+=1) {indent+=" "}}else{if(typeof space==="string") {indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")) {throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function") {JSON.parse=function (text,reviver) {var j;function walk(holder,key) {var k,v,value=holder[key];if(value&&typeof value==="object") {for(k in value) {if(Object.hasOwnProperty.call(value,k)) {v=walk(value,k);if(v!==undefined) {value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}text=String(text);cx.lastIndex=0;if(cx.test(text)) {text=text.replace(cx,function (a) {return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,""))) {j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());
//jquery fieldselection
(function () {var a={getSelection:function () {var b=this.jquery?this[0]:this;return(("selectionStart" in b&&function () {var c=b.selectionEnd-b.selectionStart;return{start:b.selectionStart,end:b.selectionEnd,length:c,text:b.value.substr(b.selectionStart,c)}})||(document.selection&&function () {b.focus();var d=document.selection.createRange();if(d==null) {return{start:0,end:b.value.length,length:0}}var c=b.createTextRange();var e=c.duplicate();c.moveToBookmark(d.getBookmark());e.setEndPoint("EndToStart",c);return{start:e.text.length,end:e.text.length+d.text.length,length:d.text.length,text:d.text}})||function () {return{start:0,end:b.value.length,length:0}})()},replaceSelection:function () {var b=this.jquery?this[0]:this;var c=arguments[0]||"";return(("selectionStart" in b&&function () {b.value=b.value.substr(0,b.selectionStart)+c+b.value.substr(b.selectionEnd,b.value.length);return this})||(document.selection&&function () {b.focus();document.selection.createRange().text=c;return this})||function () {b.value+=c;return this})()}};jQuery.each(a,function (b) {jQuery.fn[b]=this})})();
/**
 * AutoCompleter Object, refactored closure style from
 * jQuery autocomplete plugin
 * @param {Object=} options Settings
 * @constructor
 */
var AutoCompleter = function (options) {

    /**
     * Default options for autocomplete plugin
     */
    var defaults = {
        promptText: '',
        autocompleteMultiple: true,
        multipleSeparator: ' ',//a single character
        inputClass: 'acInput',
        loadingClass: 'acLoading',
        resultsClass: 'acResults',
        selectClass: 'acSelect',
        queryParamName: 'q',
        limitParamName: 'limit',
        extraParams: {},
        lineSeparator: '\n',
        cellSeparator: '|',
        minChars: 2,
        maxItemsToShow: 10,
        delay: 400,
        useCache: true,
        maxCacheLength: 10,
        matchSubset: true,
        matchCase: false,
        matchInside: true,
        mustMatch: false,
        preloadData: false,
        selectFirst: false,
        stopCharRegex: /\s+/,
        selectOnly: false,
        formatItem: null,           // TBD
        onItemSelect: false,
        autoFill: false,
        filterResults: true,
        sortResults: true,
        sortFunction: false,
        onNoMatch: false
    };

    /**
     * Options dictionary
     * @type Object
     * @private
     */
    this.options = $.extend({}, defaults, options);

    /**
     * Cached data
     * @type Object
     * @private
     */
    this.cacheData_ = {};

    /**
     * Number of cached data items
     * @type number
     * @private
     */
    this.cacheLength_ = 0;

    /**
     * Class name to mark selected item
     * @type string
     * @private
     */
    this.selectClass_ = 'jquery-autocomplete-selected-item';

    /**
     * Handler to activation timeout
     * @type ?number
     * @private
     */
    this.keyTimeout_ = null;

    /**
     * Last key pressed in the input field (store for behavior)
     * @type ?number
     * @private
     */
    this.lastKeyPressed_ = null;

    /**
     * Last value processed by the autocompleter
     * @type ?string
     * @private
     */
    this.lastProcessedValue_ = null;

    /**
     * Last value selected by the user
     * @type ?string
     * @private
     */
    this.lastSelectedValue_ = null;

    /**
     * Is this autocompleter active?
     * @type boolean
     * @private
     */
    this.active_ = false;

    /**
     * Is it OK to finish on blur?
     * @type boolean
     * @private
     */
    this.finishOnBlur_ = true;

    this._isRunning = false;

    this.options.minChars = parseInt(this.options.minChars, 10);
    if (isNaN(this.options.minChars) || this.options.minChars < 1) {
        this.options.minChars = 2;
    }

    this.options.maxItemsToShow = parseInt(this.options.maxItemsToShow, 10);
    if (isNaN(this.options.maxItemsToShow) || this.options.maxItemsToShow < 1) {
        this.options.maxItemsToShow = 10;
    }

    this.options.maxCacheLength = parseInt(this.options.maxCacheLength, 10);
    if (isNaN(this.options.maxCacheLength) || this.options.maxCacheLength < 1) {
        this.options.maxCacheLength = 10;
    }

    if (this.options['preloadData'] === true) {
        this.fetchRemoteData('', function () {});
    }
};
inherits(AutoCompleter, WrappedElement);

AutoCompleter.prototype.decorate = function (element) {

    /**
     * Init DOM elements repository
     */
    this._element = element;

    /**
     * Switch off the native autocomplete
     */
    this._element.attr('autocomplete', 'off');

    /**
     * Set prompt text
     */
    if (this.options['promptText']) {
        this.setPrompt();
    }

    /**
     * Create DOM element to hold results
     */
    this._results = $('<div></div>').hide();
    if (this.options.resultsClass) {
        this._results.addClass(this.options.resultsClass);
    }
    this._results.css({
        position: 'absolute'
    });
    $('body').append(this._results);

    this.setEventHandlers();
};

AutoCompleter.prototype.setPrompt = function () {
    this._element.val(this.options['promptText']);
    this._element.addClass('prompt');
};

AutoCompleter.prototype.removePrompt = function () {
    if (this._element.hasClass('prompt')) {
        this._element.removeClass('prompt');
        var val = this._element.val();
        if (val === this.options['promptText']) {
            this._element.val('');
        }
    }
};

AutoCompleter.prototype.setEventHandlers = function () {
    /**
     * Shortcut to self
     */
    var self = this;

    /**
     * Attach keyboard monitoring to $elem
     */
    self._element.keydown(function (e) {

        self.removePrompt();

        self.lastKeyPressed_ = e.keyCode;
        switch(self.lastKeyPressed_) {

            case 38: // up
                e.preventDefault();
                if (self.active_) {
                    self.focusPrev();
                } else {
                    self.activate();
                }
                return false;
            break;

            case 40: // down
                e.preventDefault();
                if (self.active_) {
                    self.focusNext();
                } else {
                    self.activate();
                }
                return false;
            break;

            case 9: // tab
            case 13: // return
                if (self.active_) {
                    e.preventDefault();
                    self.selectCurrent();
                    return false;
                }
            break;

            case 27: // escape
                if ($.trim(self._element.val()) === '') {
                    self._element.blur();
                    return false;
                }
                if (self.active_) {
                    e.preventDefault();
                    self.finish();
                    return false;
                }
            break;

            default:
                self.activate();

        }
    });
    self._element.focus(function () {
        self.removePrompt();
    });
    self._element.blur(function () {
        if ($.trim(self._element.val()) === '') {
            self.setPrompt();
            self._results.hide();
            return true;
        }
        if (self.finishOnBlur_) {
            setTimeout(function () { self.finish(); }, 200);
        }
    });
};

AutoCompleter.prototype.position = function () {
    var offset = this._element.offset();
    this._results.css({
        top: offset.top + this._element.outerHeight(),
        left: offset.left
    });
};

AutoCompleter.prototype.cacheRead = function (filter) {
    var filterLength, searchLength, search, maxPos, pos;
    if (this.options.useCache) {
        filter = String(filter);
        filterLength = filter.length;
        if (this.options.matchSubset) {
            searchLength = 1;
        } else {
            searchLength = filterLength;
        }
        while (searchLength <= filterLength) {
            if (this.options.matchInside) {
                maxPos = filterLength - searchLength;
            } else {
                maxPos = 0;
            }
            pos = 0;
            while (pos <= maxPos) {
                search = filter.substr(0, searchLength);
                if (this.cacheData_[search] !== undefined) {
                    return this.cacheData_[search];
                }
                pos++;
            }
            searchLength++;
        }
    }
    return false;
};

AutoCompleter.prototype.cacheWrite = function (filter, data) {
    if (this.options.useCache) {
        if (this.cacheLength_ >= this.options.maxCacheLength) {
            this.cacheFlush();
        }
        filter = String(filter);
        if (this.cacheData_[filter] !== undefined) {
            this.cacheLength_++;
        }
        return this.cacheData_[filter] = data;
    }
    return false;
};

AutoCompleter.prototype.cacheFlush = function () {
    this.cacheData_ = {};
    this.cacheLength_ = 0;
};

AutoCompleter.prototype.callHook = function (hook, data) {
    var f = this.options[hook];
    if (f && $.isfunction (f)) {
        return f(data, this);
    }
    return false;
};

AutoCompleter.prototype.activate = function () {
    var self = this;
    var activateNow = function () {
        self.activateNow();
    };
    var delay = parseInt(this.options.delay, 10);
    if (isNaN(delay) || delay <= 0) {
        delay = 250;
    }
    if (this.keyTimeout_) {
        clearTimeout(this.keyTimeout_);
    }
    this.keyTimeout_ = setTimeout(activateNow, delay);
};

AutoCompleter.prototype.activateNow = function () {
    if (this._isRunning) {
        return;
    }
    var value = this.getValue();
    if (value.length === 0) {
        this.finish();
    }
    if (value !== this.lastProcessedValue_ && value !== this.lastSelectedValue_) {
        if (value.length >= this.options.minChars) {
            this.active_ = true;
            this.lastProcessedValue_ = value;
            this.fetchData(value);
        }
    }
};

AutoCompleter.prototype.setIsRunning = function (isRunning) {
    this._isRunning = isRunning;
};

AutoCompleter.prototype.fetchData = function (value) {
    var self = this;
    this.fetchRemoteData(value, function (remoteData) {
        self.filterAndShowResults(remoteData, value);
    });
};

AutoCompleter.prototype.fetchRemoteData = function (filter, callback) {
    var data = this.cacheRead(filter);
    if (data) {
        callback(data);
    } else {
        var self = this;
        if (this._element) {
            this._element.addClass(this.options.loadingClass);
        }
        var ajaxCallback = function (data) {
            var parsed = false;
            if (data !== false) {
                parsed = self.parseRemoteData(data);
                self.options.data = parsed;//cache data forever - E.F.
                self.cacheWrite(filter, parsed);
            }
            if (self._element) {
                self._element.removeClass(self.options.loadingClass);
            }
            callback(parsed);
        };
        $.ajax({
            url: this.makeUrl(filter),
            success: function (data) {
                ajaxCallback(data);
                self.setIsRunning(false);
                //if query changed - rerun the search immediately
                var newQuery = self.getValue();
                if (newQuery && newQuery !== filter) {
                    self.activateNow();
                }
            },
            error: function () {
                ajaxCallback(false);
                self.setIsRunning(false);
            }
        });
        self.setIsRunning(true);
    }
};

AutoCompleter.prototype.setOption = function (name, value) {
    this.options[name] = value;
};

AutoCompleter.prototype.setExtraParam = function (name, value) {
    var index = $.trim(String(name));
    if (index) {
        if (!this.options.extraParams) {
            this.options.extraParams = {};
        }
        if (this.options.extraParams[index] !== value) {
            this.options.extraParams[index] = value;
            this.cacheFlush();
        }
    }
};

AutoCompleter.prototype.makeUrl = function (param) {
    var self = this;
    var url = this.options.url;
    var params = $.extend({}, this.options.extraParams);
    // If options.queryParamName === false, append query to url
    // instead of using a GET parameter
    if (this.options.queryParamName === false) {
        url += encodeURIComponent(param);
    } else {
        params[this.options.queryParamName] = param;
    }

    if (this.options.limitParamName && this.options.maxItemsToShow) {
        params[this.options.limitParamName] = this.options.maxItemsToShow;
    }

    var urlAppend = [];
    $.each(params, function (index, value) {
        urlAppend.push(self.makeUrlParam(index, value));
    });
    if (urlAppend.length) {
        url += url.indexOf('?') == -1 ? '?' : '&';
        url += urlAppend.join('&');
    }
    return url;
};

AutoCompleter.prototype.makeUrlParam = function (name, value) {
    return String(name) + '=' + encodeURIComponent(value);
};

/**
 * Sanitize CR and LF, then split into lines
 */
AutoCompleter.prototype.splitText = function (text) {
    return String(text).replace(/(\r\n|\r|\n)/g, '\n').split(this.options.lineSeparator);
};

AutoCompleter.prototype.parseRemoteData = function (remoteData) {
    var value, lines, i, j, data;
    var results = [];
    var lines = this.splitText(remoteData);
    for (i = 0; i < lines.length; i++) {
        var line = lines[i].split(this.options.cellSeparator);
        data = [];
        for (j = 0; j < line.length; j++) {
            data.push(unescape(line[j]));
        }
        value = data.shift();
        results.push({ value: unescape(value), data: data });
    }
    return results;
};

AutoCompleter.prototype.filterAndShowResults = function (results, filter) {
    this.showResults(this.filterResults(results, filter), filter);
};

AutoCompleter.prototype.filterResults = function (results, filter) {

    var filtered = [];
    var value, data, i, result, type, include;
    var regex, pattern, testValue;

    for (i = 0; i < results.length; i++) {
        result = results[i];
        type = typeof result;
        if (type === 'string') {
            value = result;
            data = {};
        } else if ($.isArray(result)) {
            value = result[0];
            data = result.slice(1);
        } else if (type === 'object') {
            value = result.value;
            data = result.data;
        }
        value = String(value);
        if (value > '') {
            if (typeof data !== 'object') {
                data = {};
            }
            if (this.options.filterResults) {
                pattern = String(filter);
                testValue = String(value);
                if (!this.options.matchCase) {
                    pattern = pattern.toLowerCase();
                    testValue = testValue.toLowerCase();
                }
                include = testValue.indexOf(pattern);
                if (this.options.matchInside) {
                    include = include > -1;
                } else {
                    include = include === 0;
                }
            } else {
                include = true;
            }
            if (include) {
                filtered.push({ value: value, data: data });
            }
        }
    }

    if (this.options.sortResults) {
        filtered = this.sortResults(filtered, filter);
    }

    if (this.options.maxItemsToShow > 0 && this.options.maxItemsToShow < filtered.length) {
        filtered.length = this.options.maxItemsToShow;
    }

    return filtered;

};

AutoCompleter.prototype.sortResults = function (results, filter) {
    var self = this;
    var sortFunction = this.options.sortFunction;
    if (!$.isfunction (sortFunction)) {
        sortFunction = function (a, b, f) {
            return self.sortValueAlpha(a, b, f);
        };
    }
    results.sort(function (a, b) {
        return sortfunction (a, b, filter);
    });
    return results;
};

AutoCompleter.prototype.sortValueAlpha = function (a, b, filter) {
    a = String(a.value);
    b = String(b.value);
    if (!this.options.matchCase) {
        a = a.toLowerCase();
        b = b.toLowerCase();
    }
    if (a > b) {
        return 1;
    }
    if (a < b) {
        return -1;
    }
    return 0;
};

AutoCompleter.prototype.showResults = function (results, filter) {
    var self = this;
    var $ul = $('<ul></ul>');
    var i, result, $li, extraWidth, first = false, $first = false;
    var numResults = results.length;
    for (i = 0; i < numResults; i++) {
        result = results[i];
        $li = $('<li>' + this.showResult(result.value, result.data) + '</li>');
        $li.data('value', result.value);
        $li.data('data', result.data);
        $li.click(function () {
            var $this = $(this);
            self.selectItem($this);
        }).mousedown(function () {
            self.finishOnBlur_ = false;
        }).mouseup(function () {
            self.finishOnBlur_ = true;
        });
        $ul.append($li);
        if (first === false) {
            first = String(result.value);
            $first = $li;
            $li.addClass(this.options.firstItemClass);
        }
        if (i == numResults - 1) {
            $li.addClass(this.options.lastItemClass);
        }
    }

    // Alway recalculate position before showing since window size or
    // input element location may have changed. This fixes #14
    this.position();

    this._results.html($ul).show();
    extraWidth = this._results.outerWidth() - this._results.width();
    this._results.width(this._element.outerWidth() - extraWidth);
    $('li', this._results).hover(
        function () { self.focusItem(this); },
        function () { /* void */ }
    );
    if (this.autoFill(first, filter)) {
        this.focusItem($first);
    }
};

AutoCompleter.prototype.showResult = function (value, data) {
    if ($.isfunction (this.options.showResult)) {
        return this.options.showResult(value, data);
    } else {
        return value;
    }
};

AutoCompleter.prototype.autoFill = function (value, filter) {
    var lcValue, lcFilter, valueLength, filterLength;
    if (this.options.autoFill && this.lastKeyPressed_ != 8) {
        lcValue = String(value).toLowerCase();
        lcFilter = String(filter).toLowerCase();
        valueLength = value.length;
        filterLength = filter.length;
        if (lcValue.substr(0, filterLength) === lcFilter) {
            this._element.val(value);
            this.selectRange(filterLength, valueLength);
            return true;
        }
    }
    return false;
};

AutoCompleter.prototype.focusNext = function () {
    this.focusMove(+1);
};

AutoCompleter.prototype.focusPrev = function () {
    this.focusMove(-1);
};

AutoCompleter.prototype.focusMove = function (modifier) {
    var i, $items = $('li', this._results);
    modifier = parseInt(modifier, 10);
    for (var i = 0; i < $items.length; i++) {
        if ($($items[i]).hasClass(this.selectClass_)) {
            this.focusItem(i + modifier);
            return;
        }
    }
    this.focusItem(0);
};

AutoCompleter.prototype.focusItem = function (item) {
    var $item, $items = $('li', this._results);
    if ($items.length) {
        $items.removeClass(this.selectClass_).removeClass(this.options.selectClass);
        if (typeof item === 'number') {
            item = parseInt(item, 10);
            if (item < 0) {
                item = 0;
            } else if (item >= $items.length) {
                item = $items.length - 1;
            }
            $item = $($items[item]);
        } else {
            $item = $(item);
        }
        if ($item) {
            $item.addClass(this.selectClass_).addClass(this.options.selectClass);
        }
    }
};

AutoCompleter.prototype.selectCurrent = function () {
    var $item = $('li.' + this.selectClass_, this._results);
    if ($item.length == 1) {
        this.selectItem($item);
    } else {
        this.finish();
    }
};

AutoCompleter.prototype.selectItem = function ($li) {
    var value = $li.data('value');
    var data = $li.data('data');
    var displayValue = this.displayValue(value, data);
    this.lastProcessedValue_ = displayValue;
    this.lastSelectedValue_ = displayValue;

    this.setValue(displayValue);

    this.setCaret(displayValue.length);
    this.callHook('onItemSelect', { value: value, data: data });
    this.finish();
};

/**
 * @return {boolean} true if the symbol matches something that is
 *                   considered content and false otherwise
 * @param {string} symbol - a single char string
 */
AutoCompleter.prototype.isContentChar = function (symbol) {
    if (this.options['stopCharRegex'] && symbol.match(this.options['stopCharRegex'])) {
        return false;
    } else if (symbol === this.options['multipleSeparator']) {
        return false;
    } else {
        return true;
    }
};

/**
 * takes value from the input box
 * and saves _selection_start and _selection_end coordinates
 * respects settings autocompleteMultiple and
 * multipleSeparator
 * @return {string} the current word in the
 * autocompletable word
 */
AutoCompleter.prototype.getValue = function () {
    if (this._element === undefined) {
        return '';
    }
    var sel = this._element.getSelection();
    var text = this._element.val();
    var pos = sel.start;//estimated start
    //find real start
    var start = pos;
    for (cpos = pos; cpos >= 0; cpos = cpos - 1) {
        if (cpos === text.length) {
            continue;
        }
        var symbol = text.charAt(cpos);
        if (!this.isContentChar(symbol)) {
            break;
        }
        start = cpos;
    }
    //find real end
    var end = pos;
    for (cpos = pos; cpos < text.length; cpos = cpos + 1) {
        if (cpos === 0) {
            continue;
        }
        var symbol = text.charAt(cpos);
        if (!this.isContentChar(symbol)) {
            break;
        }
        end = cpos;
    }
    this._selection_start = start;
    this._selection_end = end;
    return text.substring(start, end);
}

/**
 * sets value of the input box
 * by replacing the previous selection
 * with the value from the autocompleter
 */
AutoCompleter.prototype.setValue = function (val) {
    var prefix = this._element.val().substring(0, this._selection_start);
    var postfix = this._element.val().substring(this._selection_end + 1);
    this._element.val(prefix + val + postfix);
};

AutoCompleter.prototype.displayValue = function (value, data) {
    if ($.isfunction (this.options.displayValue)) {
        return this.options.displayValue(value, data);
    } else {
        return value;
    }
};

AutoCompleter.prototype.clear = function () {
    this._element.val('');
    this._results.hide();
    this.lastKeyPressed_ = null;
    this.lastProcessedValue_ = null;
    if (this._keyTimeout_) {
        clearTimeout(this._keyTimeout);
    }
    this._active = false;
};

AutoCompleter.prototype.finish = function () {
    if (this.keyTimeout_) {
        clearTimeout(this.keyTimeout_);
    }
    if (this._element.val() !== this.lastSelectedValue_) {
        if (this.options.mustMatch) {
            this._element.val('');
        }
        this.callHook('onNoMatch');
    }
    this._results.hide();
    this.lastKeyPressed_ = null;
    this.lastProcessedValue_ = null;
    if (this.active_) {
        this.callHook('onFinish');
    }
    this.active_ = false;
};

AutoCompleter.prototype.selectRange = function (start, end) {
    var input = this._element.get(0);
    if (input.setSelectionRange) {
        input.focus();
        input.setSelectionRange(start, end);
    } else if (this.createTextRange) {
        var range = this.createTextRange();
        range.collapse(true);
        range.moveEnd('character', end);
        range.moveStart('character', start);
        range.select();
    }
};

AutoCompleter.prototype.setCaret = function (pos) {
    this.selectRange(pos, pos);
};

//(function ($) {function isRGBACapable() {var $script=$("script:first"),color=$script.css("color"),result=false;if(/^rgba/.test(color)) {result=true}else{try{result=(color!=$script.css("color","rgba(0, 0, 0, 0.5)").css("color"));$script.css("color",color)}catch(e) {}}return result}$.extend(true,$,{support:{rgba:isRGBACapable()}});var properties=["color","backgroundColor","borderBottomColor","borderLeftColor","borderRightColor","borderTopColor","outlineColor"];$.each(properties,function (i,property) {$.fx.step[property]=function (fx) {if(!fx.init) {fx.begin=parseColor($(fx.elem).css(property));fx.end=parseColor(fx.end);fx.init=true}fx.elem.style[property]=calculateColor(fx.begin,fx.end,fx.pos)}});$.fx.step.borderColor=function (fx) {if(!fx.init) {fx.end=parseColor(fx.end)}var borders=properties.slice(2,6);$.each(borders,function (i,property) {if(!fx.init) {fx[property]={begin:parseColor($(fx.elem).css(property))}}fx.elem.style[property]=calculateColor(fx[property].begin,fx.end,fx.pos)});fx.init=true};function calculateColor(begin,end,pos) {var color="rgb"+($.support.rgba?"a":"")+"("+parseInt((begin[0]+pos*(end[0]-begin[0])),10)+","+parseInt((begin[1]+pos*(end[1]-begin[1])),10)+","+parseInt((begin[2]+pos*(end[2]-begin[2])),10);if($.support.rgba) {color+=","+(begin&&end?parseFloat(begin[3]+pos*(end[3]-begin[3])):1)}color+=")";return color}function parseColor(color) {var match,triplet;if(match=/#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})/.exec(color)) {triplet=[parseInt(match[1],16),parseInt(match[2],16),parseInt(match[3],16),1]}else{if(match=/#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])/.exec(color)) {triplet=[parseInt(match[1],16)*17,parseInt(match[2],16)*17,parseInt(match[3],16)*17,1]}else{if(match=/rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(color)) {triplet=[parseInt(match[1]),parseInt(match[2]),parseInt(match[3]),1]}else{if(match=/rgba\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9\.]*)\s*\)/.exec(color)) {triplet=[parseInt(match[1],10),parseInt(match[2],10),parseInt(match[3],10),parseFloat(match[4])]}else{if(color=="transparent") {triplet=[0,0,0,0]}}}}}return triplet}})(jQuery);

/**
 * Timeago is a jQuery plugin that makes it easy to support automatically
 * updating fuzzy timestamps (e.g. "4 minutes ago" or "about 1 day ago").
 *
 * @name timeago
 * @version 0.11.1
 * @requires jQuery v1.2.3+
 * @author Ryan McGeary
 * @license MIT License - http://www.opensource.org/licenses/mit-license.php
 *
 * For usage and examples, visit:
 * http://timeago.yarp.com/
 *
 * Copyright (c) 2008-2011, Ryan McGeary (ryanonjavascript -[at]- mcgeary [*dot*] org)
 */
(function ($) {
  $.timeago = function (timestamp) {
    if (timestamp instanceof Date) {
      return inWords(timestamp);
    } else if (typeof timestamp === "string") {
      return inWords($.timeago.parse(timestamp));
    } else {
      return inWords($.timeago.datetime(timestamp));
    }
  };
  var $t = $.timeago;

  $.extend($.timeago, {
    settings: {
      refreshMillis: 60000,
      allowFuture: false,
      strings: {
        prefixAgo: null,
        prefixFromNow: null,
        suffixAgo: gettext("ago"),
        suffixFromNow: gettext("from now"),
        seconds: gettext("just now"),
        minute: gettext("about a minute"),
        minutes: gettext("%d min"),
        hour: gettext("about an hour"),
        hours: gettext("%d h"),
        day: gettext("yesterday"),
        days: gettext("%d days"),
        month: gettext("about a month"),
        months: gettext("%d months"),
        year: gettext("about a year"),
        years: gettext("%d years"),
        wordSeparator: " ",
        numbers: []
      }
    },
    inWords: function (distanceMillis) {
      var $l = this.settings.strings;
      var prefix = $l.prefixAgo;
      var suffix = $l.suffixAgo;
      if (this.settings.allowFuture) {
        if (distanceMillis < 0) {
          prefix = $l.prefixFromNow;
          suffix = $l.suffixFromNow;
        }
      }

      var seconds = Math.abs(distanceMillis) / 1000;
      var minutes = seconds / 60;
      var hours = minutes / 60;
      var days = hours / 24;
      var years = days / 365;

      function substitute(stringOrFunction, number) {
        var string = $.isfunction (stringOrFunction) ? stringOrfunction (number, distanceMillis) : stringOrFunction;
        var value = ($l.numbers && $l.numbers[number]) || number;
        return string.replace(/%d/i, value);
      }

      var words = seconds < 45 && substitute($l.seconds, Math.round(seconds)) ||
        seconds < 90 && substitute($l.minute, 1) ||
        minutes < 45 && substitute($l.minutes, Math.round(minutes)) ||
        minutes < 90 && substitute($l.hour, 1) ||
        hours < 24 && substitute($l.hours, Math.round(hours)) ||
        hours < 42 && substitute($l.day, 1) ||
        days < 30 && substitute($l.days, Math.round(days)) ||
        days < 45 && substitute($l.month, 1) ||
        days < 365 && substitute($l.months, Math.round(days / 30)) ||
        years < 1.5 && substitute($l.year, 1) ||
        substitute($l.years, Math.round(years));

      var separator = $l.wordSeparator === undefined ?  " " : $l.wordSeparator;
      return $.trim([prefix, words, suffix].join(separator));
    },
    parse: function (iso8601) {
      var s = $.trim(iso8601);
      s = s.replace(/\.\d\d\d+/,""); // remove milliseconds
      s = s.replace(/-/,"/").replace(/-/,"/");
      s = s.replace(/T/," ").replace(/Z/," UTC");
      s = s.replace(/([\+\-]\d\d)\:?(\d\d)/," $1$2"); // -04:00 -> -0400
      return new Date(s);
    },
    datetime: function (elem) {
      // jQuery's `is()` doesn't play well with HTML5 in IE
      var isTime = $(elem).get(0).tagName.toLowerCase() === "time"; // $(elem).is("time");
      var iso8601 = isTime ? $(elem).attr("datetime") : $(elem).attr("title");
      return $t.parse(iso8601);
    }
  });

  $.fn.timeago = function () {
    var self = this;
    self.each(refresh);

    var $s = $t.settings;
    if ($s.refreshMillis > 0) {
      setInterval(function () { self.each(refresh); }, $s.refreshMillis);
    }
    return self;
  };

  function refresh() {
    var data = prepareData(this);
    if (!isNaN(data.datetime)) {
      $(this).text(inWords(data.datetime));
    }
    return this;
  }

  function prepareData(element) {
    element = $(element);
    if (!element.data("timeago")) {
      element.data("timeago", { datetime: $t.datetime(element) });
      var text = $.trim(element.text());
      if (text.length > 0) {
        element.attr("title", text);
      }
    }
    return element.data("timeago");
  }

  function inWords(date) {
    var distanceMillis = distance(date);
    var seconds = Math.abs(distanceMillis) / 1000;
    var minutes = seconds / 60;
    var hours = minutes / 60;
    var days = hours / 24;
    var years = days / 365;
    var months = [
        gettext('Jan'),
        gettext('Feb'),
        gettext('Mar'),
        gettext('Apr'),
        gettext('May'),
        gettext('Jun'),
        gettext('Jul'),
        gettext('Aug'),
        gettext('Sep'),
        gettext('Oct'),
        gettext('Nov'),
        gettext('Dec')
    ];
    //todo: rewrite this in javascript
    if (days > 2) {
        var month_date = months[date.getMonth()] + ' ' + date.getDate()
        if (years == 0) {
            //how to do this in js???
            return month_date;
        } else {
            return month_date + ' ' + "'" + date.getYear() % 20;
        }
    } else if (days == 2) {
        return gettext('2 days ago')
    } else if (days == 1) {
        return gettext('yesterday')
    } else if (minutes >= 60) {
        var wholeHours = Math.floor(hours);
        return interpolate(
                    ngettext(
                        '%s hour ago',
                        '%s hours ago',
                        wholeHours
                    ),
                    [wholeHours,]
                )
    } else if (seconds > 90) {
        var wholeMinutes = Math.floor(minutes);
        return interpolate(
                    ngettext(
                        '%s min ago',
                        '%s mins ago',
                        wholeMinutes
                    ),
                    [wholeMinutes,]
                )
    } else {
        return gettext('just now')
    }
  }

  function distance(date) {
    return (new Date() - date);
  }

  // fix for IE6 suckage
  document.createElement("abbr");
  document.createElement("time");
}(jQuery));
