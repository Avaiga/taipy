# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from __future__ import annotations

import gc
import re
import sys
import textwrap
import types
from io import StringIO
from typing import List

from hamcrest import assert_that, contains_string
from hypothesis import given
from hypothesis.strategies import sampled_from

from twisted.logger import Logger
from twisted.python import util
from twisted.python.filepath import FilePath, IFilePath
from twisted.python.usage import UsageError
from twisted.scripts import trial
from twisted.trial import unittest
from twisted.trial._dist.disttrial import DistTrialRunner
from twisted.trial._dist.functional import compose
from twisted.trial.runner import (
    DestructiveTestSuite,
    TestLoader,
    TestSuite,
    TrialRunner,
    _Runner,
)
from twisted.trial.test.test_loader import testNames
from .matchers import fileContents

pyunit = __import__("unittest")


def sibpath(filename: str) -> str:
    """
    For finding files in twisted/trial/test
    """
    return util.sibpath(__file__, filename)


def logSomething() -> None:
    """
    Emit something to L{twisted.logger}.
    """
    Logger().info("something")


def parseArguments(argv: List[str]) -> trial.Options:
    """
    Parse an argument list using trial's argument parser.
    """
    config = trial.Options()
    config.parseOptions(argv)
    return config


def runFromConfig(config: trial.Options) -> trial.Options:
    """
    Run L{logSomething} as a test method using the given configuration.
    """
    runner = trial._makeRunner(config)
    runner.stream = StringIO()
    suite = TestSuite([pyunit.FunctionTestCase(logSomething)])
    runner.run(suite)
    return config


runFromArguments = compose(runFromConfig, parseArguments)


class LogfileTests(unittest.SynchronousTestCase):
    """
    Tests for the --logfile option.
    """

    @given(
        sampled_from(
            [
                "dir-a",
                "dir-b",
                "dir-c/dir-d",
            ]
        )
    )
    def test_default(self, workingDirectory: str) -> None:
        """
        If no value is given for the option then logs are written to a log
        file constructed from a default value.
        """
        config = runFromArguments(["--temp-directory", workingDirectory])
        logPath: IFilePath = FilePath(workingDirectory).preauthChild(config["logfile"])
        assert_that(logPath, fileContents(contains_string("something")))

    @given(
        sampled_from(
            [
                "somelog.txt",
                "somedir/somelog.txt",
            ]
        )
    )
    def test_relativePath(self, logfile: str) -> None:
        """
        If the value given for the option is a relative path then it is
        interpreted relative to trial's own temporary working directory and
        logs are written there.
        """
        config = runFromArguments(["--logfile", logfile])
        logPath: IFilePath = FilePath(config["temp-directory"]).preauthChild(logfile)
        assert_that(logPath, fileContents(contains_string("something")))

    @given(
        sampled_from(
            [
                "somelog.txt",
                "somedir/somelog.txt",
            ]
        )
    )
    def test_absolutePath(self, logfile: str) -> None:
        """
        If the value given for the option is an absolute path then it is
        interpreted absolutely and logs are written there.
        """
        # We don't want to scribble to arbitrary places on the host
        # filesystem.  Construct an absolute path that's beneath our working
        # directory - which trial will make into a per-run unique temporary
        # directory.
        logPath = FilePath(".").preauthChild(logfile)
        runFromArguments(["--logfile", logPath.path])
        iPath: IFilePath = logPath
        assert_that(iPath, fileContents(contains_string("something")))


class ForceGarbageCollectionTests(unittest.SynchronousTestCase):
    """
    Tests for the --force-gc option.
    """

    def setUp(self) -> None:
        self.config = trial.Options()
        self.log: list[str] = []
        self.patch(gc, "collect", self.collect)
        test = pyunit.FunctionTestCase(self.simpleTest)
        self.test = TestSuite([test, test])

    def simpleTest(self) -> None:
        """
        A simple test method that records that it was run.
        """
        self.log.append("test")

    def collect(self) -> None:
        """
        A replacement for gc.collect that logs calls to itself.
        """
        self.log.append("collect")

    def makeRunner(self) -> _Runner:
        """
        Return a L{TrialRunner} object that is safe to use in tests.
        """
        runner = trial._makeRunner(self.config)
        runner.stream = StringIO()
        return runner

    def test_forceGc(self) -> None:
        """
        Passing the --force-gc option to the trial script forces the garbage
        collector to run before and after each test.
        """
        self.config["force-gc"] = True
        self.config.postOptions()
        runner = self.makeRunner()
        runner.run(self.test)
        self.assertEqual(
            self.log, ["collect", "test", "collect", "collect", "test", "collect"]
        )

    def test_unforceGc(self) -> None:
        """
        By default, no garbage collection is forced.
        """
        self.config.postOptions()
        runner = self.makeRunner()
        runner.run(self.test)
        self.assertEqual(self.log, ["test", "test"])


