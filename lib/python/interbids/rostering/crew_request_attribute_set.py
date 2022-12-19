"""Calculate crew request group for crew

This file contains functions and classes for calculating what crew request group a crew belongs to.
The class CrewRequestAttributeSet works as an API and will return a class inheriting from
CrewAttributeSet, containing all resource attributes needed for calculating
the crew request group. The crew request group is calculated using the RequestGroupClass and
then stored as a separate attribute in the CrewRequestAttributeSet.

During the migration process we will need to support two schemas, JMP3 and JMP4.
Switching between the two schemas is done by setting the evnironment variable
SCHEMA_USED to JMP3 or JMP4. Once the migration process is done, we can remove everything related to the JMP3
schema and simplify things, for example removing the global variable SCHEMA_USED and have CrewRequestAttributeSet
inherit directly from CrewRequestAttributeSetJMP4.
"""
import os


def schema_used():
    schema = os.environ['SCHEMA_USED']
    if schema == "JMP3" or schema == "JMP4":
        return schema
    else:
        raise ValueError("Environment value SCHEMA_USED set to incorrect value")


class CrewRequestAttributeSet(object):
    """Get resource attribute values and crew request group for crew

    Will return a class inheriting from CrewAttributeSet containing all resource attributes
    and also what crew request group a crew belongs to.
    """

    def __new__(cls, tm, crew):
        schema = schema_used()
        if schema == "JMP4":
            attributes = CrewRequestAttributeSetJMP4(crew)
            request_group = RequestGroupJMP4(tm, attributes)
        elif schema == "JMP3":
            attributes = CrewRequestAttributeSetJMP3(crew)
            request_group = RequestGroupJMP3(tm, attributes)
        else:
            raise ValueError("Schema set to incorrect value")

        dates = attributes.all_attribute_dates()
        request_group_values = request_group.request_groups_at_dates(dates)
        attributes.set_values("RequestGroup", request_group_values)
        return attributes

    def get_values(self, name, date=None):
        raise NotImplementedError

    def list_values(self):
        raise NotImplementedError


class CrewAttributeSet(object):
    """Store resource attributes values

    Resource attributes have a name, value and a date-range, validfrom - validto,
    when the resource attribute is valid.
    """

    def __init__(self, *attributes):
        self._attributes = {}
        for (name, values) in attributes:
            self.set_values(name, values)

    def set_values(self, name, values):
        """Set attribute with name to values. Overrides previously set values.

        @param name: Name of attribute
        @type name: str
        @param values: Attribute values as a tuple of (validfrom, validto, value)
        @type values: Attribute values as a tuple of type (AbsTime, AbsTime, str)
        """
        merged_values = self._merge_equal_periods(values)
        self._attributes[name] = merged_values

    def get_values(self, name, date=None):
        """Get attribute values for an attribute

        Get attribute values for an attribute at a certain date.
        If date is None, return all attribute values for an attribute.

        @param name: Name of attribute
        @type name: str
        @param date: Look for attribute values ate this date
        @type date: AbsTime
        @returns: A list of attribute values tuples (validfrom, validto, value)
        @rtype: A list of (AbsTime, AbsTime, str)
        """

        if date is None:
            return self._attributes[name]

        values = []
        for (validfrom, validto, value) in self._attributes[name]:
            if CrewAttributeSet._date_is_within_range(date, validfrom, validto):
                values.append(value)
        return values

    def list_values(self):
        """Get all attribute values for all attributes

        @returns: A list of attribute values tuples (name, validfrom, validto, value)
        @rtype: A list of (str, AbsTime, AbsTime, str)
        """
        values = []
        for name in sorted(self._attributes.keys()):
            for (validfrom, validto, value) in self._attributes[name]:
                values.append((name, validfrom, validto, value))
        return values

    def all_attribute_dates(self):
        """Get all dates used for date range validity for all attributes

        @returns: A list of dates
        @rtype: A list of AbsTime
        """
        dates = set()
        for values in self._attributes.values():
            for (validfrom, validto, _) in values:
                dates.add(validfrom)
                dates.add(validto)
        return list(sorted(dates))

    def _merge_equal_periods(self, periods):
        """Combine overlapping periods with the same value"""

        periods = list(set(periods))

        if periods:
            periods.sort(key=lambda (validfrom, validto, value): (value, validfrom, validto))
            merged_periods = [periods.pop(0)]
            while periods:
                (validfrom1, validto1, value1) = merged_periods[-1]
                (validfrom2, validto2, value2) = periods.pop(0)
                if value1 == value2 and validto1 == validfrom2:
                    merged_periods.pop()
                    merged_periods.append((validfrom1, validto2, value1))
                else:
                    merged_periods.append((validfrom2, validto2, value2))
            periods = merged_periods

        periods.sort(key=lambda (validfrom, validto, x): (validfrom, x, validto))
        return periods

    @staticmethod
    def _date_is_within_range(date, start, end):
        return start <= date and (end is None or date < end)

    def __str__(self):
        return str(self._attributes)


