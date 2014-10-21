var {{variable_name}} = {
    element_id: "{{variable_name}}",
    widgetToggle: function() {
        element = document.getElementById({{variable_name}}.element_id);
        element.style.visibility = (element.style.visibility == "visible") ? "hidden" : "visible";
        if (element.style.visibility == "visible"){
            var focusInIFrame = function() {
                var iframe = document.getElementById({{ variable_name }}.element_id + 'iframe');
                iframe.focus();
            }
            setTimeout(focusInIFrame, 100);
        }
    },
    toHtml: function() {
        var html = {{ variable_name }}.createButton();
        var link = document.createElement('link');
        var protocol = document.location.protocol;

        //widget css
        link.setAttribute("rel", "stylesheet");
        link.setAttribute("href", protocol + '//{{host}}{% url render_ask_widget_css widget.id %}');

        //creating the div
        var motherDiv = document.createElement('div');
        motherDiv.setAttribute("id", {{ variable_name }}.element_id);
        motherDiv.setAttribute('class', 'AskbotAskWidget');
        motherDiv.style.visibility = "hidden";

        var containerDiv = document.createElement('div');
        containerDiv.setAttribute('class', 'AskbotWidgetContainer');
        motherDiv.appendChild(containerDiv);

        {% if widget.outer_style %}
        var outerStyle = document.createElement('style');
        outerStyle.setAttribute('type', 'text/css');
        outerStyle.innerText = {{widget.outer_style|replace('\r\n', ' ')|replace('\n', ' ')|as_json}};
        motherDiv.appendChild(outerStyle);
        {% endif %}

        var closeButton = document.createElement('a');
        closeButton.setAttribute('href', '#');
        closeButton.setAttribute('onClick', '{{variable_name}}.widgetToggle();');
        closeButton.setAttribute('class', 'AskbotClosePopup');
        closeButton.innerHTML= 'x';

        containerDiv.appendChild(closeButton);

        var iframe = document.createElement('iframe');
        iframe.setAttribute('id', {{ variable_name }}.element_id + 'iframe');
        iframe.setAttribute('class', 'AskbotAskWidgetIFrame');
        iframe.setAttribute('frameBorder', '0');
        iframe.setAttribute('src', protocol + '//{{host}}{% url ask_by_widget widget.id %}');

        containerDiv.appendChild(iframe);

        var body = document.getElementsByTagName('body')[0];
        if (body){
            body.appendChild(link);
            body.appendChild(motherDiv);
        }
    },
    createButton: function() {
        var label="{{ widget.title }}"; //TODO: add to the model
        var buttonDiv = document.createElement('div');
        buttonDiv.setAttribute('id', "AskbotAskButton" + '{{ widget.id }}');
        buttonDiv.setAttribute('class', 'AskbotWidget');

        var closeButton = document.createElement('input');
        closeButton.setAttribute('onClick', '{{variable_name}}.widgetToggle();');
        closeButton.setAttribute('type', 'button');
        closeButton.value = label;

        buttonDiv.appendChild(closeButton);
        return buttonDiv;
    }
};

var askbot = askbot || {};
askbot['widgets'] = askbot['widgets'] || {};

if (askbot['widgets']['{{ variable_name }}'] === undefined) {
    var previous_function_{{ variable_name }} = window.onload;
    var onload_functions = function(){
    if (previous_function_{{ variable_name }}){
        previous_function_{{ variable_name }}();
    }
    {{variable_name}}.toHtml();
    }
    window.onload = onload_functions;
    askbot['widgets']['{{ variable_name }}'] = {{ variable_name }};
}


document.write({{variable_name}}.createButton().outerHTML);
