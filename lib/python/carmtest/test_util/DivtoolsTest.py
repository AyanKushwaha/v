"""
Test CrewMealFlightOwnerTest
"""


from carmtest.framework import *
from AbsTime import AbsTime
import utils.divtools as d


class TestIsBaseActivity_001_test(TestFixture):
    "Base activity"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        

    def test_001_Flights(self):
        for x in ('5T071', 'Q6103', 'C6331', '7B341',
                  'SK342',     'SK0342',    'SK000342',
                  'SK 342',    'SK 0342',   'SK 000342',
                  'SK 342 ',   'SK 0342 ',  'SK 000342 ',
                  'SK342Z',    'SK0342Z',   'SK000342Z',
                  'SK 342Z',   'SK 0342Z',  'SK 000342Z',
                  '3SK342',    '3SK0342',   '3SK000342',
                  '3SK342 ',   '3SK0342 ',  '3SK000342 ',
                  '3SK342Z',   '3SK0342Z',  '3SK000342Z',
                  'SK1342',    'SK001342',  '342',
                  'SK 1342',   'SK 001342',
                  'SK 1342 ',  'SK 001342 ',
                  'SK1342Z',   'SK001342Z',
                  'SK 1342Z',  'SK 001342Z',
                  '3SK1342',   '3SK001342',
                  '3SK1342 ',  '3SK001342 ',
                  '3SK1342Z',  '3SK001342Z'):
            self.assertEqual(d.is_base_activity(x), False, x)

    def test_002_Duties(self): 
        for x in ('A', 'A0', 'A05', 'A06', 'A10', 'A10S', 'A11', 'A11S', 'A12',
                'A12S', 'A13', 'A14', 'A14S', 'A2', 'A3', 'A4', 'A5', 'A6',
                'A61', 'A66S', 'A67', 'A7', 'A8', 'A9', 'AC', 'AO', 'AS', 'B',
                'B1', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B2', 'B21',
                'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B28', 'B3', 'B31',
                'B32', 'B33', 'B34', 'B35', 'B36', 'B37', 'B4', 'B41', 'B42',
                'B43', 'B44', 'B45', 'B46', 'B47', 'B48', 'B5', 'B6', 'B61',
                'B62', 'B63', 'B64', 'B65', 'B66', 'B70', 'B71', 'B72', 'B73',
                'B74', 'B75', 'B76', 'B77', 'B78', 'B81', 'B82', 'B83', 'B84',
                'B85', 'B86', 'B91', 'B92', 'B93', 'B94', 'B95', 'B96', 'B97',
                'B98', 'B99', 'BA41', 'BA43', 'BA44', 'BA45', 'BA46', 'BB32',
                'BB33', 'BB34', 'BB35', 'BB36', 'BB51', 'BB52', 'BB53', 'BB54',
                'BB55', 'BB56', 'BC31', 'BC32', 'BC33', 'BC34', 'BC35', 'BC36',
                'BC51', 'BC52', 'BC53', 'BC54', 'BC55', 'BC56', 'BC81', 'BC82',
                'BC83', 'BC84', 'BC85', 'BC86', 'BC91', 'BC92', 'BC93', 'BC94',
                'BC95', 'BC96', 'BD31', 'BD32', 'BD33', 'BD34', 'BD35', 'BD36',
                'BD82', 'BD83', 'BE21', 'BE22', 'BE23', 'BE24', 'BE25', 'BE26',
                'BE31', 'BE32', 'BE33', 'BE34', 'BE35', 'BE36', 'BE41', 'BE42',
                'BE43', 'BE44', 'BE45', 'BE46', 'BE51', 'BE52', 'BE53', 'BE54',
                'BE55', 'BE56', 'BE61', 'BE62', 'BE63', 'BE64', 'BE65', 'BE66',
                'BE71', 'BE72', 'BE73', 'BE74', 'BE75', 'BE76', 'BE81', 'BE82',
                'BE83', 'BE84', 'BE85', 'BE86', 'BE87', 'BE88', 'BE91', 'BE92',
                'BE93', 'BE94', 'BE95', 'BE96', 'BK81', 'BK82', 'BK83', 'BK84',
                'BK85', 'BK86', 'BK88', 'BK91', 'BK92', 'BK93', 'BK94', 'BK95',
                'BK96', 'BK97', 'BK98', 'BK99', 'BL', 'BL1', 'BL12', 'BL2',
                'BL20', 'BL3', 'BL5', 'BL6', 'BL7', 'BL8', 'BL9', 'BLS',
                'BM21', 'BM22', 'BM23', 'BM24', 'BM25', 'BM26', 'BM27', 'BM31',
                'BM32', 'BM33', 'BM34', 'BM35', 'BM36', 'BM41', 'BM42', 'BM43',
                'BM44', 'BM45', 'BM46', 'BM47', 'BM49', 'BM61', 'BM62', 'BM63',
                'BM64', 'BM65', 'BM66', 'BM71', 'BM72', 'BM73', 'BM74', 'BM75',
                'BM76', 'BM77', 'BM78', 'BM81', 'BM82', 'BM83', 'BM84', 'BM85',
                'BM86', 'BM91', 'BM92', 'BM93', 'BM94', 'BM95', 'BM96', 'BM97',
                'BM98', 'BM99', 'BN81', 'BN82', 'BN83', 'BN84', 'BN85', 'BN86',
                'BO11', 'BO12', 'BO13', 'BO14', 'BO15', 'BO16', 'BO31', 'BO32',
                'BO33', 'BO34', 'BO35', 'BO36', 'BO37', 'BO91', 'BO92', 'BO93',
                'BO94', 'BO95', 'BO96', 'BOA', 'BR99', 'BS22', 'BS23', 'BS31',
                'BS32', 'BS71', 'BS72', 'BS73', 'BS74', 'BS75', 'BS76', 'BS77',
                'BS78', 'BS79', 'BS82', 'BS83', 'BS84', 'BT61', 'BT62', 'BT63',
                'BT64', 'BT65', 'BT66', 'BUS', 'BV22', 'BV23', 'BV31', 'BV32',
                'BV35', 'BV82', 'BV83', 'BV84', 'BV87', 'BX', 'BX82', 'BX83',
                'BZ41', 'BZ43', 'BZ61', 'BZ82', 'BZ83', 'C', 'C1', 'C11',
                'C12', 'C13', 'C14', 'C15', 'C16', 'C2', 'C20', 'C21', 'C210',
                'C212', 'C213', 'C214', 'C22', 'C221', 'C222', 'C223', 'C23',
                'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C2R21', 'C2R22',
                'C2R23', 'C3', 'C30', 'C31', 'C310', 'C311', 'C312', 'C313',
                'C314', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39',
                'C4', 'C40', 'C41', 'C410', 'C412', 'C413', 'C414', 'C42',
                'C43', 'C44', 'C441', 'C442', 'C443', 'C45', 'C46', 'C47',
                'C48', 'C49', 'C4R41', 'C4R42', 'C4R43', 'C5', 'C51', 'C52',
                'C53', 'C54', 'C55', 'C56', 'C6', 'C60', 'C61', 'C610', 'C612',
                'C613', 'C614', 'C62', 'C63', 'C631', 'C632', 'C633', 'C64',
                'C65', 'C66', 'C67', 'C68', 'C69', 'C691', 'C6R31', 'C6R32',
                'C6R33', 'C7', 'C70', 'C71', 'C710', 'C711', 'C712', 'C713',
                'C714', 'C72', 'C73', 'C74', 'C75', 'C76', 'C77', 'C78', 'C79',
                'C8', 'C80', 'C81', 'C810', 'C811', 'C812', 'C813', 'C814',
                'C82', 'C83', 'C84', 'C85', 'C86', 'C87', 'C88', 'C89', 'C9',
                'C90', 'C91', 'C92', 'C93', 'C94', 'C95', 'C96', 'CA07',
                'CA08', 'CA09', 'CA10', 'CA11', 'CA12', 'CA13', 'CA14', 'CA15',
                'CA16', 'CA17', 'CB', 'CB04', 'CB05', 'CB06', 'CB07', 'CB08',
                'CB09', 'CB10', 'CB11', 'CB12', 'CB13', 'CB14', 'CB15', 'CB16',
                'CB17', 'CB18', 'CB19', 'CB20', 'CB21', 'CB22', 'CC1', 'CC2',
                'CC3', 'CD8', 'CD81', 'CD82', 'CD83', 'CD84', 'CD85', 'CD86',
                'CE3', 'CE31', 'CE32', 'CE33', 'CE34', 'CE35', 'CE36', 'CE6',
                'CE61', 'CE62', 'CE63', 'CE64', 'CE65', 'CE66', 'CE8', 'CE81',
                'CE82', 'CE83', 'CE84', 'CE85', 'CE86', 'CF', 'CF30', 'CF31',
                'CF32', 'CF33', 'CF34', 'CF35', 'CF36', 'CF90', 'CF91', 'CF92',
                'CF93', 'CF94', 'CF95', 'CF96', 'CG2', 'CG20', 'CG21', 'CG22',
                'CG23', 'CG24', 'CG25', 'CG26', 'CG3', 'CG30', 'CG31', 'CG32',
                'CG33', 'CG34', 'CG35', 'CG36', 'CG4', 'CG40', 'CG41', 'CG42',
                'CG43', 'CG44', 'CG45', 'CG46', 'CG5', 'CG52', 'CG53', 'CG54',
                'CG55', 'CG56', 'CG6', 'CG60', 'CG61', 'CG62', 'CG63', 'CG64',
                'CG65', 'CG66', 'CG7', 'CG70', 'CG71', 'CG72', 'CG73', 'CG74',
                'CG75', 'CG76', 'CG8', 'CG80', 'CG81', 'CG82', 'CG83', 'CG84',
                'CG85', 'CG86', 'CG90', 'CG91', 'CG92', 'CG93', 'CH2', 'CH22',
                'CH24', 'CH25', 'CH2L', 'CH2R21', 'CH3', 'CH30', 'CH4', 'CH40',
                'CH41', 'CH42', 'CH43', 'CH44', 'CH45', 'CH46', 'CH4L',
                'CH4R41', 'CH5', 'CH6', 'CH60', 'CH61', 'CH62', 'CH63', 'CH64',
                'CH65', 'CH66', 'CH6L', 'CH6R31', 'CH7', 'CH71', 'CH72',
                'CH73', 'CH74', 'CH75', 'CH76', 'CH8', 'CH80', 'CH9', 'CL3',
                'CO30', 'CO31', 'CO32', 'CO33', 'CO34', 'CO35', 'CO36', 'CR4',
                'CR5', 'CR6', 'CS', 'CS1', 'CS10', 'CS11', 'CS12', 'CS2',
                'CS21', 'CS3', 'CS4', 'CS5', 'CT2', 'CT31', 'CT32', 'CT33',
                'CT34', 'CT35', 'CT36', 'CX', 'CX03', 'CX1', 'CX10', 'CX11',
                'CX2', 'CX21', 'CX3', 'CX34', 'CX39', 'CX4', 'CX41', 'CX46',
                'CX49', 'CX5', 'CX51', 'CX52', 'CX53', 'CX6', 'CX61', 'CX66',
                'CX7', 'CX70', 'CX8', 'CX9', 'CX91', 'D', 'D11', 'D12', 'D13',
                'D14', 'D15', 'D16', 'D21', 'D22', 'D23', 'D24', 'D25', 'D26',
                'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D41', 'D42', 'D43',
                'D44', 'D45', 'D46', 'D51', 'D52', 'D53', 'D54', 'D55', 'D56',
                'D61', 'D62', 'D63', 'D64', 'D65', 'D66', 'D70', 'D71', 'D72',
                'D73', 'D74', 'D75', 'D76', 'D79', 'D81', 'D82', 'D83', 'D84',
                'D85', 'D86', 'D91', 'D92', 'D93', 'D94', 'D95', 'D96', 'D97',
                'D98', 'D99', 'DA41', 'DA42', 'DA43', 'DA44', 'DA45', 'DA46',
                'DA51', 'DB32', 'DB33', 'DB34', 'DB35', 'DB36', 'DC31', 'DC32',
                'DC33', 'DC34', 'DC35', 'DC36', 'DC51', 'DC52', 'DC53', 'DC54',
                'DC55', 'DC56', 'DC82', 'DC83', 'DC84', 'DC85', 'DC86', 'DC87',
                'DC88', 'DC91', 'DC92', 'DC93', 'DC94', 'DC95', 'DC96', 'DD1',
                'DD2', 'DD31', 'DD32', 'DD33', 'DD34', 'DD35', 'DD36', 'DD82',
                'DD83', 'DE81', 'DE82', 'DE83', 'DE84', 'DE85', 'DE86', 'DF8',
                'DF91', 'DF92', 'DF93', 'DF94', 'DF95', 'DF96', 'DF97', 'DF98',
                'DF99', 'DM31', 'DO31', 'DO32', 'DO33', 'DO34', 'DO35', 'DO36',
                'DO37', 'DO38', 'DO91', 'DO92', 'DO93', 'DO94', 'DO95', 'DO96',
                'DQ', 'DS23', 'DS24', 'DS25', 'DS26', 'DS27', 'DS28', 'DS33',
                'DS34', 'DS35', 'DS36', 'DS37', 'DS38', 'DS42', 'DS43', 'DS44',
                'DS45', 'DS46', 'DS47', 'DS48', 'DS49', 'DS63', 'DS64', 'DS65',
                'DS66', 'DS67', 'DS68', 'DS71', 'DS72', 'DS73', 'DS74', 'DS75',
                'DS76', 'DS77', 'DS78', 'DS79', 'DS82', 'DS83', 'DS84', 'DS85',
                'DS86', 'DS87', 'DS88', 'DS93', 'DS94', 'DS95', 'DS96', 'DS97',
                'DS98', 'DV24', 'DV25', 'DV32', 'DV33', 'DV34', 'DV84', 'DV85',
                'DV86', 'DX84', 'DX85', 'DX86', 'E1', 'E2', 'E20', 'E3', 'E30',
                'E33', 'E35', 'E4', 'E40', 'E5', 'E50', 'E6', 'E60', 'E70',
                'E80', 'E90', 'ED18', 'ED28', 'ED35', 'EE', 'EE42', 'EE43',
                'EE44', 'EE47', 'EE49', 'EE52', 'EE53', 'EE54', 'EE57', 'EE59',
                'EE62', 'EE63', 'EE64', 'EE67', 'EE69', 'EH12', 'EH13', 'EH14',
                'EH18', 'EH19', 'EH22', 'EH24', 'EH28', 'EH29', 'EH33', 'EH34',
                'EH35', 'EH37', 'EH38', 'EH39', 'EJ12', 'EJ13', 'EJ14', 'EJ18',
                'EJ19', 'EJ22', 'EJ23', 'EJ24', 'EJ26', 'EJ28', 'EJ29', 'EJ32',
                'EJ33', 'EJ34', 'EJ35', 'EJ38', 'EJ39', 'EK12', 'EK13', 'EK14',
                'EK18', 'EK19', 'EK22', 'EK23', 'EK24', 'EK25', 'EK28', 'EK29',
                'EK32', 'EK33', 'EK34', 'EK35', 'EK37', 'EK38', 'EK39', 'EL10',
                'EX', 'EX1', 'EX12', 'EX13', 'EX14', 'EX15', 'EX18', 'EX19',
                'EX2', 'EX22', 'EX23', 'EX24', 'EX28', 'EX29', 'EX3', 'EX31',
                'EX33', 'EX34', 'EX35', 'EX39', 'EX70', 'EX90', 'EY90', 'F',
                'F0', 'F1', 'F10', 'F11', 'F12', 'F14', 'F2', 'F20', 'F22',
                'F3', 'F31', 'F32', 'F33', 'F34', 'F35', 'F3C', 'F3M', 'F3S',
                'F4', 'F42', 'F45', 'F5', 'F6', 'F61', 'F62', 'F65', 'F7',
                'F71', 'F72', 'F73', 'F7S', 'F8', 'F81', 'F82', 'F84', 'F85',
                'F88', 'F9', 'FB32', 'FB34', 'FB4', 'FB45', 'FB8', 'FE', 'FF',
                'FF32', 'FF34', 'FF4', 'FF45', 'FF8', 'FK', 'FN', 'FN7', 'FNC',
                'FP', 'FS', 'FT1', 'FU', 'GD', 'GS1', 'GS2', 'H', 'H01', 'H02',
                'H13', 'H19', 'H25', 'H26', 'H31', 'H32', 'H35', 'H41', 'H45',
                'H53', 'H54', 'H55', 'H57', 'H62', 'H64', 'H68', 'H73', 'H97',
                'HC', 'HO', 'ID', 'IL', 'IL1', 'IL12', 'IL12R', 'IL14',
                'IL14R', 'IL1R', 'IL2', 'IL2R', 'IL3', 'IL3R', 'IL4', 'IL41',
                'IL41R', 'IL42', 'IL42R', 'IL4R', 'IL5', 'IL5R', 'IL6', 'IL6R',
                'IL7', 'IL7R', 'IL8', 'IL81', 'IL81R', 'IL82', 'IL82R', 'IL83',
                'IL83R', 'IL8R', 'ILR', 'INN', 'J', 'K', 'K2', 'K3', 'K4',
                'K40', 'K41', 'K42', 'K43', 'K44', 'K45', 'K46', 'K47', 'K48',
                'K5', 'K6', 'K60', 'K61', 'K62', 'K63', 'K64', 'K65', 'K66',
                'K67', 'K68', 'K7', 'K71', 'K8', 'K84', 'K85', 'K9', 'K91',
                'K92', 'K93', 'K94', 'K95', 'K96', 'K97', 'K98', 'K99', 'KD',
                'KE83', 'KE84', 'KE85', 'KE86', 'KF91', 'KF92', 'KF93', 'KF94',
                'KF95', 'KF96', 'KF97', 'KF98', 'KF99', 'KT', 'KT1', 'KT2',
                'KT3', 'KT4', 'KT7', 'L', 'LA', 'LA11', 'LA12', 'LA13', 'LA14',
                'LA15', 'LA20', 'LA21', 'LA22', 'LA31', 'LA32', 'LA33', 'LA34',
                'LA35', 'LA36', 'LA37', 'LA39', 'LA4', 'LA41', 'LA42', 'LA44',
                'LA45', 'LA46', 'LA47', 'LA48', 'LA5', 'LA51', 'LA52', 'LA53',
                'LA56', 'LA57', 'LA58', 'LA59', 'LA61', 'LA62', 'LA63', 'LA64',
                'LA65', 'LA66', 'LA67', 'LA68', 'LA7', 'LA70', 'LA71', 'LA72',
                'LA73', 'LA76', 'LA77', 'LA8', 'LA80', 'LA81', 'LA82', 'LA83',
                'LA84', 'LA85', 'LA86', 'LA87', 'LA88', 'LA89', 'LA91',
                'LA91R', 'LA92', 'LA92R', 'LIM', 'M', 'M14', 'M35', 'MB64',
                'ME', 'MI', 'MT', 'MT1', 'MT11', 'MT12', 'MT17', 'MT18', 'MT2',
                'MT25', 'MT27', 'MT3', 'MT4', 'MT5', 'MT50', 'MT51', 'MT53',
                'MT54', 'MT55', 'MT56', 'MT57', 'MT58', 'MT59', 'MT6', 'MT9',
                'N00', 'N01', 'N02', 'N03', 'N04', 'N1', 'N12', 'N13', 'N14',
                'N19', 'N2', 'N22', 'N24', 'N26', 'N29', 'N3', 'N35', 'N38',
                'N5', 'N9', 'NA34', 'NB33', 'NC04', 'ND35', 'NF11', 'NF13',
                'NF19', 'NF34', 'NF35', 'NF38', 'NF44', 'NF52', 'NF54', 'NF56',
                'NF59', 'NF73', 'NF79', 'NF82', 'NF84', 'NF86', 'NF89', 'NG01',
                'NG02', 'NG03', 'NG04', 'NG05', 'NG06', 'NG07', 'NG08', 'NG09',
                'NG10', 'NG12', 'NG13', 'NG51', 'NG52', 'NG53', 'NG54', 'NG55',
                'NG56', 'NG57', 'NG58', 'NG59', 'NG60', 'NG61', 'NG62', 'NG63',
                'NG64', 'NG65', 'NG66', 'NG67', 'NG68', 'NG69', 'NG70', 'NG71',
                'NG72', 'NG73', 'NG74', 'NG75', 'NG76', 'NG77', 'NG78', 'NG79',
                'NG80', 'NG81', 'NG82', 'NG83', 'NG84', 'NG85', 'NG86', 'NG87',
                'NG88', 'NG89', 'NG90', 'NG91', 'NG92', 'NG93', 'NG94', 'NG95',
                'NG96', 'NG97', 'NG98', 'NG99', 'NH', 'NI38', 'NN', 'NP',
                'NP11', 'NP12', 'NP13', 'NP14', 'NP16', 'NP17', 'NP19', 'NP21',
                'NP22', 'NP24', 'NP25', 'NP26', 'NP27', 'NP28', 'NP29', 'NP34',
                'NP35', 'NP36', 'NP37', 'NP38', 'NP54', 'NP59', 'NP71', 'NP73',
                'NP76', 'NP78', 'NP79', 'NP92', 'NP93', 'NP95', 'NP96', 'NP97',
                'NP98', 'NP99', 'NQ13', 'NQ14', 'NQ19', 'NQ22', 'NQ24', 'NQ28',
                'NQ29', 'NQ34', 'NQ74', 'NQ92', 'NQ94', 'NS1', 'NS11', 'NS12',
                'NS13', 'NS14', 'NS16', 'NS17', 'NS19', 'NS2', 'NS21', 'NS22',
                'NS23', 'NS24', 'NS25', 'NS26', 'NS27', 'NS28', 'NS29', 'NS3',
                'NS34', 'NS35', 'NS37', 'NS38', 'NS54', 'NS7', 'NS71', 'NS9',
                'NS96', 'NS98', 'NT19', 'NT21', 'NT22', 'NT25', 'NT26', 'NT29',
                'NT34', 'NT92', 'NT96', 'NT97', 'NT98', 'NT99', 'NW', 'NW1',
                'NW11', 'NW12', 'NW13', 'NW14', 'NW16', 'NW17', 'NW19', 'NW2',
                'NW21', 'NW22', 'NW24', 'NW25', 'NW26', 'NW27', 'NW29', 'NW3',
                'NW34', 'NW35', 'NW36', 'NW37', 'NW38', 'NW54', 'NW65', 'NW7',
                'NW71', 'NW73', 'NW76', 'NW79', 'NW9', 'NW92', 'NW95', 'NW97',
                'NW98', 'NW99', 'NX11', 'NX12', 'NX16', 'NX21', 'NX25', 'NX29',
                'NX73', 'NX76', 'NX79', 'NX81', 'NX85', 'NX89', 'NX92', 'O',
                'OA1', 'OA2', 'OA3', 'OA4', 'OA5', 'OA6', 'OA7', 'OA71',
                'OA72', 'OA73', 'OA74', 'OA8', 'OA82', 'OA9', 'OA91', 'OA92',
                'OB', 'OD', 'OF1', 'OF2', 'OI2', 'OK0', 'OK01', 'OK1', 'OK10',
                'OK11', 'OK2', 'OK3', 'OK31', 'OK32', 'OK33', 'OK4', 'OK41',
                'OK5', 'OK51', 'OK52', 'OK6', 'OK61', 'OK62', 'OK63', 'OK71',
                'OK82', 'OK91', 'OK92', 'OK93', 'OL1', 'OL2', 'OL3', 'OL4',
                'OL5', 'OL6', 'OL82', 'ON1', 'OO', 'OO1', 'OO2', 'OO3', 'OO4',
                'OO5', 'OO7', 'OO8', 'OO9', 'OQ1', 'OS', 'OS1', 'OS2', 'OT',
                'OX', 'OX0', 'OX01', 'OX1', 'OX10', 'OX11', 'OX12', 'OX13',
                'OX14', 'OX15', 'OX16', 'OX17', 'OX18', 'OX19', 'OX20', 'OX3',
                'OX33', 'OX4', 'OX5', 'OX6', 'OX7', 'OX8', 'OX9', 'OX95',
                'OX98', 'OXI', 'OY', 'OZ', 'OZ1', 'OZ2', 'P01', 'P02', 'P03',
                'P04', 'P18', 'P19', 'P21', 'P24', 'P45', 'P61', 'PU01',
                'PU02', 'PU03', 'PU04', 'PU05', 'PU06', 'PU07', 'PU08', 'PU09',
                'PU11', 'PU12', 'PU13', 'PU14', 'PU15', 'PU16', 'PU17', 'PU18',
                'PU19', 'PU20', 'PU21', 'PU22', 'PU23', 'PU24', 'PU25', 'PU26',
                'PU27', 'PU28', 'PU29', 'PU30', 'PU31', 'PU32', 'PU33', 'PU34',
                'PU35', 'PU36', 'PU37', 'PU38', 'PU39', 'PU40', 'PU41', 'PU42',
                'PU43', 'PU44', 'PU45', 'PU46', 'PU47', 'PU48', 'PU49', 'PU50',
                'PU51', 'PU52', 'PU53', 'PU54', 'PU55', 'PU56', 'PU57', 'PU58',
                'PU59', 'PU60', 'PU61', 'PU62', 'PU63', 'PU64', 'PU65', 'PU66',
                'PU67', 'PU68', 'PU69', 'PU70', 'PU71', 'PU72', 'PU73', 'PU74',
                'PU75', 'PU76', 'PU77', 'PU78', 'PU79', 'PU80', 'PU81', 'PU82',
                'PU83', 'PU84', 'PU85', 'PU86', 'PU87', 'PU88', 'PU89', 'PU90',
                'PU91', 'PU92', 'PU93', 'PU94', 'PU95', 'PU96', 'PU97', 'PU98',
                'PU99', 'R', 'R0', 'R00', 'R01', 'R01S', 'R02', 'R02S', 'R03',
                'R04', 'R04S', 'R05', 'R05S', 'R06', 'R06S', 'R0S', 'R11',
                'R11S', 'R12', 'R12S', 'R13', 'R13S', 'R14', 'R14S', 'R15',
                'R15S', 'R16', 'R18', 'R19', 'R2', 'R23', 'R23S', 'R24', 'R25',
                'R26', 'R26S', 'R2S', 'R3', 'R32', 'R32S', 'R33', 'R33S',
                'R34', 'R35', 'R35S', 'R36', 'R36S', 'R37S', 'R3S', 'R4',
                'R41', 'R41S', 'R43', 'R43S', 'R45', 'R4S', 'R5', 'R53',
                'R53S', 'R57', 'R5S', 'R6', 'R62', 'R62S', 'R63', 'R63S',
                'R64', 'R64S', 'R65S', 'R67', 'R68S', 'R69', 'R6S', 'R7',
                'R73', 'R73S', 'R75S', 'R78', 'R7S', 'R8', 'R83', 'R83S',
                'R84', 'R8S', 'R9', 'R90', 'R92', 'R95', 'R97', 'R99', 'R9S',
                'RC', 'RI1', 'RL', 'RO', 'RS', 'S', 'S11', 'S12', 'S13', 'S14',
                'S15', 'S16', 'S2', 'S20', 'S21', 'S22', 'S23', 'S24', 'S25',
                'S26', 'S27', 'S28', 'S3', 'S30', 'S31', 'S32', 'S33', 'S34',
                'S35', 'S36', 'S37', 'S38', 'S39', 'S4', 'S40', 'S41', 'S42',
                'S43', 'S44', 'S45', 'S46', 'S47', 'S48', 'S49', 'S5', 'S50',
                'S51', 'S52', 'S53', 'S54', 'S55', 'S56', 'S57', 'S58', 'S59',
                'S6', 'S60', 'S61', 'S62', 'S63', 'S64', 'S65', 'S66', 'S67',
                'S68', 'S7', 'S70', 'S71', 'S72', 'S73', 'S74', 'S75', 'S76',
                'S77', 'S78', 'S79', 'S8', 'S80', 'S81', 'S82', 'S83', 'S84',
                'S85', 'S86', 'S87', 'S88', 'S89', 'S9', 'S90', 'S91', 'S92',
                'S93', 'S94', 'S95', 'S96', 'S97', 'S98', 'S99', 'SA4', 'SA41',
                'SA42', 'SA43', 'SA44', 'SA45', 'SA46', 'SB', 'SB1', 'SB2',
                'SC5', 'SC51', 'SC52', 'SC53', 'SC54', 'SC55', 'SC56', 'SC8',
                'SC81', 'SC82', 'SC83', 'SC84', 'SC85', 'SC86', 'SC87', 'SC88',
                'SD', 'SD1', 'SD2', 'SD3', 'SD5', 'SD7', 'SD8', 'SD9', 'SE2',
                'SE22', 'SE23', 'SE24', 'SE25', 'SE3', 'SE31', 'SE32', 'SE33',
                'SE34', 'SE35', 'SE36', 'SE37', 'SE38', 'SE39', 'SE71', 'SE72',
                'SE73', 'SE74', 'SE75', 'SE8', 'SE81', 'SE82', 'SE83', 'SE84',
                'SE85', 'SE86', 'SE87', 'SE88', 'SE89', 'SE9', 'SE91', 'SE92',
                'SE93', 'SE94', 'SE95', 'SE96', 'SE97', 'SE98', 'SF8', 'SF81',
                'SF82', 'SF83', 'SF84', 'SF85', 'SF86', 'SF87', 'SF88', 'SI',
                'SI1', 'SI41', 'SI42', 'SI43', 'SI44', 'SI45', 'SI46', 'SM4',
                'SM41', 'SM42', 'SM43', 'SM44', 'SM45', 'SM46', 'SO3', 'SO30',
                'SO31', 'SO32', 'SO33', 'SO34', 'SO35', 'SO36', 'SO37', 'SO38',
                'SQ01', 'SQ02', 'SQ03', 'SQ04', 'SQ05', 'SQ06', 'SQ07', 'SQ08',
                'SQ09', 'SQ10', 'SQ11', 'SQ12', 'SQ13', 'SQ14', 'SQ15', 'SQ16',
                'SQ17', 'SQ18', 'SQ19', 'SQ20', 'SQ21', 'SQ22', 'SQ23', 'SQ24',
                'SQ25', 'SQ26', 'SQ27', 'SQ28', 'SQ29', 'SQ30', 'SQ31', 'SQ32',
                'SQ33', 'SQ34', 'SQ35', 'SQ36', 'SQ37', 'SQ38', 'SQ39', 'SQ40',
                'SQ41', 'SQ42', 'SQ43', 'SQ44', 'SQ45', 'SQ46', 'SQ47', 'SQ48',
                'SQ49', 'SQ50', 'SQ51', 'SQ52', 'SQ53', 'SQ54', 'SQ55', 'SQ56',
                'SQ57', 'SQ58', 'SQ59', 'SQ60', 'SQ61', 'SQ62', 'SQ63', 'SQ64',
                'SQ65', 'SQ66', 'SQ67', 'SQ68', 'SQ69', 'SQ70', 'SQ71', 'SQ72',
                'SQ73', 'SQ74', 'SQ75', 'SQ76', 'SQ77', 'SQ78', 'SQ79', 'SQ80',
                'SQ81', 'SQ82', 'SQ83', 'SQ84', 'SQ85', 'SQ86', 'SQ87', 'SQ88',
                'SQ89', 'SQ90', 'SQ91', 'SQ92', 'SQ93', 'SQ94', 'SQ95', 'SQ96',
                'SQ97', 'SQ98', 'SQ99', 'ST1', 'ST6', 'ST62', 'ST8', 'SX8',
                'SX82', 'SX83', 'SX84', 'SX85', 'T', 'TAX', 'TH', 'TH0', 'TH1',
                'TH2', 'TH3', 'TH9', 'TN', 'TR', 'TW', 'TW01', 'TW02', 'TW03',
                'TW04', 'TW05', 'TW06', 'TW07', 'TW08', 'TW09', 'TW1', 'TW10',
                'TW11', 'TW12', 'TW13', 'TW14', 'TW15', 'TW16', 'TW17', 'TW18',
                'TW19', 'TW2', 'TW20', 'TW21', 'TW22', 'TW23', 'TW24', 'TW25',
                'TW26', 'TW27', 'TW28', 'TW29', 'TW3', 'TW30', 'TW31', 'TW32',
                'TW33', 'TW34', 'TW35', 'TW36', 'TW37', 'TW38', 'TW39', 'TW4',
                'TW40', 'TW41', 'TW42', 'TW43', 'TW44', 'TW45', 'TW46', 'TW47',
                'TW48', 'TW49', 'TW5', 'TW50', 'TW51', 'TW52', 'TW53', 'TW54',
                'TW55', 'TW56', 'TW57', 'TW58', 'TW59', 'TW6', 'TW60', 'TW61',
                'TW62', 'TW63', 'TW64', 'TW65', 'TW66', 'TW67', 'TW68', 'TW69',
                'TW7', 'TW70', 'TW71', 'TW72', 'TW73', 'TW74', 'TW75', 'TW76',
                'TW77', 'TW78', 'TW79', 'TW8', 'TW80', 'TW81', 'TW82', 'TW83',
                'TW84', 'TW85', 'TW86', 'TW87', 'TW88', 'TW89', 'TW9', 'TW90',
                'TW91', 'TW92', 'TW93', 'TW94', 'TW95', 'TW96', 'TW97', 'TW98',
                'TW99', 'TX12', 'TX13', 'TX18', 'TX2', 'TX22', 'TX24', 'TX27',
                'TX3', 'TX4', 'TX41', 'TX43', 'TX47', 'TX5', 'TX6', 'TX64',
                'TX66', 'TX68', 'TX72', 'TX73', 'UF', 'VA', 'VA1', 'VA1D',
                'VA1H', 'VA3', 'VA8', 'VAD', 'VAH', 'VB', 'W', 'WB', 'WD1',
                'WD2', 'WD3', 'WS10', 'XC11', 'Y', 'Y1', 'Y11', 'Y12', 'Y13',
                'Y14', 'Y15', 'Y16', 'Y2', 'Y20', 'Y21', 'Y22', 'Y23', 'Y24',
                'Y25', 'Y26', 'Y27', 'Y28', 'Y3', 'Y30', 'Y31', 'Y32', 'Y33',
                'Y34', 'Y35', 'Y36', 'Y37', 'Y38', 'Y39', 'Y4', 'Y40', 'Y41',
                'Y42', 'Y43', 'Y44', 'Y45', 'Y46', 'Y47', 'Y48', 'Y49', 'Y6',
                'Y60', 'Y61', 'Y62', 'Y63', 'Y64', 'Y65', 'Y66', 'Y67', 'Y68',
                'Y7', 'Y70', 'Y71', 'Y72', 'Y73', 'Y74', 'Y75', 'Y76', 'Y77',
                'Y78', 'Y79', 'Y8', 'Y80', 'Y81', 'Y82', 'Y83', 'Y84', 'Y85',
                'Y86', 'Y87', 'Y88', 'Y89', 'Y9', 'Y90', 'Y91', 'Y92', 'Y93',
                'Y94', 'Y95', 'Y96', 'Y97', 'Y98', 'YC32', 'YC34', 'YC4',
                'YC41', 'YC42', 'YC43', 'YC44', 'YC45', 'YC5', 'YC51', 'YC52',
                'YC53', 'YC54', 'YC55', 'YC56', 'YC6', 'YC61', 'YC62', 'YC63',
                'YC64', 'YC65', 'YC66', 'YC8', 'YC81', 'YC82', 'YC83', 'YC84',
                'YC85', 'YC86', 'YC87', 'YC88', 'YE2', 'YE21', 'YE22', 'YE23',
                'YE24', 'YE25', 'YE26', 'YE27', 'YE28', 'YE3', 'YE31', 'YE32',
                'YE33', 'YE34', 'YE35', 'YE36', 'YE37', 'YE38', 'YE39', 'YE4',
                'YE41', 'YE42', 'YE43', 'YE44', 'YE45', 'YE46', 'YE47', 'YE48',
                'YE8', 'YE81', 'YE82', 'YE83', 'YE84', 'YE85', 'YE86', 'YE87',
                'YE88', 'YE89', 'YF', 'YK', 'YK1', 'YK5', 'YK9', 'YM6', 'YM61',
                'YM62', 'YM63', 'YM64', 'YM65', 'YM66', 'YN5', 'YN51', 'YN52',
                'YN53', 'YN54', 'YN55', 'YN56', 'YN6', 'YN61', 'YN62', 'YN63',
                'YN64', 'YN65', 'YN66', 'YO', 'YO3', 'YO30', 'YO31', 'YO32',
                'YO33', 'YO34', 'YO35', 'YO36', 'YO37', 'YO38', 'YO4', 'YO5',
                'YO51', 'YO52', 'YO53', 'YO54', 'YO55', 'YO56', 'YO6', 'YO61',
                'YO62', 'YO63', 'YO64', 'YO65', 'YO66', 'YP5', 'YP51', 'YP52',
                'YP53', 'YP54', 'YP55', 'YP6', 'YP61', 'YP62', 'YP63', 'YP64',
                'YP65', 'YP66', 'YS', 'YX', 'YX4', 'YX82', 'YX83', 'YX84',
                'YX85', 'YY', 'Z', 'Z1', 'Z12', 'Z13', 'Z14', 'Z15', 'Z2',
                'Z20', 'Z21', 'Z22', 'Z23', 'Z24', 'Z25', 'Z26', 'Z3', 'Z30',
                'Z32', 'Z33', 'Z34', 'Z35', 'Z36', 'Z4', 'Z40', 'Z41', 'Z42',
                'Z43', 'Z44', 'Z45', 'Z46', 'Z5', 'Z52', 'Z53', 'Z54', 'Z55',
                'Z6', 'Z60', 'Z62', 'Z63', 'Z64', 'Z65', 'Z66', 'Z7', 'Z70',
                'Z71', 'Z72', 'Z73', 'Z74', 'Z75', 'Z76', 'Z8', 'Z80', 'Z82',
                'Z83', 'Z84', 'Z85', 'Z86', 'Z88', 'Z89', 'Z9', 'Z90', 'Z91',
                'Z92', 'Z93', 'Z94', 'Z95', 'Z96', 'ZC4', 'ZC41', 'ZC42',
                'ZC43', 'ZC44', 'ZC45', 'ZC46', 'ZC5', 'ZC51', 'ZC52', 'ZC53',
                'ZC54', 'ZC55', 'ZC56', 'ZC6', 'ZC61', 'ZC62', 'ZC63', 'ZC64',
                'ZC65', 'ZC66', 'ZE3', 'ZE31', 'ZE32', 'ZE33', 'ZE34', 'ZE35',
                'ZE36', 'ZE4', 'ZE41', 'ZE42', 'ZE43', 'ZE44', 'ZE45', 'ZE46',
                'ZE8', 'ZE82', 'ZE83', 'ZE84', 'ZE85', 'ZE86', 'ZE87', 'ZE88',
                'ZE89', 'ZE9', 'ZE91', 'ZE92', 'ZE93', 'ZE94', 'ZE95', 'ZE96',
                'ZO3', 'ZO30', 'ZO32', 'ZO33', 'ZO34', 'ZO35', 'ZO36'):
            self.assertEqual(d.is_base_activity(x), True, x)

