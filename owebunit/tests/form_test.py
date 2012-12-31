import owebunit
import bottle
from owebunit.tests import utils

app = bottle.Bottle()

@app.route('/one-form')
def one_form():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form action='/there' method='post'>
        <input type='text' name='textf' value='textv' />
        <input type='submit' value='Go' />
        <button name='foo' />
    </form>
</body>
</html>
'''

@app.route('/no-attribute-form')
def no_attribute_form():
    return '''
<!doctype html>
<html>
<head></head>
<body>
    <form>
        <input type='text' name='textf' value='textv' />
        <input type='submit' value='Go' />
        <button name='foo' />
    </form>
</body>
</html>
'''

utils.start_bottle_server(app, 8043)

@owebunit.config(host='localhost', port=8043)
class FormTestCase(owebunit.WebTestCase):
    def test_form_parsing(self):
        self.get('/one-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('/there', form.action)
        self.assertEqual('/there', form.computed_action)
        self.assertEqual('post', form.method)
        self.assertEqual('post', form.computed_method)
    
    def test_no_attribute_form_parsing(self):
        self.get('/no-attribute-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertIs(form.action, None)
        self.assertEqual('http://localhost:8043/no-attribute-form', form.computed_action)
        self.assertIs(form.method, None)
        self.assertEqual('get', form.computed_method)

if __name__ == '__main__':
    import unittest
    unittest.main()