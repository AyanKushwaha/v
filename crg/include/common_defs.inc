/* -*- crg -*- */

options
fontdef headerfont14 = swiss 14;
fontdef headerfont8 = swiss 8;
fontdef headerfont8b = swiss bold 8;
  fontdef roman8 = roman 8;
  fontdef roman7 = roman 7;
  fontdef roman7b = roman bold 7;
  fontdef roman7i = roman italic 7;
  fontdef roman6 = roman 6;
  fontdef roman6i = roman italic 6;
  fontdef roman5 = roman 5;
  fontdef roman4 = roman 4;
  fontdef roman3 = roman 3;
  fontdef swiss5 = swiss 5;
  fontdef swiss5b = swiss bold 5;
end

light_grey_bg_char: bitmap
9x20
<44440000111100004444000011110000444400001111000044440000111100004444000011110000>
end

dark_grey: bitmap
8x8 
<55aa55aa55aa55aa>
end


define(PADSMALL,(text noframe novspace ""))
define(PAD,(text noframe 0 vspace ""))
define(PADFULL,(text noframe " "))

define(HTEXT,text bold vspace)

