pydgutils (PYthon DownGrade UTILitieS)
=========================================

Preface
-----------------------------------------

This library use for compatilbe purpose.

It provided a simple method to preprocess sources to python2 syntax (if using python2) and do nothing while using python3.

So that you could write your project in python3 syntax and install on python2 without any changes, all jobs are done by 3to2 module which we depends on.

Usage
-----------------------------------------

Copy the pydgutils_bootstrap.py (in pydgutils source package) to the same directory of your setup.py, then modify your setup.py like this:

::

    from pydgutils_bootstrap import use_pydgutils
    use_pydgutils()
    
    import pydgutils
        
    # Convert source to v2.x if we are using python 2.x.
    source_dir = pydgutils.process()
    
    # Exclude the original source package, only accept the preprocessed package!
    packages = find_packages(where=source_dir)

    ...

