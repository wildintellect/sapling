import os

from django.test import TestCase
from django.db import models
from django.core import exceptions

from ckeditor.models import XHTMLField
from ckeditor.models import XMLField
from ckeditor.models import HTML5Field
from ckeditor.models import HTML5FragmentField
from ckeditor.widgets import CKEditor
import xssattacks


class XHTMLModel(models.Model):
    html = XHTMLField()


class HTML5Model(models.Model):
    html = HTML5Field()


class HTML5FragmentModel(models.Model):
    html = HTML5FragmentField()


class RestrictedHTML5FragmentModel(models.Model):
    html = HTML5FragmentField(allowed_elements=['a'])


class XHTMLFieldTest(TestCase):
    def test_html_schema_set(self):
        html = XHTMLField()
        self.assertTrue(isinstance(html, XMLField))
        self.assertEquals(html.schema_path, XHTMLField.schema_path)

    def test_html_schema_exists(self):
        self.assertTrue(os.path.exists(XHTMLField.schema_path))

    def test_valid_html(self):
        m = XHTMLModel()
        m.html = ('<html><head><title>Lorem</title></head>'
                  '<body>Ipsum</body></html>')
        m.clean_fields()

    def test_invalid_html(self):
        m = XHTMLModel()
        m.html = 'invalid html'
        self.assertRaises(exceptions.ValidationError, m.clean_fields)


class HTML5FieldTest(TestCase):
    def test_sanitize(self):
        m = HTML5Model()
        m.html = '<html><head/><body><script/></body></html>'
        m.clean_fields()
        self.assertEquals(m.html,
            ('<html><head/><body>&lt;html&gt;&lt;head/&gt;&lt;body&gt;'
             '&lt;script/&gt;&lt;/body&gt;&lt;/html&gt;</body></html>')
        )


class HTML5FragmentField(TestCase):
    def test_sanitize(self):
        m = HTML5FragmentModel()
        m.html = '<script/>'
        m.clean_fields()
        self.assertEquals(m.html, '&lt;script/&gt;')

    def test_allowed_elements(self):
        m = RestrictedHTML5FragmentModel()
        m.html = '<p><a href="#top">This link</a> takes you to the top</p>'
        m.clean_fields()
        self.assertEquals(m.html, ('&lt;p&gt;<a href="#top">This link</a>'
                                   ' takes you to the top&lt;/p&gt;'))


class CKEditorWidgetTest(TestCase):
    def test_default_config(self):
        ck = CKEditor()
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\n'
                    "CKEDITOR.replace('id_ck');\n"
                    '-->\n'
                    '</script>')
        self.assertEqual(rendered, expected)

    def test_config_based_on_allowed_tags(self):
        ck = CKEditor(allowed_tags=['a'])
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\n'
                    "CKEDITOR.replace('id_ck', "
                    '{"toolbar": [["Link", "Unlink", "Anchor"]]});\n'
                    '-->\n'
                    '</script>')
        self.assertEqual(rendered, expected)

    def test_custom_config(self):
        ck = CKEditor(ck_config={'extraPlugins': 'myThing'})
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\n'
                    "CKEDITOR.replace('id_ck', "
                    '{"extraPlugins": "myThing"});\n'
                    '-->\n'
                    '</script>')
        self.assertEqual(rendered, expected)


class CustomCKEditor(CKEditor):
    def get_extra_plugins(self):
        plugins = ["myPlugin1", "myPlugin2"]
        return ','.join(plugins)


class CustomCKEditorTest(TestCase):
    def test_config(self):
        ck = CustomCKEditor()
        rendered = ck.render("ck", "Test")
        expected = ('<textarea rows="10" cols="40" name="ck">Test</textarea>'
                    '<script type="text/javascript">\n'
                    '<!--\n'
                    "CKEDITOR.replace('id_ck', "
                    '{"extraPlugins": "myPlugin1,myPlugin2"});\n'
                    '-->\n'
                    '</script>')
        self.assertEqual(rendered, expected)


class XSSTest(TestCase):
    def test_xss_attacks_xhtml(self):
        for doc in xssattacks.xss_attacks():
            m = XHTMLModel()
            m.html = doc
            print doc
            self.assertRaises(exceptions.ValidationError, m.clean_fields)