class SuiteUsedTests(unittest.SynchronousTestCase):
    """
    Check the category of tests suite used by the loader.
    """

    def setUp(self) -> None:
        """
        Create a trial configuration object.
        """
        self.config = trial.Options()

    def test_defaultSuite(self) -> None:
        """
        By default, the loader should use L{DestructiveTestSuite}
        """
        loader = trial._getLoader(self.config)
        self.assertEqual(loader.suiteFactory, DestructiveTestSuite)

    def test_untilFailureSuite(self) -> None:
        """
        The C{until-failure} configuration uses the L{TestSuite} to keep
        instances alive across runs.
        """
        self.config["until-failure"] = True
        loader = trial._getLoader(self.config)
        self.assertEqual(loader.suiteFactory, TestSuite)


class TestModuleTests(unittest.SynchronousTestCase):
    def setUp(self) -> None:
        self.config = trial.Options()

    def tearDown(self) -> None:
        self.config = None  # type: ignore[assignment]

    def test_testNames(self) -> None:
        """
        Check that the testNames helper method accurately collects the
        names of tests in suite.
        """
        self.assertEqual(testNames(self), [self.id()])

    def assertSuitesEqual(self, test1: TestSuite, names: list[str]) -> None:
        loader = TestLoader()
        names1 = testNames(test1)
        names2 = testNames(TestSuite(map(loader.loadByName, names)))
        names1.sort()
        names2.sort()
        self.assertEqual(names1, names2)

    def test_baseState(self) -> None:
        self.assertEqual(0, len(self.config["tests"]))

    def test_testmoduleOnModule(self) -> None:
        """
        Check that --testmodule loads a suite which contains the tests
        referred to in test-case-name inside its parameter.
        """
        self.config.opt_testmodule(sibpath("moduletest.py"))
        self.assertSuitesEqual(
            trial._getSuite(self.config), ["twisted.trial.test.test_log"]
        )

    def test_testmoduleTwice(self) -> None:
        """
        When the same module is specified with two --testmodule flags, it
        should only appear once in the suite.
        """
        self.config.opt_testmodule(sibpath("moduletest.py"))
        self.config.opt_testmodule(sibpath("moduletest.py"))
        self.assertSuitesEqual(
            trial._getSuite(self.config), ["twisted.trial.test.test_log"]
        )

    def test_testmoduleOnSourceAndTarget(self) -> None:
        """
        If --testmodule is specified twice, once for module A and once for
        a module which refers to module A, then make sure module A is only
        added once.
        """
        self.config.opt_testmodule(sibpath("moduletest.py"))
        self.config.opt_testmodule(sibpath("test_log.py"))
        self.assertSuitesEqual(
            trial._getSuite(self.config), ["twisted.trial.test.test_log"]
        )

    def test_testmoduleOnSelfModule(self) -> None:
        """
        When given a module that refers to *itself* in the test-case-name
        variable, check that --testmodule only adds the tests once.
        """
        self.config.opt_testmodule(sibpath("moduleself.py"))
        self.assertSuitesEqual(
            trial._getSuite(self.config), ["twisted.trial.test.moduleself"]
        )

    def test_testmoduleOnScript(self) -> None:
        """
        Check that --testmodule loads tests referred to in test-case-name
        buffer variables.
        """
        self.config.opt_testmodule(sibpath("scripttest.py"))
        self.assertSuitesEqual(
            trial._getSuite(self.config),
            ["twisted.trial.test.test_log", "twisted.trial.test.test_runner"],
        )

    def test_testmoduleOnNonexistentFile(self) -> None:
        """
        Check that --testmodule displays a meaningful error message when
        passed a non-existent filename.
        """
        buffy = StringIO()
        stderr, sys.stderr = sys.stderr, buffy
        filename = "test_thisbetternoteverexist.py"
        try:
            self.config.opt_testmodule(filename)
            self.assertEqual(0, len(self.config["tests"]))
            self.assertEqual(f"File {filename!r} doesn't exist\n", buffy.getvalue())
        finally:
            sys.stderr = stderr

    def test_testmoduleOnEmptyVars(self) -> None:
        """
        Check that --testmodule adds no tests to the suite for modules
        which lack test-case-name buffer variables.
        """
        self.config.opt_testmodule(sibpath("novars.py"))
        self.assertEqual(0, len(self.config["tests"]))

    def test_testmoduleOnModuleName(self) -> None:
        """
        Check that --testmodule does *not* support module names as arguments
        and that it displays a meaningful error message.
        """
        buffy = StringIO()
        stderr, sys.stderr = sys.stderr, buffy
        moduleName = "twisted.trial.test.test_script"
        try:
            self.config.opt_testmodule(moduleName)
            self.assertEqual(0, len(self.config["tests"]))
            self.assertEqual(f"File {moduleName!r} doesn't exist\n", buffy.getvalue())
        finally:
            sys.stderr = stderr

    def test_parseLocalVariable(self) -> None:
        declaration = "-*- test-case-name: twisted.trial.test.test_tests -*-"
        localVars = trial._parseLocalVariables(declaration)
        self.assertEqual({"test-case-name": "twisted.trial.test.test_tests"}, localVars)

    def test_trailingSemicolon(self) -> None:
        declaration = "-*- test-case-name: twisted.trial.test.test_tests; -*-"
        localVars = trial._parseLocalVariables(declaration)
        self.assertEqual({"test-case-name": "twisted.trial.test.test_tests"}, localVars)

    def test_parseLocalVariables(self) -> None:
        declaration = (
            "-*- test-case-name: twisted.trial.test.test_tests; " "foo: bar -*-"
        )
        localVars = trial._parseLocalVariables(declaration)
        self.assertEqual(
            {"test-case-name": "twisted.trial.test.test_tests", "foo": "bar"}, localVars
        )

    def test_surroundingGuff(self) -> None:
        declaration = "## -*- test-case-name: " "twisted.trial.test.test_tests -*- #"
        localVars = trial._parseLocalVariables(declaration)
        self.assertEqual({"test-case-name": "twisted.trial.test.test_tests"}, localVars)

    def test_invalidLine(self) -> None:
        self.assertRaises(ValueError, trial._parseLocalVariables, "foo")

    def test_invalidDeclaration(self) -> None:
        self.assertRaises(ValueError, trial._parseLocalVariables, "-*- foo -*-")
        self.assertRaises(
            ValueError, trial._parseLocalVariables, "-*- foo: bar; qux -*-"
        )
        self.assertRaises(
            ValueError, trial._parseLocalVariables, "-*- foo: bar: baz; qux: qax -*-"
        )

    def test_variablesFromFile(self) -> None:
        localVars = trial.loadLocalVariables(sibpath("moduletest.py"))
        self.assertEqual({"test-case-name": "twisted.trial.test.test_log"}, localVars)

    def test_noVariablesInFile(self) -> None:
        localVars = trial.loadLocalVariables(sibpath("novars.py"))
        self.assertEqual({}, localVars)

    def test_variablesFromScript(self) -> None:
        localVars = trial.loadLocalVariables(sibpath("scripttest.py"))
        self.assertEqual(
            {
                "test-case-name": (
                    "twisted.trial.test.test_log," "twisted.trial.test.test_runner"
                )
            },
            localVars,
        )

    def test_getTestModules(self) -> None:
        modules = trial.getTestModules(sibpath("moduletest.py"))
        self.assertEqual(modules, ["twisted.trial.test.test_log"])

    def test_getTestModules_noVars(self) -> None:
        modules = trial.getTestModules(sibpath("novars.py"))
        self.assertEqual(len(modules), 0)

    def test_getTestModules_multiple(self) -> None:
        modules = trial.getTestModules(sibpath("scripttest.py"))
        self.assertEqual(
            set(modules),
            {"twisted.trial.test.test_log", "twisted.trial.test.test_runner"},
        )

    def test_looksLikeTestModule(self) -> None:
        for filename in ["test_script.py", "twisted/trial/test/test_script.py"]:
            self.assertTrue(
                trial.isTestFile(filename),
                f"{filename!r} should be a test file",
            )
        for filename in [
            "twisted/trial/test/moduletest.py",
            sibpath("scripttest.py"),
            sibpath("test_foo.bat"),
        ]:
            self.assertFalse(
                trial.isTestFile(filename),
                f"{filename!r} should *not* be a test file",
            )