class TestURLParser(TestFixture):
    "Test URL parser"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        u = d.simple_urlparser("https://user:password@www.acosta.se:1234/info/family;params?query.cgi#frag")
        self.assertEqual(u.scheme, "https")
        self.assertEqual(u.username, "user")
        self.assertEqual(u.password, "password")
        self.assertEqual(u.port, 1234)
        self.assertEqual(u.hostname, "www.acosta.se")
        self.assertEqual(u.path, "info/family")
        self.assertEqual(u.params, "params")
        self.assertEqual(u.query, "query.cgi")
        self.assertEqual(u.fragment, "frag")


class TestFD(TestFixture):
    "Test FD"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    def test_001(self):
        self.p = d.fd_parser("SK    2")
        self.assertEqual(self.p, ("SK", 2, ""))
        self.assertEqual(self.p.flight_id, "SK 0002 ")
        self.assertEqual(self.p.flight_name, "002")
        self.assertEqual(self.p.flight_descriptor, "SK 000002 ")

    def test_002(self):
        self.p = d.fd_parser("SK0002Z")
        self.assertEqual(self.p, ("SK", 2, "Z"))
        self.assertEqual(self.p.flight_id, "SK 0002Z")
        self.assertEqual(self.p.flight_name, "002Z")
        self.assertEqual(self.p.flight_descriptor, "SK 000002Z")

    def test_003(self):
        self.p = d.fd_parser("SK1234")
        self.assertEqual(self.p, ("SK", 1234, ""))
        self.assertEqual(self.p.flight_id, "SK 1234 ")
        self.assertEqual(self.p.flight_name, "1234")
        self.assertEqual(self.p.flight_descriptor, "SK 001234 ")

    def test_004(self):
        self.p = d.fd_parser("LH3456Z")
        self.assertEqual(self.p, ("LH", 3456, "Z"))
        self.assertEqual(self.p.flight_id, "LH 3456Z")
        self.assertEqual(self.p.flight_name, "LH3456Z")
        self.assertEqual(self.p.flight_descriptor, "LH 003456Z")

    def test_005(self):
        def failtry():
            return d.fd_parser("SKZN2")
        self.assertRaises(ValueError, failtry)

    def test_006(self):
        self.p = d.fd_parser("SK 000983")
        self.assertEqual(self.p, ("SK", 983, ""))
        self.assertEqual(self.p.flight_id, "SK 0983 ")
        self.assertEqual(self.p.flight_name, "983")
        self.assertEqual(self.p.flight_descriptor, "SK 000983 ")
        self.p = d.fd_parser("SK 000983 ")
        self.assertEqual(self.p, ("SK", 983, ""))
        self.assertEqual(self.p.flight_id, "SK 0983 ")
        self.assertEqual(self.p.flight_name, "983")
        self.assertEqual(self.p.flight_descriptor, "SK 000983 ")
        self.p = d.fd_parser(" SK 000983 ")
        self.assertEqual(self.p, ("SK", 983, ""))
        self.assertEqual(self.p.flight_id, "SK 0983 ")
        self.assertEqual(self.p.flight_name, "983")
        self.assertEqual(self.p.flight_descriptor, "SK 000983 ")

    def test_007(self):
        self.p = d.fd_parser("5T511")
        self.assertEqual(self.p, ("5T", 511, ""))

        self.p = d.fd_parser("Q6311")
        self.assertEqual(self.p, ("Q6", 311, ""))

        self.p = d.fd_parser("Q603")
        self.assertEqual(self.p, ("Q6", 3, ""))


