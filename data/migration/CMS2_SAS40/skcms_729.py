import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2016_08_16'

@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):
    ops = []

    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'DBML',
        'si': 'DIABETIC MEAL',
    }))
    
    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'GFML',
        'si': 'GLUTEN-FREE MEAL',
    }))
    
    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'MOML',
        'si': 'MOSLEM MEAL',
    }))
    
    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'NLML',
        'si': 'NON LACTOSE MEAL',
    }))
    
    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'VGML',
        'si': 'VEGETARIAN MEAL (NON-DAIRY)',
    }))
    
    ops.append(fixrunner.createOp('meal_special_code_set', 'W', {
        'id': 'VLML',
        'si': 'VEGETARIAN MEAL (LACTO-OVO)',
    }))
    
    ops.append(fixrunner.createOp('special_schedules_set', 'W', {
        'typ': 'SpecialMealCode',
        'si': 'Code for special meal',
    }))

    print "done"
    return ops


fixit.program = 'skcms_729.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ",__version__