class WithoutModuleTests(unittest.SynchronousTestCase):
    """
    Test the C{without-module} flag.
    """

    def setUp(self) -> None:
        """
        Create a L{trial.Options} object to be used in the tests, and save
        C{sys.modules}.
        """
        self.config = trial.Options()
        self.savedModules = dict(sys.modules)

    def tearDown(self) -> None:
        """
        Restore C{sys.modules}.
        """
        for module in ("imaplib", "smtplib"):
            if module in self.savedModules:
                sys.modules[module] = self.savedModules[module]
            else:
                sys.modules.pop(module, None)

    def _checkSMTP(self) -> object:
        """
        Try to import the C{smtplib} module, and return it.
        """
        import smtplib

        return smtplib

    def _checkIMAP(self) -> object:
        """
        Try to import the C{imaplib} module, and return it.
        """
        import imaplib

        return imaplib

    def test_disableOneModule(self) -> None:
        """
        Check that after disabling a module, it can't be imported anymore.
        """
        self.config.parseOptions(["--without-module", "smtplib"])
        self.assertRaises(ImportError, self._checkSMTP)
        # Restore sys.modules
        del sys.modules["smtplib"]
        # Then the function should succeed
        self.assertIsInstance(self._checkSMTP(), types.ModuleType)

    def test_disableMultipleModules(self) -> None:
        """
        Check that several modules can be disabled at once.
        """
        self.config.parseOptions(["--without-module", "smtplib,imaplib"])
        self.assertRaises(ImportError, self._checkSMTP)
        self.assertRaises(ImportError, self._checkIMAP)
        # Restore sys.modules
        del sys.modules["smtplib"]
        del sys.modules["imaplib"]
        # Then the functions should succeed
        self.assertIsInstance(self._checkSMTP(), types.ModuleType)
        self.assertIsInstance(self._checkIMAP(), types.ModuleType)

    def test_disableAlreadyImportedModule(self) -> None:
        """
        Disabling an already imported module should produce a warning.
        """
        self.assertIsInstance(self._checkSMTP(), types.ModuleType)
        self.assertWarns(
            RuntimeWarning,
            "Module 'smtplib' already imported, disabling anyway.",
            trial.__file__,
            self.config.parseOptions,
            ["--without-module", "smtplib"],
        )
        self.assertRaises(ImportError, self._checkSMTP)


