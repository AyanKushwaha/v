# This script can be run from within studio and tries to find descripancies in booked/assigned values between rave and db entries.
# See SKWD-671 for more information.
import carmensystems.rave.api as R
from tm import TM

def leg_id(leg):
    return "%s+%s+%s" % (leg.udor.yyyymmdd()[:8], leg.fd, leg.adep.id)

def trip_id(trip):
    return "%s+%s" % (trip.udor.yyyymmdd()[:8], trip.id)

def main():
    pos_conv = {}

    for compl in TM.crew_complement:
        pos_conv[compl.idx] = compl.pos.id
        pos_conv[compl.pos.id] = compl.idx

    leg_assigned = {}
    leg_booked = {}
    leg_trips = {}

    for cfd in TM.crew_flight_duty:
        # print "CFD", cfd
        if cfd.pos.id in ('DH',):
            continue
        position = pos_conv[cfd.pos.id]
        leg = leg_id(cfd.leg)
        if not leg in leg_assigned:
            leg_assigned[leg] = {}
        leg_assigned[leg][position] = leg_assigned[leg].get(position, 0) + 1

    for tfd in TM.trip_flight_duty:
        if tfd.pos != None and tfd.pos.id == 'DH':
            continue
        if tfd.leg.statcode.id == 'C':
            continue
        try:
            leg = leg_id(tfd.leg)
            if not leg in leg_booked:
                leg_booked[leg] = {}
                for i in range(0, 10):
                    leg_booked[leg][i] = leg_assigned.get(leg, {}).get(i, 0)
            trip_contributes = False
            for i in range(0, 10):
                contrib = getattr(tfd.trip, 'cc_%s' % i)
                leg_booked[leg][i] += contrib
                if contrib > 0:
                    trip_contributes = True

            if trip_contributes:
                leg_trips[leg] = leg_trips.get(leg, []) + [trip_id(tfd.trip)]

        except modelserver.ReferenceError:
            print "Unknown leg!"

    leg_assigned_rave = {}
    leg_booked_rave = {}
    default_bag = R.context('sp_crew').bag()
    for roster_bag in default_bag.iterators.roster_set():
        for leg_bag in roster_bag.iterators.leg_set(where='leg.%is_flight_duty% and not leg.%is_deadhead%'):
            leg = "%s+%s+%s" % (leg_bag.leg.udor().yyyymmdd()[:8], leg_bag.leg.flight_descriptor(), leg_bag.leg.start_station())
            if not leg in leg_booked_rave:
                leg_booked_rave[leg] = {}
                for i in range(0, 10):
                    leg_booked_rave[leg][i] = getattr(leg_bag, 'booked_crew_position_%s' % (i + 1))()

            if not leg in leg_assigned_rave:
                leg_assigned_rave[leg] = {}
                for i in range(0, 10):
                    leg_assigned_rave[leg][i] = getattr(leg_bag, 'assigned_crew_position_%s' % (i + 1))()
            else:
                for i in range(0, 10):
                    leg_assigned_rave[leg][i] += getattr(leg_bag, 'assigned_crew_position_%s' % (i + 1))()


    crr_bag = R.context('sp_crrs').bag()

    for leg_bag in crr_bag.iterators.leg_set(where='leg.%is_flight_duty% and not leg.%is_deadhead%'):
        leg = "%s+%s+%s" % (leg_bag.leg.udor().yyyymmdd()[:8], leg_bag.leg.flight_descriptor(), leg_bag.leg.start_station())
        if not leg in leg_booked_rave:
            leg_booked_rave[leg] = {}
            for i in range(0, 10):
                leg_booked_rave[leg][i] = getattr(leg_bag, 'booked_crew_position_%s' % (i + 1))()


    for leg in leg_booked:
        output = False
        for i in range(0, 10):
            if leg_booked.get(leg, {}).get(i, 0) != leg_booked_rave.get(leg, {}).get(i, 0) or leg_assigned.get(leg, {}).get(i, 0) != leg_assigned_rave.get(leg, {}).get(i, 0):
                output = True
                break

        if output:
            print "Info for leg %s" % leg
            print "pos\tbook (rave)\tass  (rave)"
            for i in range(0, 10):
                print "%s\t%s    (%s)\t%s    (%s)" % (i,
                                           leg_booked.get(leg, {}).get(i, 0),
                                           leg_booked_rave.get(leg, {}).get(i, 0),
                                           leg_assigned.get(leg, {}).get(i, 0),
                                           leg_assigned_rave.get(leg, {}).get(i, 0))
            contrib_trips = leg_trips.get(leg, None)
            if contrib_trips != None:
                print "trips with booking contributions:", ", ".join(contrib_trips)
            print "================================="

if __name__ == '__main__':
    main()
