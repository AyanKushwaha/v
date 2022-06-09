
import  carmensystems.publisher.api as publisher
import carmensystems.rave.api as rave

def _generate_reciept(self):
    '''
    Generate a reciept of granted requests as a pdf-report.
    '''

    #crew_context = rave.context("sp_crew").bag()


    #Generate the report
    publisher.generateReport("report_sources.report_server.rs_RequestReciept",
                             "/users/annao/request_test",
                             reportparams={"crew_id":"10034"})

    #Save the report in a tmp directory

    #Move the saved report to the


if __name__ == '__main__':
    
    _generate_reciept(None)
