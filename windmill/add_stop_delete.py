from windmill.authoring import WindmillTestClient

def test():
    client = WindmillTestClient(__name__)

    client.click(name=u'name')
    client.type(text=u'adding activity', name=u'name')
    client.click(xpath=u"//form[@id='add_activity']/input[2]")
    client.waits.forElement(link=u'Stop', timeout=u'')
    client.asserts.assertText(xpath=u"//td", validator=u'adding activity')
    client.click(link=u'Stop')
    client.waits.forElement(xpath=u"//a[@href='/delete']", timeout=u'')
    client.click(link=u"Delete")
    client.waits.forNotElement(xpath=u'//td', timeout=u'')
    client.asserts.assertNotNode(xpath=u'//td')