class CrewRequestAttributeSetJMP3(CrewAttributeSet):
    """Resource attributes values for JMP3 schema"""

    def __init__(self, crew):
        self._crew = crew
        super(CrewRequestAttributeSetJMP3, self).__init__(
            ("Empno", [(x.validfrom, x.validto, x.extperkey)
                       for x in self._crew.referers("crew_employment", "crew")]),
            ("Category", [(x.validfrom, x.validto, x.titlerank.maincat.id)
                          for x in self._crew.referers("crew_employment", "crew")]),
            ("AcQual", [(x.validfrom, x.validto, x.qual.subtype)
                        for x in self._crew.referers("crew_qualification", "crew")
                        if x.qual.typ == "ACQUAL"]),
            ("Base", [(x.validfrom, x.validto, x.base.id)
                      for x in self._crew.referers("crew_employment", "crew")]),
            ("Rank", [(x.validfrom, x.validto, x.crewrank.id)
                      for x in self._crew.referers("crew_employment", "crew")]),
            ("Station", [(x.validfrom, x.validto, x.station)
                         for x in self._crew.referers("crew_employment", "crew")]),
            ("Contract", [(x.validfrom, x.validto, x.contract.id)
                          for x in self._crew.referers("crew_contract", "crew")]),
            ("Country", [(x.validfrom, x.validto, x.country.id)
                         for x in self._crew.referers("crew_employment", "crew")]),
            ("Company", [(x.validfrom, x.validto, x.company.id)
                         for x in self._crew.referers("crew_employment", "crew")]),
            ("Region", [(x.validfrom, x.validto, x.region.id)
                        for x in self._crew.referers("crew_employment", "crew")]),
            ("Instructor", [(x.validfrom, x.validto, x.qual.subtype)
                            for x in self._crew.referers("crew_qualification", "crew")
                            if x.qual.typ == "INSTRUCTOR"]),
            ("Airport", [(x.validfrom, x.validto, x.qual.subtype)
                         for x in self._crew.referers("crew_qualification", "crew")
                         if x.qual.typ == "AIRPORT"]),
            ("LCP", [(x.validfrom, x.validto, x.qual.subtype)
                     for x in self._crew.referers("crew_qualification", "crew")
                     if x.qual.subtype == "LCP"]),
            ("Position", [(x.validfrom, x.validto, x.qual.subtype)
                          for x in self._crew.referers("crew_qualification", "crew")
                          if x.qual.typ == "POSITION"]),
            ("New", [(x.validfrom, x.validto, x.rest.typ)
                     for x in self._crew.referers("crew_restriction", "crew")
                     if x.rest.typ == "NEW"]),
            ("Medical", [(x.validfrom, x.validto, x.rest.subtype)
                         for x in self._crew.referers("crew_restriction", "crew")
                         if x.rest.typ == "MEDICAL"]),
            ("Training", [(x.validfrom, x.validto, x.rest.subtype)
                          for x in self._crew.referers("crew_restriction", "crew")
                          if x.rest.typ == "TRAINING"]),
            ("ContractType", [(x.validfrom, x.validto, x.contract.grouptype)
                              for x in self._crew.referers("crew_contract", "crew")]),
            ("ContractCycleStart", [(x.validfrom, x.validto, x.cyclestart)
                                    for x in self._crew.referers("crew_contract", "crew")]),
            ("ACInstructor", [(x.validfrom, x.validto, x.acqqual.subtype)
                              for x in self._crew.referers("crew_qual_acqual", "crew")
                              if x.acqqual.typ == "INSTRUCTOR"]),
            ("ContractDutyPercent", [(x.validfrom, x.validto, x.contract.dutypercent)
                                     for x in self._crew.referers("crew_contract", "crew")]),
            ("AgreementGroup", [(x.validfrom, x.validto, x.contract.agmtgroup)
                                for x in self._crew.referers("crew_contract", "crew")]))


