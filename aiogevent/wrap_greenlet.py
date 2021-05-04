import asyncio

import gevent


def wrap_greenlet(gt, loop=None):
    """Wrap a greenlet into a Future object.

    The Future object waits for the completion of a greenlet. The result or the
    exception of the greenlet will be stored in the Future object.

    Greenlet of greenlet and gevent modules are supported: gevent.greenlet
    and greenlet.greenlet.

    The greenlet must be wrapped before its execution starts. If the greenlet
    is running or already finished, an exception is raised.

    For gevent.Greenlet, the _run attribute must be set. For greenlet.greenlet,
    the run attribute must be set.
    """
    fut = asyncio.Future(loop=loop)

    if not isinstance(gt, greenlet.greenlet):
        raise TypeError("greenlet.greenlet or gevent.greenlet request, not %s"
                        % type(gt))

    if gt.dead:
        raise RuntimeError("wrap_greenlet: the greenlet already finished")

    if isinstance(gt, gevent.Greenlet):
        # Don't use gevent.Greenlet.__bool__() because since gevent 1.0, a
        # greenlet is True if it already starts, and gevent.spawn() starts
        # the greenlet just after its creation.
        if _PY3:
            is_running = greenlet.greenlet.__bool__
        else:
            is_running = greenlet.greenlet.__nonzero__
        if is_running(gt):
            raise RuntimeError("wrap_greenlet: the greenlet is running")

        try:
            orig_func = gt._run
        except AttributeError:
            raise RuntimeError("wrap_greenlet: the _run attribute "
                               "of the greenlet is not set")
        def wrap_func(*args, **kw):
            try:
                result = orig_func(*args, **kw)
            except Exception as exc:
                fut.set_exception(exc)
            else:
                fut.set_result(result)
        gt._run = wrap_func
    else:
        if gt:
            raise RuntimeError("wrap_greenlet: the greenlet is running")

        try:
            orig_func = gt.run
        except AttributeError:
            raise RuntimeError("wrap_greenlet: the run attribute "
                               "of the greenlet is not set")
        def wrap_func(*args, **kw):
            try:
                result = orig_func(*args, **kw)
            except Exception as exc:
                fut.set_exception(exc)
            else:
                fut.set_result(result)
        gt.run = wrap_func
    return fut

