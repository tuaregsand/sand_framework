ERROR:api_gateway.core.config:RAILWAY_ENVIRONMENT_ID: cd0c4fff-597f-4cd3-941e-09a43b3cf54b

ERROR:api_gateway.core.config:RAILWAY_ENVIRONMENT_NAME: production

ERROR:api_gateway.core.config:RAILWAY_GIT_AUTHOR: tuaregsand

ERROR:api_gateway.core.config:RAILWAY_GIT_BRANCH: main

/usr/local/lib/python3.11/site-packages/pydantic/_internal/_config.py:321: UserWarning: Valid config keys have changed in V2:

* 'orm_mode' has been renamed to 'from_attributes'

  warnings.warn(message, UserWarning)

Traceback (most recent call last):

  File "<frozen runpy>", line 198, in _run_module_as_main

  File "<frozen runpy>", line 88, in _run_code

  File "/usr/local/lib/python3.11/site-packages/uvicorn/__main__.py", line 4, in <module>

    uvicorn.main()

  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1161, in __call__

    return self.main(*args, **kwargs)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1082, in main

    rv = self.invoke(ctx)

         ^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1443, in invoke

    return ctx.invoke(self.callback, **ctx.params)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 788, in invoke

    return __callback(*args, **kwargs)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 416, in main

    run(

  File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 587, in run

    server.run()

  File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 61, in run

    return asyncio.run(self.serve(sockets=sockets))

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run

    return runner.run(main)

           ^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run

    return self._loop.run_until_complete(task)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete

    return future.result()

           ^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 68, in serve

    config.load()

  File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 467, in load

    self.loaded_app = import_from_string(self.app)

                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 24, in import_from_string

    raise exc from None

  File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 21, in import_from_string

    module = importlib.import_module(module_str)

             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module

    return _bootstrap._gcd_import(name[level:], package, level)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import

  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load

  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked

  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked

  File "<frozen importlib._bootstrap_external>", line 940, in exec_module

  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed

  File "/app/api_gateway/main.py", line 12, in <module>

    from api_gateway.routes import analytics, devagent, system

  File "/app/api_gateway/routes/system.py", line 5, in <module>

    import psutil

ModuleNotFoundError: No module named 'psutil'