class CrewRequestAttributeSetJMP4(CrewAttributeSet):
    """Resource attributes values for JMP4 schema"""

    def __init__(self, crew):
        self._crew = crew
        super(CrewRequestAttributeSetJMP4, self).__init__(
            ("Category", [(x.validfrom, x.validto, x.titlerank.maincat.id)
                          for x in self._crew.referers("crew_employment", "crew")]),
            ("AcQual", [(x.validfrom, x.validto, x.qual.subtype)
                        for x in self._crew.referers("crew_qualification", "crew")
                        if x.qual.typ == "ACQUAL"]),
            ("Rank", [(x.validfrom, x.validto, x.crewrank.id)
                      for x in self._crew.referers("crew_employment", "crew")]),
            ("Base", [(x.validfrom, x.validto, x.base.id)
                      for x in self._crew.referers("crew_employment", "crew")]),
            ("Company", [(x.validfrom, x.validto, x.company.id)
                         for x in self._crew.referers("crew_employment", "crew")]),
            ("Region", [(x.validfrom, x.validto, x.region.id)
                        for x in self._crew.referers("crew_employment", "crew")]),
            ("Contract", [(x.validfrom, x.validto, x.contract.id)
                          for x in self._crew.referers("crew_contract", "crew")]),
            ("ContractType", [(x.validfrom, x.validto, x.contract.grouptype)
                              for x in self._crew.referers("crew_contract", "crew")]),
            ("ContractDutyPercent", [(x.validfrom, x.validto, x.contract.dutypercent)
                                     for x in self._crew.referers("crew_contract", "crew")]),
            ("AgreementGroup", [(x.validfrom, x.validto, x.contract.agmtgroup.id)
                                for x in self._crew.referers("crew_contract", "crew")]),
            ("Instructor", [(x.validfrom, x.validto, x.qual.subtype)
                            for x in self._crew.referers("crew_qualification", "crew")
                            if x.qual.typ == "INSTRUCTOR"]),
            ("Position", [(x.validfrom, x.validto, x.qual.subtype)
                          for x in self._crew.referers("crew_qualification", "crew")
                          if x.qual.typ == "POSITION"]),
            ("Airport", [(x.validfrom, x.validto, x.acqqual.subtype)
                         for x in self._crew.referers("crew_qual_acqual", "crew")
                         if x.acqqual.typ == "AIRPORT"]),
            ("ACInstructor", [(x.validfrom, x.validto, x.acqqual.subtype)
                              for x in self._crew.referers("crew_qual_acqual", "crew")
                              if x.acqqual.typ == "INSTRUCTOR"]),
            ("Medical", [(x.validfrom, x.validto, x.rest.subtype)
                         for x in self._crew.referers("crew_restriction", "crew")
                         if x.rest.typ == "MEDICAL"]),
            ("ContractTag", [(x.validfrom, x.validto, x.contract.congrouptype.id)
                             for x in self._crew.referers("crew_contract", "crew")
                             if x.contract.congrouptype is not None]))