class TestRoman(TestFixture):
    "Test Roman"
    
    @REQUIRE("Tracking")
    def __init__(self):
        TestFixture.__init__(self)        
    
    facit = (
        (1, "I"), (2, "II"), (3, "III"), (4, "IV"), (5, "V"),
        (6, "VI"), (7, "VII"), (8, "VIII"), (9, "IX"), 
        (10, "X"), (11, "XI"), (12, "XII"), (13, "XIII"), (14, "XIV"), 
        (15, "XV"), (16, "XVI"), (17, "XVII"), (18, "XVIII"), (19, "XIX"), 
        (20, "XX"), (21, "XXI"), (25, "XXV"),
        (30, "XXX"), (35, "XXXV"),
        (40, "XL"), (45, "XLV"), (49, "XLIX"),
        (50, "L"),
        (60, "LX"), (69, "LXIX"),
        (70, "LXX"), # Septuagint
        (76, "LXXVI"),
        (80, "LXXX"), (90, "XC"), (99, "XCIX"),
        (100, "C"), (150, "CL"),
        (200, "CC"), (300, "CCC"), (400, "CD"), (499, "CDXCIX"), (500, "D"),
        (600, "DC"), (666, "DCLXVI"), # Every symbole except M in descending order
        (700, "DCC"), (800, "DCCC"), (900, "CM"), (999, "CMXCIX"),
        (1000, "M"), (1444, "MCDXLIV"), # smallest pandigital number
        (1666, "MDCLXVI"), # largest efficient pandigital number
        (1965, "MCMLXV"), (1990, "MCMXC"), (1997, "MCMXCVII"), (1999, "MCMXCIX"),
        (2000, "MM"), (2001, "MMI"), (2010, "MMX"),
        (2500, "MMD"), (3000, "MMM"),
        (3888, "MMMDCCCLXXXVIII"), # longest without overline
        (3999, "MMMCMXCIX"), # largest without overline
    )

    def test_i2rm(self):
        for n, r in self.facit:
            self.assertEqual(d.i2rm(n), r)

    def test_rm2i(self):
        for n, r in self.facit:
            self.assertEqual(d.rm2i(r), n)

    