class CoverageTests(unittest.SynchronousTestCase):
    """
    Tests for the I{coverage} option.
    """

    if getattr(sys, "gettrace", None) is None:
        skip = "Cannot test trace hook installation without inspection API."

    def setUp(self) -> None:
        """
        Arrange for the current trace hook to be restored when the
        test is complete.
        """
        self.addCleanup(sys.settrace, sys.gettrace())

    def test_tracerInstalled(self) -> None:
        """
        L{trial.Options} handles C{"--coverage"} by installing a trace
        hook to record coverage information.
        """
        options = trial.Options()
        options.parseOptions(["--coverage"])
        assert options.tracer is not None
        self.assertEqual(
            sys.gettrace(),
            # the globaltrace attribute of trace.Trace is undocumented
            options.tracer.globaltrace,  # type: ignore[attr-defined]
        )

    def test_coverdirDefault(self) -> None:
        """
        L{trial.Options.coverdir} returns a L{FilePath} based on the default
        for the I{temp-directory} option if that option is not specified.
        """
        options = trial.Options()
        self.assertEqual(
            options.coverdir(),
            FilePath(".").descendant([options["temp-directory"], "coverage"]),
        )

    def test_coverdirOverridden(self) -> None:
        """
        If a value is specified for the I{temp-directory} option,
        L{trial.Options.coverdir} returns a child of that path.
        """
        path = self.mktemp()
        options = trial.Options()
        options.parseOptions(["--temp-directory", path])
        self.assertEqual(options.coverdir(), FilePath(path).child("coverage"))


