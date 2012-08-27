import htmllib, formatter
import re

def unescape_html(s):
    p = htmllib.HTMLParser(formatter.NullFormatter() )
    # we need to preserve line breaks, nofill makes sure we don't
    # loose them
    p.nofill = True
    p.save_bgn()
    p.feed(s)
    return p.save_end().strip()

LANG_DIALECT_RE = re.compile(r'(?P<lang_code>[\w]{2,13})(?P<dialect>-[\w]{2,8})?(?P<rest>-[\w]*)?')

def to_bcp47(code):
    """
    This is an ugly hack. I should be ashamed, but I'm not.
    Implementing BCP47 will be much more work.
    The idea is to translate from a lang code unilangs supports
    into the bpc47 format. There are cases where this might fail
    (as if the dialect code is not recognized by bcp47). For most cases this should be ok.

    Simple sanity chech:
    assert (unilangs.to_bcp47("en-us"), unilangs.to_bcp47('en'), unilangs.to_bcp47('ug_Arab-cn')) == ('en-US', 'en', 'ug_Arab-CN'
)
    """
    match = LANG_DIALECT_RE.match(code)
    if not match:
         raise ValueError("%s code does not seem to be a valid language code.")

    match_dict = match.groupdict()
    return "%s%s%s" % (match_dict['lang_code'],
                       (match_dict.get('dialect', "") or "").upper(),
                       match_dict.get('rest', '') or "")