class RequestGroup(object):
    """Calculate crew request group for crew"""

    def __init__(self, tm, fields, attributes):
        self._tm = tm
        self._fields = fields
        self._attributes = attributes

    def request_groups_at_dates(self, dates):
        """
        Calculate active request groups at dates based on crew resource attributes.

        Takes a list of dates that will be combined into ranges. Each range will be associated with a request group.

        @param name: List of dates.
        @type name: List of AbsTime
        @returns: A list of attribute values tuples (validfrom, validto, value)
        @rtype: A list of (AbsTime, AbsTime, str)
        """

        values = []
        for (validfrom, validto) in zip(dates, dates[1:]+[None]):
            for value in self.request_group_at_date(validfrom):
                print "Logging the request groups infomation for crew - Valid from : ", validfrom , " valid to : ", validto , " value :  " , value.name
                values.append((validfrom, validto, value))
        return values

    def request_group_at_date(self, date):
        """
        Calculate active request groups at date based on crew resource attributes.

        @param name: date.
        @type name: AbsTime
        @returns: A list of attribute values tuples (validfrom, validto, value)
        @rtype: A list of (AbsTime, AbsTime, str)
        """

        cat = self._attributes.get_values("Category")[-1][2]
        for crew_group in self._tm.table("crew_filter"):
            if crew_group.typ.id != "REQUEST" or crew_group.cat != cat:
                continue

            expressions = crew_group.selvalue.split(":") + ["*"]*30

            if self._crew_group_matches_attributes(expressions, date):
                yield crew_group

    def _crew_group_matches_attributes(self, expressions, date):
        matches = []
        for (expression, field_name) in zip(expressions, self._fields):
            matches.append(self._eval_crew_filter_expression(expression, field_name, date))
        return all(matches)

    def _eval_crew_filter_expression(self, expression, field_name, date):
        if expression == "*":
            return True

        values = map(str, self._attributes.get_values(field_name, date))

        return self._eval_crew_filter_disjunctions(expression, values)

    def _eval_crew_filter_disjunctions(self, expression, values):
        matches = []
        for conj_expression in expression.split("|"):
            matches.append(self._eval_crew_filter_conjunctions(conj_expression, values))
        return any(matches)

    def _eval_crew_filter_conjunctions(self, expression, values):
        matches = []
        for variable_expression in expression.split("&"):
            matches.append(self._eval_crew_filter_variable(variable_expression, values))
        return all(matches)

    def _eval_crew_filter_variable(self, variable, values):
        if variable.startswith("!"):
            operation = RequestGroup._inverse
            variable = variable[1:]
        else:
            operation = RequestGroup._identity

        if variable == "*":
            return operation(True)

        return operation(variable in values)

    @staticmethod
    def _inverse(x):
        return not x

    @staticmethod
    def _identity(x):
        return x


class RequestGroupJMP4(RequestGroup):
    """Calculate crew request group for crew using JMP4 schema"""

    def __init__(self, tm, attributes):
        fields = ["AcQual",
                  "Rank",
                  "Base",
                  "Company",
                  "Region",
                  "Contract",
                  "ContractType",
                  "ContractDutyPercent",
                  "AgreementGroup",
                  "Instructor",
                  "Position",
                  "Airport",
                  "ACInstructor",
                  "Medical",
                  "ContractTag"]
        super(RequestGroupJMP4, self).__init__(tm, fields, attributes)


class RequestGroupJMP3(RequestGroup):
    """Calculate crew request group for crew using JMP3 schema"""

    def __init__(self, tm, attributes):
        fields = ["CrewGroup",
                  "AcQual",
                  "Base",
                  "Rank",
                  "Station",
                  "Contract",
                  "Country",
                  "Company",
                  "Region",
                  "Instructor",
                  "Airport",
                  "LCP",
                  "Position",
                  "New",
                  "Medical",
                  "Training",
                  "ContractType",
                  "ContractCycleStart",
                  "ACInstructor",
                  "ContractDutyPercent",
                  "AgreementGroup"]
        super(RequestGroupJMP3, self).__init__(tm, fields, attributes)
