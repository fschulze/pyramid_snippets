from pyramid.exceptions import ConfigurationError
from pyramid.i18n import TranslationStringFactory, get_localizer
from pyramid.interfaces import IRequest, IRouteRequest
from pyramid.request import Request
from pyramid.view import render_view
from zope.interface import Interface, implementedBy, providedBy
import re
import urllib


_ = TranslationStringFactory('pyramid_snippets')


# Regexp based on Wordpress' shortcode implementation
snippet_regexp = re.compile(
    r'\['                            # Opening bracket
    r'(?P<escapeopen>\[?)'           # 1: Optional second opening bracket for escaping snippets: [[tag]]
    r'(?P<name>[\w\d\_-]+)'          # 2: Snippet name
    r'\b'                            # Word boundary
    r'(?P<arguments>'                # 3: Unroll the loop: Inside the opening snippet tag
        r'[^\]\/]*'                  # Not a closing bracket or forward slash
        r'(?:'
            r'\/(?!\])'              # A forward slash not followed by a closing bracket
            r'[^\]\/]*'              # Not a closing bracket or forward slash
        r')*?'
    r')'
    r'(?:'
        r'(?P<selfclosing>\/)'       # 4: Self closing tag ...
        r'\]'                        # ... and closing bracket
    r'|'
        r'\]'                        # Closing bracket
        r'(?:'
            r'(?P<content>'          # 5: Unroll the loop: Optionally, anything between the opening and closing snippet tags
                r'[^\[]*'            # Not an opening bracket
                r'(?:'
                    r'\[(?!\/(?P=name)\])'  # An opening bracket not followed by the closing snippet tag
                    r'[^\[]*'        # Not an opening bracket
                r')*'
            r')'
            r'\[\/(?P=name)\]'       # Closing snippet tag
        r')?'
    r')'
    r'(?P<escapeclose>\]?)')                        # 6: Optional second closing bracket for escaping snippets: [[tag]]


class ISnippet(Interface):
    pass


def render_snippet(context, request, name, arguments):
    snippet_request = Request.blank(
        request.path + '/snippet-%s' % name,
        base_url=request.application_url,
        POST=urllib.urlencode(arguments))
    snippet_request.registry = request.registry
    return render_view(
        context,
        snippet_request,
        'snippet-%s' % name)


def render_snippets(context, request, body):
    localizer = get_localizer(request)

    def sub(match):
        infos = match.groupdict()
        if infos['selfclosing'] is None and infos['content'] is None:
            return '<div class="alert alert-error">{0}</div>'.format(
                localizer.translate(
                    _("Snippet tag '${name}' not closed",
                      mapping=dict(name=infos['name']))))
        if infos['escapeopen'] and infos['escapeclose']:
            return ''.join((
                infos['escapeopen'],
                infos['name'],
                infos['arguments'],
                infos['selfclosing'],
                infos['escapeclose']))
        arguments = {}
        last_key = None
        for arg in infos['arguments'].split(' '):
            if '=' in arg:
                key, value = arg.split('=')
                key = key.strip()
                value = value.strip()
                arguments[key] = value
                last_key = key
            elif last_key is not None:
                arguments[last_key] = "%s %s" % (arguments[last_key], arg)
        arguments['body'] = infos['content']
        result = render_snippet(context, request, infos['name'], arguments)
        if result is None:
            return '<div class="alert alert-error">{0}</div>'.format(
                localizer.translate(
                    _("No snippet with name '${name}' registered.",
                      mapping=dict(name=infos['name']))))
        return result

    return snippet_regexp.sub(sub, body)


def get_snippets(context, request):
    return dict(request.registry.adapters.lookupAll(
        (providedBy(request), providedBy(context)),
        ISnippet))


def add_snippet(self, snippet=None, **kwargs):
    name = kwargs['name']
    del kwargs['name']
    route_name = kwargs.get('route_name')
    request_iface = IRequest
    if route_name is not None:
        request_iface = self.registry.queryUtility(IRouteRequest,
                                                   name=route_name)
        if request_iface is None:
            # route configuration should have already happened in
            # phase 2
            raise ConfigurationError(
                'No route named %s found for view registration' %
                route_name)
    self.registry.registerAdapter(
        snippet,
        (request_iface, implementedBy(kwargs.get('context'))), ISnippet, name)
    self.add_view(view=snippet, name='snippet-%s' % name, **kwargs)


def includeme(config):
    config.add_directive('add_snippet', add_snippet)
