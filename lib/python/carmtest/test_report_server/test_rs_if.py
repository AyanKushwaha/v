# ../../../report_sources/hidden/rs_if.py

import os
import copy

from tempfile import mkstemp
from carmtest.framework import *
from report_sources.report_server.rs_if import RSv1_report, RSv2_report
from report_sources.report_server.rs_if import RSv2_report_delta, RSv2_report_file
from report_sources.report_server.rs_if import add_reportprefix, argfix

def report(*a, **k):
    return "%s, %s" % (a, k)

def report_delta(*a, **k):
    if len(a) > 0 and a[0] == 'a':
        return "%s, %s" % (a, k), True
    else:
        return "%s, %s" % (a, k), False

def report_file(*a, **k):
    fd, fn = mkstemp(suffix='.tmp', prefix='test_rs_if',
            dir=os.environ['CARMTMP'], text=True)
    f = os.fdopen(fd, 'w')
    f.write("%s, %s" % (a, k))
    f.close()
    return fn

_arg_t = ('a', 'b', 'c')
_arg_d = {'kw1': 'A', 'kw2': 'B'}

_args_as_string = "%s, %s" % (_arg_t, _arg_d)

_prefix = 'pReFiX'

_report_list = [{
    'content': _args_as_string, 
    'content-type': 'text/plain',
    'destination': [('default', {})],
}]

_report_list_scheduler = [{
    'content': "%s, %s" % ((), _arg_d),
    'content-type': 'text/plain',
    'destination': [('default', {})],
}]

class Test_argfix(TestFixture):
    """
    Arg Fix
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test1(self):
        @argfix
        def generate(*a, **k):
            return a, k
        self.assertEqual(generate(), ((), {}))
        self.assertEqual(generate('a', k='b'), (('a',), {'k': 'b'}))
        self.assertEqual(generate((_arg_t, _arg_d)), (_arg_t, _arg_d))
        self.assertEqual(generate(_arg_d), ((), _arg_d))

class Test_RSv1_report(TestFixture):
    """
    RSv1 report
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test(self):
        @RSv1_report
        @argfix
        def save(*a, **k):
            return report(*a, **k)
        fn = save(_arg_t, _arg_d)
        F = open(fn, "r")
        result = '\n'.join(F.readlines())
        os.unlink(fn)
        self.assertEqual(result, _args_as_string)

class Test_RSv2_report(TestFixture):
    """
    RSv2 report
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test1(self):
        @RSv2_report()
        @argfix
        def generate(*a, **k):
            return report(*a, **k)
        self.assertEqual(generate((_arg_t, _arg_d)), (_report_list, False))

    def test2(self):
        @argfix
        @RSv2_report(use_delta=True)
        def generate(*a, **k):
            return report(*a, **k)
        self.assertEqual(generate((_arg_t, _arg_d)), (_report_list, True))

    def test3(self):
        @RSv2_report()
        @argfix
        def generate(*a, **k):
            return report(*a, **k)
        self.assertEqual(generate(_arg_d), (_report_list_scheduler, False))

class Test_RSv2_report_delta(TestFixture):
    """
    RSv2 report delta
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test1(self):
        @RSv2_report_delta()
        @argfix
        def generate(*a, **k):
            return report_delta(*a, **k)
        self.assertEqual(generate((_arg_t, _arg_d)), (_report_list, True))
        self.assertEqual(generate(_arg_d), (_report_list_scheduler, False))

    def test2(self):
        @RSv2_report_delta()
        @argfix
        def generate(*a, **k):
            return report_delta(*a, **k)
        arg = (('b', 'b', 'c'), _arg_d)
        report_list = copy.deepcopy(_report_list)
        report_list[0]['content'] = "%s, %s" % arg
        self.assertEqual(generate(arg), (report_list, False))