class OptionsTests(unittest.TestCase):
    """
    Tests for L{trial.Options}.
    """

    def setUp(self) -> None:
        """
        Build an L{Options} object to be used in the tests.
        """
        self.options = trial.Options()

    def test_getWorkerArguments(self) -> None:
        """
        C{_getWorkerArguments} discards options like C{random} as they only
        matter in the manager, and forwards options like C{recursionlimit} or
        C{disablegc}.
        """
        self.addCleanup(sys.setrecursionlimit, sys.getrecursionlimit())
        if gc.isenabled():
            self.addCleanup(gc.enable)

        self.options.parseOptions(
            ["--recursionlimit", "2000", "--random", "4", "--disablegc"]
        )
        args = self.options._getWorkerArguments()
        self.assertIn("--disablegc", args)
        args.remove("--disablegc")
        self.assertEqual(["--recursionlimit", "2000"], args)

    def test_jobsConflictWithDebug(self) -> None:
        """
        C{parseOptions} raises a C{UsageError} when C{--debug} is passed along
        C{--jobs} as it's not supported yet.

        @see: U{http://twistedmatrix.com/trac/ticket/5825}
        """
        error = self.assertRaises(
            UsageError, self.options.parseOptions, ["--jobs", "4", "--debug"]
        )
        self.assertEqual("You can't specify --debug when using --jobs", str(error))

    def test_jobsConflictWithProfile(self) -> None:
        """
        C{parseOptions} raises a C{UsageError} when C{--profile} is passed
        along C{--jobs} as it's not supported yet.

        @see: U{http://twistedmatrix.com/trac/ticket/5827}
        """
        error = self.assertRaises(
            UsageError, self.options.parseOptions, ["--jobs", "4", "--profile"]
        )
        self.assertEqual("You can't specify --profile when using --jobs", str(error))

    def test_jobsConflictWithDebugStackTraces(self) -> None:
        """
        C{parseOptions} raises a C{UsageError} when C{--debug-stacktraces} is
        passed along C{--jobs} as it's not supported yet.

        @see: U{http://twistedmatrix.com/trac/ticket/5826}
        """
        error = self.assertRaises(
            UsageError,
            self.options.parseOptions,
            ["--jobs", "4", "--debug-stacktraces"],
        )
        self.assertEqual(
            "You can't specify --debug-stacktraces when using --jobs", str(error)
        )

    def test_orderConflictWithRandom(self) -> None:
        """
        C{parseOptions} raises a C{UsageError} when C{--order} is passed along
        with C{--random}.
        """
        error = self.assertRaises(
            UsageError,
            self.options.parseOptions,
            ["--order", "alphabetical", "--random", "1234"],
        )
        self.assertEqual("You can't specify --random when using --order", str(error))


class MakeRunnerTests(unittest.TestCase):
    """
    Tests for the L{_makeRunner} helper.
    """

    def setUp(self) -> None:
        self.options = trial.Options()

    def test_jobs(self) -> None:
        """
        L{_makeRunner} returns a L{DistTrialRunner} instance when the C{--jobs}
        option is passed.  The L{DistTrialRunner} knows how many workers to
        run and the C{workerArguments} to pass to them.
        """
        self.options.parseOptions(["--jobs", "4", "--force-gc"])
        runner = trial._makeRunner(self.options)
        assert isinstance(runner, DistTrialRunner)
        self.assertIsInstance(runner, DistTrialRunner)
        self.assertEqual(4, runner._maxWorkers)
        self.assertEqual(["--force-gc"], runner._workerArguments)

    def test_dryRunWithJobs(self) -> None:
        """
        L{_makeRunner} returns a L{TrialRunner} instance in C{DRY_RUN} mode
        when the C{--dry-run} option is passed, even if C{--jobs} is set.
        """
        self.options.parseOptions(["--jobs", "4", "--dry-run"])
        runner = trial._makeRunner(self.options)
        assert isinstance(runner, TrialRunner)
        self.assertIsInstance(runner, TrialRunner)
        self.assertEqual(TrialRunner.DRY_RUN, runner.mode)

    def test_DebuggerNotFound(self) -> None:
        namedAny = trial.reflect.namedAny

        def namedAnyExceptdoNotFind(fqn: str) -> object:
            if fqn == "doNotFind":
                raise trial.reflect.ModuleNotFound(fqn)
            return namedAny(fqn)

        self.patch(trial.reflect, "namedAny", namedAnyExceptdoNotFind)

        options = trial.Options()
        options.parseOptions(["--debug", "--debugger", "doNotFind"])

        self.assertRaises(trial._DebuggerNotFound, trial._makeRunner, options)

    def test_exitfirst(self) -> None:
        """
        Passing C{--exitfirst} wraps the reporter with a
        L{reporter._ExitWrapper} that stops on any non-success.
        """
        self.options.parseOptions(["--exitfirst"])
        runner = trial._makeRunner(self.options)
        assert isinstance(runner, TrialRunner)
        self.assertTrue(runner._exitFirst)


