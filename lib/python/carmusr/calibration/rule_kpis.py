
def in_studio():
    try:
        import Cui  # @UnusedImport
        return True
    except ImportError:
        # We are in an optimizer
        return False


def use_only_these_kpis_for_legs_or_acrots(kpiself, add_matrix=True, add_vectors=True):
    """
    Called in the very beginning of the CustomKPI.create method.
    """
    if not in_studio():
        return False

    import carmusr.calibration.util.rule_kpis_imp as rki
    return rki._use_only_these_kpis_for_legs_or_acrots(kpiself, add_matrix, add_vectors)


def add_kpis(kpiself, bag, add_matrix=True, add_vectors=True):
    """
    Called from the CustomKPI.create method for trip-rule KPIs.
    """
    if not in_studio():
        return

    import carmusr.calibration.util.rule_kpis_imp as rki
    rki._add_kpis(kpiself, bag, add_matrix, add_vectors, variant=None)
