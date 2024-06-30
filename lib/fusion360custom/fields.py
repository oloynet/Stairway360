import adsk.cam, adsk.core, adsk.fusion
import math, os
from ...lib import fusion360utils as futil

# ------------------------------------------------------------------------------

class Fields:

    def __init__( self, fields: dict = {} ):

        self.fields = fields

    # ------------------------------------------------------------------------------

    def getValueByID( self,
            id:    str,
            label: str = None,
            value: int | float | complex | bool | str = None,
            unit : str = None
        ):

        # futil.log( f' > : getValueByID()' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]  if( label == None )  else label
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputUnit  = self.fields[ id ][ 'unit' ]   if( unit  == None )  else unit

        # futil.log( ' >' )
        # futil.log( ' ------------------------------------------' )
        # futil.log( ' >' )
        # futil.log( f' > getValueByID : inputId    = {inputId}' )
        # futil.log( f' > getValueByID : inputLabel = {inputLabel}' )
        # futil.log( f' > getValueByID : inputValue = {inputValue}' )
        # futil.log( f' > getValueByID : inputUnit  = {inputUnit}' )

        app = adsk.core.Application.get()
        design:       adsk.fusion.Design     = app.activeProduct
        unitsManager: adsk.core.UnitsManager = design.unitsManager


        if isinstance( inputValue, bool ):
            # futil.log( f' > getValueByID : isinstance == bool ***************************' )

            value = adsk.core.ValueInput.createByReal( inputValue )
            unit  = '' # force with no unit

        elif isinstance( inputValue, int ):
            # futil.log( f' > getValueByID : isinstance == int ***************************' )

            value = adsk.core.ValueInput.createByReal( inputValue )
            unit  = inputUnit

        elif isinstance( inputValue, float ):
            # futil.log( f' > getValueByID : isinstance == float ***************************' )

            value = adsk.core.ValueInput.createByReal( inputValue )
            unit  = inputUnit

        elif isinstance( inputValue, str ):
            # futil.log( f' > getValueByID : isinstance == str ***************************' )

            if inputValue == '' and inputUnit in ( 'deg', 'degree', 'rad', 'mm', 'cm', '' ):
                inputValue = '0'

            value = adsk.core.ValueInput.createByString( inputValue )
            unit  = inputUnit

        else:
            # futil.log( f' > getValueByID : *************************' )
            return False


        # valueType = value.valueType
        # futil.log( f' > readParameterByIDValue : valueType   = {valueType}' )

        match value.valueType:

            case adsk.core.ValueTypes.StringValueType:

                if( inputUnit == 'bool' ):
                    resultVar = bool( unitsManager.evaluateExpression( value.stringValue, '' ) )
                    # futil.log( f' > getValueByID : resultVar  = {resultVar}' )

                else:
                    resultVar = unitsManager.evaluateExpression( value.stringValue, inputUnit )
                    # futil.log( f' > getValueByID : resultVar  = {resultVar}' )

                    if isinstance( inputValue, int ):
                        resultVar = int( round( resultVar, 0 ) )

            case adsk.core.ValueTypes.RealValueType:

                if( inputUnit == 'bool' ):
                    resultVar = bool( value.realValue )
                    # futil.log( f' > getValueByID : resultVar  = {resultVar}' )

                else:
                    resultVar = value.realValue
                    # futil.log( f' > getValueByID : resultVar  = {resultVar}' )

                    if isinstance( inputValue, int ):
                        resultVar = int( round( resultVar, 0 ) )

            case adsk.core.ValueTypes.BooleanValueType:

                resultVar = value.booleanValue
                # futil.log( f' > getValueByID : resultVar  = {resultVar}' )

            case _:
                return None

        return resultVar


    # ------------------------------------------------------------------------------
    # FIELDS
    # ------------------------------------------------------------------------------

    def createTabCommandInput( self,
            ref:   adsk.core.CommandInputs,
            id:    str,

        ) -> adsk.core.TabCommandInput:

        futil.log( f' > : createTabCommandInput( \'{id}\' )' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.TabCommandInput = ref.addTabCommandInput(
            inputId,
            inputLabel

            # id   = inputId,
            # name = inputLabel
        )

        # ------------------------------------------------------------------------------

        return resultInput


    def createGroupCommandInput( self,
            ref:        adsk.core.CommandInputs,
            id:         str,
            value:      bool = None

        ) -> adsk.core.GroupCommandInput:

        futil.log( f' > : createGroupCommandInput( \'{id}\' ) = {value}' )

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.GroupCommandInput = ref.addGroupCommandInput(
            id   = id,
            name = self.fields[ id ][ 'label' ]
        )

        # ------------------------------------------------------------------------------

        resultInput.isExpanded = self.fields[ id ][ 'value' ]  if( value == None )  else value

        if 'isCheckBox' in self.fields[ id ].keys():
            resultInput.isEnabledCheckBoxDisplayed = self.fields[ id ][ 'isCheckBox' ]
            resultInput.isEnabledCheckBoxChecked   = resultInput.isExpanded

        # if 'isEnabledCheckBoxDisplayed' in self.fields[ id ].keys():
        #     resultInput.isEnabledCheckBoxDisplayed = self.fields[ id ][ 'isEnabledCheckBoxDisplayed' ]

        if 'tooltip'    in self.fields[ id ].keys():
            resultInput.tooltip = self.fields[ id ][ 'tooltip' ]

        # ------------------------------------------------------------------------------

        return resultInput


    def createValueCommandInput( self,
            ref:   adsk.core.CommandInputs,
            id:    str,
            value: bool = None
        ) -> adsk.core.ValueCommandInput:

        futil.log( f' > : createValueCommandInput( \'{id}\' ) = {value}' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]
        inputUnit  = self.fields[ id ][ 'unit' ]
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value

        if isinstance( inputValue, bool ):
            initialValue = adsk.core.ValueInput.createByBoolean( inputValue )

        elif isinstance( inputValue, int ):
            initialValue = adsk.core.ValueInput.createByReal( inputValue )

        elif isinstance( inputValue, float ):
            initialValue = adsk.core.ValueInput.createByReal( inputValue )

        elif isinstance( inputValue, str ):
            initialValue = adsk.core.ValueInput.createByString( inputValue )

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.ValueCommandInput = ref.addValueInput(
            id           = inputId,
            name         = inputLabel,
            unitType     = inputUnit,
            initialValue = initialValue
        )

        # ------------------------------------------------------------------------------

        if 'tooltip'         in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description'     in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        # ------------------------------------------------------------------------------

        if 'mini'            in self.fields[ id ].keys():
            resultInput.minimumValue       = self.fields[ id ][ 'mini' ]

        if 'isMiniLimited'   in self.fields[ id ].keys():
            resultInput.isMinimumLimited   = self.fields[ id ][ 'isMiniLimited' ]

        if 'isMiniInclusive' in self.fields[ id ].keys():
            resultInput.isMinimumInclusive = self.fields[ id ][ 'isMiniInclusive' ]

        # ------------------------------------------------------------------------------

        if 'maxi'            in self.fields[ id ].keys():
            resultInput.maximumValue       = self.fields[ id ][ 'maxi' ]

        if 'isMaxiLimited'   in self.fields[ id ].keys():
            resultInput.isMaximumLimited   = self.fields[ id ][ 'isMaxiLimited' ]

        if 'isMaxiInclusive' in self.fields[ id ].keys():
            resultInput.isMaximumInclusive = self.fields[ id ][ 'isMaxiInclusive' ]

        # ------------------------------------------------------------------------------

        return resultInput


    def createBoolValueCommandInput( self,
            ref:            adsk.core.CommandInputs,
            id:             str,
            value:          bool = None,
        ) -> adsk.core.BoolValueCommandInput:

        futil.log( f' > : createBoolValueCommandInput( \'{id}\' ) = {value}' )

        # ------------------------------------------------------------------------------

        inputId             = id
        inputLabel          = self.fields[ id ][ 'label' ]
        inputIsCheckBox     = self.fields[ id ][ 'isCheckBox' ]
        inputResourceFolder = self.fields[ id ][ 'resourceFolder' ]
        inputValue          = self.fields[ id ][ 'value' ]   if( value == None )  else value


        if inputResourceFolder != '':
            inputResourceFolder = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), inputResourceFolder, '' )


        # futil.log( f' > : : inputIsCheckBox     = {inputIsCheckBox}' )
        # futil.log( f' > : : inputResourceFolder = {inputResourceFolder}' )
        # futil.log( f' > : : inputValue          = {inputValue}' )

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.BoolValueCommandInput = ref.addBoolValueInput( 

            # TODO problem with named parameters in addBoolValueInput
            # id             = inputId,
            # name           = inputLabel,
            # isCheckBox     = inputIsCheckBox,
            # resourceFolder = inputResourceFolder,
            # initialValue   = inputValue,

            inputId,
            inputLabel,
            inputIsCheckBox,
            inputResourceFolder,
            inputValue
        )

        # ------------------------------------------------------------------------------

        if 'tooltip'     in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description' in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        # ------------------------------------------------------------------------------

        return resultInput


    def createTextBoxCommandInput( self,
            ref:        adsk.core.CommandInputs,
            id:         str,
            value:      str  = None,
        ) -> adsk.core.TextBoxCommandInput:

        futil.log( f' > : createTextBoxCommandInput( \'{id}\' ) = {value}' )

        # ------------------------------------------------------------------------------

        inputId         = id
        inputLabel      = self.fields[ id ][ 'label' ]
        inputValue      = self.fields[ id ][ 'value' ]      if( value  == None )  else value
        inputNumRows    = self.fields[ id ][ 'numRows' ]     
        inputIsReadOnly = self.fields[ id ][ 'isReadOnly' ]

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.TextBoxCommandInput = ref.addTextBoxCommandInput(
            id            = inputId,
            name          = inputLabel,
            formattedText = inputValue,
            numRows       = inputNumRows,
            isReadOnly    = inputIsReadOnly
        )

        # ------------------------------------------------------------------------------

        if 'tooltip'     in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description' in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        # ------------------------------------------------------------------------------

        return resultInput


    def createFloatSliderCommandInput( self,
            ref:             adsk.core.CommandInputs,
            id:              str,
            value:           float = None,
            mini:            float = None,
            maxi:            float = None
        ) -> adsk.core.FloatSliderCommandInput:

        futil.log( f' > : createFloatSliderCommandInput( \'{id}\' ) = {value}, mini = {mini}, maxi = {maxi}' )

        # ------------------------------------------------------------------------------

        inputId              = id
        inputLabel           = self.fields[ id ][ 'label' ]
        inputValue           = self.fields[ id ][ 'value' ]          if( value == None )  else value
        inputUnit            = self.fields[ id ][ 'unit' ]
        inputMini            = self.fields[ id ][ 'mini' ]           if( mini  == None )  else mini
        inputMaxi            = self.fields[ id ][ 'maxi' ]           if( maxi  == None )  else maxi
        inputHasTwoSliders   = self.fields[ id ][ 'hasTwoSliders' ]

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.FloatSliderCommandInput = ref.addFloatSliderCommandInput(
            id            = inputId,
            name          = inputLabel,
            unitType      = inputUnit,
            min           = inputMini,
            max           = inputMaxi,
            hasTwoSliders = inputHasTwoSliders
        )

        # ------------------------------------------------------------------------------

        if 'tooltip'         in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description'     in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        if 'isMiniLimited'   in self.fields[ id ].keys():
            resultInput.isMinimumLimited   = self.fields[ id ][ 'isMiniLimited' ]

        if 'isMiniInclusive' in self.fields[ id ].keys():
            resultInput.isMinimumInclusive = self.fields[ id ][ 'isMiniInclusive' ]

        if 'isMaxiLimited'   in self.fields[ id ].keys():
            resultInput.isMaximumLimited   = self.fields[ id ][ 'isMaxiLimited' ]

        if 'isMaxiInclusive' in self.fields[ id ].keys():
            resultInput.isMaximumInclusive = self.fields[ id ][ 'isMaxiInclusive' ]

        if 'step'            in self.fields[ id ].keys():
            resultInput.spinStep = self.fields[ id ][ 'step' ]

        # ------------------------------------------------------------------------------

        resultInput.valueOne = inputValue

        # ------------------------------------------------------------------------------

        return resultInput


    def createIntegerSliderCommandInput( self,
            ref:   adsk.core.CommandInputs,
            id:    str,
            value: int = None,
            mini:  int = None,
            maxi:  int = None
        ) -> adsk.core.IntegerSliderCommandInput:

        futil.log( f' > : createIntegerSliderCommandInput( \'{id}\' ) = {value}, mini = {mini}, maxi = {maxi}' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputMini  = self.fields[ id ][ 'mini' ]   if( mini  == None )  else mini
        inputMaxi  = self.fields[ id ][ 'maxi' ]   if( maxi  == None )  else maxi

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.IntegerSliderCommandInput = ref.addIntegerSliderCommandInput(
            id   = inputId,
            name = inputLabel,
            min  = int( round( inputMini, 0 ) ),
            max  = int( round( inputMaxi, 0 ) )
        )

        # ------------------------------------------------------------------------------

        if 'tooltip'     in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description' in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        # ------------------------------------------------------------------------------

        resultInput.valueOne = int( round( inputValue, 0 ) )

        # ------------------------------------------------------------------------------

        return resultInput


    def createIntegerSliderListCommandInput( self,
            ref:   adsk.core.CommandInputs,                                            
            id:    str,
            value: str         = None,
            list:  list[ int ] = None
        ) -> adsk.core.IntegerSliderCommandInput:

        futil.log( f' > : createIntegerSliderListCommandInput( \'{id}\' ) = {value}, list = {list}' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputList  = self.fields[ id ][ 'list' ]   if( list  == None )  else list

        # ------------------------------------------------------------------------------

        resultInput: adsk.core.IntegerSliderCommandInput = ref.addIntegerSliderListCommandInput(
            id           = inputId,
            name         = inputLabel,
            valueList    = inputList
        )

        # ------------------------------------------------------------------------------

        if 'tooltip' in self.fields[ id ].keys():
            resultInput.tooltip            = self.fields[ id ][ 'tooltip' ]

        if 'description' in self.fields[ id ].keys():
            resultInput.tooltipDescription = self.fields[ id ][ 'description' ]

        # ------------------------------------------------------------------------------

        resultInput.valueOne = int( round( inputValue, 0 ) )

        # ------------------------------------------------------------------------------

        return resultInput


    # ------------------------------------------------------------------------------
    # PARAMETERS
    # ------------------------------------------------------------------------------

    def readParameterByID( self,
            id:    str,
            label: str = None,
            value: int | float | complex | bool | str = None,
            unit : str = None
        ):

        futil.log( f' > : readParameterByID( \'{id}\' )' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]  if( label == None )  else label
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputUnit  = self.fields[ id ][ 'unit' ]   if( unit  == None )  else unit

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        userParameters: adsk.fusion.UserParameters = design.userParameters
        unitsManager:   adsk.core.UnitsManager     = design.unitsManager

        # get parameter

        paramItem = userParameters.itemByName( inputId )

        # if not exists, get default

        if paramItem == None:
            return self.getValueByID( id, label, value, unit )

        # ------------------------------------------------------------------------------



        if( inputUnit == 'bool' ):
            resultVar = bool( unitsManager.evaluateExpression( paramItem.expression, '' ) )
        else:
            resultVar = unitsManager.evaluateExpression( paramItem.expression, inputUnit )

            if isinstance( inputValue, int ):
                resultVar = int( round( resultVar, 0 ) )

        # futil.log( f' > createOrGetParameterByID : resultVar      = {resultVar}' )
        # futil.log( f' > ------------------------' )
        # futil.log( f' >' )

        return resultVar


    def saveParameterByID( self,
            id:    str,
            label: str = None,
            value: int | float | complex | bool | str = None,
            unit : str = None
    ):
        # futil.log( f' > : saveParameterByID()' )

        # ------------------------------------------------------------------------------

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]  if( label == None )  else label
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputUnit  = self.fields[ id ][ 'unit' ]   if( unit  == None )  else unit

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        userParameters = design.userParameters
        #unitsMgr   = design.unitsManager

        param = userParameters.itemByName( inputId )

        if param:
            if inputUnit == '':
                param.expression = '{}' . format( inputValue )
            elif inputUnit == 'mm':
                param.expression = '{} mm' . format( inputValue * 10 )
            elif inputUnit == 'cm':
                param.expression = '{} cm' . format( inputValue )
            elif inputUnit in ( 'deg', 'degree' ):
                param.expression = '{} deg' . format( math.degrees( inputValue ) )

            return True

        else:

            if isinstance( inputValue, bool ):

                # futil.log( f' > createOrGetParameterByID : isinstance == bool' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = '' # force with no unit

            elif isinstance( inputValue, int ):

                # futil.log( f' > createOrGetParameterByID : isinstance == int' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = inputUnit

            elif isinstance( inputValue, float ):

                #futil.log( f' > createOrGetParameterByID : isinstance == float' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = inputUnit

            elif isinstance( inputValue, str ):

                # futil.log( f' > createOrGetParameterByID : isinstance == str' )

                if inputValue == '' and inputUnit in ( 'deg', 'degree', 'rad', 'mm', 'cm', '' ):
                    inputValue = '0'

                value = adsk.core.ValueInput.createByString( inputValue )
                unit  = inputUnit

            else:

                # futil.log( f' > createOrGetParameterByID : *************************' )
                return False

            paramItem = userParameters.add( inputId, value, unit, inputLabel )

        return True


    # ------------------------------------------------------------------------------

    def createOrGetParameterByID( self,
            id:    str,
            label: str = None,
            value: int | float | complex | bool | str = None,
            unit : str = None
        ):

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]  if( label ) == None  else label
        inputValue = self.fields[ id ][ 'value' ]  if( value ) == None  else value
        inputUnit  = self.fields[ id ][ 'unit' ]   if( unit  ) == None  else unit

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        userParameters: adsk.fusion.UserParameters = design.userParameters
        unitsManager:  adsk.core.UnitsManager      = design.unitsManager

        # get parameter
        paramItem = userParameters.itemByName( inputId )

        # futil.log( f' > createOrGetParameterByID : paramItem      = {paramItem}' )

        if paramItem == None:

            if isinstance( inputValue, bool ):

                # futil.log( f' > createOrGetParameterByID : isinstance == bool' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = '' # force with no unit

            elif isinstance( inputValue, int ):

                # futil.log( f' > createOrGetParameterByID : isinstance == int' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = inputUnit

            elif isinstance( inputValue, float ):

                #futil.log( f' > createOrGetParameterByID : isinstance == float' )

                value = adsk.core.ValueInput.createByReal( inputValue )
                unit  = inputUnit

            elif isinstance( inputValue, str ):

                # futil.log( f' > createOrGetParameterByID : isinstance == str' )

                if inputValue == '' and inputUnit in ( 'deg', 'degree', 'rad', 'mm', 'cm', '' ):
                    inputValue = '0'

                value = adsk.core.ValueInput.createByString( inputValue )
                unit  = inputUnit

            else:

                # futil.log( f' > createOrGetParameterByID : *************************' )
                return False

            paramItem = userParameters.add( inputId, value, unit, inputLabel )

            # futil.log( f' > createOrGetParameterByID : value          = {value}' )
            # futil.log( f' > createOrGetParameterByID : unit           = {unit}' )
            # futil.log( f' > createOrGetParameterByID : paramItem      = {paramItem}' )

        # force result as number to be same as input

        if( inputUnit == 'bool' ):
            resultVar = bool( unitsManager.evaluateExpression( paramItem.expression, '' ) )
        else:
            resultVar = unitsManager.evaluateExpression( paramItem.expression, inputUnit )

            if isinstance( inputValue, int ):
                resultVar = int( round( resultVar, 0 ) )

        return resultVar


    def updateParameterByID( self,
            id:    str,
            label: str = None,
            value: int | float | complex | bool | str = None,
            unit : str = None
    ):

        inputId    = id
        inputLabel = self.fields[ id ][ 'label' ]  if( label == None )  else label
        inputValue = self.fields[ id ][ 'value' ]  if( value == None )  else value
        inputUnit  = self.fields[ id ][ 'unit' ]   if( unit  == None )  else unit

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        userParams = design.userParameters
        #unitsMgr   = design.unitsManager

        param = userParams.itemByName( inputId )

        if param:
            if inputUnit == '':
                param.expression = '{}' . format( inputValue )
            elif inputUnit == 'mm':
                param.expression = '{} mm' . format( inputValue * 10 )
            elif inputUnit == 'cm':
                param.expression = '{} cm' . format( inputValue )
            elif inputUnit in ( 'deg', 'degree' ):
                param.expression = '{} deg' . format( math.degrees( inputValue ) )

            return True

        return False