class RunTests(unittest.TestCase):
    """
    Tests for the L{run} function.
    """

    def setUp(self) -> None:
        # don't re-parse cmdline options, because if --reactor was passed to
        # the test run trial will try to restart the (already running) reactor
        self.patch(trial.Options, "parseOptions", lambda self: None)

    def test_debuggerNotFound(self) -> None:
        """
        When a debugger is not found, an error message is printed to the user.

        """

        def _makeRunner(*args: object, **kwargs: object) -> None:
            raise trial._DebuggerNotFound("foo")

        self.patch(trial, "_makeRunner", _makeRunner)

        try:
            trial.run()
        except SystemExit as e:
            self.assertIn("foo", str(e))
        else:
            self.fail("Should have exited due to non-existent debugger!")


class TestArgumentOrderTests(unittest.TestCase):
    """
    Tests for the order-preserving behavior on provided command-line tests.
    """

    def setUp(self) -> None:
        self.config = trial.Options()
        self.loader = TestLoader()

    def test_preserveArgumentOrder(self) -> None:
        """
        Multiple tests passed on the command line are not reordered.
        """
        tests = [
            "twisted.trial.test.test_tests",
            "twisted.trial.test.test_assertions",
            "twisted.trial.test.test_deferred",
        ]
        self.config.parseOptions(tests)

        suite = trial._getSuite(self.config)
        names = testNames(suite)

        expectedSuite = TestSuite(map(self.loader.loadByName, tests))
        expectedNames = testNames(expectedSuite)

        self.assertEqual(names, expectedNames)


