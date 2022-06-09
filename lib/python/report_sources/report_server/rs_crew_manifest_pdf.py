

"""
This report handles the PDF report intended for Chinese authorities.  There are
also EDIFACT messages (APIS) involved, they are handled in rs_crew_manifest.py
"""

from report_sources.report_server.rs_if import argfix
from report_sources.hidden.CrewManifestPDF import generate_many


@argfix
def generate(*a, **k):
    return generate_many(**k)


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
