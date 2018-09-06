Troubleshooting
===============


Installing lxml on Mac
----------------------

Traceback::

    Getting distribution for 'lxml==3.6.0'.
    Building lxml version 3.6.0.
    Building without Cython.
    Using build configuration of libxslt 1.1.29
    Building against libxml2/libxslt in the following directory: /Library/Developer/CommandLineTools/SDKs/MacOSX10.14.sdk/usr/lib
    ld: file not found: /usr/lib/system/libsystem_containermanager.dylib for architecture x86_64
    clang: error: linker command failed with exit code 1 (use -v to see invocation)
    error: Setup script exited with error: command 'gcc' failed with exit status 1
    An error occurred when trying to install /var/folders/jq/6tgjjm2s36dcf30zb3_n29dc0000gn/T/tmpMTD8XUget_dist/lxml-3.6.0.tar.gz. Look above this message for any errors that were output by easy_install.
    While:
      Installing instance.
      Getting distribution for 'lxml==3.6.0'.

    An internal error occurred due to a bug in either zc.buildout or in a
    recipe being used:
    Traceback (most recent call last):
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/buildout.py", line 2128, in main
        getattr(buildout, command)(args)
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/buildout.py", line 798, in install
        installed_files = self[part]._call(recipe.install)
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/buildout.py", line 1558, in _call
        return f()
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/plone.recipe.zope2instance-4.3-py2.7.egg/plone/recipe/zope2instance/__init__.py", line 113, in install
        installed.extend(self.install_scripts())
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/plone.recipe.zope2instance-4.3-py2.7.egg/plone/recipe/zope2instance/__init__.py", line 620, in install_scripts
        requirements, ws = self.egg.working_set(['plone.recipe.zope2instance'])
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.recipe.egg-1.3.2-py2.7.egg/zc/recipe/egg/egg.py", line 101, in working_set
        **kw)
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/easy_install.py", line 957, in install
        return installer.install(specs, working_set)
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/easy_install.py", line 682, in install
        for dist in self._get_dist(requirement, ws):
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/easy_install.py", line 574, in _get_dist
        dists = [_move_to_eggs_dir_and_compile(dist, self._dest)]
      File "/Users/rbartl/develop/ridingbytes/bhp.lims/eggs/zc.buildout-2.12.1-py2.7.egg/zc/buildout/easy_install.py", line 1740, in _move_to_eggs_dir_and_compile
        [tmp_loc] = glob.glob(os.path.join(tmp_dest, '*'))
    ValueError: need more than 0 values to unpack

Install `lxml` explicitly::

    ./bin/buildout install lxml
