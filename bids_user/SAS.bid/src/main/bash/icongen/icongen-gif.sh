#!/bin/sh

# BASEDIR points to the project home folder
BASEDIR="../../webapp/"
if [ -d "${BASEDIR}" ] ; then
	ALL="is well"
else
	BASEDIR="result/"
fi
IMGDIR="${BASEDIR}img/gen/"
CSSDIR="${BASEDIR}css/"
CSSFILE="${CSSDIR}generated-gif.css"

IMAGEMAGICK=`which composite`
if [ -z "${IMAGEMAGICK}" ] ; then
	echo "Can't find ImageMagick command composite (which composite), aborting."
	exit 1
fi
COMMAND="${IMAGEMAGICK} -compose over "

# delete previous data
if [ -d "${IMGDIR}" ] ; then
	echo -n "Cleaning up output directory ${IMGDIR}:"
	rm ${IMGDIR}/*.gif 2> /dev/null
	echo "done"
	echo
else
	echo -n "Creating output directory ${IMGDIR}:"
	mkdir -p "${IMGDIR}"
	echo "done"
	echo
fi
if [ -d "${CSSDIR}" ] ; then
	rm ${CSSFILE} 2> /dev/null
else 
	mkdir -p "${CSSDIR}"
fi

# work with each base icon
for i in `ls -1 base-*.png 2> /dev/null` ; do

	BASE=`echo $i | sed -e 's/base-//;s/\.png//'`
	CSS_BASE='generated'
	echo -n "Working with $BASE:" 

	convert $i "${IMGDIR}${BASE}.gif";
	cp $i "${IMGDIR}${BASE}.png";
	echo ".${BASE} { background-image: url(../img/gen/${BASE}.gif) !important; }" >> "${CSSFILE}"
	echo -n " base"
	
	# create base+left overlay combinations
	for l in overlay-left*.png; do
		LEFT=`echo $l | sed -e 's/overlay-left-//' | sed -e 's/\.png//'`

		$COMMAND $l $i "${IMGDIR}${BASE}-${LEFT}.gif"
		echo ".${BASE}-${LEFT} { background-image: url(../img/gen/${BASE}-${LEFT}.gif); }" >> "${CSSFILE}"
		echo -n " $LEFT"
	done;

	# create base+right overlay combinations
	for r in overlay-right*.png; do
		RIGHT=`echo $r | sed -e 's/overlay-right-//' | sed -e 's/\.png//'`

		$COMMAND $r $i "${IMGDIR}${BASE}-${RIGHT}.gif"
		echo ".${BASE}-${RIGHT} { background-image: url(../img/gen/${BASE}-${RIGHT}.gif); }" >> "${CSSFILE}"
	#	echo "right" >> "css/${CSS_BASE}.css"
		echo -n " $RIGHT"
	done;

	echo "."
done

# create base+left+right combinations
for l in overlay-left*.png; do
	LEFT=`echo $l | sed -e 's/overlay-left-//' | sed -e 's/\.png//'`
	for r in overlay-right*.png; do
		RIGHT=`echo $r | sed -e 's/overlay-right-//' | sed -e 's/\.png//'`

		# combine left+right
		echo "Working with ${LEFT}-${RIGHT}:"
		TMP="${IMGDIR}temp-${LEFT}-${RIGHT}.png"
		$COMMAND $r $l $TMP

		# combine with base
		for i in base-*.png ; do

			BASE=`echo $i | sed -e 's/base-//;s/\.png//'`
			CSS_BASE=`echo $BASE | cut -d '-' -f 1`
			CSS_BASE='generated'

			echo -n " $BASE"
			$COMMAND $TMP $i "${IMGDIR}${BASE}-${LEFT}-${RIGHT}.gif"
			echo ".${BASE}-${LEFT}-${RIGHT} { background-image: url(../img/gen/${BASE}-${LEFT}-${RIGHT}.gif); }" >> "${CSSFILE}"
		done
		echo "."

		rm $TMP
	done
done

echo -n "Finalizing CSS file:"
	BKP="${CSSFILE}.bkp"
	sort ${CSSFILE} > ${BKP}
	rm ${CSSFILE}
	
	# make 22px space for the icon
	cat ${BKP} | sed -e 's/ {/ ,{/' | cut -d '{' -f 1 >> ${CSSFILE};
	echo ".class-summary { padding-left: 22px; background: transparent url(../img/empty.gif) no-repeat scroll 0% 50%; }" >> ${CSSFILE};
	echo "" >> ${CSSFILE};
	
	# but remove 21px space for icon menu items
	cat ${BKP} | sed -e 's/ {/ ,{/' | sed -e 's/\./.x-menu-list ./' | cut -d '{' -f 1 >> ${CSSFILE};
	echo ".x-menu-list .class-summary { padding-left: 1px; }" >> ${CSSFILE};
	echo "" >> ${CSSFILE};
	
	# last but not least, add all image paths to the final result 
	cat ${BKP} >> ${CSSFILE}
	rm ${BKP}
echo " done."
