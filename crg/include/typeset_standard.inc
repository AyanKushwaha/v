/* -*- crg -*- */

define(ASCII_VERSION,false)
ifdef({USE_CARMEN_LOGO},,{define(USE_CARMEN_LOGO,false)})
include(CRGInclude/common_defs.inc)

include(CRGInclude/carmen_logo.inc)
include(CRGInclude/customer_logo.inc)
include(CRGInclude/sas_logo.inc)

options
  hstretch = 100;
  fstretch = 100;
  text = noframe prop novspace;
  papersize = sizea4; /* In US: sizeletter */
end

header:
box
   repeat foreach default_context;
   make
      r0: row (text headerfont14 bold "%s", NameOfReport),*,(bitmap sas_logo);
      r1: row (text nospace headerfont8 "%s", 
	       if is_dated_mode then "Planning Period:" else "Standard Period:"),
	  (text nospace headerfont8b "%s  ", crg_date.%print_pp%),
	  (text nospace headerfont8 "Rule Set:"),
	  (text nospace headerfont8b "%s  ", rule_set_name),
	  (text nospace headerfont8 "Plan:"),
	  (text nospace headerfont8b "%s/%s/%s/%s  ", fp_name,fp_version,lp_name,sp_name),*;
      if crg_comment <> "" then
      r2: row (text nospace headerfont8 "Comment:"),(text headerfont8b max 80x2 wbreak "%s", crg_comment),*;
      end
      
      hd0: column r0,r1,r2;
      column hd0, PAD, !!;

   end
end

footer:
box
  if USE_CARMEN_LOGO then
     clogo: column (row *,(bitmap carmen_logo)), PAD, !!, PAD;
  else 
  clogo: column PAD, !!, PAD;
  end    
  column clogo,
         (row (text headerfont8 "Created %s by %s", crg_date.%now_abs%, user),
               *, 
	  (text headerfont8 "%p (%t)","EndOfReport"));
end

options
  text = noframe fixed novspace;
end
