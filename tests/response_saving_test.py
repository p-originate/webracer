import os
import os.path
import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

try:
    # python 3.3?
    file_not_found_exception_class = FileNotFoundError
except NameError:
    file_not_found_exception_class = IOError

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8060)

save_dir = os.environ.get('WEBRACER_TEST_TMP') or os.path.join(os.path.dirname(__file__), 'tmp')
nonexistent_save_dir = '/tmp/nonexistent.dee11123e367b4a7506f856cc55898fabd4caeff'

def list_save_dir():
    entries = os.listdir(save_dir)
    entries = [entry for entry in entries if entry[0] != '.']
    return entries

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8060)
class ResponseTest(webracer.WebTestCase):
    def setUp(self, *args, **kwargs):
        super(ResponseTest, self).setUp(*args, **kwargs)
        
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        else:
            for entry in list_save_dir():
                os.unlink(os.path.join(save_dir, entry))
    
    @webracer.config(save_responses=True, save_dir=save_dir)
    def test_save_successful(self):
        self.assertEqual(0, len(list_save_dir()))
        
        self.get('/ok')
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)
        
        entries = list_save_dir()
        # response + last symlink
        self.assertEqual(2, len(entries))
        assert 'last' in entries
        entries.remove('last')
        assert entries[0].startswith('response')
    
    @webracer.config(save_responses=True, save_dir=nonexistent_save_dir)
    def test_save_to_nonexistent_dir(self):
        assert not os.path.exists(nonexistent_save_dir)
        
        with self.assert_raises(file_not_found_exception_class) as cm:
            self.get('/ok')
        
        assert nonexistent_save_dir in str(cm.exception)
        
        assert not os.path.exists(nonexistent_save_dir)
    
    @webracer.config(save_responses=False, save_failed_responses=True,
        save_dir=save_dir)
    def test_save_failed_request(self):
        self.assertEqual(0, len(list_save_dir()))
        
        self.get('/internal_server_error')
        
        self.assertEqual(0, len(list_save_dir()))
        
        with self.assert_raises(AssertionError):
            # triggers save
            self.assert_status(200)
        
        entries = list_save_dir()
        # response + last symlink
        self.assertEqual(2, len(entries))
        assert 'last' in entries
        entries.remove('last')
        assert entries[0].startswith('response')
    
    @webracer.config(save_responses=False, save_failed_responses=True,
        save_dir=nonexistent_save_dir)
    def test_save_failed_request_to_nonexistent_dir(self):
        assert not os.path.exists(nonexistent_save_dir)
        
        self.get('/internal_server_error')
        
        with self.assert_raises(AssertionError) as cm:
            # triggers save
            self.assert_status(200)
        
        # Resulting exception should contain both assertion failure message
        # and the message involving inability to save response
        assert 'Response status 200 expected but was 500' in str(cm.exception)
        assert 'No such file or directory' in str(cm.exception)
        assert nonexistent_save_dir in str(cm.exception)
        
        assert not os.path.exists(nonexistent_save_dir)
