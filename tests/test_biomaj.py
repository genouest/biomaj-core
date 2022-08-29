import shutil
import os
import sys
import tempfile
import stat
import pytest

from biomaj_core.config import BiomajConfig
from biomaj_core.utils import Utils
from biomaj_core.bmajindex import BmajIndex



class UtilsForTest:
    """
    Copy properties files to a temp directory and update properties to
    use a temp directory
    """

    def __init__(self):
        """
        Setup the temp dirs and files.
        """
        self.global_properties = None
        self.global_properties_hl = None
        self.bank_properties = None

        self.test_dir = tempfile.mkdtemp('biomaj')

        self.conf_dir = os.path.join(self.test_dir, 'conf')
        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)
        self.data_dir = os.path.join(self.test_dir, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.log_dir = os.path.join(self.test_dir, 'log')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.process_dir = os.path.join(self.test_dir, 'process')
        if not os.path.exists(self.process_dir):
            os.makedirs(self.process_dir)
        self.lock_dir = os.path.join(self.test_dir, 'lock')
        if not os.path.exists(self.lock_dir):
            os.makedirs(self.lock_dir)
        self.cache_dir = os.path.join(self.test_dir, 'cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        if self.global_properties is None:
            self.__copy_global_properties()

        if self.global_properties_hl is None:
            self.__copy_global_properties_hl()

        if self.bank_properties is None:
            self.__copy_test_bank_properties()

    def clean(self):
        """
        Deletes temp directory
        """
        shutil.rmtree(self.test_dir)

    def __copy_test_bank_properties(self):
        if self.bank_properties is not None:
            return
        self.bank_properties = ['alu', 'local', 'testhttp', 'directhttp',
                                'noname', 'noexe', 'noargs', 'prenoname',
                                'prenoexe', 'prenoargs', 'rmnoname', 'rmnoexe',
                                'rmnoargs']
        curdir = os.path.dirname(os.path.realpath(__file__))
        for b in self.bank_properties:
            from_file = os.path.join(curdir, b+'.properties')
            to_file = os.path.join(self.conf_dir, b+'.properties')
            shutil.copyfile(from_file, to_file)

        self.bank_process = ['test.sh']
        curdir = os.path.dirname(os.path.realpath(__file__))
        procdir = os.path.join(curdir, 'bank/process')
        for proc in self.bank_process:
            from_file = os.path.join(procdir, proc)
            to_file = os.path.join(self.process_dir, proc)
            shutil.copyfile(from_file, to_file)
            os.chmod(to_file, stat.S_IRWXU)

        # Manage local bank test, use bank test subdir as remote
        properties = ['multi.properties', 'computederror.properties',
                      'error.properties', 'local.properties',
                      'localprocess.properties', 'testhttp.properties',
                      'computed.properties', 'computed2.properties',
                      'sub1.properties', 'sub2.properties',
                      'hardlinks.properties']
        for prop in properties:
            from_file = os.path.join(curdir, prop)
            to_file = os.path.join(self.conf_dir, prop)
            fout = open(to_file,'w', encoding='UTF-8')
            with open(from_file,'r', encoding='UTF-8') as fin:
                for line in fin:
                    if line.startswith('remote.dir'):
                        fout.write("remote.dir="+os.path.join(curdir,
                                                              'bank') + "\n")
                    elif line.startswith('remote.files'):
                        fout.write(line.replace('/tmp', os.path.join(curdir,
                                                                     'bank')))
                    else:
                        fout.write(line)
            fout.close()

    def __copy_global_properties(self):
        if self.global_properties is not None:
            return
        self.global_properties = os.path.join(self.conf_dir, 'global.properties')
        curdir = os.path.dirname(os.path.realpath(__file__))
        global_template = os.path.join(curdir, 'global.properties')
        fout = open(self.global_properties, 'w', encoding='UTF-8')
        with open(global_template,'r', encoding='UTF-8') as fin:
            for line in fin:
                if line.startswith('conf.dir'):
                    fout.write("conf.dir="+self.conf_dir+"\n")
                elif line.startswith('log.dir'):
                    fout.write("log.dir="+self.log_dir+"\n")
                elif line.startswith('data.dir'):
                    fout.write("data.dir="+self.data_dir+"\n")
                elif line.startswith('process.dir'):
                    fout.write("process.dir="+self.process_dir+"\n")
                elif line.startswith('lock.dir'):
                    fout.write("lock.dir="+self.lock_dir+"\n")
                else:
                    fout.write(line)
        fout.close()

    def __copy_global_properties_hl(self):
        if self.global_properties_hl is not None:
            return
        self.global_properties_hl = os.path.join(self.conf_dir, 'global_hardlinks.properties')
        curdir = os.path.dirname(os.path.realpath(__file__))
        global_template = os.path.join(curdir, 'global_hardlinks.properties')
        fout = open(self.global_properties_hl, 'w', encoding='UTF-8')
        with open(global_template,'r', encoding='UTF-8') as fin:
            for line in fin:
                if line.startswith('conf.dir'):
                    fout.write("conf.dir="+self.conf_dir+"\n")
                elif line.startswith('log.dir'):
                    fout.write("log.dir="+self.log_dir+"\n")
                elif line.startswith('data.dir'):
                    fout.write("data.dir="+self.data_dir+"\n")
                elif line.startswith('process.dir'):
                    fout.write("process.dir="+self.process_dir+"\n")
                elif line.startswith('lock.dir'):
                    fout.write("lock.dir="+self.lock_dir+"\n")
                else:
                    fout.write(line)
        fout.close()


class TestBiomajUtils():

    def setup_method(self, m):
        self.utils = UtilsForTest()

    def teardown_method(self, m):
        self.utils.clean()

    def test_properties_override(self):
        BiomajConfig.load_config(self.utils.global_properties,
                                 allow_user_config=False)
        config = BiomajConfig('local')
        ldap_host = config.get('ldap.host')
        assert (ldap_host == 'localhost')
        os.environ['BIOMAJ_LDAP_HOST'] = 'someserver'
        ldap_host = config.get('ldap.host')
        assert (ldap_host == 'someserver')

    def test_service_config_override(self):
        config = {
            'rabbitmq': { 'host': '1.2.3.4'},
            'web': {'local_endpoint': 'http://localhost'}
        }
        Utils.service_config_override(config)
        assert (config['rabbitmq']['host'] == '1.2.3.4')
        os.environ['RABBITMQ_HOST'] = '4.3.2.1'
        Utils.service_config_override(config)
        assert (config['rabbitmq']['host'] == '4.3.2.1')
        os.environ['WEB_LOCAL_ENDPOINT_DOWNLOAD'] = 'http://download'
        Utils.service_config_override(config)
        assert (config['web']['local_endpoint_download'] == 'http://download')
        endpoint = Utils.get_service_endpoint(config, 'download')
        assert (endpoint == 'http://download')
        endpoint = Utils.get_service_endpoint(config, 'process')
        assert (endpoint == 'http://localhost')

    def test_use_hardlinks_config(self):
        """
        Test that hardlinks are disabled by default and can be overridden.
        """
        BiomajConfig.load_config(self.utils.global_properties,
                                 allow_user_config=False)
        # Must be disabled in local.properties
        config = BiomajConfig('local')
        assert not config.get_bool("use_hardlinks")
        # Must be enabled for hardlinks.properties (override)
        config = BiomajConfig('hardlinks')
        assert config.get_bool("use_hardlinks")
        # Reload file with use_hardlinks=1
        BiomajConfig.load_config(self.utils.global_properties_hl,
                                 allow_user_config=False)
        config = BiomajConfig('local')
        assert config.get_bool("use_hardlinks")

    def test_mimes(self):
        fasta_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'bank/test2.fasta')
        (mime, _) = Utils.detect_format(fasta_file)
        assert 'application/fasta' == mime

    def test_uncompress(self):
        from_file = { 'root': os.path.dirname(os.path.realpath(__file__)),
                      'name': 'bank/test.fasta.gz'
                      }

        to_dir = self.utils.data_dir
        Utils.copy_files([from_file], to_dir)
        Utils.uncompress(os.path.join(to_dir, from_file['name']))
        assert os.path.exists(to_dir+'/bank/test.fasta')

    def test_copy_with_regexp(self):
        from_dir = os.path.dirname(os.path.realpath(__file__))
        to_dir = self.utils.data_dir
        Utils.copy_files_with_regexp(from_dir, to_dir, [r'.*\.py'])
        assert os.path.exists(to_dir+'/test_biomaj.py')

    def test_copy_with_regexp_hardlink(self):
        """
        Test copy with hardlinks: we create files in data_dir and try to
        link them. This should work unless /tmp don't accept hardlinks.
        """
        # Create 5 files and a directory in data_dir. We don't destroy them
        # since they are in /tmp.
        suffix = ".dat"
        regexp = ".*\\" + suffix
        orig_file_full = [
            tempfile.mkstemp(dir=self.utils.data_dir, suffix=suffix)[1]
            for i in range(5)
        ]
        to_dir = tempfile.mkdtemp(dir=self.utils.data_dir)
        new_file_full = [os.path.join(to_dir, os.path.basename(f))
                         for f in orig_file_full]
        # Copy
        from_dir = self.utils.data_dir
        Utils.copy_files_with_regexp(from_dir, to_dir, [regexp],
                                     use_hardlinks=True)
        # Check if files was copied
        for orig, new in zip(orig_file_full, new_file_full):
            assert (os.path.exists(new))
            # Check if it's really a hardlink. This may fail so we catch
            # any exceptions.
            orig_file_stat = os.stat(orig)
            new_file_stat = os.stat(new)
            try:
                assert (orig_file_stat.st_ino == new_file_stat.st_ino)
            except Exception:
                msg = "In %s: copy worked but hardlinks were not used." % orig_file_full
                print(msg, file=sys.stderr)

    def test_copy(self):
        from_dir = os.path.dirname(os.path.realpath(__file__))
        local_file = 'test_biomaj.py'
        files_to_copy = [ {'root': from_dir, 'name': local_file}]
        to_dir = self.utils.data_dir
        Utils.copy_files(files_to_copy, to_dir)
        assert os.path.exists(to_dir+'/test_biomaj.py')

    def test_copy_hardlink(self):
        """
        Test copy with hardlinks: we create a file in data_dir and try to
        link it. This should work unless /tmp don't accept hardlinks.
        """
        # Create a file and a directory in data_dir. We don't destroy them
        # since they are in /tmp.
        _, orig_file_full = tempfile.mkstemp(dir=self.utils.data_dir)
        orig_file = os.path.basename(orig_file_full)
        to_dir = tempfile.mkdtemp(dir=self.utils.data_dir)
        new_file_full = os.path.join(to_dir, orig_file)
        # Copy
        from_dir = self.utils.data_dir
        files_to_copy = [{'root': from_dir, 'name': orig_file}]
        Utils.copy_files(files_to_copy, to_dir, use_hardlinks=True)
        # Check if file was copied
        assert (os.path.exists(new_file_full))
        # Check if it's really a hardlink. This may fail so we catch
        # any exceptions.
        orig_file_stat = os.stat(orig_file_full)
        new_file_stat = os.stat(new_file_full)
        try:
            assert orig_file_stat.st_ino == new_file_stat.st_ino
        except Exception:
            msg = "In %s: copy worked but hardlinks were not used." % orig_file_full
            print(msg, file=sys.stderr)

    def test_check_method(self):
        """Check .name, .exe and .args are well check during bank configuration
        checking"""
        BiomajConfig.load_config(self.utils.global_properties)
        for conf in ['noname', 'noexe', 'noargs', 'prenoname', 'prenoexe',
                     'prenoargs', 'rmnoname', 'rmnoexe', 'rmnoargs']:
            config = BiomajConfig(conf)
            assert not config.check()


class TestElastic():
    """
    test indexing and search
    """

    def setup_method(self, m):
        BmajIndex.es = None
        self.utils = UtilsForTest()
        # curdir = os.path.dirname(os.path.realpath(__file__))
        BiomajConfig.load_config(self.utils.global_properties,
                                 allow_user_config=False)
        if BmajIndex.do_index == False:
            pytest.skip("Skipping indexing tests due to elasticsearch not available")
        # Delete all banks
        # b = Bank('local')
        # b.banks.remove({})
        BmajIndex.delete_all_bank('local')

        self.config = BiomajConfig('local')
        data_dir = self.config.get('data.dir')
        lock_file = os.path.join(data_dir,'local.lock')
        if os.path.exists(lock_file):
            os.remove(lock_file)

    def teardown_method(self, m):
        data_dir = self.config.get('data.dir')
        lock_file = os.path.join(data_dir,'local.lock')
        if os.path.exists(lock_file):
            os.remove(lock_file)
        self.utils.clean()
        BmajIndex.delete_all_bank('test')

    def test_index(self):
        BmajIndex.do_index = True
        prod = {
    			"data_dir" : "/tmp/test/data",
    			"formats" : {
    				"fasta" : [
    					{
    						"files" : [
    							"fasta/chr1.fa",
    							"fasta/chr2.fa"
    						],
    						"types" : [
    							"nucleic"
    						],
    						"tags" : {
    							"organism" : "hg19"
    						}
    					}
    				],
    				"blast": [
    					{
    						"files" : [
    							"blast/chr1/chr1db"
    						],
    						"types" : [
    							"nucleic"
    						],
    						"tags" : {
    							"chr" : "chr1",
    							"organism" : "hg19"
    						}
    					}
    				]

    			},
    			"freeze" : False,
    			"session" : 1416229253.930908,
    			"prod_dir" : "alu-2003-11-26",
    			"release" : "2003-11-26",
    			"types" : [
    				"nucleic"
    			]
    		}

        BmajIndex.add('test',prod, True)

        query = {
          'query' : {
            'match' : {'bank': 'test'}
            }
          }
        res = BmajIndex.search(query)
        assert len(res)==2


    def test_remove_all(self):
        self.test_index()
        query = {
          'query' : {
            'match' : {'bank': 'test'}
            }
          }
        BmajIndex.delete_all_bank('test')
        res = BmajIndex.search(query)
        assert len(res)==0
