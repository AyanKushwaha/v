"""
Test CrewMealTest
"""


from carmtest.framework import *

class crew_001_CrewInfoTest(TestFixture):

    @REQUIRE("Tracking", "PlanLoaded")
    def __init__(self):
        TestFixture.__init__(self)

    def test_001_initiateTables(self):
        import meal.MealOrderFormHandler as M
        M.initFormTableManager()

        self.assertEquals("tmp_meal_order_param", M.MH.paramTable.name)
        self.assertEquals("tmp_filter_month", M.MH.filterTable.name)
        self.assertEquals("tmp_meal_message", M.MH.messageTable.name)
        self.assertEquals("tmp_meal_order", M.MH.orderTable.name)
        self.assertEquals("tmp_meal_forecast", M.MH.forecastTable.name)
        self.assertEquals("tmp_meal_order_lines", M.MH.orderLineTable.name)
        self.assertEquals("tmp_nr_selected", M.MH.nrSelectedTable.name)
    
