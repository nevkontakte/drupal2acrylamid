__author__ = 'aleks'


def filter_markdownify(post, soup):
    for p in soup.find_all("p"):
        p.append("\n\n")
        p.unwrap()

    for n in range(1, 7):
        tag = "h" + str(n)

        for h in soup.find_all(tag):
            h.insert_before(soup.new_string(("#" * n) + ' '))
            h.append("\n")
            h.unwrap()

    for a in soup.find_all("a"):
        if 'href' not in a:
            continue
        text = u'[{text}]({url})'.format(text=a.string, url=a['href'])
        a.replace_with(soup.new_string(text))

    for b in soup.find_all("b") + soup.find_all("strong"):
        text = u'**%s**' % b.string
        b.replace_with(soup.new_string(text))

    return post, soup
