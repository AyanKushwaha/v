/* -*- crg -*- */

cost_elements:
box
  repeat 100 times;
  make
    if trip_cost.%element_exist%(index(1), index) then
      name: text 30x1 "%D", trip_cost.%element_name%(index(1), index);
      cost: text 15x1 RIGHT "%D", trip_cost.%total_element_cost%(index(1), index);
      element: row name, cost, *;
    end
  relate
    if trip_cost.%element_exist%(index(1), index) then
      column +element, element;
    end
  end

  column -+element;
end

cost_sections:
box
  repeat 100 times;
  make
    if trip_cost.%section_exist%(index) then
      name: text 30x1 "%D", trip_cost.%section_name%(index);
      cost: text 15x1 RIGHT "%D", trip_cost.%total_section_cost%(index);

      section_header: row name, cost, *;
      section_elements: box cost_elements;

      cost_section: 
        column section_header, !,
               section_elements,
               (text 1x1 "");
    end
  relate
    if trip_cost.%section_exist%(index) then
      column +cost_section, page, cost_section;
    end
  end
end

cost_overview:
box
    repeat 100 times;
    make
    if trip_cost.%section_exist%(index) then
      name: text 30x1 "%D", trip_cost.%section_name%(index);
      cost: text 15x1 RIGHT "%D", trip_cost.%total_section_cost%(index);

      section_header: row name, cost, *;
    end
  relate
    if trip_cost.%section_exist_ix% then
      column +section_header, page, section_header;
    end
  end

  header: text 30x1 "TOTAL COSTS";
  total:  text 15x1 RIGHT "%D", trip_cost.%total_trip_total_cost%;
  header_row: row header, total, *;


  column header_row, !, -+section_header;
end

apc_costs:
box
  repeat foreach default_context;
  make  
    column (box cost_overview), 
           (text 2x2 ""),
           (box cost_sections);
  end
end
