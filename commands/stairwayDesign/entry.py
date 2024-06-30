import adsk.cam, adsk.core, adsk.fusion
import os
from ...    import config
from ...lib import fusion360utils as futil

from .stairwayDesign import *

# -----------------------------------------------------------------------------------


app = adsk.core.Application.get()
ui  = app.userInterface

# -----------------------------------------------------------------------------------

CMD_ID            = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmd_stairway_design'
CMD_NAME          = 'Stairway360'
CMD_DESCRIPTION   = 'Design a stairway with balanced steps'

# -----------------------------------------------------------------------------------

WORKSPACE_ID      = 'FusionSolidEnvironment'
PANEL_ID          = 'SolidCreatePanel'
COMMAND_BESIDE_ID = 'FusionCreateNewComponentCommand'
IS_PROMOTED       = True
ICON_FOLDER       = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'resources', '' )

# -----------------------------------------------------------------------------------

local_handlers = []

stairway = StairwayDesign()


# -----------------------------------------------------------------------------------

def start():
    "Executed when add-in is run."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : start()' )

    # -----------------------------------------------------------------------------------

    try:
        if ui.commandDefinitions.itemById( CMD_ID ) != None:
            futil.log( f' > : {CMD_NAME} is already executed' )
            stop()
            return
        
        # futil.log( f'ICON_FOLDER : {ICON_FOLDER}' )

        # Create a command Definition.
        cmd_def = ui.commandDefinitions.addButtonDefinition( CMD_ID, CMD_NAME, CMD_DESCRIPTION, ICON_FOLDER )

    except RuntimeError: 
        futil.log( f'RuntimeError : {CMD_NAME} is already executed' )
        stop()
        return 
     

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler( cmd_def.commandCreated, command_created )

    # -----------------------------------------------------------------------------------

    workspace = ui.workspaces.itemById( WORKSPACE_ID )
    panel     = workspace.toolbarPanels.itemById( PANEL_ID )
    
    control   = panel.controls.addCommand( cmd_def, COMMAND_BESIDE_ID, False )
    control.isPromoted = IS_PROMOTED


def stop():
    "Executed when add-in is stopped."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : stop()' )

    # Get the various UI elements for this command
    workspace          = ui.workspaces.itemById( WORKSPACE_ID)
    panel              = workspace.toolbarPanels.itemById( PANEL_ID )
    command_control    = panel.controls.itemById( CMD_ID )
    command_definition = ui.commandDefinitions.itemById( CMD_ID )

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# -----------------------------------------------------------------------------------

def command_created( args: adsk.core.CommandCreatedEventArgs ):
    "Function that is called when a user clicks the corresponding button in the UI. This defines the contents of the command dialog and connects to the command related events."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_created()' )

    # -----------------------------------------------------------------------------------

    # Define

    # args.command.setDialogMinimumSize( 200, 200 )
    # args.command.isOKButtonVisible = True
    # args.command.okButtonText      = 'Valid'
    # args.command.cancelButtonText  = 'Cancel'

    # Add events to handler

    futil.add_handler( args.command.inputChanged,   command_input_changed,  local_handlers = local_handlers )
    # futil.add_handler( args.command.validateInputs, command_validate_input, local_handlers = local_handlers )
    futil.add_handler( args.command.executePreview, command_preview,        local_handlers = local_handlers )
    futil.add_handler( args.command.execute,        command_execute,        local_handlers = local_handlers )
    futil.add_handler( args.command.destroy,        command_destroy,        local_handlers = local_handlers )

    # -----------------------------------------------------------------------------------

    stairway.eventCreated( args )


def command_validate_input( args: adsk.core.ValidateInputsEventArgs ):
    "This event handler is called when the user interacts with any of the inputs in the dialog which allows you to verify that all of the inputs are valid and enables the OK button."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_validate_input()' )

    # -----------------------------------------------------------------------------------

    stairway.eventValidateInput( args )


def command_input_changed( args: adsk.core.InputChangedEventArgs ):
    "This event handler is called when the user changes anything in the command dialog allowing you to modify values of other inputs based on that change."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_input_changed()' )

    # -----------------------------------------------------------------------------------

    #futil.log( f'{CMD_NAME} : > Input Changed Event fired from a change to {changed_input.id}' )

    stairway.eventInputChanged( args )


def command_preview( args: adsk.core.CommandEventArgs ):
    "This event handler is called when the command needs to compute a new preview in the graphics window."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_preview()' )
    
    # -----------------------------------------------------------------------------------

    stairway.eventPreview( args )


def command_execute( args: adsk.core.CustomEventArgs ):
    "This event handler is called when the user clicks the OK button in the command dialog or is immediately called after the created event not command inputs were created for the dialog."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_execute()' )

    # -----------------------------------------------------------------------------------

    stairway.eventExecute( args )


def command_destroy( args: adsk.core.CommandEventArgs ):
    "This event handler is called when the command terminates."

    futil.log( f' ' )
    futil.log( f'{CMD_NAME} : command_destroy' )

    # -----------------------------------------------------------------------------------

    global local_handlers
    local_handlers = []

    # -----------------------------------------------------------------------------------

    stairway.eventDestroy( args )
