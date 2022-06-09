import utils
import carmtest.framework.TestFunctions as TF

def __root__(request):
    tests = TF.list_categories()
    return utils.template('reports.html', locals())