from . import commands
from .lib import fusion360utils as futil


def run( context ):
    """This will run the start function in each of your commands as defined in commands/__init__.py"""
    try:
        commands.start()

    except:
        futil.handle_error( 'run' )


def stop( context ):
    """Remove all of the event handlers your app has created"""
    try:
        futil.clear_handlers()

        # This will run the stop function in each of your commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error( 'stop' )