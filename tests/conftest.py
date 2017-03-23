# coding=utf-8
import glob

def pytest_generate_tests(metafunc):
    if 'xml_reconstitute' in metafunc.fixturenames:
        metafunc.parametrize("xml_reconstitute", glob.glob('tests/data/reconstitute/*.xml'))

    if 'xml_filter_template' in metafunc.fixturenames:
        metafunc.parametrize("xml_filter_template", glob.glob('tests/data/filter/tmpl/*.xml'))

    if 'ini_filter_template' in metafunc.fixturenames:
        metafunc.parametrize("ini_filter_template", glob.glob('tests/data/filter/tmpl/*.ini'))