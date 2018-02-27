from lektor.pluginsystem import Plugin
import uuid
from lektor.utils import slugify
from markupsafe import Markup
from collections import namedtuple, Counter


TocEntry = namedtuple('TocEntry', ['level', 'anchor', 'title', 'children'])


def unique_anchor(slug_counter, raw):
    """ Return a unique anchor """
    slug = slugify(raw)
    slug_counter[slug] += 1
    if slug_counter[slug] > 1:
        return '{}~{}'.format(slug, slug_counter[slug])
    return slug
  

class MarkdownHeaderAnchorsPlugin(Plugin):
    name = 'Markdown Header Anchors'
    description = 'Adds anchors to markdown headers.'

    def on_markdown_config(self, config, **extra):
        class HeaderAnchorMixin(object):
            def header(renderer, text, level, raw):
                if self.get_config().get('anchor-type') == "random":
                    anchor = uuid.uuid4().hex[:6]
                else:
                    anchor = unique_anchor(renderer.meta['anchor_slug_counter'], raw)
                renderer.meta['toc'].append(TocEntry(level, anchor, Markup(text), []))
                return '<h%d id="%s">%s</h%d>' % (level, anchor, text, level)
        config.renderer_mixins.append(HeaderAnchorMixin)

    def on_markdown_meta_init(self, meta, **extra):
        meta['toc'] = []
        meta['anchor_slug_counter'] = Counter()

    def on_markdown_meta_postprocess(self, meta, **extra):
        # sentinel node, will not be removed, simplifes operations
        stack = [TocEntry(-1, None, None, [])]

        for entry in meta['toc']:
            while stack[-1].level >= entry.level:
                stack.pop()
            stack[-1].children.append(entry)
            stack.append(entry)

        meta['toc'] = stack[0].children