class Test_RSv2_report_file(TestFixture):
    """
    RSv2 report file
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test1(self):
        @RSv2_report_file()
        @argfix
        def generate(*a, **k):
            return report_file(*a, **k)
        rlist, delta = generate((_arg_t, _arg_d))
        self.assertEqual(delta, False)
        self.assertEqual(len(rlist), 1)
        rep = rlist[0]
        self.assertEqual(rep['destination'], [('default', {})])
        file = open(rep['content-location'], "r")
        result = file.readlines()[0]
        file.close()
        os.unlink(rep['content-location'])
        self.assertEqual(result, _args_as_string)

    def test2_args(self):
        @RSv2_report_file(use_delta=True, destination=[('abc', {})])
        @argfix
        def generate(*a, **k):
            return report_file(*a, **k)
        rlist, delta = generate((_arg_t, _arg_d))
        self.assertEqual(delta, True)
        self.assertEqual(len(rlist), 1)
        rep = rlist[0]
        self.assertEqual(rep['destination'], [('abc', {})])
        file = open(rep['content-location'], "r")
        result = file.readlines()[0]
        file.close()
        os.unlink(rep['content-location'])
        self.assertEqual(result, _args_as_string)

    def test3_sched(self):
        @RSv2_report_file(use_delta=True, destination=[('abc', {})])
        @argfix
        def generate(*a, **k):
            return report_file(*a, **k)
        rlist, delta = generate(_arg_d)
        self.assertEqual(delta, True)
        self.assertEqual(len(rlist), 1)
        rep = rlist[0]
        self.assertEqual(rep['destination'], [('abc', {})])
        file = open(rep['content-location'], "r")
        result = file.readlines()[0]
        file.close()
        os.unlink(rep['content-location'])
        self.assertEqual(result, "%s, %s" % ((), _arg_d))

class Test_add_reportprefix(TestFixture):
    """
    Add report prefix
    """
    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test1_without_prefix(self):
        @argfix
        @add_reportprefix
        @RSv2_report_delta()
        def generate(*a, **k):
            return report_delta(*a, **k)
        self.assertEqual(generate((_arg_t, _arg_d)), (
            [{
                'content': '%s, %s' % (_arg_t, _arg_d),
                'content-type': 'text/plain',
                'destination': [('default', {})]
            }], True))

    def test2_without_prefix_scheduler(self):
        @argfix
        @add_reportprefix
        @RSv2_report_delta()
        def generate(*a, **k):
            return report_delta(*a, **k)
        # Note: delta will be false since no positional arguments.
        self.assertEqual(generate(_arg_d), (
            [{
                'content': '%s, %s' % ((), _arg_d),
                'content-type': 'text/plain',
                'destination': [('default', {})]
            }], False))

    def test3_with_prefix(self):
        @argfix
        @add_reportprefix
        @RSv2_report_delta(destination=[('anydest', {}), ('anotherdest', {})])
        def generate(*a, **k):
            return report_delta(*a, **k)
        arg_d = copy.deepcopy(_arg_d)
        arg_d['reportprefix'] = _prefix
        self.assertEqual(generate((_arg_t, arg_d)), (
            [{
                'content': '%s, %s' % (_arg_t, arg_d),
                'content-type': 'text/plain',
                'destination': [(_prefix + 'anydest', {}), (_prefix + 'anotherdest', {})]
            }], True))

    def test4_with_prefix_scheduler(self):
        @argfix
        @add_reportprefix
        @RSv2_report_delta()
        def generate(*a, **k):
            return report_delta(*a, **k)
        arg_d = copy.deepcopy(_arg_d)
        arg_d['reportprefix'] = _prefix
        self.assertEqual(generate(arg_d), (
            [{
                'content': '%s, %s' % ((), arg_d),
                'content-type': 'text/plain',
                'destination': [(_prefix, {})]
            }], False))

    def test5(self):
        result_a = [{'content': 'xyz', 'content-type': 'text-plain',
                'destination': [('default', {})]}], True
        result_b = [{'content': 'xyz', 'content-type': 'text-plain',
                'destination': [(_prefix, {})]}], True
        @add_reportprefix
        def generate1(*a, **k):
            return result_a

        @add_reportprefix
        def generate2(**k):
            return result_a

        @add_reportprefix
        def generate3():
            return result_a
        self.assertEqual(generate1('alfa', beta='gamma'), result_a)
        self.assertEqual(generate2(beta='gamma', reportprefix=_prefix), result_b)
        self.assertEqual(generate3(), result_a)