class OrderTests(unittest.TestCase):
    """
    Tests for the --order option.
    """

    def setUp(self) -> None:
        self.config = trial.Options()

    def test_alphabetical(self) -> None:
        """
        --order=alphabetical causes trial to run tests alphabetically within
        each test case.
        """
        self.config.parseOptions(
            ["--order", "alphabetical", "twisted.trial.test.ordertests.FooTest"]
        )

        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        self.assertEqual(
            testNames(suite),
            [
                "twisted.trial.test.ordertests.FooTest.test_first",
                "twisted.trial.test.ordertests.FooTest.test_fourth",
                "twisted.trial.test.ordertests.FooTest.test_second",
                "twisted.trial.test.ordertests.FooTest.test_third",
            ],
        )

    def test_alphabeticalModule(self) -> None:
        """
        --order=alphabetical causes trial to run test classes within a given
        module alphabetically.
        """
        self.config.parseOptions(
            ["--order", "alphabetical", "twisted.trial.test.ordertests"]
        )
        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        self.assertEqual(
            testNames(suite),
            [
                "twisted.trial.test.ordertests.BarTest.test_bar",
                "twisted.trial.test.ordertests.BazTest.test_baz",
                "twisted.trial.test.ordertests.FooTest.test_first",
                "twisted.trial.test.ordertests.FooTest.test_fourth",
                "twisted.trial.test.ordertests.FooTest.test_second",
                "twisted.trial.test.ordertests.FooTest.test_third",
            ],
        )

    def test_alphabeticalPackage(self) -> None:
        """
        --order=alphabetical causes trial to run test modules within a given
        package alphabetically, with tests within each module alphabetized.
        """
        self.config.parseOptions(["--order", "alphabetical", "twisted.trial.test"])
        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        names = testNames(suite)
        self.assertTrue(names, msg="Failed to load any tests!")
        self.assertEqual(names, sorted(names))

    def test_toptobottom(self) -> None:
        """
        --order=toptobottom causes trial to run test methods within a given
        test case from top to bottom as they are defined in the body of the
        class.
        """
        self.config.parseOptions(
            ["--order", "toptobottom", "twisted.trial.test.ordertests.FooTest"]
        )

        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        self.assertEqual(
            testNames(suite),
            [
                "twisted.trial.test.ordertests.FooTest.test_first",
                "twisted.trial.test.ordertests.FooTest.test_second",
                "twisted.trial.test.ordertests.FooTest.test_third",
                "twisted.trial.test.ordertests.FooTest.test_fourth",
            ],
        )

    def test_toptobottomModule(self) -> None:
        """
        --order=toptobottom causes trial to run test classes within a given
        module from top to bottom as they are defined in the module's source.
        """
        self.config.parseOptions(
            ["--order", "toptobottom", "twisted.trial.test.ordertests"]
        )
        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        self.assertEqual(
            testNames(suite),
            [
                "twisted.trial.test.ordertests.FooTest.test_first",
                "twisted.trial.test.ordertests.FooTest.test_second",
                "twisted.trial.test.ordertests.FooTest.test_third",
                "twisted.trial.test.ordertests.FooTest.test_fourth",
                "twisted.trial.test.ordertests.BazTest.test_baz",
                "twisted.trial.test.ordertests.BarTest.test_bar",
            ],
        )

    def test_toptobottomPackage(self) -> None:
        """
        --order=toptobottom causes trial to run test modules within a given
        package alphabetically, with tests within each module run top to
        bottom.
        """
        self.config.parseOptions(["--order", "toptobottom", "twisted.trial.test"])
        loader = trial._getLoader(self.config)
        suite = loader.loadByNames(self.config["tests"])

        names = testNames(suite)
        # twisted.trial.test.test_module, so split and key on the first 4 to
        # get stable alphabetical sort on those
        self.assertEqual(
            names,
            sorted(names, key=lambda name: name.split(".")[:4]),
        )

    def test_toptobottomMissingSource(self) -> None:
        """
        --order=toptobottom detects the source line of methods from modules
        whose source file is missing.
        """
        tempdir = self.mktemp()
        package = FilePath(tempdir).child("twisted_toptobottom_temp")
        package.makedirs()
        package.child("__init__.py").setContent(b"")
        package.child("test_missing.py").setContent(
            textwrap.dedent(
                """
        from twisted.trial.unittest import TestCase
        class TestMissing(TestCase):
            def test_second(self) -> None: pass
            def test_third(self) -> None: pass
            def test_fourth(self) -> None: pass
            def test_first(self) -> None: pass
        """
            ).encode("utf8")
        )
        pathEntry = package.parent().path
        sys.path.insert(0, pathEntry)
        self.addCleanup(sys.path.remove, pathEntry)
        from twisted_toptobottom_temp import test_missing  # type: ignore[import]

        self.addCleanup(sys.modules.pop, "twisted_toptobottom_temp")
        self.addCleanup(sys.modules.pop, test_missing.__name__)
        package.child("test_missing.py").remove()

        self.config.parseOptions(
            ["--order", "toptobottom", "twisted.trial.test.ordertests"]
        )
        loader = trial._getLoader(self.config)
        suite = loader.loadModule(test_missing)

        self.assertEqual(
            testNames(suite),
            [
                "twisted_toptobottom_temp.test_missing.TestMissing.test_second",
                "twisted_toptobottom_temp.test_missing.TestMissing.test_third",
                "twisted_toptobottom_temp.test_missing.TestMissing.test_fourth",
                "twisted_toptobottom_temp.test_missing.TestMissing.test_first",
            ],
        )

    def test_unknownOrder(self) -> None:
        """
        An unknown order passed to --order raises a L{UsageError}.
        """

        self.assertRaises(
            UsageError, self.config.parseOptions, ["--order", "I don't exist"]
        )


class HelpOrderTests(unittest.TestCase):
    """
    Tests for the --help-orders flag.
    """

    def test_help_ordersPrintsSynopsisAndQuits(self) -> None:
        """
        --help-orders prints each of the available orders and then exits.
        """
        self.patch(sys, "stdout", stdout := StringIO())

        exc = self.assertRaises(
            SystemExit, trial.Options().parseOptions, ["--help-orders"]
        )
        self.assertEqual(exc.code, 0)

        output = stdout.getvalue()

        msg = "%r with its description not properly described in %r"
        for orderName, (orderDesc, _) in trial._runOrders.items():
            match = re.search(
                f"{re.escape(orderName)}.*{re.escape(orderDesc)}",
                output,
            )

            self.assertTrue(match, msg=msg % (orderName, output))
