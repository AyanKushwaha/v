# awk program.

BEGIN {
 FS = "[;,]"
 OFS= ","
 print "4"
 print "SBase,"
 print "ASBdate,"
 print "Iupper,"
 print "Ilower,"
 basePat = "CPH|ARN|STO|OSL|STV|TRD"

}

#main calls
$1 ~ basePat && (length($1) > 0) {
    if ((NF == 4)) {
      print "\""$1"\"", $2, $3, $4+0, ""
    }
}


#############
# util functions
#############

function formatDate(iDate) {
  cmd ="date \"+%d%b%Y\" -d \""iDate"\""
  cmd | getline var
  return var
}
function isempNo(empNo) {
  print empNo, empNoPat
  return empNo ~ /^[0-9]{5}/
}

function getCode(code, desc) {
  match(code,/[ ]/)
  type = substr(code, 1, RSTART-1)
  if (type == "LA"){
    match(desc,/LA[0-9]+/)
    if (RSTART > 0){
      type = trim(substr(desc, RSTART, 4))
    }
  }
  return type
}

function ltrim(s) { gsub(/^[( .]+/, "", s); return s }
function rtrim(s) { gsub(/[) .]+$/, "", s); return s }
function trim(s)  { return rtrim(ltrim(s)); }

function convertToBool(code) {
  if (length(code) > 2) {
    return code
  } else {
    return "FALSE"
  }
}