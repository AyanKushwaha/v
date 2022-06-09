UDMAIRPATH=$(CARMSYS)/data/config/models/udm_air1
UDMADMINPATH=$(CARMSYS)/data/config/models/udm_admin2

UDMXML=$(UDMAIRPATH)/air1_core.xml \
    $(UDMAIRPATH)/air1_crew.xml \
    $(UDMAIRPATH)/air1_aircraft.xml \
    $(UDMAIRPATH)/air1_airport.xml \
    $(UDMAIRPATH)/air1_manpower.xml \
    $(UDMAIRPATH)/air1_planning.xml \
    $(UDMAIRPATH)/air1_tracking.xml \
    $(UDMAIRPATH)/air1_iocs.xml \
    $(UDMAIRPATH)/air1_urm.xml \
    $(UDMAIRPATH)/air1_origsuffix.xml \
    $(UDMAIRPATH)/air1_aoc.xml \
    $(UDMAIRPATH)/air1_ctraining.xml \
    $(UDMADMINPATH)/admin2_dig.xml \
    $(UDMADMINPATH)/admin2_rave.xml \
    $(UDMADMINPATH)/admin2_audit.xml \
    $(UDMADMINPATH)/admin2_datacontext.xml 

SASUDMPATH=$(CARMUSR)/data/config/models

SASUDMXML=$(SASUDMPATH)/cmp_transition.xml \
 $(SASUDMPATH)/sas_accounts.xml \
 $(SASUDMPATH)/sas_admin.xml \
 $(SASUDMPATH)/sas_air_aircraft.xml \
 $(SASUDMPATH)/sas_air_core.xml \
 $(SASUDMPATH)/sas_air_crew.xml \
 $(SASUDMPATH)/sas_air_tracking.xml \
 $(SASUDMPATH)/sas_annotations.xml \
 $(SASUDMPATH)/sas_attributes.xml \
 $(SASUDMPATH)/sas_base_breaks.xml \
 $(SASUDMPATH)/sas_bought_days.xml \
 $(SASUDMPATH)/sas_calloutlist.xml \
 $(SASUDMPATH)/sas_checkin.xml \
 $(SASUDMPATH)/sas_crew_meals.xml \
 $(SASUDMPATH)/sas_crew_needs.xml \
 $(SASUDMPATH)/sas_crew_user_filter.xml \
 $(SASUDMPATH)/sas_dig_recipients.xml \
 $(SASUDMPATH)/sas_financial.xml \
 $(SASUDMPATH)/sas_handover_reports.xml \
 $(SASUDMPATH)/sas_hotel_bookings.xml \
 $(SASUDMPATH)/sas_integration.xml \
 $(SASUDMPATH)/sas_leave_parameters.xml \
 $(SASUDMPATH)/sas_legality.xml \
 $(SASUDMPATH)/sas_manpower_accumulators.xml \
 $(SASUDMPATH)/sas_notification.xml \
 $(SASUDMPATH)/sas_passive_bookings.xml \
 $(SASUDMPATH)/sas_paxlst.xml \
 $(SASUDMPATH)/sas_planning.xml \
 $(SASUDMPATH)/sas_published.xml \
 $(SASUDMPATH)/sas_rave.xml \
 $(SASUDMPATH)/sas_rule_violation.xml \
 $(SASUDMPATH)/sas_special_local_transport.xml \
 $(SASUDMPATH)/sas_special_schedules.xml \
 $(SASUDMPATH)/sas_standby.xml \
 $(SASUDMPATH)/sas_table_accumulators.xml \
 $(SASUDMPATH)/sas_training.xml \
 $(SASUDMPATH)/sas_transport_bookings.xml

XML=$(UDMXML) $(SASUDMXML)

udm.pdf: schema/udm.tex figures/figures.tex
	./mkdocpdf $<

figures/figures.tex: $(CARMSYS)/bin/davemodel2tex $(XML) 
	mkdir -p figures
	$(CARMSYS)/bin/davemodel2tex -d figures -o figures.tex -p -N $(XML)
verify: 
	xmllint --noout $(XML)
clean:
	-rm -rf figures tmp* udm.pdf
