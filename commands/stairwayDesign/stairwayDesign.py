import adsk.core, adsk.fusion
import math

from ...lib import fusion360utils as futil
from ...lib.fusion360custom.misc   import *
from ...lib.fusion360custom.fields import *

# ------------------------------------------------------------------------------

class StairwayDesign:

    IS_EVENT_PREVIEW_ONLY       = False   # (for developement) don't execute 'eventExecute' if True, then only preview 2D Sketch
    IS_AUTO_CAMERA_FIT          = True

    IS_READ_PARAMETERS          = False
    IS_STORE_PARAMETERS         = False


    def __init__( self ):

        if True:
            self.isInitialized: bool             = False
            self.isNeedToComputeStepNumber: bool = True
            self.isNeedCameraToFitView: bool     = True
            self.isPreviewEventAvailable: bool   = True

            # TAB1 -------------------------------------------------------------------------
            self.stairHeight: float             = None
            self.stairWidth: float              = None
            self.walkpathRadius: float          = None
            self.insideRadius: float            = None
            self.stairAngle: float              = None       # data for flight group
            self.isPreviewRadiating: bool       = None
            self.isPreviewBalancing: bool       = None
            # ------------------------------------------------------------------------------
            self.stepNumber: int                = None
            self.stepNumberMini: int            = None
            self.stepNumberMaxi: int            = None
            # ------------------------------------------------------------------------------
            self.stairThickness: float          = None
            self.startLength: float             = None
            self.frontReserveLength: float      = None
            # ------------------------------------------------------------------------------
            self.isOverlap: bool                = True
            self.overlapLength: float           = None
            self.isOverlapLast: bool            = None
            # ------------------------------------------------------------------------------
            self.isRiser: bool                  = False
            self.riserThickness: float          = None
            self.riserGroove: float             = None
            self.riserRabbet: float             = None
            # ------------------------------------------------------------------------------
            self.walkpathLength: float          = None       # data for compute group
            self.totalLength: float             = None
            self.stepHeight: float              = None
            self.stepGoing: float               = None
            self.blondelLaw: float              = None
            self.climbAngle: float              = None
            # ------------------------------------------------------------------------------
            self.flightLength1: float           = None       # data for flight group
            self.flightBalanceProp1: float      = None       # data for flight group
            self.flightLength2: float           = None       # data for flight group
            self.flightBalanceProp2: float      = None       # data for flight group
            self.flightBalanceDelta: float      = None       # data for flight group

            # TAB2 -------------------------------------------------------------------------
            self.isCreateSteps: bool            = None
            self.isCreateRisers: bool           = None
            self.isEngraveReference: bool       = None
            # ------------------------------------------------------------------------------
            self.isCreateStairLayout: bool      = None
            self.flatModulo                     = None
            self.flatOriginX                    = None
            self.flatOriginY                    = None
            self.flatSpaceX                     = None
            self.flatSpaceY                     = None


            # ------------------------------------------------------------------------------
            self.walkLine:    adsk.fusion.SketchLine = None
            self.insideLine:  adsk.fusion.SketchLine = None
            self.outsideLine: adsk.fusion.SketchLine = None
            # ------------------------------------------------------------------------------
            self.walkCurvesSKT: list            = []
            self.insideCurvesSKT: list          = []
            self.outsideCurvesSKT: list         = []
            # ------------------------------------------------------------------------------
            self.walkSteps: dict                = {}
            # ------------------------------------------------------------------------------
            self.radiatingSteps: dict           = {}
            self.radiatingStepsOverlap: dict    = {}
            self.radiatingStepsRiser: dict      = {}
            self.radiatingStepsBack: dict       = {}
            # ------------------------------------------------------------------------------
            self.balancingSteps: dict           = {}
            self.balancingStepsOverlap: dict    = {}
            self.balancingStepsRiser: dict      = {}
            self.balancingStepsBack: dict       = {}
            # ------------------------------------------------------------------------------
            self.stairs: dict                   = {}
            # ------------------------------------------------------------------------------
            self.stairwayOccurence:         adsk.fusion.Occurrence = None # the main occurence
            self.stairOccurence:            adsk.fusion.Occurrence = None # the stair occurence child of the main occurence
            self.stairLayoutOccurence:      adsk.fusion.Occurrence = None # the stair layout occurence child of the main occurence
            self.stepsGroupOccurence:       adsk.fusion.Occurrence = None
            self.risersGroupOccurence:      adsk.fusion.Occurrence = None

        # ------------------------------------------------------------------------------
        # init class field
        # ------------------------------------------------------------------------------

        self.fields = Fields( {

            # ------------------------------------------------------------------------------
            'design_tab': {
                'label':            'Conception',
                'tooltip':          '',
                'description':      '',
                'value':            True,
                'unit':             'bool',
            },
            # ------------------------------------------------------------------------------

            'stair_height': {
                'label':            'Hauteur totale',
                'tooltip':          'Hauteur totale à monter (du sol au ras du plancher d\'arrivée)',
                'description':      'Distance verticale entre le palier de départ et le palier d\'arrivée.',
                'value':            '3000 mm',
                'unit':             'mm',
                'mini':             20,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'stair_width': {
                'label':            'Emmarchement',
                'tooltip':          'Emmarchement ou largeur de l\'escalier',
                'description':      'Largeur utile de l\'escalier. Sa valeur idéale est supérieure ou égale à 800 mm.',
                'value':            '1000 mm',
                'unit':             'mm',
                'mini':             40,  # "400 mm" - 70
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'walkpath_radius': {
                'label':            'Foulée / jour',
                'tooltip':          'Ligne de foulée / jour (côté interieur)',
                'description':      'Au delà d\'une largeur de l\'escalier de 1000 mm, la valeur maximale conseillée est de 500 mm',
                'value':            '500 mm',
                'unit':             'mm',
                'mini':             20,  # "200 mm" - 50
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'inside_radius': {
                'label':            'Rayon limon jour',
                'tooltip':          'Rayon du limon jour (côté intérieur)',
                'description':      '',
                'value':            '1 mm',
                'unit':             'mm',
                'mini':             0.1,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'stair_angle': {
                'label':            'Angle',
                'tooltip':          'Angle de rotation de l\'escalier. Quart-tournant gauche = -90°, Droit = 0° et quart-tournant droite = 90°',
                'description':      '',
                'value':            '90 deg',
                'unit':             'deg',
                'mini':             -math.radians( 120 ),
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             math.radians( 120 ),
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,
                #'step':            math.radians( 5 ),
            },

            'is_preview_radiating': {
                'label':            'Prévi. rayonn. ?',
                'tooltip':          'Prévisualisation des marches rayonnantes',
                'description':      '',
                'value':            False,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },

            'is_preview_balancing': {
                'label':            'Prévisualisat. marches',
                'tooltip':          'Prévisualisation des marches balancées',
                'description':      '',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   'resources/switch3-blue',
                # 'resourceFolder':   '',
            },


            # ------------------------------------------------------------------------------
            'is_overlap': {
                'label':            'Nez de marche', # Step nosing
                'tooltip':          '',
                'description':      'Partie saillante d\'une marche qui recouvre la marche inférieure et apporte du confort à l\'utilisateur.',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },
            # ------------------------------------------------------------------------------

            'overlap_length': {
                'label':            'Recouvrement',
                'tooltip':          'Distance de recouvrement du nez de marche',
                'description':      'Partie de la marche recouverte par la marche du dessus. Le recouvrement permet d\'améliorer le confort de l\'escalier.',
                'value':            '30 mm',
                'unit':             'mm',
                'mini':             1, # 10 mm
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             10,
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,

            },

            'is_overlap_last': {
                'label':            'Marche palière ?',                           # Landing step
                'tooltip':          'Marche dans le prolongement du palier d\'arrivée',
                'description':      'Elle permet d\'avoir un recouvrement sur la dernière marche. Elle facilite également le raccordement du limon et de la main courante avec le palier d\'arrivée.',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },


            # ------------------------------------------------------------------------------
            'is_riser': {
                'label':            'Contremarche',
                'tooltip':          'Contre-marche',
                'description':      'Partie verticale reliant 2 marches consécutives.',
                'value':            False,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },
            # ------------------------------------------------------------------------------

            'riser_thickness': {
                'label':            'Epaisseur',
                'tooltip':          'Epaisseur de la contremarche',
                'description':      'Par défaut 19 mm. Si aucune contre-marche alors 0 mm',
                'value':            '19 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             5,
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,
            },

            'riser_groove': {
                'label':            'Rainure',
                'tooltip':          'Rainure dans la marche haute pour emboiter la contremarche',
                'description':      '',
                'value':            '8 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'riser_rabbet': {
                'label':            'Feuillure',
                'tooltip':          'Feuillure dans la marche basse pour positionner la contremarche',
                'description':      '',
                'value':            '5 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },


            # ------------------------------------------------------------------------------
            'stair_group': {
                'label':            'Marche et foulée',
                'tooltip':          '',
                'description':      'Surface horizontale sur laquelle on pose le pied.',
                'value':            False,
                'unit':             'bool',
            },
            # ------------------------------------------------------------------------------

            'step_number': {
                'label':            'Nombre',
                'tooltip':          'Nombre de marches de l\'escalier',
                'description':      '',
                'value':            '',
                'unit':             '', # No units
            },

            'step_number_mini': {
                'label':            'Nb de marches mini.',
                'tooltip':          'Nombre de marches minimum',
                'description':      '',
                'value':            '',
                'unit':             '', # No units
            },

            'step_number_maxi': {
                'label':            'Nb de marches maxi.',
                'tooltip':          'Nombre de marches maximum',
                'description':      '',
                'value':            '',
                'unit':             '', # No units
            },

            'stair_thickness': {
                'label':            'Epaisseur',
                'tooltip':          'Epaisseur de la marche',
                'description':      'Par défaut 40 mm',
                'value':            '40 mm',
                'unit':             'mm',
                'mini':             1, # 10 mm
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'front_reserve_length': {
                'label':            'Réserve à l\'avant',
                'tooltip':          'Réserve à l\'avant de la 1ere marche',
                'description':      'Espace reservé à l\'avant de la 1ere marche pour les limons dans le cas des escaliers à la française.',
                'value':            '0 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'walkpath_length': {
                'label':            'Longueur foulée',
                'tooltip':          'Longueur de la foulée (L)',
                'description':      'Ligne fictive symbolisant le passage de l\'utilisateur. Elle permet de déterminer le giron pour les escaliers tournants. Si l\'emmarchement est inférieur ou égal à 1m alors la ligne de foulée est située au milieu. Si l\'emmarchement est supérieur à 1m alors la ligne de foulée est située à 500mm de la main-courante intérieure.',
                'value':            '',
                'unit':             'mm',
                'numRows':          1,
                'isReadOnly':       True,
            },

            'total_length': {
                'label':            'Longueur totale',
                'tooltip':          'Longueur totale ou emprise',
                'description':      'Emprise (reculée), c\'est égal à longueur de la ligne de foulée + le nez de marche + la réserve à l\'avant pour les limons',
                'value':            '',
                'unit':             'mm',
                'numRows':          1,
                'isReadOnly':       True,
            },

            'step_height': {
                'label':            'Hauteur de marche',
                'tooltip':          'Hauteur de marche (H)',
                'description':      'Distance verticale entre deux nez de marche. La hauteur de marche doit être comprise entre 150 et 200 mm. Sa valeur idéale est de 175 mm.',
                'value':            '',
                'unit':             'mm',
                'numRows':          1,
                'isReadOnly':       True,
            },

            'step_going': {
                'label':            'Giron',
                'tooltip':          'Giron de marche (G)',
                'description':      'Distance horizontale entre deux nez de marche. Le giron doit être compris entre 230 et 330 mm. Sa valeur idéale est de 280 mm.',
                'value':            '',
                'unit':             'mm',
                'numRows':          1,
                'isReadOnly':       True,
            },

            'blondel_law': {
                'label':            'Loi de Blondel',
                'tooltip':          'Loi de Blondel (1G + 2H)',
                'description':      'Formule inventée par l\'architecte français François-Blondel (1618-1686) vérifiant la cohérence entre la hauteur de marche et le giron. Elle est comprise entre 590 à 650 mm. La valeur idéale est de 630 mm.',
                'value':            '',
                'unit':             'mm',
                'numRows':          1,
                'isReadOnly':       True,
            },

            'climb_angle': {
                'label':            'Angle ascension',
                'tooltip':          'Angle d\'ascension ou montée',
                'description':      'Détermine la pente de l\'escalier. L\'angle doit être compris entre 20 et 50°. Sa valeur idéale est de 30°.',
                'value':            '',
                'unit':             'deg',
                'numRows':          1,
                'isReadOnly':       True,
            },


            # ------------------------------------------------------------------------------
            'flight_group': {
                'label':            'Volées de marches',
                'tooltip':          'Volées de marches et limons',
                'description':      '',
                'value':            True,
                'unit':             'bool',
            },
            # ------------------------------------------------------------------------------

            'flight_length_1': {
                'label':            'Long. 1er limon ext.',
                'tooltip':          'Longueur du 1er limon extérieur',
                'description':      'La valeur minimale dépend de l\'angle de l\'escalier, de l\'emmarchement, du rayon de jour et de la profondeur des nez de marche',
                'value':            '3000 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  False,
            },

            'flight_balance_prop_1': {
                'label':            'Prop. bal. 1ere volée',
                'tooltip':          'Proportion de balancement de la 1ere volée de marches. De 0 à 100%',
                'description':      '',
                'value':            50,
                'unit':             '', # No units
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             100,
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,
                # 'list':           [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                'suffix':           '%',
            },

            'flight_length_2': {
                'label':            'Long. 2e limon ext.',
                'tooltip':          'Longueur du 2eme limon extérieur',
                'description':      '',
                'value':            '3000 mm',
                'unit':             'mm',
                'mini':             0.1,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'flight_balance_prop_2': {
                'label':            'Prop. bal. 2eme volée',
                'tooltip':          'Proportion de balancement de la 2eme volée de marches. De 0 à 100%',
                'description':      '',
                'value':            50,
                'unit':             '', # No units
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             100,
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,
                # 'list':           [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                'suffix':           '%',
            },

            'flight_balance_delta': {
                'label':            'Ajust. angle balanc.',
                'tooltip':          'Ajustement de l\'angle de balancement entre les 2 volées',
                'description':      '',
                'value':            '0 deg',
                'unit':             'deg',
                'mini':             -math.radians( 20 ),
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
                'maxi':             math.radians( 20 ),
                'isMaxiLimited':    True,
                'isMaxiInclusive':  True,
                'step':             math.radians( 1 ),
            },


            # ------------------------------------------------------------------------------
            'manufacturing_tab': {
                'label':            'Fabrication',
                'tooltip':          '',
                'description':      '',
                'value':            False,
                'unit':             'bool',
            },
            # ------------------------------------------------------------------------------

            'is_create_steps': {
                'label':            'Générer marches ?',
                'tooltip':          'Générer les marches de l\'escalier',
                'description':      '',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },

            'is_create_risers': {
                'label':            'Générer contremarches ?',
                'tooltip':          'Générer les contremarches de l\'escalier',
                'description':      '',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },

            'is_engrave_reference': {
                'label':            'Graver les références ?',
                'tooltip':          'Graver au dos des marches et contremarches les références',
                'description':      '',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',   # resources/switch3-blue
            },


            # ------------------------------------------------------------------------------
            'is_create_stair_layout': {
                'label':            'Mettre à plat ?',
                'tooltip':          'Mettre à plat les pièces (marches et contremarches)',
                'description':      '',
                'value':            True,
                'unit':             'bool',
                'isCheckBox':       True,
                'resourceFolder':   '',
            },
            # ------------------------------------------------------------------------------

            'flat_modulo': {
                'label':            'Nombre par colonne',
                'tooltip':          'Nombre de pièces par colonne',
                'description':      '',
                'value':            4,
                'unit':             '',
                'mini':             1,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'flat_origin_x': {
                'label':            'Origine en X',
                'tooltip':          'Origine en X des pièces',
                'description':      '',
                'value':            '0 mm',
                'unit':             'mm',
            },

            'flat_origin_y': {
                'label':            'Origine en Y',
                'tooltip':          'Origine en Y des pièces',
                'description':      '',
                'value':            '0 mm',
                'unit':             'mm',
            },

            'flat_space_x': {
                'label':            'Espacement largeur',
                'tooltip':          'Espacement entre les pièces sur la largeur',
                'description':      '',
                'value':            '300 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },

            'flat_space_y': {
                'label':            'Espacement profondeur',
                'tooltip':          'Espacement entre les pièces en profondeur',
                'description':      '',
                'value':            '600 mm',
                'unit':             'mm',
                'mini':             0,
                'isMiniLimited':    True,
                'isMiniInclusive':  True,
            },


            # 'is_overlap_balanced': {
            #     'label':          'Balancé',
            #     'tooltip':        'Balancement du nez de marche',
            #     'description':    '*** ceci est un paramètre experimental',
            #     'value':          False,
            #     'unit':           'bool'
            # },

            # ------------------------------------------------------------------------------
            # 'stairwell': {
            #     'label':          'Longueur trémie',
            #     'tooltip':        '',
            #     'description':    'Ouverture dans le palier d'arrivée permettant le passage de l'escalier. Longueur de l\'ouverture de la trémie au dessus de l\'emprise (reculée)',
            #     'value':          '0 mm',
            #     'unit':           'mm',
            # },

            # 'ceiling_height': {
            #     'label':          'Hauteur du plafond',
            #     'tooltip':        '',
            #     'description':    '',
            #     'value':          '2800 mm',
            #     'unit':           'mm',
            # },

            # 'headroom': {
            #     'label':          'Passage de tête',
            #     'tooltip':        'Passage de tête (échappée)',
            #     'description':    'Distance entre le plafond et la ligne de foulée au niveau de la trémie. L\'échappée doit être supérieure à 1900mm et sa valeur idéale est supérieure ou égale à 2100mm.',
            #     'value':          '2100 mm',
            #     'unit':           'mm',
            # },

            # 'string_section': {
            #     'label':          'Section des limons',
            #     'tooltip':        '',
            #     'description':    '', # TODO : faut il separer exterieur et intérieur ?
            #     'value':          '0 mm',
            #     'unit':           'mm',
            # },

        } )



    # ------------------------------------------------------------------------------
    # FIRED BY EVENTS
    # ------------------------------------------------------------------------------~
    # see command_created definition  in entry.py to active/desactivate events
    # ------------------------------------------------------------------------------

    def eventCreated( self, eventArgs: adsk.core.CommandCreatedEventArgs ):

        futil.log( f' >>> eventCreated()' )

        # -----------------------------------------------------------------------------------

        self.inputs: adsk.core.CommandInputs = eventArgs.command.commandInputs

        # -----------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        rootComponent:   adsk.fusion.Component   = design.rootComponent
        rootOccurrences: adsk.fusion.Occurrences = rootComponent.occurrences

        # ------------------------------------------------------------------------------

        # Create stairway occurence

        self.stairwayOccurence = rootOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        stairwayComponent: adsk.fusion.Component = self.stairwayOccurence.component
        stairwayComponent.name = f'STAIRWAY'

        # ------------------------------------------------------------------------------

        # Create sketch on XY plane

        sketches = stairwayComponent.sketches
        xyPlane  = stairwayComponent.xYConstructionPlane

        self.sketch: adsk.fusion.Sketch = sketches.add( xyPlane )
        self.sketch.name = f'Sketch Stairway'

        # ------------------------------------------------------------------------------

        # Verify that a sketch is active.

        # if False and app.activeEditObject.objectType != adsk.fusion.Sketch.classType():
        #     ui.messageBox( 'A sketch on a XY plane needs to be active.' )
        #     return False

        # ------------------------------------------------------------------------------

        # Verify if selected XY plane is selected

        # if False and self.sketch.referencePlane.name != 'XY':
        #     ui.messageBox( 'The sketch must be define on a XY plane.' )
        #     return False


        # -----------------------------------------------------------------------------------

        # sketch options

        self.sketch.arePointsShown              = True
        self.sketch.areConstraintsShown         = False
        self.sketch.areDimensionsShown          = True
        self.sketch.areProfilesShown            = False
        self.sketch.isConstructionGeometryShown = True
        self.sketch.isProjectedGeometryShown    = False

        # ------------------------------------------------------------------------------

        # reset

        self.walkCurvesSKT: list            = []
        self.insideCurvesSKT: list          = []
        self.outsideCurvesSKT: list         = []
        self.walkSteps: dict                = {}
        self.radiatingSteps: dict           = {}
        self.radiatingStepsOverlap: dict    = {}
        self.radiatingStepsRiser: dict      = {}
        self.radiatingStepsBack: dict       = {}
        self.balancingSteps: dict           = {}
        self.balancingStepsOverlap: dict    = {}
        self.balancingStepsRiser: dict      = {}
        self.balancingStepsBack: dict       = {}
        self.stairs: dict                   = {}

        # get default values

        self.getDefaultValues()

        # read all parameters

        self.readAllParameters()

        # create all inputs fields

        self.createAllFields()

        self.displayStepNumberField()
        self.updateIsCreateRisersInputField()

        # update flight length mini fields

        flightLengthMinimum = self.computeFlightLengthMinimum()
        self.setFlightLengthMinimumField( 'flight_length_1', flightLengthMinimum )
        self.setFlightLengthMinimumField( 'flight_length_2', flightLengthMinimum )

        #

        self.isNeedCameraToFitView     = True
        self.isNeedToComputeStepNumber = True

        # initialized

        self.isInitialized   = True


    def eventValidateInput( self, eventArgs: adsk.core.ValidateInputsEventArgs ):

        inputs: adsk.core.CommandInputs = eventArgs.inputs

        # ------------------------------------------------------------------------------

        futil.log( f' >>> eventValidateInput()' )

        # ------------------------------------------------------------------------------

        # TODO

        # self.insideRadius = self.inputs.itemById( 'inside_radius' ).value

        # if self.insideRadius >= 0.1:
        #     eventArgs.areInputsValid = True
        # else:
        #     eventArgs.areInputsValid = False

        # ------------------------------------------------------------------------------


    def eventInputChanged( self, eventArgs: adsk.core.InputChangedEventArgs ):

        inputs: adsk.core.CommandInputs = eventArgs.inputs
        input: adsk.core.CommandInput   = eventArgs.input

        # ------------------------------------------------------------------------------

        futil.log( f' >>> eventInputChanged( \'{input.id}\')' )

        # ------------------------------------------------------------------------------

        self.isPreviewEventAvailable = True

        if input.classType() == adsk.core.ValueCommandInput.classType() and input.isValidExpression == False:
            self.isPreviewEventAvailable = False

        # ------------------------------------------------------------------------------

        match input.id:

            # TAB1 -------------------------------------------------------------------------

            case 'stair_height':
                self.stairHeight       = self.inputs.itemById( input.id ).value # ValueCommandInput
                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            case 'stair_width':
                self.stairWidth     = self.inputs.itemById( input.id ).value
                self.walkpathRadius = self.getWalkpathMaxiRadius( self.stairWidth )
                self.inputs.itemById( 'walkpath_radius' ).value = self.walkpathRadius
                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            case 'walkpath_radius':
                self.walkpathRadius    = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            case 'inside_radius':
                self.insideRadius      = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            case 'stair_angle':
                #self.stairAngle = self.inputs.itemById( input.id ).valueOne              # FloatSliderCommandInput
                self.stairAngle = self.inputs.itemById( input.id ).value                  # ValueCommandInput

                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            # ------------------------------------------------------------------------------

            case 'stair_group':
                self.isStairGroup         = self.inputs.itemById( input.id ).isExpanded
                self.isNeedToComputeStepNumber = True

            case 'step_number':
                self.stepNumber           = self.inputs.itemById( input.id ).valueOne              # IntegerSliderListCommandInput
                #self.disablePreviewFields()

            case 'stair_thickness':
                self.stairThickness       = self.inputs.itemById( input.id ).value

            case 'front_reserve_length':
                self.frontReserveLength   = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True

            # ------------------------------------------------------------------------------

            case 'is_overlap':
                self.isOverlap            = self.inputs.itemById( input.id ).isExpanded
                self.isNeedToComputeStepNumber = True

            case 'overlap_length':
                self.overlapLength        = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True

            case 'is_overlap_last':
                self.isOverlapLast        = self.inputs.itemById( input.id ).value

            # ------------------------------------------------------------------------------

            case 'is_riser':
                self.isRiser = self.inputs.itemById( input.id ).isExpanded
                self.isNeedToComputeStepNumber = True

                self.updateIsCreateRisersInputField()

            case 'riser_thickness':
                self.riserThickness       = self.inputs.itemById( input.id ).value

            case 'riser_groove':
                self.riserGroove          = self.inputs.itemById( input.id ).value

            case 'riser_rabbet':
                self.riserRabbet          = self.inputs.itemById( input.id ).value

            # ------------------------------------------------------------------------------

            case 'is_preview_radiating':
                self.isPreviewRadiating      = self.inputs.itemById( input.id ).value

            case 'is_preview_balancing':
                self.isPreviewBalancing      = self.inputs.itemById( input.id ).value
                pass

            # ------------------------------------------------------------------------------

            case 'flight_group':
                self.isFlightGroup        = self.inputs.itemById( input.id ).isExpanded

            case 'flight_length_1':
                self.flightLength1        = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True

                # self.disablePreviewFields()

            case 'flight_balance_prop_1':
                self.flightBalanceProp1   = self.inputs.itemById( input.id ).value          # ValueCommandInput

            case 'flight_length_2':
                self.flightLength2        = self.inputs.itemById( input.id ).value
                self.isNeedToComputeStepNumber = True
                # self.disablePreviewFields()

            case 'flight_balance_prop_2':
                self.flightBalanceProp2   = self.inputs.itemById( input.id ).value          # ValueCommandInput

            case 'flight_balance_delta':
                self.flightBalanceDelta   = self.inputs.itemById( input.id ).value          # ValueCommandInput

            # TAB2 -------------------------------------------------------------------------

            case 'is_create_steps':
                self.isCreateSteps        = self.inputs.itemById( input.id ).value

            case 'is_create_risers':
                self.isCreateRisers       = self.inputs.itemById( input.id ).value

            case 'is_engrave_reference':
                self.isEngraveReference   = self.inputs.itemById( input.id ).value

            # ------------------------------------------------------------------------------

            case 'is_create_stair_layout':
                self.isCreateStairLayout   = self.inputs.itemById( input.id ).isExpanded

            case 'flat_modulo':

                # TODO put in validate event

                self.flatModulo = int( math.floor( self.inputs.itemById( input.id ).value ) )
                self.inputs.itemById( 'flat_modulo' ).value = self.flatModulo

                futil.log( f'self.flatModulo = {self.flatModulo}' )

            case 'flat_origin_x':
                self.flatOriginX          = self.inputs.itemById( input.id ).value

            case 'flat_origin_y':
                self.flatOriginY          = self.inputs.itemById( input.id ).value

            case 'flat_space_x':
                self.flatSpaceX           = self.inputs.itemById( input.id ).value

            case 'flat_space_y':
                self.flatSpaceY           = self.inputs.itemById( input.id ).value


        # ------------------------------------------------------------------------------

        flightLengthMinimum = self.computeFlightLengthMinimum()
        self.setFlightLengthMinimumField( 'flight_length_1', flightLengthMinimum )
        self.setFlightLengthMinimumField( 'flight_length_2', flightLengthMinimum )

        # return True

    # ------------------------------------------------------------------------------

    def eventPreview( self, eventArgs: adsk.core.CommandEventArgs ):

        futil.log( f' >>> eventPreview()' )

        # ------------------------------------------------------------------------------

        inputs: adsk.core.CommandInputs = eventArgs.command.commandInputs

        if not( self.isPreviewEventAvailable ): # WORKAROUND
            return

        # ------------------------------------------------------------------------------
        # draw the stair
        # ------------------------------------------------------------------------------

        self.sketch.isComputeDeferred = True

        ( self.outsideLine, self.insideLine, self.walkLine ) = self.drawStairwaySketch2D( self.sketch, True )

        if self.isNeedCameraToFitView:
            self.cameraFitView()
            self.isNeedCameraToFitView = False # one shot


        # TO DEBUG 2D DRAWING
        # if self.IS_EVENT_PREVIEW_ONLY:
        #     eventArgs.isValidResult = True
        #     return True


        self.checkSelectedLines()
        self.getCurvesFromSelectedLines()

        # ------------------------------------------------------------------------------
        # compute step distance & walkpath length & total length
        # ------------------------------------------------------------------------------

        self.computeWalkpathValues()

        # ------------------------------------------------------------------------------
        # get the ideal step number associate to the closest blondel law value found
        # ------------------------------------------------------------------------------

        if self.isNeedToComputeStepNumber:
            self.computeStepNumberOptimal()
            self.isNeedToComputeStepNumber = False # one shot


        # ------------------------------------------------------------------------------
        # compute step
        # ------------------------------------------------------------------------------

        self.computeStepValues()
        self.displayStepNumberField()
        self.displayAllWalkpathFields()
        self.displayAllTextFieldsComputed()

        # ------------------------------------------------------------------------------
        # compute WALK steps
        # ------------------------------------------------------------------------------

        self.walkSteps = self.computeWalkSteps()

        # ------------------------------------------------------------------------------
        # compute RADIATING steps
        # ------------------------------------------------------------------------------

        self.radiatingSteps = self.computeRadiatingSteps( self.walkSteps )
        self.radiatingStepsOverlap.clear()
        self.radiatingStepsRiser.clear()
        self.radiatingStepsBack.clear()

        if self.isOverlapStair():
            self.radiatingStepsOverlap = self.computeParallelSteps( self.radiatingSteps, offset = -self.overlapLength )

        if self.isRiserStair():
            self.radiatingStepsRiser   = self.computeParallelSteps( self.radiatingSteps, offset = self.riserThickness )
            self.radiatingStepsBack    = self.computeParallelSteps( self.radiatingSteps, offset = self.riserRabbet )

        # ------------------------------------------------------------------------------
        # compute BALANCING steps
        # ------------------------------------------------------------------------------

        if self.isPreviewBalancing:

            self.balancingSteps = self.computeBalancingStepsAll( self.radiatingSteps )
            self.balancingStepsOverlap.clear()
            self.balancingStepsRiser.clear()
            self.radiatingStepsBack.clear()

            if self.isOverlapStair():
                self.balancingStepsOverlap = self.computeParallelSteps( self.balancingSteps, offset = -self.overlapLength )

            if self.isRiserStair():
                self.balancingStepsRiser   = self.computeParallelSteps( self.balancingSteps, offset = self.riserThickness )
                self.radiatingStepsBack    = self.computeParallelSteps( self.balancingSteps, offset = self.riserRabbet )

        # ------------------------------------------------------------------------------
        # draw RADIATING steps & BALANCING steps
        # ------------------------------------------------------------------------------

        if self.isPreviewRadiating:
            self.drawLineStepsSketch2D( self.radiatingSteps, True )

            if self.isOverlapStair():
                self.drawLineStepsSketch2D( self.radiatingStepsOverlap, True )

            if self.isRiserStair():
                self.drawLineStepsSketch2D( self.radiatingStepsRiser, True )

        # ------------------------------------------------------------------------------

        if self.isPreviewBalancing:

            if self.isOverlapStair():
                self.drawLineStepsSketch2D( self.balancingSteps, True )
                self.drawLineStepsSketch2D( self.balancingStepsOverlap )
            else:
                self.drawLineStepsSketch2D( self.balancingSteps )

            if self.isRiserStair():
                self.drawLineStepsSketch2D( self.balancingStepsRiser, True )
                self.drawLineStepsSketch2D( self.balancingStepsBack, True  )

        # ------------------------------------------------------------------------------

        if not( self.isPreviewRadiating or self.isPreviewBalancing ):
            self.drawPointStepsSketch2D( self.walkSteps )

        # ------------------------------------------------------------------------------

        self.sketch.isComputeDeferred = False

        # ------------------------------------------------------------------------------
        # Set the isValidResult property to use these results at the final result.
        # This will result in the execute event not being fired.
        # Used during the commandStarting event to get or set that the result of preview is valid
        # and the command can reuse the result when OK is hit.
        # This property should be ignored for all events besides the executePreview event.
        # ------------------------------------------------------------------------------
        if self.IS_EVENT_PREVIEW_ONLY:
            eventArgs.isValidResult = True
            return True
        # ------------------------------------------------------------------------------


    def eventExecute( self, eventArgs: adsk.core.CommandEventArgs ):

        futil.log( f' >>> eventExecute()' )

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        ui  = app.userInterface

        design: adsk.fusion.Design      = app.activeProduct
        inputs: adsk.core.CommandInputs = eventArgs.command.commandInputs

        # ------------------------------------------------------------------------------

        if not self.isInitialized:
            ui.messageBox( 'Not initialized' )
            return False

        # ------------------------------------------------------------------------------
        # draw stairway
        # ------------------------------------------------------------------------------

        self.sketch.isComputeDeferred = True

        ( self.outsideLine, self.insideLine, self.walkLine ) = self.drawStairwaySketch2D( self.sketch, True )
        self.getCurvesFromSelectedLines()

        # ------------------------------------------------------------------------------
        # compute WALK steps
        # ------------------------------------------------------------------------------

        self.walkSteps = self.computeWalkSteps()

        # ------------------------------------------------------------------------------
        # compute RADIATING steps
        # ------------------------------------------------------------------------------

        self.radiatingSteps = self.computeRadiatingSteps( self.walkSteps )
        self.radiatingStepsOverlap.clear()
        self.radiatingStepsRiser.clear()
        self.radiatingStepsBack.clear()

        # ------------------------------------------------------------------------------

        if self.isOverlapStair():
            self.radiatingStepsOverlap = self.computeParallelSteps( self.radiatingSteps, offset = - self.overlapLength )

        if self.isRiserStair():
            self.radiatingStepsRiser = self.computeParallelSteps( self.radiatingSteps, offset = self.riserThickness )
            self.balancingStepsBack  = self.computeParallelSteps( self.radiatingSteps, offset = self.riserRabbet )

        # ------------------------------------------------------------------------------
        # compute BALANCING steps
        # ------------------------------------------------------------------------------

        self.balancingSteps = self.computeBalancingStepsAll( self.radiatingSteps )
        self.balancingStepsOverlap.clear()
        self.balancingStepsRiser.clear()
        self.balancingStepsBack.clear()

        if self.isOverlapStair():
            self.balancingStepsOverlap = self.computeParallelSteps( self.balancingSteps, offset = - self.overlapLength )

        if self.isRiserStair():
            self.balancingStepsRiser = self.computeParallelSteps( self.balancingSteps, offset = self.riserThickness )
            self.balancingStepsBack  = self.computeParallelSteps( self.balancingSteps, offset = self.riserRabbet )

        # ------------------------------------------------------------------------------
        # compute stairs
        # ------------------------------------------------------------------------------

        self.computeStair()

        # ------------------------------------------------------------------------------
        # draw 2D stairs sketch
        # ------------------------------------------------------------------------------

        self.drawStairLinesSketch2D()
        self.sketch.isVisible = False
        self.sketch.isComputeDeferred = False

        # ------------------------------------------------------------------------------
        # Create stair + stair layout
        # ------------------------------------------------------------------------------

        stairwayOccurrences: adsk.fusion.Occurrences = self.stairwayOccurence.component.occurrences

        # ------------------------------------------------------------------------------

        self.stairOccurence = stairwayOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        self.stairOccurence.isGroundToParent = True

        stairComponent: adsk.fusion.Component = self.stairOccurence.component
        stairComponent.name = f'STAIR'

        # ------------------------------------------------------------------------------

        if self.isCreateStairLayout:

            self.stairLayoutOccurence = stairwayOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
            self.stairLayoutOccurence.isGroundToParent = False

            stairLayoutComponent: adsk.fusion.Component = self.stairLayoutOccurence.component
            stairLayoutComponent.name = f'STAIR layout'

        # ------------------------------------------------------------------------------
        # create steps components + layout
        # ------------------------------------------------------------------------------

        isSteps = self.createSteps3D()

        if isSteps:
            self.createLayoutSteps3D()

        # ------------------------------------------------------------------------------
        # create risers components + layout
        # ------------------------------------------------------------------------------

        isRisers = self.createRisers3D()

        if isRisers:
            self.createLayoutRisers3D()

        # ------------------------------------------------------------------------------
        # Move layout occurence and capture position
        # ------------------------------------------------------------------------------

        if self.isCreateStairLayout:
            moveOccurence( self.stairLayoutOccurence, x = 500 )

            snapshot = design.snapshots.add()
            snapshot.name = f'Capture position stair layout'

        # ------------------------------------------------------------------------------
        # fit camera view
        # ------------------------------------------------------------------------------

        self.cameraFitView()

        # ------------------------------------------------------------------------------
        # save parameters
        # ------------------------------------------------------------------------------

        self.writeAllParameters()

        # ------------------------------------------------------------------------------

        #ui.messageBox( 'That\'s all folks' )

        return True


    def eventDestroy( self, eventArgs: adsk.core.CommandEventArgs ):

        futil.log( f' >>> eventDestroy()' )

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        # ------------------------------------------------------------------------------

        match eventArgs.terminationReason:

            case adsk.core.CommandTerminationReason.CompletedTerminationReason:
                futil.log( ' > : The command is terminated by clicking OK button, and executed successfully.' )

            case adsk.core.CommandTerminationReason.AbortedTerminationReason:
                futil.log( ' > : The command is terminated by clicking OK button, and executed failed.' )

            case adsk.core.CommandTerminationReason.CancelledTerminationReason:
                futil.log( ' > : The command is terminated by clicking Cancel button.' )

            case adsk.core.CommandTerminationReason.PreEmptedTerminationReason:
                futil.log( ' > : The command is terminated by activating another command.' )

            case adsk.core.CommandTerminationReason.SessionEndingTerminationReason:
                futil.log( ' > : The command is terminated by closing the document.' )

            case adsk.core.CommandTerminationReason.UnknownTerminationReason:
                futil.log( ' > : The command is terminated out of the reasons list below.' )

        # ------------------------------------------------------------------------------
        # remove component if not completed
        # ------------------------------------------------------------------------------

        if eventArgs.terminationReason != adsk.core.CommandTerminationReason.CompletedTerminationReason:

            rootComponent: adsk.fusion.Component = design.rootComponent

            for occurrence in rootComponent.occurrencesByComponent( self.stairwayOccurence.component ):
                occurrence.deleteMe()

                futil.log( ' > : remove Stairway component' )


    # ------------------------------------------------------------------------------
    # DRAW 2D
    # ------------------------------------------------------------------------------

    def drawStairwaySketch2D( self,
            sketch:       adsk.fusion.Sketch,
            isWalkpath:   bool = False,
            isConstraint: bool = False
        ) -> bool:


        futil.log( f' > : drawStairwaySketch2D( \'{sketch.name}\' )' )

        #sketch: adsk.fusion.Sketch = app.activeEditObject

        outsideStringLine1: adsk.fusion.SketchLine = None
        insideStringLine1:  adsk.fusion.SketchLine = None
        walkpathLine1:      adsk.fusion.SketchLine = None

        # ------------------------------------------------------------------------------

        stairAngle            = -self.stairAngle
        stairWidth            = self.stairWidth
        walkpathRadius        = self.walkpathRadius
        outsideStringLength1  = self.flightLength1
        outsideStringLength2  = self.flightLength2
        insideStringRadius    = self.insideRadius

        # ------------------------------------------------------------------------------

        sketchPoints: adsk.fusion.SketchPoints              = sketch.sketchPoints
        sketchLines: adsk.fusion.SketchLines                = sketch.sketchCurves.sketchLines
        #sketchCircles: adsk.fusion.SketchCircles           = sketch.sketchCurves.sketchCircles
        sketchArcs: adsk.fusion.SketchArcs                  = sketch.sketchCurves.sketchArcs
        sketchDimensions: adsk.fusion.SketchDimensions      = sketch.sketchDimensions
        sketchConstraints: adsk.fusion.GeometricConstraints = sketch.geometricConstraints

        sketchOffset       = sketch.offset
        sketchOriginPoint  = sketch.originPoint

        # ------------------------------------------------------------------------------

        insideOffsetX = stairWidth
        insideOffsetY = 0

        insideStringLength1 = outsideStringLength1 - stairWidth
        insideStringLength2 = 0

        # ------------------------------------------------------------------------------

        walkOffsetX   = insideOffsetX - walkpathRadius
        walkOffsetY   = 0

        #walkRadius        = insideStringRadius  + walkpathRadius
        walkpathLength1   = insideStringLength1 + walkpathRadius

        # ------------------------------------------------------------------------------

        if stairAngle != 0:
            insideStringLength2 = outsideStringLength2 - stairWidth
            walkpathLength2     = insideStringLength2 + walkpathRadius


        # futil.log( f'> : insideOffsetX       = {insideOffsetX} ' )
        # futil.log( f'> : insideOffsetY       = {insideOffsetY} ' )
        # futil.log( ' ' )

        # futil.log( f'> : walkOffsetX         = {walkOffsetX} ' )
        # futil.log( f'> : walkOffsetY         = {walkOffsetY} ' )
        # futil.log( ' ' )

        # futil.log( f'> : outsideStringLength1 = {outsideStringLength1} ' )
        # futil.log( f'> : outsideStringLength2 = {outsideStringLength2} ' )
        # futil.log( f'> : insideStringLength1  = {insideStringLength1} ' )
        # futil.log( f'> : insideStringLength2  = {insideStringLength2} ' )
        # futil.log( f'> : walkpathLength1      = {walkpathLength1} ' )
        # futil.log( f'> : walkpathLength2      = {walkpathLength2} ' )
        # futil.log( ' ' )

        # ------------------------------------------------------------------------------
        # ----- draw the OUTSIDE STRING curves
        # ------------------------------------------------------------------------------

        if True:

            # ----- start point

            if stairAngle == 0:
                startOutsidePoint = adsk.core.Point3D.create( -walkOffsetX, walkOffsetY, 0 )
            else:
                startOutsidePoint = adsk.core.Point3D.create( walkOffsetX * sign( stairAngle ), walkOffsetY, 0 )

            startOutsideSketchPoint = sketchPoints.add( startOutsidePoint )


            # ----- outside string line #1

            if stairAngle != 0:
                outsideStringLine1 = sketchLines.addByTwoPoints(
                    startOutsideSketchPoint,
                    offsetPoint( startOutsideSketchPoint, 0, outsideStringLength1, 0 )
                )

            else:
                outsideStringLine1 = sketchLines.addByTwoPoints(
                    startOutsideSketchPoint,
                    offsetPoint( startOutsideSketchPoint, 0, outsideStringLength1 + outsideStringLength2, 0 )
                )

            if True:
                # add 1st outside string dimension

                sketchDimensions.addDistanceDimension(
                    outsideStringLine1.startSketchPoint,
                    outsideStringLine1.endSketchPoint,
                    adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,
                    middlePoint( sketch,  outsideStringLine1.startSketchPoint, outsideStringLine1.endSketchPoint, -40.0 * sign( stairAngle ) )
                )


            if False:

                pass
                # ----- constraints

                # sketchConstraints.addVertical( outsideStringLine1 )


                # ----- constraints on origin

                # if startOutsidePoint.x == 0 and startOutsidePoint.y == 0:

                #     sketchConstraints.addCoincident(
                #         startOutsideSketchPoint,
                #         sketchOriginPoint
                #     )

                # if startOutsidePoint.x == 0:
                #     sketchConstraints.addVerticalPoints(
                #         sketchOriginPoint,
                #         startOutsideSketchPoint
                #     )
                #     sketchDimensions.addDistanceDimension(
                #         startOutsideSketchPoint,
                #         sketchOriginPoint,
                #         adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,
                #         middlePoint( sketch,  startOutsideSketchPoint, sketchOriginPoint, -60 )
                #     )

                # if startOutsidePoint.y == 0:
                #     sketchConstraints.addHorizontalPoints(
                #         sketchOriginPoint,
                #         startOutsideSketchPoint
                #     )
                #     sketchDimensions.addDistanceDimension(
                #         startOutsideSketchPoint,
                #         sketchOriginPoint,
                #         adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                #         middlePoint( sketch,  startOutsideSketchPoint, sketchOriginPoint, -60 )
                #     )


            # ----- outside string line #2 ( only for stairAngle != 0 )

            if stairAngle != 0:

                # ----- create line #2 and rotate

                line3D  = adsk.core.Line3D.create(
                    outsideStringLine1.endSketchPoint.geometry,
                    offsetPoint( outsideStringLine1.endSketchPoint, 0, outsideStringLength2, 0 )
                )

                vectorZ = adsk.core.Vector3D.create( z = 1 ) # Z axe  # need a XY plane

                rotationMatrix = adsk.core.Matrix3D.create()
                rotationMatrix.setToRotation( stairAngle, vectorZ, outsideStringLine1.endSketchPoint.geometry )

                line3D.transformBy( rotationMatrix )

                outsideStringLine2 = sketchLines.addByTwoPoints(
                    line3D.startPoint,
                    line3D.endPoint
                )

                if True:

                    # add 2nd outside string dimension

                    sketchDimensions.addDistanceDimension(
                        outsideStringLine2.startSketchPoint,
                        outsideStringLine2.endSketchPoint,
                        adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,
                        middlePoint( sketch,  outsideStringLine2.startSketchPoint, outsideStringLine2.endSketchPoint, -40.0 * sign( stairAngle ) )
                    )

                    # add outside string angular dimension (1st and 2nd)

                    sketchDimensions.addAngularDimension(
                        outsideStringLine1,
                        outsideStringLine2,
                        middlePoint( sketch,  outsideStringLine1.endSketchPoint, outsideStringLine2.startSketchPoint, 40.0 )
                    )

                # ----- constraints

                # sketchConstraints.addCoincident(
                #     outsideStringLine1.endSketchPoint,
                #     outsideStringLine2.startSketchPoint
                # )



        # ------------------------------------------------------------------------------
        # ----- create curves collection to make offset
        # ------------------------------------------------------------------------------

        curves = adsk.core.ObjectCollection.create()
        curves.add( outsideStringLine1 )

        if stairAngle != 0:
            curves.add( outsideStringLine2 )



        # ------------------------------------------------------------------------------
        # ----- draw the INSIDE STRING curves with offset
        # ------------------------------------------------------------------------------

        if True:

            directionPoint = adsk.core.Point3D.create( -stairWidth * sign( stairAngle ) + walkOffsetX * sign( stairAngle ), walkOffsetY,  0 )


            # # TODO optimize + hide offset dimensions
            insideCurves = sketchOffset( curves, directionPoint )


            insideStringLine1 = insideCurves.item( 0 )

            if stairAngle != 0:
                insideStringLine2  = insideCurves.item( 1 )

            # ----- inside string arc

            if stairAngle != 0:

                insideArc = sketchArcs.addFillet(
                    insideStringLine1, insideStringLine1.endSketchPoint.geometry,
                    insideStringLine2, insideStringLine2.startSketchPoint.geometry,
                    insideStringRadius
                )
                insideArc.isConstruction = False

                if insideStringRadius > 0.1:

                    # add inside string angular dimension if > 1mm

                    sketchDimensions.addRadialDimension(
                        insideArc,
                        middlePoint( sketch,  insideArc.startSketchPoint, insideArc.endSketchPoint, 0 )
                    )



        # ------------------------------------------------------------------------------
        # ----- draw the WALK PATH curves with offset
        # ------------------------------------------------------------------------------

        if isWalkpath:

            if stairAngle == 0:
                directionPoint = adsk.core.Point3D.create( ( stairWidth - walkpathRadius ) - walkOffsetX, walkOffsetY,  0 )
            else:
                directionPoint = adsk.core.Point3D.create( - ( stairWidth - walkpathRadius ) * sign( stairAngle ) + walkOffsetX * sign( stairAngle ), walkOffsetY,  0 )

            # directionPoint = adsk.core.Point3D.create( ( stairWidth - walkpathRadius - walkOffsetX ) * sign( -stairAngle ), walkOffsetY,  0 )

            # TODO optimize + hide offset dimensions
            walkCurves = sketchOffset( curves, directionPoint )


            walkpathLine1 = walkCurves.item( 0 )
            walkpathLine1.isConstruction = True

            if stairAngle != 0:

                walkpathLine2 = walkCurves.item( 1 )
                walkpathLine2.isConstruction = True

                # ----- walk arc

                walkArc = sketchArcs.addFillet(
                    walkpathLine1, walkpathLine1.endSketchPoint.geometry,
                    walkpathLine2, walkpathLine2.startSketchPoint.geometry,
                    insideStringRadius + walkpathRadius
                )
                walkArc.isConstruction   = True

                if False:
                    # add walkpath angular dimension

                    sketchDimensions.addRadialDimension(
                        walkArc,
                        middlePoint( sketch, walkArc.startSketchPoint, walkArc.endSketchPoint, 0 )
                    )

            # ------------------------------------------------------------------------------

            if True and stairAngle != 0:

                # add a driven dimension angle inside

                sketchDimensions.addAngularDimension(
                    insideStringLine1,
                    insideStringLine2,
                    middlePoint( sketch,  insideStringLine1.startSketchPoint, insideStringLine2.endSketchPoint ),
                    False
                )


            if True:

                sketchDimensions.addDistanceDimension(
                    insideStringLine1.startSketchPoint,
                    walkpathLine1.startSketchPoint,
                    adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,
                    middlePoint( sketch,  insideStringLine1.startSketchPoint, walkpathLine1.startSketchPoint, -40.0 * sign( stairAngle ) ),
                    False
                )


                sketchDimensions.addDistanceDimension(
                    insideStringLine1.startSketchPoint,
                    outsideStringLine1.startSketchPoint,
                    adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,
                    middlePoint( sketch,  insideStringLine1.startSketchPoint, outsideStringLine1.startSketchPoint, -80.0 * sign( stairAngle ) ),
                    False
                )





        # ------------------------------------------------------------------------------
        # ----- add 1 mm fillet on outside string (WORKAROUND for compute)
        # ------------------------------------------------------------------------------

        if stairAngle != 0:

            outsideArc = sketchArcs.addFillet(
                outsideStringLine1, outsideStringLine1.endSketchPoint.geometry,
                outsideStringLine2, outsideStringLine2.startSketchPoint.geometry,
                0.1
            )
            outsideArc.isConstruction = False

            if False:
                sketchDimensions.addRadialDimension(
                    outsideArc,
                    middlePoint( sketch,  outsideArc.startSketchPoint, outsideArc.endSketchPoint, 0 )
                )

        # ------------------------------------------------------------------------------

        return( outsideStringLine1, insideStringLine1, walkpathLine1 )

    # ------------------------------------------------------------------------------

    def drawPointStepsSketch2D( self, walkSteps: dict  ) -> bool:

        futil.log( f' > drawPointStepsSketch2D()')

        # ------------------------------------------------------------------------------

        sketchPoints: adsk.fusion.SketchPoints = self.sketch.sketchPoints

        # ------------------------------------------------------------------------------

        for walkStep in walkSteps.values():
            sketchPoints.add( walkStep[ 'Point3D' ] )

        return True


    def drawLineStepsSketch2D( self, steps: dict, isConstruction = False ) -> bool:

        futil.log( f' > drawLineStepsSketch2D()')

        # ------------------------------------------------------------------------------

        sketchPoints: adsk.fusion.SketchPoints               = self.sketch.sketchPoints
        sketchLines: adsk.fusion.SketchLines                 = self.sketch.sketchCurves.sketchLines

        # ------------------------------------------------------------------------------

        for step in steps.values():

            walk    = step[ 'Walk' ]
            inside  = step[ 'Inside' ]
            outside = step[ 'Outside' ]

            if 'Point3D' in walk.keys():
                walkPointSKT    = sketchPoints.add( step[ 'Walk' ] [ 'Point3D' ] )

            if 'Point3D' in inside.keys():
                insidePointSKT  = sketchPoints.add( step[ 'Inside' ] [ 'Point3D' ] )

            if 'Point3D' in outside.keys():
                outsidePointSKT = sketchPoints.add( step[ 'Outside' ] [ 'Point3D' ] )

            if 'Point3D' in inside.keys() and 'Point3D' in outside.keys():
                stepLineSKT = sketchLines.addByTwoPoints( insidePointSKT, outsidePointSKT )
                stepLineSKT.isConstruction = isConstruction

        return True


    def drawStairLinesSketch2D( self ) -> bool:

        futil.log( f' > drawStairLinesSketch2D()')

        # ------------------------------------------------------------------------------

        if len( self.stairs ) == 0:
            return False

        # ------------------------------------------------------------------------------

        sketchPoints: adsk.fusion.SketchPoints = self.sketch.sketchPoints
        sketchLines: adsk.fusion.SketchLines   = self.sketch.sketchCurves.sketchLines

        # ------------------------------------------------------------------------------

        for stair in self.stairs.values():

            # {
            #     'FrontLine3D': Line3D,
            #     'BackLine3D':  Line3D,
            #     'RabbetLine3D': Line3D,
            # }

            if 'FrontLine3D'  in stair.keys() and stair[ 'FrontLine3D' ] != None:
                overlapLineSKT: adsk.fusion.SketchLine = sketchLines.addByTwoPoints( stair[ 'FrontLine3D' ].startPoint, stair[ 'FrontLine3D' ].endPoint )
                overlapLineSKT.isConstruction = False

            if 'BackLine3D'   in stair.keys() and stair[ 'BackLine3D' ] != None:
                backLineSKT: adsk.fusion.SketchLine    = sketchLines.addByTwoPoints( stair[ 'BackLine3D' ].startPoint, stair[ 'BackLine3D' ].endPoint )
                backLineSKT.isConstruction = False

            if 'RabbetLine3D' in stair.keys() and stair[ 'RabbetLine3D' ] != None:
                backLineSKT: adsk.fusion.SketchLine    = sketchLines.addByTwoPoints( stair[ 'RabbetLine3D' ].startPoint, stair[ 'RabbetLine3D' ].endPoint )
                backLineSKT.isConstruction = True

            # if 'grooveLine3D_1' in stair.keys() and stair[ 'grooveLine3D_1' ] != None:
            #     backLineSKT: adsk.fusion.SketchLine    = sketchLines.addByTwoPoints( stair[ 'grooveLine3D_1' ].startPoint, stair[ 'grooveLine3D_1' ].endPoint )
            #     backLineSKT.isConstruction = True

            # if 'grooveLine3D_2' in stair.keys() and stair[ 'grooveLine3D_2' ] != None:
            #     backLineSKT: adsk.fusion.SketchLine    = sketchLines.addByTwoPoints( stair[ 'RabbetLine3D' ].startPoint, stair[ 'RabbetLine3D' ].endPoint )
            #     backLineSKT.isConstruction = True


    # ------------------------------------------------------------------------------
    # COMPUTE STAIR (BEFORE 3D)
    # ------------------------------------------------------------------------------

    def computeStair( self ) -> bool:

        futil.log( f' > computeStair()' )

        # balancingSteps:        dict = {},
        # balancingStepsOverlap: dict = {},
        # balancingStepsRiser:   dict = {},
        # balancingStepsBack:    dict = {},

        # ------------------------------------------------------------------------------

        isOverlap = True  if( self.isOverlapStair() and len( self.balancingStepsOverlap ) > 0 )  else False
        isRiser   = True  if( self.isRiserStair()   and len( self.balancingStepsRiser )   > 0 )  else False

        # ------------------------------------------------------------------------------

        data: dict = {}

        for step in range( 0, self.stepNumber ):

            # ------------------------------------------------------------------------------
            # frontLine3D
            # ------------------------------------------------------------------------------

            stepIndex = step

            if isOverlap:
                frontLine3D = self.createInOutLine3D( self.balancingStepsOverlap.get( stepIndex ) )
            else:
                frontLine3D = self.createInOutLine3D( self.balancingSteps.get( stepIndex ) )

            # ------------------------------------------------------------------------------
            # backLine3D - riser not for the last
            # ------------------------------------------------------------------------------

            stepIndex = step + 1

            if isRiser and stepIndex < self.stepNumber:
                backLine3D = self.createInOutLine3D( self.balancingStepsBack.get( stepIndex ) )
            else:
                backLine3D = self.createInOutLine3D( self.balancingSteps.get( stepIndex ) )

            # ------------------------------------------------------------------------------

            rabbetLine3D   = None
            grooveLine3D_1 = None
            grooveLine3D_2 = None

            # ------------------------------------------------------------------------------
            # rabbetLine3D
            # ------------------------------------------------------------------------------

            stepIndex = step + 1

            if isRiser and stepIndex < self.stepNumber:
                rabbetLine3D = self.createInOutLine3D( self.balancingSteps.get( stepIndex ) )

            # ------------------------------------------------------------------------------
            # grooveLine3D_1
            # ------------------------------------------------------------------------------

            stepIndex = step

            if isRiser and stepIndex >= 0:
                grooveLine3D_1 = self.createInOutLine3D( self.balancingSteps.get( stepIndex ) )

            # ------------------------------------------------------------------------------
            # grooveLine3D_2
            # ------------------------------------------------------------------------------

            stepIndex = step

            if isRiser and stepIndex >= 0:
                grooveLine3D_2 = self.createInOutLine3D( self.balancingStepsRiser.get( stepIndex ) )


            # ------------------------------------------------------------------------------
            # add dict
            # ------------------------------------------------------------------------------

            data[ step ] = {
                'FrontLine3D':    frontLine3D,
                'BackLine3D':     backLine3D,
                'RabbetLine3D':   rabbetLine3D,
                'GrooveLine3D_1': grooveLine3D_1,
                'GrooveLine3D_2': grooveLine3D_2,
            }

        # ------------------------------------------------------------------------------

        # last stair is a nose stair (overlap only - no riser)

        if self.isOverlapLast and isOverlap:

            step = self.stepNumber

            # ------------------------------------------------------------------------------
            # frontLine3D

            frontLine3D = self.createInOutLine3D( self.balancingStepsOverlap.get( step ) )

            # ------------------------------------------------------------------------------
            # backLine3D

            backLine3D = self.createInOutLine3D( self.balancingSteps.get( step ) )

            # ------------------------------------------------------------------------------
            # add dict

            data[ step ] = {
                'FrontLine3D':    frontLine3D,
                'BackLine3D':     backLine3D,
                'RabbetLine3D':   None,
                'GrooveLine3D_1': None,
                'GrooveLine3D_2': None,
            }

        # ------------------------------------------------------------------------------

        self.stairs = data

        return True


    def createInOutLine3D( self, stepItem: dict ) -> adsk.core.Line3D:

        line3D: adsk.core.Line3D = None

        is_inside  = 'Point3D' in stepItem[ 'Inside' ].keys();
        is_outside = 'Point3D' in stepItem[ 'Outside' ].keys();

        if is_inside and is_outside:
            line3D = adsk.core.Line3D.create(
                stepItem[ 'Inside' ]  [ 'Point3D' ],
                stepItem[ 'Outside' ] [ 'Point3D' ]
            )

        return line3D


    # ------------------------------------------------------------------------------
    # CREATE 3D STAIRS AND RISERS COMPONENTS
    # ------------------------------------------------------------------------------

    def createSteps3D( self ) -> bool:

        futil.log( f' > createSteps3D()')

        # ------------------------------------------------------------------------------

        if self.isCreateSteps == False:
            return False

        if len( self.stairs ) == 0:
            return False

        if self.stairThickness == 0:
            return False

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        # ------------------------------------------------------------------------------
        # Create parent component for all steps
        # ------------------------------------------------------------------------------

        parentOccurrences: adsk.fusion.Occurrences = self.stairOccurence.component.occurrences

        parentOccurrence:  adsk.fusion.Occurrence  = parentOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        parentOccurrence.isGroundToParent = True

        parentComponent:   adsk.fusion.Component   = parentOccurrence.component
        parentComponent.name = f'STEPS'

        # Get occurences of the parent component to add sub components

        subOccurrences: adsk.fusion.Occurrences    = parentComponent.occurrences

        # ------------------------------------------------------------------------------
        # Create steps
        # ------------------------------------------------------------------------------

        timeline: adsk.fusion.Timeline = design.timeline
        timelineStart = None
        timelineEnd   = None

        for step, stair in self.stairs.items():

            # Create reference

            reference = f'S-{step + 1}'

            # Create transform matrix

            matrixTransform = adsk.core.Matrix3D.create()

            ( xTrans, yTrans, zTrans, zAngleRotate ) = self.getStairXYZandAngleByLevel( step + 1, stair[ 'FrontLine3D' ] )

            if zAngleRotate != 0:

                zAxis = adsk.core.Vector3D.create( z = 1 )

                matrixRotation = adsk.core.Matrix3D.create()
                matrixRotation.setToRotation( -zAngleRotate, zAxis, adsk.core.Point3D.create() )
                matrixTransform.transformBy( matrixRotation )

            matrixTranslation = adsk.core.Matrix3D.create()
            matrixTranslation.translation = adsk.core.Vector3D.create( xTrans, yTrans, zTrans )
            matrixTransform.transformBy( matrixTranslation )

            # Create sub occurence

            subOccurrence: adsk.fusion.Occurrence = subOccurrences.addNewComponent( matrixTransform )
            subOccurrence.isGroundToParent = True

            # Create sub component in sub occurence

            subComponent: adsk.fusion.Component   = subOccurrence.component
            subComponent.name = f'STEP {reference}'
            subComponent.partNumber = reference

            # subComponent.material
            # subComponent.componentColor

            # ------------------------------------------------------------------------------
            # Init index start timelineObject
            # ------------------------------------------------------------------------------

            if timelineStart == None:
                timelineStart = subOccurrence.timelineObject.index

            # ------------------------------------------------------------------------------
            # Extrude stair step
            # ------------------------------------------------------------------------------

            body = None

            if True:

                # Create sketch on xyPlane

                sketchBase: adsk.fusion.Sketch = subComponent.sketches.add( subComponent.xYConstructionPlane )
                sketchBase.name = f'Sketch Step {reference}'
                sketchBase.arePointsShown              = False
                sketchBase.areConstraintsShown         = False
                sketchBase.areDimensionsShown          = False
                sketchBase.areProfilesShown            = True # need to extrude profile
                sketchBase.isConstructionGeometryShown = False
                sketchBase.isProjectedGeometryShown    = False
                sketchBase.isComputeDeferred           = True

                sketchLines: adsk.fusion.SketchLines = sketchBase.sketchCurves.sketchLines

                # ------------------------------------------------------------------------------

                timelineEnd = sketchBase.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------

                # Draw inside and outside strings lines

                self.drawStairwaySketch2D( sketchBase )

                # Draw front and back sketch lines

                if stair[ 'FrontLine3D' ] != None  and  stair[ 'BackLine3D' ] != None:
                    frontLineSKT: adsk.fusion.SketchLine = sketchLines.addByTwoPoints( stair[ 'FrontLine3D' ].startPoint, stair[ 'FrontLine3D' ].endPoint )
                    frontLineSKT.isConstruction = False

                    backLineSKT: adsk.fusion.SketchLine  = sketchLines.addByTwoPoints( stair[ 'BackLine3D' ].startPoint, stair[ 'BackLine3D' ].endPoint )
                    backLineSKT.isConstruction = False

                # ------------------------------------------------------------------------------

                self.moveSketchToFrontLineByLevel( step + 1, sketchBase, stair[ 'FrontLine3D' ] )

                # ------------------------------------------------------------------------------

                sketchBase.isVisible = False
                sketchBase.isComputeDeferred = False

                # Extrude the profile to create the body

                if True and len( sketchBase.profiles ) > 0:

                    profileExtrude: adsk.fusion.Profile = sketchBase.profiles.item( 0 )
                    distanceExtrude = adsk.core.ValueInput.createByReal( self.stairThickness )

                    extrudeFeatures: adsk.fusion.ExtrudeFeatures = subComponent.features.extrudeFeatures

                    extrudeFeature:  adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple( profileExtrude, distanceExtrude, adsk.fusion.FeatureOperations.NewBodyFeatureOperation )
                    extrudeFeature.name = f'Extrude Step {reference}'

                    # ------------------------------------------------------------------------------

                    body: adsk.fusion.BRepBody = extrudeFeature.bodies.item( 0 )
                    body.name = f'Body Step {reference}'

                    # ------------------------------------------------------------------------------

                    timelineEnd = extrudeFeature.timelineObject.index # timeline last operation


            # ------------------------------------------------------------------------------
            # Engraving reference on BOTTOM face
            # ------------------------------------------------------------------------------

            if self.isEngraveReference and body != None and not( step == self.stepNumber and self.isOverlapStair() ):

                # faceTop    = max( faces, key = ( lambda f: f.centroid.z ) )
                # faceBottom = min( faces, key = ( lambda f: f.centroid.z ) )
                # faceRight  = max( faces, key = ( lambda f: f.centroid.x ) )
                # faceLeft   = min( faces, key = ( lambda f: f.centroid.x ) )
                # faceFront  = min( faces, key = ( lambda f: f.centroid.y ) )
                # faceBack   = max( faces, key = ( lambda f: f.centroid.y ) )

                faces:      adsk.fusion.BRepFaces = body.faces
                faceBottom: adsk.fusion.BRepFace  = min( faces, key = ( lambda f: f.centroid.z ) ) # bottom face

                # create sketch on 'bottom' face of stair

                sketchEngrave: adsk.fusion.Sketch = subComponent.sketches.addWithoutEdges( faceBottom )
                sketchEngrave.name = f'Sketch Step Engrave {reference}'
                sketchEngrave.arePointsShown              = False
                sketchEngrave.areConstraintsShown         = False
                sketchEngrave.areDimensionsShown          = False
                sketchEngrave.areProfilesShown            = True # need to extrude profile
                sketchEngrave.isConstructionGeometryShown = False
                sketchEngrave.isProjectedGeometryShown    = False
                sketchEngrave.isComputeDeferred           = True

                sketchLines: adsk.fusion.SketchLines = sketchEngrave.sketchCurves.sketchLines

                # ------------------------------------------------------------------------------

                timelineEnd = sketchEngrave.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------

                # METHOD 1 : sketchText with createInput

                if True:
                    sketchTexts: adsk.fusion.SketchTexts = sketchEngrave.sketchTexts
                    textInput = sketchTexts.createInput(
                        f'{reference}',
                        5,
                        sketchEngrave.modelToSketchSpace( faceBottom.centroid )
                    )
                    sketchText = sketchTexts.add( textInput )


                # METHOD 2 : sketchText with createInput2 with WORKAROUND

                if False:

                    minPoint: adsk.core.Point3D = faceBottom.boundingBox.minPoint
                    maxPoint: adsk.core.Point3D = faceBottom.boundingBox.maxPoint

                    #sketchLines.addTwoPointRectangle( minPoint, maxPoint )

                    # xDelta = maxPoint.x - minPoint.x
                    # yDelta = maxPoint.y - minPoint.y
                    # zDelta = maxPoint.z - minPoint.z

                    # deltaPoint = adsk.core.Point3D.create( xDelta, yDelta, zDelta )

                    futil.log( f'minPoint {minPoint.asArray()}' )
                    futil.log( f'maxPoint {maxPoint.asArray()}' )
                    futil.log( ' - ' )
                    # futil.log( f'deltaPoint {deltaPoint.asArray()}' )
                    # futil.log( ' - ' )

                    # WORKAROUND - future TODO move/rotate with matrix because the coordinates are globals or set component active

                    if self.stairAngle >= 0:
                        minPoint.x = -minPoint.x
                    else:
                        maxPoint.x = -maxPoint.x

                    sketchLines.addTwoPointRectangle( minPoint, maxPoint )


                    sketchTexts: adsk.fusion.SketchTexts = sketchEngrave.sketchTexts
                    textInput = sketchTexts.createInput2( f'{reference}', 5 )
                    textInput.setAsMultiLine(
                        minPoint,
                        maxPoint,
                        adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                        adsk.core.VerticalAlignments.MiddleVerticalAlignment,
                        0
                    )
                    sketchText = sketchTexts.add( textInput )


                # ------------------------------------------------------------------------------
                # extrude Text

                extrudeFeatures = subComponent.features.extrudeFeatures

                # METHOD : addSimple
                # extrudeText: adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple(
                #     sketchText,
                #     adsk.core.ValueInput.createByReal( -0.1 ),
                #     adsk.fusion.FeatureOperations.CutFeatureOperation
                # )
                # extrudeText.name = f'Engrave Step {reference} with addSimple'

                # METHOD : createInput + add
                extrudeFeature = extrudeFeatures.createInput( sketchText, adsk.fusion.FeatureOperations.CutFeatureOperation )
                extrudeFeature.setDistanceExtent( False, adsk.core.ValueInput.createByReal( -0.1 ) )
                extrudeFeature.participantBodies = [ body ]

                extrudeText: adsk.fusion.ExtrudeFeature = extrudeFeatures.add( extrudeFeature )                        
                extrudeText.name = f'Engrave Step {reference}'

                # ------------------------------------------------------------------------------

                timelineEnd =  extrudeText.timelineObject.index # timeline last operation


            # ------------------------------------------------------------------------------
            # Make a groove in body for riser on BOTTOM face
            # ------------------------------------------------------------------------------

            if body != None and self.isRiserStair() and self.riserGroove > 0:

                if stair[ 'GrooveLine3D_1' ] != None and stair[ 'GrooveLine3D_2' ] != None:

                    # create sketch on 'xyPlane' face

                    sketchGroove: adsk.fusion.Sketch = subComponent.sketches.add( subComponent.xYConstructionPlane )
                    sketchGroove.name = f'Sketch Step Groove {reference}'
                    sketchGroove.arePointsShown              = False
                    sketchGroove.areConstraintsShown         = False
                    sketchGroove.areDimensionsShown          = False
                    sketchGroove.areProfilesShown            = True # need to extrude profile
                    sketchGroove.isConstructionGeometryShown = False
                    sketchGroove.isProjectedGeometryShown    = False
                    sketchGroove.isComputeDeferred           = True

                    sketchLines: adsk.fusion.SketchLines = sketchGroove.sketchCurves.sketchLines

                    # ------------------------------------------------------------------------------

                    timelineEnd = sketchGroove.timelineObject.index # timeline last operation

                    # ------------------------------------------------------------------------------

                    # draw sketch inside and outside strings lines on 'bottom' face of stair

                    self.drawStairwaySketch2D( sketchGroove )

                    # draw sketch groove lines in sketch in 'bottom' face of stair

                    backLineSKT: adsk.fusion.SketchLine    = sketchLines.addByTwoPoints( stair[ 'GrooveLine3D_1' ].startPoint, stair[ 'GrooveLine3D_1' ].endPoint )
                    backLineSKT.isConstruction = False

                    overlapLineSKT: adsk.fusion.SketchLine = sketchLines.addByTwoPoints( stair[ 'GrooveLine3D_2' ].startPoint, stair[ 'GrooveLine3D_2' ].endPoint )
                    overlapLineSKT.isConstruction = False

                    # ------------------------------------------------------------------------------

                    self.moveSketchToFrontLineByLevel( step + 1, sketchGroove, stair[ 'FrontLine3D' ] )

                    # ------------------------------------------------------------------------------
                    # make a groove in the body (cut)

                    if len( sketchGroove.profiles ) > 0:

                        extrudeFeatures: adsk.fusion.ExtrudeFeatures = subComponent.features.extrudeFeatures
                        profileGroove:   adsk.fusion.Profile = sketchGroove.profiles.item( 0 )

                        distanceGroove = adsk.core.ValueInput.createByReal( self.riserGroove )

                        # METHOD : addSimple
                        # extrudeGroove: adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple( profileGroove, distanceGroove, adsk.fusion.FeatureOperations.CutFeatureOperation )
                        # extrudeGroove.name = f'Cut Step Groove Riser {reference} with addSimple'

                        # METHOD : createInput + add
                        extrudeFeatureGroove = extrudeFeatures.createInput( profileGroove, adsk.fusion.FeatureOperations.CutFeatureOperation )
                        extrudeFeatureGroove.setDistanceExtent( False, distanceGroove )
                        extrudeFeatureGroove.participantBodies = [ body ]

                        extrudeGroove: adsk.fusion.ExtrudeFeature = extrudeFeatures.add( extrudeFeatureGroove )                        
                        extrudeGroove.name = f'Cut Step Groove Riser {reference}'

                        # ------------------------------------------------------------------------------

                        timelineEnd = extrudeGroove.timelineObject.index # timeline last operation

                    # ------------------------------------------------------------------------------

                    sketchGroove.isVisible = False
                    sketchGroove.isComputeDeferred = False

        # ------------------------------------------------------------------------------
        # Create timeline group
        # ------------------------------------------------------------------------------

        timelineGroup = timeline.timelineGroups.add(
            timelineStart,
            timelineEnd
        )
        timelineGroup.name = f'Group Steps'

        # ------------------------------------------------------------------------------

        self.stepsGroupOccurence = parentOccurrence

        return True


    def createLayoutSteps3D( self )-> adsk.fusion.Occurrence:

        futil.log( f' > createLayoutSteps3D()')

        # ------------------------------------------------------------------------------

        if self.isCreateSteps == False:
            return False

        if self.isCreateStairLayout == False:
            return None

        if self.stepsGroupOccurence == None:
            return None

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        xOrigin  = self.flatOriginX + 0
        yOrigin  = self.flatOriginY
        xSpacing = self.flatSpaceX + self.stepGoing
        ySpacing = self.flatSpaceY + self.stairWidth
        modulo   = self.flatModulo
        index    = 0

        # ------------------------------------------------------------------------------
        # Create parent component for layout stairs
        # ------------------------------------------------------------------------------

        parentOccurrences: adsk.fusion.Occurrences = self.stairLayoutOccurence.component.occurrences
        parentOccurrence:  adsk.fusion.Occurrence  = parentOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        parentOccurrence.isGroundToParent = False

        # parent component

        parentComponent:   adsk.fusion.Component   = parentOccurrence.component
        parentComponent.name = f'STEPS layout'

        # Get occurences of the parent component to add sub components

        subOccurrences: adsk.fusion.Occurrences    = parentComponent.occurrences

        # ------------------------------------------------------------------------------

        timeline: adsk.fusion.Timeline = design.timeline
        timelineStart = None
        timelineEnd   = None

        # ------------------------------------------------------------------------------

        for sourceOccurence in self.stepsGroupOccurence.childOccurrences:

            col = index % modulo
            row = math.floor( index / modulo )

            xDestination = row * xSpacing
            yDestination = col * ySpacing

            # ------------------------------------------------------------------------------

            # init matrix
            matrixTransform = adsk.core.Matrix3D.create()

            # rotation
            matrixRotation = adsk.core.Matrix3D.create()
            matrixRotation.setToRotation(
                -math.pi / 2,
                adsk.core.Vector3D.create( z = 1 ),
                adsk.core.Point3D.create( x = xDestination, y = yDestination )
            )
            matrixTransform.transformBy( matrixRotation )

            # rotation 2
            matrixRotation = adsk.core.Matrix3D.create()
            matrixRotation.setToRotation(
                math.pi,
                adsk.core.Vector3D.create( y = 1 ),
                adsk.core.Point3D.create( x = xDestination, y = yDestination )
            )
            matrixTransform.transformBy( matrixRotation )

            # translation
            matrixTransform.translation = adsk.core.Vector3D.create( xDestination, yDestination, self.stairThickness )

            # add
            subOccurrence = subOccurrences.addExistingComponent( sourceOccurence.component, matrixTransform )

            # ------------------------------------------------------------------------------

            if timelineStart == None:
                timelineStart = subOccurrence.timelineObject.index
            else:
                timelineEnd   = subOccurrence.timelineObject.index

            # ------------------------------------------------------------------------------

            index += 1

        # ------------------------------------------------------------------------------

        # Create timeline parent

        timelineGroup = timeline.timelineGroups.add(
            timelineStart,
            timelineEnd
        )
        timelineGroup.name = f'Group Flatted Steps'

        # ------------------------------------------------------------------------------

        # Move parent occurence to xOrigin, yOrigin

        moveOccurence( parentOccurrence, x = xOrigin, y = yOrigin )


        # ------------------------------------------------------------------------------

        return True

    # ------------------------------------------------------------------------------

    def createRisers3D( self ) -> adsk.fusion.Occurrence:

        futil.log( f' > createRisers3D()')

        # ------------------------------------------------------------------------------

        if self.isRiserStair() == False:
            return False

        if self.isCreateRisers == False:
            return False

        if self.riserThickness == 0:
            return False

        if len( self.stairs ) == 0:
            return False

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct

        # ------------------------------------------------------------------------------

        timeline: adsk.fusion.Timeline = design.timeline
        timelineStart = None
        timelineEnd   = None

        # ------------------------------------------------------------------------------
        # Create group component for all risers
        # ------------------------------------------------------------------------------

        parentOccurrences: adsk.fusion.Occurrences = self.stairOccurence.component.occurrences

        parentOccurrence:  adsk.fusion.Occurrence  = parentOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        parentOccurrence.isGroundToParent = True

        parentComponent:   adsk.fusion.Component   = parentOccurrence.component
        parentComponent.name = f'RISERS'

        # Get occurences of the group component to add sub components

        subOccurrences: adsk.fusion.Occurrences   = parentComponent.occurrences

        # ------------------------------------------------------------------------------
        # Create risers
        # ------------------------------------------------------------------------------

        for step, stair in self.stairs.items():

            # Break for the last stair is overlap

            if step == self.stepNumber and self.isOverlapStair():
                break

            # Create reference

            reference = f'R-{step+1}'

            # Create transform matrix

            matrixTransform = adsk.core.Matrix3D.create()

            ( xTrans, yTrans, zTrans, zAngleRotate ) = self.getStairXYZandAngleByLevel( step, stair[ 'GrooveLine3D_1' ] )

            if zAngleRotate != 0:

                zAxis = adsk.core.Vector3D.create( z = 1 )

                matrixRotation = adsk.core.Matrix3D.create()
                matrixRotation.setToRotation( -zAngleRotate, zAxis, adsk.core.Point3D.create() )
                matrixTransform.transformBy( matrixRotation )

            matrixTranslation = adsk.core.Matrix3D.create()
            matrixTranslation.translation = adsk.core.Vector3D.create( xTrans, yTrans, zTrans )
            matrixTransform.transformBy( matrixTranslation )

            # Create sub occurence

            subOccurrence: adsk.fusion.Occurrence = subOccurrences.addNewComponent( matrixTransform )
            subOccurrence.isGroundToParent = True

            # Create sub component in sub occurence

            subComponent: adsk.fusion.Component   = subOccurrence.component
            subComponent.name = f'RISER {reference}'
            subComponent.partNumber = reference

            # subComponent.material
            # subComponent.componentColor

            # ------------------------------------------------------------------------------
            # Init index start timelineObject
            # ------------------------------------------------------------------------------

            if timelineStart == None:
                timelineStart = subOccurrence.timelineObject.index

            # ------------------------------------------------------------------------------
            # Extrude riser
            # ------------------------------------------------------------------------------

            body = None

            if True:

                # Create sketch on xyPlane

                sketchBase: adsk.fusion.Sketch = subComponent.sketches.add( subComponent.xYConstructionPlane )
                sketchBase.name = f'Sketch Riser {reference}'
                sketchBase.arePointsShown              = False
                sketchBase.areConstraintsShown         = False
                sketchBase.areDimensionsShown          = False
                sketchBase.areProfilesShown            = True # need to extrude profile
                sketchBase.isConstructionGeometryShown = False
                sketchBase.isProjectedGeometryShown    = False
                sketchBase.isComputeDeferred           = True

                sketchLines: adsk.fusion.SketchLines = sketchBase.sketchCurves.sketchLines

                # ------------------------------------------------------------------------------

                timelineEnd = sketchBase.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------

                # Draw inside and outside strings lines

                self.drawStairwaySketch2D( sketchBase )

                # Draw front and back sketch lines

                if stair[ 'GrooveLine3D_1' ] != None  and  stair[ 'GrooveLine3D_2' ] != None:
                    frontLineSKT: adsk.fusion.SketchLine = sketchLines.addByTwoPoints( stair[ 'GrooveLine3D_1' ].startPoint, stair[ 'GrooveLine3D_1' ].endPoint )
                    frontLineSKT.isConstruction = False

                    backLineSKT: adsk.fusion.SketchLine  = sketchLines.addByTwoPoints( stair[ 'GrooveLine3D_2' ].startPoint, stair[ 'GrooveLine3D_2' ].endPoint )
                    backLineSKT.isConstruction = False

                # ------------------------------------------------------------------------------

                self.moveSketchToFrontLineByLevel( step, sketchBase, stair[ 'GrooveLine3D_1' ] )

                # ------------------------------------------------------------------------------

                sketchBase.isVisible = False
                sketchBase.isComputeDeferred = False

                # Extrude the profile to create the body

                if True and len( sketchBase.profiles ) > 0:

                    if step == 0:
                        distance = self.stepHeight + self.riserGroove - self.stairThickness
                    else:
                        distance = self.stepHeight + self.riserGroove


                    profileExtrude: adsk.fusion.Profile = sketchBase.profiles.item( 0 )
                    distanceExtrude = adsk.core.ValueInput.createByReal( distance )

                    extrudeFeatures: adsk.fusion.ExtrudeFeatures = subComponent.features.extrudeFeatures

                    extrudeFeature:  adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple( profileExtrude, distanceExtrude, adsk.fusion.FeatureOperations.NewBodyFeatureOperation )
                    extrudeFeature.name = f'Extrude Riser {reference}'

                    # ------------------------------------------------------------------------------

                    body: adsk.fusion.BRepBody = extrudeFeature.bodies.item( 0 )
                    body.name = f'Body Riser {reference}'

                    # ------------------------------------------------------------------------------

                    timelineEnd = extrudeFeature.timelineObject.index # timeline last operation

            # ------------------------------------------------------------------------------
            # Engraving riser number on BOTTOM face
            # ------------------------------------------------------------------------------

            if self.isEngraveReference and body != None:

                # faceTop    = max( faces, key = ( lambda f: f.centroid.z ) )
                # faceBottom = min( faces, key = ( lambda f: f.centroid.z ) )
                # faceRight  = max( faces, key = ( lambda f: f.centroid.x ) )
                # faceLeft   = min( faces, key = ( lambda f: f.centroid.x ) )
                # faceFront  = min( faces, key = ( lambda f: f.centroid.y ) )
                # faceBack   = max( faces, key = ( lambda f: f.centroid.y ) )

                faces:    adsk.fusion.BRepFaces = body.faces
                faceBack: adsk.fusion.BRepFace  = max( faces, key = ( lambda f: f.centroid.y ) ) # back face

                # create sketch on 'bottom' face

                sketchEngrave: adsk.fusion.Sketch = subComponent.sketches.addWithoutEdges( faceBack )
                sketchEngrave.name = f'Sketch Riser Engrave {reference}'
                sketchEngrave.arePointsShown              = False
                sketchEngrave.areConstraintsShown         = False
                sketchEngrave.areDimensionsShown          = False
                sketchEngrave.areProfilesShown            = True # need to extrude profile
                sketchEngrave.isConstructionGeometryShown = False
                sketchEngrave.isProjectedGeometryShown    = False
                sketchEngrave.isComputeDeferred           = True

                sketchLines: adsk.fusion.SketchLines = sketchEngrave.sketchCurves.sketchLines

                # ------------------------------------------------------------------------------

                timelineEnd = sketchEngrave.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------

                # METHOD 1 : sketchText with createInput
                if True:

                    sketchTexts: adsk.fusion.SketchTexts = sketchEngrave.sketchTexts
                    textInput = sketchTexts.createInput(
                        f'{reference}',
                        5,
                        sketchEngrave.modelToSketchSpace( faceBack.centroid )
                    )
                    sketchText = sketchTexts.add( textInput )


                # METHOD 2 : sketchText with createInput2 with WORKAROUND
                if False:

                    minPoint: adsk.core.Point3D = faceBack.boundingBox.minPoint
                    maxPoint: adsk.core.Point3D = faceBack.boundingBox.maxPoint

                    #sketchLines.addTwoPointRectangle( minPoint, maxPoint )

                    # xDelta = maxPoint.x - minPoint.x
                    # yDelta = maxPoint.y - minPoint.y
                    # zDelta = maxPoint.z - minPoint.z

                    # deltaPoint = adsk.core.Point3D.create( xDelta, yDelta, zDelta )

                    futil.log( f'minPoint {minPoint.asArray()}' )
                    futil.log( f'maxPoint {maxPoint.asArray()}' )
                    futil.log( ' - ' )
                    # futil.log( f'deltaPoint {deltaPoint.asArray()}' )
                    # futil.log( ' - ' )

                    # WORKAROUND - future TODO move/rotate with matrix because the coordinates are globals or set component active

                    if self.stairAngle >= 0:
                        minPoint.x = -minPoint.x
                    else:
                        maxPoint.x = -maxPoint.x

                    minPoint.y = minPoint.z
                    maxPoint.y = maxPoint.z

                    minPoint.z = 0
                    maxPoint.z = 0

                    sketchLines.addTwoPointRectangle( minPoint, maxPoint )


                    sketchTexts: adsk.fusion.SketchTexts = sketchEngrave.sketchTexts
                    textInput = sketchTexts.createInput2( f'{reference}', 5 )
                    textInput.setAsMultiLine(
                        minPoint,
                        maxPoint,
                        adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
                        adsk.core.VerticalAlignments.MiddleVerticalAlignment,
                        0
                    )
                    sketchText = sketchTexts.add( textInput )


                # ------------------------------------------------------------------------------
                # extrude Text

                extrudeFeatures = subComponent.features.extrudeFeatures

                # METHOD : addSimple
                # extrudeText: adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple(
                #     sketchText,
                #     adsk.core.ValueInput.createByReal( -0.1 ),
                #     adsk.fusion.FeatureOperations.CutFeatureOperation
                # )
                # extrudeText.name = f'Engrave Riser {reference} with addSimple'

                # METHOD : createInput + add
                extrudeFeature = extrudeFeatures.createInput( sketchText, adsk.fusion.FeatureOperations.CutFeatureOperation )
                extrudeFeature.setDistanceExtent( False, adsk.core.ValueInput.createByReal( -0.1 ) )
                extrudeFeature.participantBodies = [ body ]

                extrudeText: adsk.fusion.ExtrudeFeature = extrudeFeatures.add( extrudeFeature )                        
                extrudeText.name = f'Engrave Riser {reference}'


                # ------------------------------------------------------------------------------

                timelineEnd =  extrudeText.timelineObject.index # timeline last operation


            # ------------------------------------------------------------------------------
            # Make a rabbet in riser for stair (cut) on FRONT face
            # ------------------------------------------------------------------------------

            if body != None and self.isRiserStair() and self.riserRabbet > 0 and step > 0:

                # faceTop    = max( faces, key = ( lambda f: f.centroid.z ) )
                # faceBottom = min( faces, key = ( lambda f: f.centroid.z ) )
                # faceRight  = max( faces, key = ( lambda f: f.centroid.x ) )
                # faceLeft   = min( faces, key = ( lambda f: f.centroid.x ) )
                # faceFront  = min( faces, key = ( lambda f: f.centroid.y ) )
                # faceBack   = max( faces, key = ( lambda f: f.centroid.y ) )

                faces:     adsk.fusion.BRepFaces = body.faces
                faceFront: adsk.fusion.BRepFace  = min( faces, key = ( lambda f: f.centroid.y ) ) # front face
                #faceBack: adsk.fusion.BRepFace  = max( faces, key = ( lambda f: f.centroid.y ) ) # back face

                # ------------------------------------------------------------------------------
                # Create sketch on 'front' face

                sketchRabbet: adsk.fusion.Sketch = subComponent.sketches.addWithoutEdges( faceFront )
                sketchRabbet.name = f'Sketch Riser Rabbet {reference}'
                sketchRabbet.arePointsShown              = False
                sketchRabbet.areConstraintsShown         = False
                sketchRabbet.areDimensionsShown          = False
                sketchRabbet.areProfilesShown            = True # need to extrude profile
                sketchRabbet.isConstructionGeometryShown = False
                sketchRabbet.isProjectedGeometryShown    = False
                sketchRabbet.isComputeDeferred           = True

                sketchLines: adsk.fusion.SketchLines = sketchRabbet.sketchCurves.sketchLines

                # ------------------------------------------------------------------------------

                timelineEnd = sketchRabbet.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------
                # Draw rabbet ractangle extended on X

                xMin = faceFront.boundingBox.minPoint.x - self.riserThickness # WORKAROUND : remove riser thickness to enlarge xMin
                xMax = faceFront.boundingBox.maxPoint.x + self.riserThickness # WORKAROUND : add riser thickness to enlarge xMax

                startPoint = adsk.core.Point3D.create( xMin, 0, 0 )
                endPoint   = adsk.core.Point3D.create( xMax, self.stairThickness, 0 )

                rectangleSketchLines = sketchLines.addTwoPointRectangle( startPoint, endPoint )

                # ------------------------------------------------------------------------------
                # Make a rabbet in the body (cut)

                if len( sketchRabbet.profiles ) > 0:

                    extrudeFeatures: adsk.fusion.ExtrudeFeatures = subComponent.features.extrudeFeatures
                    profileRabbet:   adsk.fusion.Profile = sketchRabbet.profiles.item( 0 )

                    distanceRabbet = adsk.core.ValueInput.createByReal( -self.riserRabbet )

                    # METHOD : addSimple
                    # extrudeRabbet: adsk.fusion.ExtrudeFeature = extrudeFeatures.addSimple( profileRabbet, distanceRabbet, adsk.fusion.FeatureOperations.CutFeatureOperation )
                    # extrudeRabbet.name = f'Cut Riser Rabbet {reference} with addSimple'

                    # METHOD : createInput + add
                    extrudeFeatureRabbet = extrudeFeatures.createInput( profileRabbet, adsk.fusion.FeatureOperations.CutFeatureOperation )
                    extrudeFeatureRabbet.setDistanceExtent( False, distanceRabbet )
                    extrudeFeatureRabbet.participantBodies = [ body ]

                    extrudeRabbet: adsk.fusion.ExtrudeFeature = extrudeFeatures.add( extrudeFeatureRabbet )                        
                    extrudeRabbet.name = f'Cut Riser Rabbet {reference}'

                    # ------------------------------------------------------------------------------

                    timelineEnd = extrudeRabbet.timelineObject.index # timeline last operation

                # ------------------------------------------------------------------------------

                sketchRabbet.isVisible = False
                sketchRabbet.isComputeDeferred = False

        # ------------------------------------------------------------------------------
        # Create timeline group
        # ------------------------------------------------------------------------------

        timelineGroup = timeline.timelineGroups.add(
            timelineStart,
            timelineEnd
        )
        timelineGroup.name = f'Group Risers'

        # ------------------------------------------------------------------------------

        self.risersGroupOccurence = parentOccurrence

        return True


    def createLayoutRisers3D( self ) -> adsk.fusion.Occurrence:

        futil.log( f' > createLayoutRisers3D()')

        # ------------------------------------------------------------------------------

        if self.isRiserStair() == False:
            return False

        if self.isCreateRisers == False:
            return False

        if self.isCreateStairLayout == False:
            return False

        if self.risersGroupOccurence == None:
            return False

        # ------------------------------------------------------------------------------

        app = adsk.core.Application.get()
        design: adsk.fusion.Design = app.activeProduct


        xOrigin  = self.flatOriginX + 500
        yOrigin  = self.flatOriginY
        xSpacing = self.flatSpaceX + self.stepGoing
        ySpacing = self.flatSpaceY + self.stairWidth
        modulo   = self.flatModulo
        index    = 0

        # ------------------------------------------------------------------------------
        # Create parent component for layout risers
        # ------------------------------------------------------------------------------

        parentOccurrences: adsk.fusion.Occurrences = self.stairLayoutOccurence.component.occurrences
        parentOccurrence:  adsk.fusion.Occurrence  = parentOccurrences.addNewComponent( adsk.core.Matrix3D.create() )
        parentOccurrence.isGroundToParent = False

        parentComponent:   adsk.fusion.Component   = parentOccurrence.component
        parentComponent.name = f'RISERS layout'

        # Get occurences of the parent component to add sub components

        subOccurrences: adsk.fusion.Occurrences    = parentComponent.occurrences

        # ------------------------------------------------------------------------------

        timeline: adsk.fusion.Timeline = design.timeline
        timelineStart = None
        timelineEnd   = None

        for sourceOccurence in self.risersGroupOccurence.childOccurrences:

            col = index % modulo
            row = math.floor( index / modulo )

            xDestination = row * xSpacing
            yDestination = col * ySpacing

            # ------------------------------------------------------------------------------

            # init matrix
            matrixTransform = adsk.core.Matrix3D.create()

            # rotation
            zAxis = adsk.core.Vector3D.create( z = 1 )
            matrixRotation = adsk.core.Matrix3D.create()
            matrixRotation.setToRotation( - math.pi / 2, zAxis, adsk.core.Point3D.create( x = xDestination, y = yDestination ) )
            matrixTransform.transformBy( matrixRotation )

            # rotation2
            zAxis = adsk.core.Vector3D.create( y = 1 )
            matrixRotation = adsk.core.Matrix3D.create()
            matrixRotation.setToRotation( math.pi / 2, zAxis, adsk.core.Point3D.create( x = xDestination, y = yDestination ) )
            matrixTransform.transformBy( matrixRotation )

            # translation
            matrixTransform.translation = adsk.core.Vector3D.create( xDestination, yDestination, self.riserThickness )

            # add
            subOccurrence = subOccurrences.addExistingComponent( sourceOccurence.component, matrixTransform )

            # ------------------------------------------------------------------------------

            if timelineStart == None:
                timelineStart = subOccurrence.timelineObject.index
            else:
                timelineEnd   = subOccurrence.timelineObject.index

            index += 1

        # ------------------------------------------------------------------------------

        # Create timeline parent

        timelineGroup = timeline.timelineGroups.add(
            timelineStart,
            timelineEnd
        )
        timelineGroup.name = f'Group Flatted Risers'

        # ------------------------------------------------------------------------------

        # Move parent occurence to xOrigin, yOrigin

        moveOccurence( parentOccurrence, x = xOrigin, y = yOrigin )


        # ------------------------------------------------------------------------------

        return True

    # ------------------------------------------------------------------------------

    # voir https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-20302b02-fd08-11e4-b923-3417ebd3d5be

    def getStepHeightByLevel( self, level ) -> float:

        if level == 0:
            return 0
        return self.stepHeight * level - self.stairThickness


    def getStairXYZandAngleByLevel( self, level, line3D: adsk.core.Line3D ) -> tuple:

        xTrans = line3D.startPoint.x
        yTrans = line3D.startPoint.y
        zTrans = self.getStepHeightByLevel( level )

        # Compute rotate

        xDelta = line3D.endPoint.x - line3D.startPoint.x
        yDelta = line3D.endPoint.y - line3D.startPoint.y
        zDelta = 0

        vectorFrontLine = adsk.core.Vector3D.create( x = xDelta, y = yDelta )
        zAngleRotate = vectorFrontLine.angleTo( adsk.core.Vector3D.create( x = -1 ) )

        if self.stairAngle < 0:
            zAngleRotate += math.pi

        return ( xTrans, yTrans, zTrans, zAngleRotate )


    def moveSketchToFrontLineByLevel( self, level, sketch: adsk.fusion.Sketch, line3D: adsk.core.Line3D ) -> bool:

        ( xTrans, yTrans, zTrans, zAngleRotate ) = self.getStairXYZandAngleByLevel( level, line3D )

        sketchCurvesCollection = adsk.core.ObjectCollection.create()
        for sketchCurve in sketch.sketchCurves:
            sketchCurvesCollection.add( sketchCurve )

        # translate and rotate sketch

        matrixTransform = sketch.transform
        matrixTransform.translation = adsk.core.Vector3D.create( -xTrans, -yTrans, 0 ) # z=0 to stay on xyPlane of component

        if zAngleRotate != 0:
            zAxis = adsk.core.Vector3D.create( z = 1 )
            matrixRotation = adsk.core.Matrix3D.create()
            matrixRotation.setToRotation( zAngleRotate, zAxis, adsk.core.Point3D.create() )
            matrixTransform.transformBy( matrixRotation )

        sketch.move( sketchCurvesCollection, matrixTransform )

        return True


    # ------------------------------------------------------------------------------
    # COMPUTE STEP VALUES (going, height, blondelLaw, climbAngle)
    # ------------------------------------------------------------------------------

    def computeStepValues( self ) -> bool:

        futil.log( f' > computeStepValues()' )

        # ------------------------------------------------------------------------------

        self.stepGoing  = self.computeStepGoing( self.stepNumber )
        self.stepHeight = self.computeStepHeight( self.stepNumber )
        self.blondelLaw = self.computeStepBlondelLaw( self.stepGoing, self.stepHeight )
        self.climbAngle = self.computeStepClimbAngle( self.stepGoing, self.stepHeight )

        # ------------------------------------------------------------------------------

        return True

    # ------------------------------------------------------------------------------

    def computeStepGoing( self, stepNumber: int ) -> float:

        futil.log( f' > : computeStepGoing()' )

        # ------------------------------------------------------------------------------

        return self.walkpathLength / stepNumber


    def computeStepHeight( self, stepNumber: int ) -> float:

        futil.log( f' > : computeStepHeight()' )

        # ------------------------------------------------------------------------------

        return self.stairHeight / ( stepNumber + 1 )


    def computeStepBlondelLaw( self, stepGoing: float, stepHeight: float ) -> float:

        futil.log( f' > : computeStepBlondelLaw()' )

        # ------------------------------------------------------------------------------

        return stepHeight * 2 + stepGoing


    def computeStepClimbAngle( self, width: float, height: float ) -> float:

        futil.log( f' > : computeStepClimbAngle()' )

        # ------------------------------------------------------------------------------

        return math.atan( height / width )


    # ------------------------------------------------------------------------------
    # COMPUTE FLIGHT LENGTH MINI
    # ------------------------------------------------------------------------------

    def computeFlightLengthMinimum( self ) -> float:

        futil.log( f' > : computeFlightLengthMinimum()' )

        # ------------------------------------------------------------------------------

        lengthMinimum = math.sin( self.stairAngle ) * ( self.stairWidth + self.insideRadius )
        if( self.isOverlapStair() ):
            lengthMinimum += self.overlapLength

        # futil.log( f'lengthMinimum = {lengthMinimum}' )

        return lengthMinimum


    def setFlightLengthMinimumField( self, id: str, lengthMinimum: float ):

        futil.log( f' > : setFlightLengthMinimumField( {lengthMinimum} )' )

        # ------------------------------------------------------------------------------

        self.inputs.itemById( id ).minimumValue = lengthMinimum

        return True

    # ------------------------------------------------------------------------------
    # COMPUTE STEP NUMBER
    # ------------------------------------------------------------------------------

    def computeStepNumberMini( self ) -> int:

        futil.log( f' > : computeStepNumberMini()' )

        # ------------------------------------------------------------------------------

        return int( math.ceil( self.stairHeight / 20.0 ) - 1 )


    def computeStepNumberMaxi( self ) -> int:

        futil.log( f' > : computeStepNumberMaxi()' )

        # ------------------------------------------------------------------------------

        return int( math.floor( self.stairHeight / 15.0 ) - 1 )


    def computeStepNumberMiddle( self ) -> int:

        futil.log( f' > : computeStepNumberMiddle()' )

        # ------------------------------------------------------------------------------

        return int( round( ( self.stepNumberMini + self.stepNumberMaxi ) / 2, 0 ) )

    # ------------------------------------------------------------------------------

    def computeStepNumberOptimal( self ) -> bool:

        futil.log( f' > computeStepNumberOptimal()' )

        # ------------------------------------------------------------------------------

        # compute steps mini and maxi for 200 mm and 150 mm
        stepNumberMini = self.computeStepNumberMini()
        stepNumberMaxi = self.computeStepNumberMaxi()

        # generate lists
        stepNumberList = []
        stepGoingList  = []
        blondelLawList = []

        for stepNumber in range( stepNumberMini, stepNumberMaxi + 1 ):
            stepNumberList.append( stepNumber )

            stepGoing = self.computeStepGoing( stepNumber )
            stepGoingList.append( stepGoing )

            blondelLaw = self.computeStepBlondelLaw( stepGoing, self.computeStepHeight( stepNumber ) )
            blondelLawList.append( blondelLaw )

        # search the blondel law value closest to 630 mm
        self.blondelLaw = blondelLawList[ min( range( len( blondelLawList ) ), key = lambda i: abs( blondelLawList[ i ] - 63.0 ) ) ]

        # search the stepNumber for the closest blondel law value found
        for id, blondelLaw in enumerate( blondelLawList ):

            if self.blondelLaw == blondelLaw:
                stepNumber = stepNumberList[ id ]
                stepGoing  = stepGoingList[ id ]
                break

        # sets
        self.stepNumber = stepNumber
        self.stepNumberMini = min( stepNumber, stepNumberMini )
        self.stepNumberMaxi = max( stepNumber, stepNumberMaxi )

        futil.log( f' > : self.stepNumberMini = {self.stepNumberMini}' )
        futil.log( f' > : self.stepNumberMaxi = {self.stepNumberMaxi}' )
        futil.log( f' > : self.stepNumber     = {self.stepNumber}' )

        return True


    # ------------------------------------------------------------------------------
    # COMPUTE WALKPATH
    # ------------------------------------------------------------------------------

    def getWalkpathMaxiRadius( self, stairWidth: float ) -> float:

        return min( stairWidth / 2.0, 50.0 )


    def computeWalkpathValues( self) -> bool:

        futil.log( f' > computeWalkpathValues()' )

        # ------------------------------------------------------------------------------

        self.startLength = self.frontReserveLength

        if self.isOverlapStair():
            self.startLength += self.overlapLength

        self.totalLength     = self.getTotalLengthCurves( self.walkCurvesSKT )
        self.walkpathLength  = self.totalLength - self.startLength

        return True

    # ------------------------------------------------------------------------------

    def computeWalkSteps( self, offset: float = 0 ) -> dict:

        futil.log( f' > computeWalkSteps( {offset * 10} )')

        # ------------------------------------------------------------------------------

        data: dict = {}

        for step in range( 0, self.stepNumber + 1 ):

            # compute walkDistance

            walkDistance = ( self.stepGoing * step ) + self.startLength - offset

            # limit walkDistance

            walkDistance = min( walkDistance, self.totalLength )

            # ------------------------------------------------------------------------------

            # futil.log( f' > step : # {step}' )
            # futil.log( f' > offset               : {offset * 10}' )
            # futil.log( f' > walkDistance         : {walkDistance * 10}' )
            # futil.log( f' > self.walkpathLength  : {self.walkpathLength * 10}' )
            # futil.log( f' > self.totalLength     : {self.totalLength * 10}' )
            # futil.log( f' >' )

            # ------------------------------------------------------------------------------

            ( isDataAtLength, walkPoint3D, walkCurveSKT, walkTangentVector ) = self.getDataAtLength( walkDistance, self.walkCurvesSKT )

            if isDataAtLength:

                # create crosswise Line3D from tangent

                startPoint3D: adsk.core.Point3D = walkPoint3D

                endPoint3D: adsk.core.Point3D = walkPoint3D.copy() # make a copy from point before translate
                endPoint3D.translateBy( walkTangentVector )  # move

                walkCrosswiseLine3D = adsk.core.Line3D.create( startPoint3D, endPoint3D )

                # create matrix totate 90° Z axe

                vectorZ        = adsk.core.Vector3D.create( z = 1 )
                rotationMatrix = adsk.core.Matrix3D.create()
                rotationMatrix.setToRotation( math.pi / 2, vectorZ, startPoint3D )

                # rotation

                walkCrosswiseLine3D.transformBy( rotationMatrix )

                # display vector (debug)

                # sketchLines.addByTwoPoints( walkCrosswiseLine3D.startPoint, walkCrosswiseLine3D.endPoint )
                # sketchLines.isConstruction = True

                # ------------------------------------------------------------------------------

                # add dict

                data[ step ] = {
                    'Point3D':         walkPoint3D,
                    'CurveSKT':        walkCurveSKT,
                    'Distance':        walkDistance,
                    'CrosswiseLine3D': walkCrosswiseLine3D
                }


        # ------------------------------------------------------------------------------

        return data


    def computeWalkStepsCrosswise( self, walkData: dict, curves: list ) -> dict:

        futil.log( f' > : computeWalkStepsCrosswise()' )

        # ------------------------------------------------------------------------------

        data: dict = {}

        bigCurves: adsk.core.NurbsCurve3D = getBigNurbsCurve( curves )

        # ------------------------------------------------------------------------------

        for step, walkData in walkData.items():

            # get the nearest point to the intersection of a line with curves

            ( isFound, nearestPoint3D, nearestCurveSKT, nearestCurveId ) = self.getNearestPointIntersectLineOnCurves( walkData[ 'CrosswiseLine3D' ], curves, False)

            if isFound:

                # compute distance

                #( isLength, length ) = getLengthAtPointOnCurves( nearestPoint, curves )

                ( _, startP, endP )   = bigCurves.evaluator.getParameterExtents()
                ( _, parameter )      = bigCurves.evaluator.getParameterAtPoint( nearestPoint3D )
                ( isLength, length )  = bigCurves.evaluator.getLengthAtParameter( startP, parameter )

                # add dict

                data[ step ] = {
                    'Point3D'  : nearestPoint3D,
                    'CurveSKT' : nearestCurveSKT,
                    'Distance' : length
                }

        # ------------------------------------------------------------------------------

        return data


    def getDataAtLength( self, length: float, curves: list ):

        ( isFound, curveId, curveSKT, startCurve ) = self.getCurveFromLength( length, curves )

        if not isFound:
            futil.log( 'NOT FOUND for curveId {} - length {}'.format( curveId, length * 10 ) )


        if isFound:

            nurbs = curveSKT.geometry.asNurbsCurve

            # test if need to reverse the nurbs curve

            if curveId > 0:

                prevWalkCurve = curves[ curveId - 1 ]
                prevNurbs     = prevWalkCurve.geometry.asNurbsCurve

                prevStart: adsk.core.Point3D = prevNurbs.controlPoints[ 0 ]
                prevEnd:   adsk.core.Point3D = prevNurbs.controlPoints[ - 1 ] # last

                newStart:   adsk.core.Point3D = nurbs.controlPoints[ 0 ]
                newEnd:     adsk.core.Point3D = nurbs.controlPoints[ - 1 ] # last

                if prevEnd.isEqualTo( newEnd ):
                    nurbs = reverseNurbsCurve( nurbs )


            # get paramLength

            ( _, startP, endP )       = nurbs.evaluator.getParameterExtents()
            ( isLength, paramLength ) = nurbs.evaluator.getParameterAtLength( startP, length - startCurve )
            if isLength:

                # get point

                ( isPoint, point ) = nurbs.evaluator.getPointAtParameter( paramLength )
                if isPoint:

                    # get tangent

                    ( isTangent, tangentVector ) = nurbs.evaluator.getTangent( paramLength )
                    if isTangent:

                        return ( True, point, curveSKT, tangentVector )

        return ( False, None, None, None )


    def getCurveFromLength( self, length: float, curves: list ):

        prevLength = 0
        isFound    = False

        for curveId, curveSKT in enumerate( curves ):

            lengthCurve = curveSKT.length
            startCurve  = prevLength
            endCurve    = prevLength + lengthCurve

            if startCurve <= length <= endCurve:
                return ( True, curveId, curveSKT, startCurve )

            prevLength = prevLength + lengthCurve

        #return ( isFound, curveId, curveSKT, None )

        return ( True, len( curves ) - 1, curves[ -1 ], startCurve ) # WORKAROUND : get the last curve if not found


    # ------------------------------------------------------------------------------
    # COMPUTE RADIATING STEPS + PARALLEL STEPS
    # ------------------------------------------------------------------------------

    def computeRadiatingSteps( self, walkData: dict ) -> dict:

        futil.log( f' > computeRadiatingSteps()' )

        # ------------------------------------------------------------------------------

        # get data from the inside line crosswise to the walkpath
        insideData = self.computeWalkStepsCrosswise(  walkData, self.insideCurvesSKT )

        # get data from the outside line crosswise to the walkpath
        outsideData = self.computeWalkStepsCrosswise( walkData, self.outsideCurvesSKT )


        # ------------------------------------------------------------------------------

        data: dict = {}

        for step in range( 0, self.stepNumber + 1 ):

            # add dict

            data[ step ] = {
                'Walk':     walkData[ step ],
                'Inside':   insideData[ step ],
                'Outside':  outsideData[ step ]
            }


        # ------------------------------------------------------------------------------

        return data

    # ------------------------------------------------------------------------------

    def computeParallelSteps( self, radiatingSteps: dict, offset: float = 0 ) -> dict:

        futil.log( f' > computeParallelSteps( {offset * 10} )' )

        # ------------------------------------------------------------------------------

        # sketchPoints: adsk.fusion.SketchPoints = self.sketch.sketchPoints
        # sketchLines: adsk.fusion.SketchLines   = self.sketch.sketchCurves.sketchLines

        # ------------------------------------------------------------------------------

        # WORKAROUND to compute parallel

        if self.stairAngle < 0:
            offset *= -1

        # ------------------------------------------------------------------------------

        data: dict = {}

        for step, radiatingStep in radiatingSteps.items():

            walkPoint3D:   adsk.core.Point3D = radiatingStep[ 'Walk' ]   [ 'Point3D' ]
            insidePoint3D: adsk.core.Point3D = radiatingStep[ 'Inside' ] [ 'Point3D' ]

            # walkLineSKT = sketchLines.addByTwoPoints( walkPoint3D, insidePoint3D )
            # walkLineSKT.isConstruction = True


            # ------------------------------------------------------------------------------

            distance = walkPoint3D.distanceTo( insidePoint3D )

            xDelta = walkPoint3D.x - insidePoint3D.x
            yDelta = walkPoint3D.y - insidePoint3D.y

            distX  = xDelta / distance * abs( offset )
            distY  = yDelta / distance * abs( offset )

            # ------------------------------------------------------------------------------

            startPoint3D = walkPoint3D

            vectorXY = adsk.core.Vector3D.create( distX, distY, 0 )
            vectorXY.add( startPoint3D.asVector() )

            endPoint3D   = vectorXY.asPoint()


            # ------------------------------------------------------------------------------

            vectorZ        = adsk.core.Vector3D.create( z = 1 ) # Z axis # need a XY plane
            rotationMatrix = adsk.core.Matrix3D.create()
            lineRotate3D   = adsk.core.Line3D.create( startPoint3D, endPoint3D )


            if offset > 0:
                rotationMatrix.setToRotation( - math.pi / 2, vectorZ, startPoint3D )
            else:
                rotationMatrix.setToRotation(   math.pi / 2, vectorZ, startPoint3D )

            lineRotate3D.transformBy( rotationMatrix )

            # ------------------------------------------------------------------------------

            # lineRotateSKT = sketchLines.addByTwoPoints( lineRotate3D.startPoint, lineRotate3D.endPoint  )
            # lineRotateSKT.isConstruction = False

            # ------------------------------------------------------------------------------
            # ------------------------------------------------------------------------------

            newStartPoint3D = lineRotate3D.endPoint
            newVectorXY     = adsk.core.Vector3D.create( distX, distY, 0 )
            newVectorXY.add( newStartPoint3D.asVector() )
            newEndPoint3D   = newVectorXY.asPoint()
            newLineRotate3D = adsk.core.Line3D.create( newStartPoint3D, newEndPoint3D )

            # ------------------------------------------------------------------------------

            # newLineSKT = sketchLines.addByTwoPoints( newLineRotate3D.startPoint, newLineRotate3D.endPoint )
            # newLineSKT.isConstruction = False

            # ------------------------------------------------------------------------------

            walk: dict    = {}
            inside: dict  = {}
            outside: dict = {}

            ( isWalk, nearestPoint3D, nearestCurveSKT, nearestCurveId ) = self.getNearestPointIntersectLineOnCurves( newLineRotate3D, self.walkCurvesSKT, False)

            if isWalk:
                walk = {
                    'Point3D':  nearestPoint3D,
                    'CurveSKT': nearestCurveSKT,
                    'CurveId':  nearestCurveId,
                }

            ( isInside, nearestPoint3D, nearestCurveSKT, nearestCurveId ) = self.getNearestPointIntersectLineOnCurves( newLineRotate3D, self.insideCurvesSKT, False)

            if isInside:
                inside = {
                    'Point3D':  nearestPoint3D,
                    'CurveSKT': nearestCurveSKT,
                    'CurveId':  nearestCurveId,
                }

            ( isOutside, nearestPoint3D, nearestCurveSKT, nearestCurveId ) = self.getNearestPointIntersectLineOnCurves( newLineRotate3D, self.outsideCurvesSKT, False)

            if isOutside:
                outside = {
                    'Point3D':  nearestPoint3D,
                    'CurveSKT': nearestCurveSKT,
                    'CurveId':  nearestCurveId,
                }


            data[ step ] = {
                'Walk':     walk,
                'Inside':   inside,
                'Outside':  outside
            }


        return data


    # ------------------------------------------------------------------------------
    # COMPUTE BALANCING STEPS
    # ------------------------------------------------------------------------------

    def computeBalancingStepsAll( self, radiatingSteps: dict ) -> bool:

        futil.log( f' > : computeBalancingStepsAll()' )

        # ------------------------------------------------------------------------------

        balancingSteps = {}

        # ------------------------------------------------------------------------------
        # compute balanced steps on 1st string
        # ------------------------------------------------------------------------------

        if True:
            self.computeBalancingStepsSection(
                radiatingSteps,
                balancingSteps,

                0, # start
                - self.stairAngle + self.flightBalanceDelta,
                self.flightBalanceProp1,
                False
            )

        # ------------------------------------------------------------------------------
        # compute balanced steps on 2nd string
        # ------------------------------------------------------------------------------

        if True:
            self.computeBalancingStepsSection(
                radiatingSteps,
                balancingSteps,

                self.stepNumber, # end
                - self.stairAngle - self.flightBalanceDelta,
                self.flightBalanceProp2,
                True
            )


        # ------------------------------------------------------------------------------
        # add not balanced steps with radial steps
        # ------------------------------------------------------------------------------

        if True:
            for step, radiatingStep in radiatingSteps.items():

                if step not in balancingSteps.keys():

                    # add dict

                    balancingSteps[ step ] = radiatingStep

                    # balancingSteps[ step ] = {
                    #     'Walk':    radiatingStep[ 'Walk' ],
                    #     'Inside':  radiatingStep[ 'Inside' ],
                    #     'Outside': radiatingStep[ 'Outside' ]
                    # }

        # ------------------------------------------------------------------------------

        return balancingSteps


    def computeBalancingStepsSection( self,
            radiatingSteps:    dict,
            balancingSteps:    dict,

            stepStartIndex:    int,
            stairAngle:        float,
            balanceProportion: int,
            isReverse:         bool
        ):

        futil.log( f' > computeBalancingStepsSection()' )

        # ------------------------------------------------------------------------------

        data: dict = radiatingSteps[ stepStartIndex ]

        ( _, startP, endP )     = data[ 'Walk' ] [ 'CurveSKT' ].geometry.evaluator.getParameterExtents()
        ( _, walkPointParam )   = data[ 'Walk' ] [ 'CurveSKT' ].geometry.evaluator.getParameterAtPoint( data[ 'Walk' ] [ 'Point3D' ] )
        ( _, walkLength )       = data[ 'Walk' ] [ 'CurveSKT' ].geometry.evaluator.getLengthAtParameter( startP, walkPointParam )

        # ------------------------------------------------------------------------------

        ( _, startP, endP )     = data[ 'Inside' ] [ 'CurveSKT' ].geometry.evaluator.getParameterExtents()
        ( _, insidePointParam ) = data[ 'Inside' ] [ 'CurveSKT' ].geometry.evaluator.getParameterAtPoint( data[ 'Inside' ] [ 'Point3D' ] )
        ( _, insideLength )     = data[ 'Inside' ] [ 'CurveSKT' ].geometry.evaluator.getLengthAtParameter( startP, insidePointParam )

        # ------------------------------------------------------------------------------

        if not isReverse:
            walkLengthLeft      = data[ 'Walk' ] [ 'CurveSKT' ].length   - walkLength
            insideLengthLeft    = data[ 'Inside' ] [ 'CurveSKT' ].length - insideLength

        else:
            walkLengthLeft      = walkLength
            insideLengthLeft    = insideLength

        # ------------------------------------------------------------------------------

        walkOffsetBalanceR      = walkLengthLeft * ( 1 - balanceProportion / 100 )
        walkOffsetBalanceStep   = int( walkOffsetBalanceR / self.stepGoing )
        walkOffsetBalance       = walkOffsetBalanceStep * self.stepGoing
        walkLengthToBalance     = walkLengthLeft - walkOffsetBalance

        insideOffsetBalanceR    = insideLengthLeft * ( 1 - balanceProportion / 100 )
        insideOffsetBalanceStep = int( insideOffsetBalanceR / self.stepGoing )
        insideOffsetBalance     = insideOffsetBalanceStep * self.stepGoing
        insideLengthToBalance   = insideLengthLeft - insideOffsetBalance

        # ------------------------------------------------------------------------------

        # compute the balanced stairs

        balanceAngle = math.fabs( stairAngle / 2 )

        # futil.log( f' > : stepStartIndex      = {stepStartIndex}' )
        # futil.log( f' > : self.stairWidth     = {self.stairWidth}' )
        # futil.log( f' > : stairAngle          = {stairAngle}' )
        # futil.log( f' > : balanceProportion   = {balanceProportion}' )
        # futil.log( f' > : self.insideRadius   = {self.insideRadius}' )
        # futil.log( f' > : isReverse           = {isReverse}' )
        # futil.log( f' ' )
        # futil.log( f' > : self.stepGoing      = {self.stepGoing}' )
        # futil.log( f' > : walkLengthToBalance = {walkLengthToBalance}' )
        # futil.log( f' > : balanceAngle        = {balanceAngle} rad' )
        # futil.log( f' ' )

        harrowBalancedSteps = self.computeBalancingStepsHarrowMethod( self.stepGoing, self.stairWidth, self.insideRadius, walkLengthToBalance, balanceAngle )

        for step, ( insideB, walkB, angleB ) in enumerate( harrowBalancedSteps ):

            if not isReverse:
                stepIndex = stepStartIndex + step + 1 + walkOffsetBalanceStep
                walkL     = data[ 'Walk' ] [ 'Distance' ]   + ( walkOffsetBalance   + walkB )
                insideL   = data[ 'Inside' ] [ 'Distance' ] + ( insideOffsetBalance + insideB )

            else:
                stepIndex = stepStartIndex - step - 1 - walkOffsetBalanceStep
                walkL     = data[ 'Walk' ] [ 'Distance' ]   - ( walkOffsetBalance   + walkB )
                insideL   = data[ 'Inside' ] [ 'Distance' ] - ( insideOffsetBalance + insideB )

            # ------------------------------------------------------------------------------

            # draw the step line (walkpath - inside) if not already done

            isStepLine = True  if( round( ( step + 1 ) * self.stepGoing - walkB, 2 ) == 0.0 ) else False

            # futil.log( f' > : step       = {step}  -  insideB    = {insideB}      -  walkB      = {walkB}' )
            # futil.log( f' > : stepIndex  = {stepIndex}  -  insideL    = {insideL}      -  walkL      = {walkL}' )
            # futil.log( f' > : isStepLine = {isStepLine}' )
            # futil.log( f' ' )

            if isStepLine and stepIndex not in balancingSteps.keys():

                # get insidePoint and walkPoint

                ( isOK, insidePoint3D, insideCurveSKT, insideTangentVector ) = self.getDataAtLength( insideL, self.insideCurvesSKT )
                ( isOK, walkPoint3D,   walkCurveSKT,   walkTangentVector )   = self.getDataAtLength( walkL,   self.walkCurvesSKT )

                # ------------------------------------------------------------------------------
                # compute the step line (walkpath and outside)

                stepInsideLine3D = adsk.core.Line3D.create( insidePoint3D, walkPoint3D )

                ( isFound, outsidePoint3D, outsideCurveSKT, outsideCurveId ) = self.getNearestPointIntersectLineOnCurves( stepInsideLine3D, self.outsideCurvesSKT, False )

                if isFound:

                    # add dict

                    balancingSteps[ stepIndex ] = {
                        #'Step':  stepIndex,

                        'Walk': {
                            'Point3D':  walkPoint3D,
                            'CurveSKT': walkCurveSKT
                        },

                        'Inside': {
                            'Point3D':  insidePoint3D,
                            'CurveSKT': insideCurveSKT
                        },

                        'Outside': {
                            'Point3D':  outsidePoint3D,
                            'CurveSKT': outsideCurveSKT
                        }
                    }


        # ------------------------------------------------------------------------------


    def computeBalancingStepsHarrowMethod( self,
            stepGoing:      float,
            stairWidth:     float,
            insideRadius:   float,
            straightLength: float,
            balanceAngleTo: float
        ) -> list:

        futil.log( f' > : computeBalancingStepsHarrowMethod()' )

        # ------------------------------------------------------------------------------

        result = []

        walkpathRadius     = self.getWalkpathMaxiRadius( stairWidth )
        walkpathBalance    = ( walkpathRadius * 2 + insideRadius * 2 ) * balanceAngleTo / 2
        walkpathTotal      = straightLength + walkpathBalance
        insidePathTotal    = straightLength + insideRadius * balanceAngleTo

        stepNumberStraight = math.floor( straightLength / stepGoing )      # not used
        stepNumber         = math.ceil( walkpathTotal / stepGoing )

        angleB             = math.atan( walkpathTotal / insidePathTotal )
        angleA             = math.pi - ( 2 * angleB )

        for step in range( stepNumber ):

            walk   = stepGoing * ( step + 1 )  if( stepGoing * ( step + 1 ) < walkpathTotal )  else walkpathTotal
            angle  = math.atan( walk / insidePathTotal )
            inside = insidePathTotal / ( math.tan( angleA ) / math.tan( angle ) + 1 ) / math.cos( angleA )

            result.append( [ inside, walk, angle ] )

        return result


    # ------------------------------------------------------------------------------
    # MISCELLANEOUS
    # ------------------------------------------------------------------------------

    def checkSelectedLines( self ) -> bool:

        app = adsk.core.Application.get()
        ui  = app.userInterface

        if self.walkLine.objectType != adsk.fusion.SketchLine.classType() or self.walkLine == None:
            #eventArgs.isValidResult = False
            ui.messageBox( 'No walkpath line selected.' )
            return False

        if self.insideLine.objectType != adsk.fusion.SketchLine.classType() or self.insideLine == None:
            #eventArgs.isValidResult = False
            ui.messageBox( 'No interior stringers line selected.' )
            return False

        if self.outsideLine.objectType != adsk.fusion.SketchLine.classType() or self.outsideLine == None:
            #eventArgs.isValidResult = False
            ui.messageBox( 'No exterior stringers line selected.' )
            return False

        return True


    def getCurvesFromSelectedLines( self ) -> bool:

        self.walkCurvesSKT    = self.sketch.findConnectedCurves( self.walkLine )
        self.insideCurvesSKT  = self.sketch.findConnectedCurves( self.insideLine )
        self.outsideCurvesSKT = self.sketch.findConnectedCurves( self.outsideLine )

        return True

    # ------------------------------------------------------------------------------

    def getNearestPointIntersectLineOnCurves( self,
            line3D: adsk.core.Line3D,
            curves: list,
            isEndpoint: bool = False
        ) -> tuple:

        """Get the nearest point to the intersection of a line with curves"""

        isFound: bool = False
        isInit:  bool = False

        nearestCurveId:  int = None
        nearestDistance: float = None
        nearestPoint3D:  adsk.core.Point3D = None
        nearestCurveSKT: adsk.fusion.SketchCurve = None

        # convert to infinite line

        infiniteLine = line3D.asInfiniteLine()


        # define the from point

        fromPoint3D = line3D.startPoint

        if isEndpoint:
            fromPoint3D = line3D.endPoint
        else:
            fromPoint3D = line3D.startPoint



        # iterate curves

        for curveId, curveSKT in enumerate( curves ):

            # get points intersect woth current curve

            intersectPoints = infiniteLine.intersectWithCurve( curveSKT.geometry )

            # init the first result

            if not isInit and len( intersectPoints ) > 0:

                isInit  = True
                isFound = True
                nearestPoint3D  = intersectPoints[ 0 ]
                nearestDistance = fromPoint3D.distanceTo( intersectPoints[ 0 ] )
                nearestCurveSKT = curveSKT
                nearestCurveId  = curveId

        # find the nearest point

            if len( intersectPoints ) > 0:

                for intersectPoint in intersectPoints:

                    distance = fromPoint3D.distanceTo( intersectPoint )

                    if distance < nearestDistance:

                        isFound = True
                        nearestPoint3D  = intersectPoint
                        nearestDistance = distance
                        nearestCurveSKT = curveSKT
                        nearestCurveId  = curveId

        return ( isFound, nearestPoint3D, nearestCurveSKT, nearestCurveId )


    def getTotalLengthCurves( self, curvesSKT: list ) -> float:

        length = 0

        for curveSKT in curvesSKT:
            length = length + curveSKT.length

        return length


    # ------------------------------------------------------------------------------
    # FLAGS
    # ------------------------------------------------------------------------------


    def isOverlapStair( self ) -> bool:

        if self.isOverlap and self.overlapLength > 0:
            return True

        return False


    def isRiserStair( self ) -> bool:

        if self.isRiser and self.riserThickness > 0:
            return True

        return False


    # ------------------------------------------------------------------------------
    # DISPLAY WALKPATH INPUTS FIELDS
    # ------------------------------------------------------------------------------

    def displayAllWalkpathFields( self ) -> bool:

        #self.displayWalkpathRadiusField()
        self.displayWalkPathLengthField()
        self.displayTotalLengthField()

        return True

    # ------------------------------------------------------------------------------

    def displayWalkPathLengthField( self ) -> bool:

        stringFormat = '{:.3f} mm'

        self.inputs.itemById( 'walkpath_length' ).formattedText = stringFormat.format( self.walkpathLength * 10 )

        return True


    def displayTotalLengthField( self ) -> bool:

        stringFormat = '{:.3f} mm'
        self.inputs.itemById( 'total_length' ).formattedText = stringFormat.format( self.totalLength * 10 )

        #futil.log( f' > displayTotalLength       - totalLength {self.totalLength}' )
        return True


    # ------------------------------------------------------------------------------
    # DISPLAY STEP INPUTS TEXT FIELDS
    # ------------------------------------------------------------------------------

    def displayAllTextFieldsComputed( self ) -> bool:

        futil.log( f' > displayAllTextFieldsComputed()')

        # ------------------------------------------------------------------------------

        self.displayStepGoingField()
        self.displayStepHeightField()
        self.displayStepBlondelLawField()
        self.displayStepClimbAngleField()

        return True

    # ------------------------------------------------------------------------------

    def displayStepNumberField( self ) -> bool:

        futil.log( f' > displayStepNumberField()')

        # ------------------------------------------------------------------------------

        stepNumberField: adsk.core.IntegerSliderCommandInput = self.inputs.itemById( 'step_number' )

        stepNumberField.minimumValue = max( 2, self.stepNumberMini - 1 )
        stepNumberField.maximumValue = self.stepNumberMaxi + 3
        stepNumberField.valueOne     = self.stepNumber

        futil.log( f' > : self.stepNumberMini = {self.stepNumberMini}' )
        futil.log( f' > : self.stepNumberMaxi = {self.stepNumberMaxi}' )
        futil.log( f' > : self.stepNumber     = {self.stepNumber}' )

        return True

    # ------------------------------------------------------------------------------

    def displayStepGoingField( self ) -> bool:

        futil.log( f' > : displayStepGoingField()')

        # ------------------------------------------------------------------------------

        # Entre 230 and 330 mm - idéal 280 mm - https://calcul-escaliers.web4me.fr/Definitions.htm

        if self.stepGoing < 23:
            text = '<span style="color:Red">{:.3f} mm</span> (&lt; 230 mm)'
        elif self.stepGoing > 33:
            text = '<span style="color:Red">{:.3f} mm</span> (&gt; 330 mm)'
        else:
            text = '<span style="color:DodgerBlue">{:.3f} mm</span>'

        self.inputs.itemById( 'step_going' ).formattedText = text.format( self.stepGoing * 10 )

        return True


    def displayStepHeightField( self ) -> bool:

        futil.log( f' > : displayStepHeightField()')

        # ------------------------------------------------------------------------------

        # Entre 150 et 200 mm - idéal 175 mm - https://calcul-escaliers.web4me.fr/Definitions.htm

        if self.stepHeight < 15:
            text = '<span style="color:Red">{:.3f} mm</span> (&lt; 150 mm)'
        elif self.stepHeight > 20:
            text = '<span style="color:Red">{:.3f} mm</span> (&gt; 200 mm)'
        else:
            text = '<span style="color:DodgerBlue">{:.3f} mm</span>'

        self.inputs.itemById( 'step_height' ).formattedText = text.format( self.stepHeight * 10 )

        return True


    def displayStepBlondelLawField( self ) -> bool:

        futil.log( f' > : displayStepBlondelLawField()')

        # ------------------------------------------------------------------------------

        # Entre 590 à 650 mm - idéal 630 mm - ex. 280 + 175 * 2 = 630 mm - https://calcul-escaliers.web4me.fr/Definitions.htm

        if self.blondelLaw < 59:
            text = '<span style="color:Red">{:.3f} mm</span> (&lt; 590 mm)'
        elif self.blondelLaw > 65:
            text = '<span style="color:Red">{:.3f} mm</span> (&gt; 650 mm)'
        else:
            text = '<span style="color:DodgerBlue">{:.3f} mm</span>'

        self.inputs.itemById( 'blondel_law' ).formattedText = text.format( self.blondelLaw  * 10 )

        return True


    def displayStepClimbAngleField( self ) -> bool:

        futil.log( f' > : displayStepClimbAngleField()')

        # ------------------------------------------------------------------------------

        climbAngleDEG = math.degrees( self.climbAngle )

        # Entre 20 et 50° - idéal 30° - https://calcul-escaliers.web4me.fr/Definitions.htm

        if climbAngleDEG < 24:
            text = '<span style="color:OrangeRed">{:.1f} ° (rampe d\'accès)</span>'

        elif climbAngleDEG > 80:
            text = '<span style="color:Red">{:.1f} °</span> (échelle)'

        elif climbAngleDEG > 70:
            text = '<span style="color:Red">{:.1f} °</span> (échelle de meunier)'

        elif climbAngleDEG > 45:
            text = '<span style="color:Red">{:.1f} °</span> (trop élevé)'

        elif climbAngleDEG > 40:
            text = '<span style="color:OrangeRed">{:.1f} °</span> (trop élevé pour les locaux publics)'

        else:
            text = '<span style="color:DodgerBlue">{:.1f} °</span>'

        self.inputs.itemById( 'climb_angle' ).formattedText = text.format( climbAngleDEG )

        return True


    def updateIsCreateRisersInputField( self ):
        createRisersInput           = self.inputs.itemById( 'is_create_risers' )
        createRisersInput.isEnabled = self.inputs.itemById( 'is_riser' ).isExpanded

        return True


    # ------------------------------------------------------------------------------
    # VALUES & PARAMETERS
    # ------------------------------------------------------------------------------


    def getDefaultValues( self ):

        futil.log( f' > getDefaultValues()' )

        # ------------------------------------------------------------------------------

        if True:

            self.stairHeight         = self.fields.getValueByID( id = 'stair_height'           )
            self.stairWidth          = self.fields.getValueByID( id = 'stair_width'            )
            self.walkpathRadius      = self.fields.getValueByID( id = 'walkpath_radius'        )
            self.insideRadius        = self.fields.getValueByID( id = 'inside_radius'          )
            self.stairAngle          = self.fields.getValueByID( id = 'stair_angle'            )
            self.isPreviewRadiating  = self.fields.getValueByID( id = 'is_preview_radiating'   )
            self.isPreviewBalancing  = self.fields.getValueByID( id = 'is_preview_balancing'   )
            # ------------------------------------------------------------------------------
            self.stepNumberMini      = self.fields.getValueByID( id = 'step_number_mini',     value = self.computeStepNumberMini()   )
            self.stepNumberMaxi      = self.fields.getValueByID( id = 'step_number_maxi',     value = self.computeStepNumberMaxi()   )
            self.stepNumber          = self.fields.getValueByID( id = 'step_number',          value = self.computeStepNumberMiddle() )
            self.stairThickness      = self.fields.getValueByID( id = 'stair_thickness'        )
            self.frontReserveLength  = self.fields.getValueByID( id = 'front_reserve_length'   )
            # ------------------------------------------------------------------------------
            self.flightLength1       = self.fields.getValueByID( id = 'flight_length_1'        )
            self.flightBalanceProp1  = self.fields.getValueByID( id = 'flight_balance_prop_1'  )
            self.flightLength2       = self.fields.getValueByID( id = 'flight_length_2'        )
            self.flightBalanceProp2  = self.fields.getValueByID( id = 'flight_balance_prop_2'  )
            self.flightBalanceDelta  = self.fields.getValueByID( id = 'flight_balance_delta'   )
            # ------------------------------------------------------------------------------
            self.isOverlap           = self.fields.getValueByID( id = 'is_overlap'             )
            self.overlapLength       = self.fields.getValueByID( id = 'overlap_length'         )
            self.isOverlapLast       = self.fields.getValueByID( id = 'is_overlap_last'        )
            # ------------------------------------------------------------------------------
            self.isRiser             = self.fields.getValueByID( id = 'is_riser'               )
            self.riserThickness      = self.fields.getValueByID( id = 'riser_thickness'        )
            self.riserGroove         = self.fields.getValueByID( id = 'riser_groove'           )
            self.riserRabbet         = self.fields.getValueByID( id = 'riser_rabbet'           )
            # ------------------------------------------------------------------------------
            self.walkLength          = self.fields.getValueByID( id = 'walkpath_length'        )
            self.totalLength         = self.fields.getValueByID( id = 'total_length'           )
            self.stepHeight          = self.fields.getValueByID( id = 'step_height'            )
            self.stepGoing           = self.fields.getValueByID( id = 'step_going'             )
            self.blondelLaw          = self.fields.getValueByID( id = 'blondel_law'            )
            self.climbAngle          = self.fields.getValueByID( id = 'climb_angle'            )
            # ------------------------------------------------------------------------------
            self.isCreateSteps       = self.fields.getValueByID( id = 'is_create_steps'        )
            self.isCreateRisers      = self.fields.getValueByID( id = 'is_create_risers'       )
            self.isEngraveReference  = self.fields.getValueByID( id = 'is_engrave_reference'   )
            # ------------------------------------------------------------------------------
            self.isCreateStairLayout = self.fields.getValueByID( id = 'is_create_stair_layout' )
            self.flatModulo          = self.fields.getValueByID( id = 'flat_modulo'            )
            self.flatOriginX         = self.fields.getValueByID( id = 'flat_origin_x'          )
            self.flatOriginY         = self.fields.getValueByID( id = 'flat_origin_y'          )
            self.flatSpaceX          = self.fields.getValueByID( id = 'flat_space_x'           )
            self.flatSpaceY          = self.fields.getValueByID( id = 'flat_space_y'           )


    def readAllParameters( self ):

        futil.log( f' > readAllParameters()' )

        # ------------------------------------------------------------------------------

        if self.IS_READ_PARAMETERS:

            self.stairHeight         = self.fields.readParameterByID( id = 'stair_height',           value = self.stairHeight         )
            self.stairWidth          = self.fields.readParameterByID( id = 'stair_width',            value = self.stairWidth          )
            self.walkpathRadius      = self.fields.readParameterByID( id = 'walkpath_radius',        value = self.walkpathRadius      )
            self.insideRadius        = self.fields.readParameterByID( id = 'inside_radius',          value = self.insideRadius        )
            self.stairAngle          = self.fields.readParameterByID( id = 'stair_angle',            value = self.stairAngle          )
            self.isPreviewRadiating  = self.fields.readParameterByID( id = 'is_preview_radiating',   value = self.isPreviewRadiating  )
            self.isPreviewBalancing  = self.fields.readParameterByID( id = 'is_preview_balancing',   value = self.isPreviewBalancing  )
            # -----------------------------------------------------------------------------
            self.stepNumberMini      = self.fields.readParameterByID( id = 'step_number_mini',       value = self.stepNumberMini      )
            self.stepNumberMaxi      = self.fields.readParameterByID( id = 'step_number_maxi',       value = self.stepNumberMaxi      )
            self.stepNumber          = self.fields.readParameterByID( id = 'step_number',            value = self.stepNumber          )
            self.stairThickness      = self.fields.readParameterByID( id = 'stair_thickness',        value = self.stairThickness      )
            self.frontReserveLength  = self.fields.readParameterByID( id = 'front_reserve_length',   value = self.frontReserveLength  )
            # -----------------------------------------------------------------------------
            self.flightLength1       = self.fields.readParameterByID( id = 'flight_length_1',        value = self.flightLength1       )
            self.flightBalanceProp1  = self.fields.readParameterByID( id = 'flight_balance_prop_1',  value = self.flightBalanceProp1  )
            self.flightLength2       = self.fields.readParameterByID( id = 'flight_length_2',        value = self.flightLength2       )
            self.flightBalanceProp2  = self.fields.readParameterByID( id = 'flight_balance_prop_2',  value = self.flightBalanceProp2  )
            self.flightBalanceDelta  = self.fields.readParameterByID( id = 'flight_balance_delta',   value = self.flightBalanceDelta  )
            # -----------------------------------------------------------------------------
            self.isOverlap           = self.fields.readParameterByID( id = 'is_overlap',             value = self.isOverlap           )
            self.overlapLength       = self.fields.readParameterByID( id = 'overlap_length',         value = self.overlapLength       )
            self.isOverlapLast       = self.fields.readParameterByID( id = 'is_overlap_last',        value = self.isOverlapLast       )
            # -----------------------------------------------------------------------------
            self.isRiser             = self.fields.readParameterByID( id = 'is_riser',               value = self.isRiser             )
            self.riserThickness      = self.fields.readParameterByID( id = 'riser_thickness',        value = self.riserThickness      )
            self.riserGroove         = self.fields.readParameterByID( id = 'riser_groove',           value = self.riserGroove         )
            self.riserRabbet         = self.fields.readParameterByID( id = 'riser_rabbet',           value = self.riserRabbet         )
            # -----------------------------------------------------------------------------
            self.walkLength          = self.fields.readParameterByID( id = 'walkpath_length',        value = self.walkLength          )
            self.totalLength         = self.fields.readParameterByID( id = 'total_length',           value = self.totalLength         )
            self.stepHeight          = self.fields.readParameterByID( id = 'step_height',            value = self.stepHeight          )
            self.stepGoing           = self.fields.readParameterByID( id = 'step_going',             value = self.stepGoing           )
            self.blondelLaw          = self.fields.readParameterByID( id = 'blondel_law',            value = self.blondelLaw          )
            self.climbAngle          = self.fields.readParameterByID( id = 'climb_angle',            value = self.climbAngle          )
            # -----------------------------------------------------------------------------
            self.isCreateSteps       = self.fields.readParameterByID( id = 'is_create_steps',        value = self.isCreateSteps       )
            self.isCreateRisers      = self.fields.readParameterByID( id = 'is_create_risers',       value = self.isCreateRisers      )
            self.isEngraveReference  = self.fields.readParameterByID( id = 'is_engrave_reference',   value = self.isEngraveReference  )
            # -----------------------------------------------------------------------------
            self.isCreateStairLayout = self.fields.readParameterByID( id = 'is_create_stair_layout', value = self.isCreateStairLayout )
            self.flatModulo          = self.fields.readParameterByID( id = 'flat_modulo',            value = self.flatModulo          )
            self.flatOriginX         = self.fields.readParameterByID( id = 'flat_origin_x',          value = self.flatOriginX         )
            self.flatOriginY         = self.fields.readParameterByID( id = 'flat_origin_y',          value = self.flatOriginY         )
            self.flatSpaceX          = self.fields.readParameterByID( id = 'flat_space_x',           value = self.flatSpaceX          )
            self.flatSpaceY          = self.fields.readParameterByID( id = 'flat_space_y',           value = self.flatSpaceY          )


    def writeAllParameters( self ):

        futil.log( f' > writeAllParameters()' )

        # ------------------------------------------------------------------------------

        if self.IS_STORE_PARAMETERS:

            self.fields.saveParameterByID( id = 'stair_height',          value = self.stairHeight        )
            self.fields.saveParameterByID( id = 'stair_width',           value = self.stairWidth         )
            self.fields.saveParameterByID( id = 'walkpath_radius',       value = self.walkpathRadius     )
            self.fields.saveParameterByID( id = 'inside_radius',         value = self.insideRadius       )
            self.fields.saveParameterByID( id = 'stair_angle',           value = self.stairAngle         )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'step_number_mini',      value = self.stepNumberMini     )
            self.fields.saveParameterByID( id = 'step_number_maxi',      value = self.stepNumberMaxi     )
            self.fields.saveParameterByID( id = 'step_number',           value = self.stepNumber         )
            self.fields.saveParameterByID( id = 'stair_thickness',       value = self.stairThickness     )
            self.fields.saveParameterByID( id = 'front_reserve_length',  value = self.frontReserveLength )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'flight_length_1',       value = self.flightLength1      )
            self.fields.saveParameterByID( id = 'flight_balance_prop_1', value = self.flightBalanceProp1 )
            self.fields.saveParameterByID( id = 'flight_length_2',       value = self.flightLength2      )
            self.fields.saveParameterByID( id = 'flight_balance_prop_2', value = self.flightBalanceProp2 )
            self.fields.saveParameterByID( id = 'flight_balance_delta',  value = self.flightBalanceDelta )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'is_overlap',            value = self.isOverlap          )
            self.fields.saveParameterByID( id = 'overlap_length',        value = self.overlapLength      )
            self.fields.saveParameterByID( id = 'is_overlap_last',       value = self.isOverlapLast      )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'is_riser',              value = self.isRiser            )
            self.fields.saveParameterByID( id = 'riser_thickness',       value = self.riserThickness     )
            self.fields.saveParameterByID( id = 'riser_groove',          value = self.riserGroove        )
            self.fields.saveParameterByID( id = 'riser_rabbet',          value = self.riserRabbet        )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'walkpath_length',       value = self.walkpathLength     )
            self.fields.saveParameterByID( id = 'total_length',          value = self.totalLength        )
            self.fields.saveParameterByID( id = 'step_height',           value = self.stepHeight         )
            self.fields.saveParameterByID( id = 'step_going',            value = self.stepGoing          )
            self.fields.saveParameterByID( id = 'blondel_law',           value = self.blondelLaw         )
            self.fields.saveParameterByID( id = 'climb_angle',           value = self.climbAngle         )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'is_create_steps',       value = self.isCreateSteps      )
            self.fields.saveParameterByID( id = 'is_create_risers',      value = self.isCreateRisers     )
            self.fields.saveParameterByID( id = 'is_engrave_reference',  value = self.isEngraveReference )
            # ------------------------------------------------------------------------------
            self.fields.saveParameterByID( id = 'is_create_stair_layout',  value = self.isCreateStairLayout )
            self.fields.saveParameterByID( id = 'flat_modulo',           value = self.flatModulo         )
            self.fields.saveParameterByID( id = 'flat_origin_x',         value = self.flatOriginX        )
            self.fields.saveParameterByID( id = 'flat_origin_y',         value = self.flatOriginY        )
            self.fields.saveParameterByID( id = 'flat_space_x',          value = self.flatSpaceX         )
            self.fields.saveParameterByID( id = 'flat_space_y',          value = self.flatSpaceY         )

            futil.log( ' > : parameters have been written...' )

        return True


    # ------------------------------------------------------------------------------
    # COMMAND INPUTS (FIELDS)
    # ------------------------------------------------------------------------------

    def createAllFields ( self ) -> bool:

        futil.log( f' > createAllFields()' )

        # ------------------------------------------------------------------------------
        tab = self.fields.createTabCommandInput(         ref = self.inputs,     id = 'design_tab' )
        # ------------------------------------------------------------------------------

        self.fields.createValueCommandInput(             ref = tab.children,    id = 'stair_height',         value = self.stairHeight     )
        self.fields.createValueCommandInput(             ref = tab.children,    id = 'stair_width',          value = self.stairWidth      )
        self.fields.createValueCommandInput(             ref = tab.children,    id = 'walkpath_radius',      value = self.walkpathRadius  )
        self.fields.createValueCommandInput(             ref = tab.children,    id = 'inside_radius',        value = self.insideRadius    )
        self.fields.createValueCommandInput(             ref = tab.children,    id = 'stair_angle',          value = self.stairAngle      )

        #self.fields.createBoolValueCommandInput(        ref = tab.children,    id = 'is_preview_radiating', value = self.isPreviewRadiating )
        self.fields.createBoolValueCommandInput(         ref = tab.children,    id = 'is_preview_balancing', value = self.isPreviewBalancing )

        # ------------------------------------------------------------------------------

        group = self.fields.createGroupCommandInput(     ref = tab.children,    id = 'is_overlap',           value = self.isOverlap       )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'overlap_length',       value = self.overlapLength   )
        self.fields.createBoolValueCommandInput(         ref = group.children,  id = 'is_overlap_last',      value = self.isOverlapLast   )

        # ------------------------------------------------------------------------------

        group = self.fields.createGroupCommandInput(     ref = tab.children,    id = 'is_riser',             value = self.isRiser         )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'riser_thickness',      value = self.riserThickness  )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'riser_groove',         value = self.riserGroove     )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'riser_rabbet',         value = self.riserRabbet     )

        # ------------------------------------------------------------------------------

        group = self.fields.createGroupCommandInput(     ref = tab.children,    id = 'stair_group' )
        self.fields.createIntegerSliderCommandInput(     ref = group.children,  id = 'step_number',           value = self.stepNumber,       mini = self.stepNumberMini,  maxi = self.stepNumberMaxi )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'stair_thickness',       value = self.stairThickness     )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'front_reserve_length',  value = self.frontReserveLength )

        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'walkpath_length' )
        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'total_length'    )
        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'step_height'     )
        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'step_going'      )
        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'blondel_law'     )
        self.fields.createTextBoxCommandInput(           ref = group.children,  id = 'climb_angle'     )

        # ------------------------------------------------------------------------------

        group = self.fields.createGroupCommandInput(     ref = tab.children,    id = 'flight_group' )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flight_length_1',       value = self.flightLength1      )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flight_balance_prop_1', value = self.flightBalanceProp1 )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flight_length_2',       value = self.flightLength2      )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flight_balance_prop_2', value = self.flightBalanceProp2 )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flight_balance_delta',  value = self.flightBalanceDelta )

        # ------------------------------------------------------------------------------
        tab = self.fields.createTabCommandInput(         ref = self.inputs,     id = 'manufacturing_tab' )
        # ------------------------------------------------------------------------------

        self.fields.createBoolValueCommandInput(         ref = tab.children,    id = 'is_create_steps',      value = self.isCreateSteps      )
        self.fields.createBoolValueCommandInput(         ref = tab.children,    id = 'is_create_risers',     value = self.isCreateRisers     )
        self.fields.createBoolValueCommandInput(         ref = tab.children,    id = 'is_engrave_reference', value = self.isEngraveReference )

        # ------------------------------------------------------------------------------

        group = self.fields.createGroupCommandInput(     ref = tab.children,    id = 'is_create_stair_layout' ) # , value = self.isCreateStairLayout
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flat_modulo',          value = self.flatModulo  )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flat_origin_x',        value = self.flatOriginX )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flat_origin_y',        value = self.flatOriginY )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flat_space_x',         value = self.flatSpaceX  )
        self.fields.createValueCommandInput(             ref = group.children,  id = 'flat_space_y',         value = self.flatSpaceY  )

        # ------------------------------------------------------------------------------

        return True


    # ------------------------------------------------------------------------------
    # CAMERA
    # ------------------------------------------------------------------------------

    def cameraFitView( self ):

        if self.IS_AUTO_CAMERA_FIT:

            app = adsk.core.Application.get()

            camera = app.activeViewport.camera
            camera.isFitView = True

            app.activeViewport.camera = camera

        return True


    # ------------------------------------------------------------------------------
    # EXPERIMENTAL with createInput OR createInput2
    # ------------------------------------------------------------------------------

    def moveOccurenceFromLine( self, occurrence: adsk.fusion.Occurrence, step, line3D: adsk.core.Line3D, x = 0, y = 0, z = 0, angle = 0 ):

        component: adsk.fusion.Component = occurrence.component
        body:      adsk.fusion.BRepBody  = component.bRepBodies[0]

        ( xTrans, yTrans, zTrans, zAngleRotate ) = self.getStairXYZandAngleByLevel( step + 1, line3D )

        # ------------------------------------------------------------------------------
        # METHOD : moveFeatures.createInput

        if True:

            # Create translation matrix

            matrixTranslation = adsk.core.Matrix3D.create()
            matrixTranslation.translation = adsk.core.Vector3D.create( -xTrans, -yTrans, -zTrans )

            # Transform matrix translation with rotate matrix

            if zAngleRotate != 0:
                zAxis    = adsk.core.Vector3D.create( z = 1 )
                matrixRotation = adsk.core.Matrix3D.create()
                matrixRotation.setToRotation( zAngleRotate, zAxis, adsk.core.Point3D.create() )
                matrixTranslation.transformBy( matrixRotation )

            # moveFeatures

            bodies = adsk.core.ObjectCollection.create()
            bodies.add( body )

            features: adsk.fusion.Features         = component.features
            moveFeatures: adsk.fusion.MoveFeatures = features.moveFeatures

            moveFeatureInput = moveFeatures.createInput( bodies, matrixTranslation )
            moveFeatures.add( moveFeatureInput )

        # ------------------------------------------------------------------------------
        # METHOD : moveFeatures.createInput2 # TODO

        if False:

            xDistance = adsk.core.ValueInput.createByReal( - xTrans )
            yDistance = adsk.core.ValueInput.createByReal( - yTrans )
            zDistance = adsk.core.ValueInput.createByReal( - zTrans )

            #zAxis     = component.zConstructionAxis
            zAxis     = component.zConstructionAxis.createForAssemblyContext( occurrence )

            zAngle    = adsk.core.ValueInput.createByReal( zAngleRotate )
            # zAngle  = adsk.core.ValueInput.createByString( '90 deg' )

            bodies = adsk.core.ObjectCollection.create()
            bodies.add( body )

            features: adsk.fusion.Features         = component.features
            moveFeatures: adsk.fusion.MoveFeatures = features.moveFeatures

            moveFeatureInput = moveFeatures.createInput2( bodies )
            moveFeatureInput.defineAsTranslateXYZ( xDistance, yDistance, zDistance, True )

            if zAngleRotate != 0:
                moveFeatureInput.defineAsRotate( zAxis, zAngle )

            moveFeatures.add( moveFeatureInput )
