from report_sources.report_server.rs_if import argfix
from crewlists.crewlist_safetynet import run

@argfix
def generate(*a, **k):
    return run(*a, **k)
