icongen - generation of image combinations and accompanying css classes

The purpose of the script is to ease the burden of icon creation.
It uses ImageMagick to combine all "base" icons with all "layover" icons in the current directory
and creates all combinations possible.

A bid icon should be 16x16 pixels. 
The name of the icon must be base-{bidtype}.gif for IE6 and base-{bidtype}.png for all other browsers.
The files must be placed in the icongen directory prior to running the scripts.

Step by step guide:
	1. You need to copy the icongen folder to a Unix machine that has ImageMagick 6.1 or above installed.
	2. If you copied the folder from a windows machine run:
		dos2unix icongen.sh
		dos2unix icongen-gif.sh
	3. Run the scripts on the unix machine. 
   	   The output will be in the result directory.
	4. Copy the resulting css files to your css directory.
	5. Copy the resulting gen directory to your img directory.
	6. You will need to refresh you img directory in eclipse for the new images to be shown in the GUI.

	
Troubleshooting:
	1. l you get error message: "./icongen.sh: Command not found."
	   This is because windows uses \r\n for newlines and unix only \n. To fix this run:
	   dos2unix icongen.sh 
	2. If the images look real crappy or if you get strange messages from the convert commands:
	   Make sure you use a recent version of ImageMagick, should at least be 6.1. To test this run:
	   convert -version
	   You will get an output like "Version:  ImageMagick 6.2.8 ..."


Example Usage: The simple case

Consider the following contents:

  src/main/bash/icongen/
    '--  base-folder.png
	'--  overlay-left-submitted.png
	'--  overlay-right-warning.png
	'--  overlay-right-error.png

When running icongen.sh this will produce:

  src/main/webapp/
    '-- img/gen/
	   '-- folder.png
	   '-- folder-error.png
	   '-- folder-warning.png
	   '-- folder-submitted.png
	   '-- folder-submitted-error.png
	   '-- folder-submitted-warning.png
    '-- css/
	   '-- generated.css

The CSS file looks like:

	.folder,
	.folder-error,
	.folder-warning,
	.folder-submitted,
	.folder-submitted-error,
	.folder-submitted-warning,
	.class-summary { /* this line is here just to ease the CSS generation step */
		padding-left: 22px;
		background: transparent url(../img/s.gif) no-repeat 0% 50%;
	}
	.folder { background-image: url(../img/gen/folder.png) !important }
	.folder-error { background-image: url(../img/gen/folder-error.png) !important }
	.folder-warning { background-image: url(../img/gen/folder-warning.png) !important }
	.folder-submitted { background-image: url(../img/gen/folder-submitted.png) !important }
	.folder-submitted-error { background-image: url(../img/gen/folder-submitted-error.png) !important }
	.folder-submitted-warning { background-image: url(../img/gen/folder-submitted-warning.png) !important }


 