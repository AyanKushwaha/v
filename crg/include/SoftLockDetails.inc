/* -*- crg -*- */

options
  text = noframe fixed;
  ascii = asctrimpage;
  ascwidth = 1000;
end

leg_details:
box
  repeat soft_locks.%table_nr_of_rows% times;
  make
    if not (studio_soft_locks.%one_row_desc%(index) = "Leg mismatch") then
      t_left: text "  %s", studio_soft_locks.%one_row_desc%(index);
    else
      text 1x1 "";
    end
  relate
    column  +t_left, t_left;
  empty
    text "...";
  end
  l: column -+t_left;
end

leg_result:
box
  repeat soft_locks.%table_nr_of_rows% times;
  make
    if not (studio_soft_locks.%one_row_desc%(index) = "Leg mismatch") then
      t_right: text "%s (row %2d)", studio_soft_locks.%one_row_desc_result%(index), index;
    else
      text 1x1 "";
    end
  relate
    column  +t_right, t_right;
  empty
    text "...";
  end
  r: column -+t_right;
end

trip_details:
box
  repeat foreach soft_locks.sl_leg_set;
  where studio_soft_locks.%leg_has_soft_lock%;
  make
    leg_box: column
      !, (row
        (text left "%s%d %s-%s (leg %d)", flight_carrier, flight_number, departure_airport_name, arrival_airport_name, soft_locks.%leg_pos_in_trip%)
      ), !,
      (row (text bold "  SoftLock"), *, (text bold "Penalty         ")),
      (row (box leg_details), *, (box leg_result));
  relate
    column  +leg_box, page, leg_box;
  empty
    text "No SoftLocks in trip";
  end
  t: column -+leg_box;
end

box
    repeat foreach marked_in_window_main;
    where studio_soft_locks.%trip_has_soft_lock%;
    make
        trip_box: column
            (box trip_details),page,(text noframe 1x1 "");
    relate
        column +trip_box, page, trip_box;
    empty
        text "No Soft Locks on selected trips";
    end

    column [left]
    -+trip_box,
    (tag "EndOfReport");
end
