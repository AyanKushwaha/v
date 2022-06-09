#! /usr/bin/perl

use MQSeries;
use MIME::Base64;
sub print_help;

if ($ARGV[0] eq '--help'){
        print_help;
        exit 0;
}

if (@ARGV < 2) {
        print_help;
        exit 0;
}
$|++;

#
# Get arguments
#
$host = "taramajima";
$port = "1415";
$channel = "SYSTEM.DEF.SVRCONN";
$qmgr = "";
$queue = "";
$altuser = "";
$maxlen = 4194304;
$file = "";
while ($arg = shift) {
  if ($arg eq '-m' || $arg eq '--qmgr') {
	$qmgr = uc(shift);
  }
  elsif ($arg eq '-q' || $arg eq '--queue') {
	$queue = uc(shift);
  }
  elsif ($arg eq '-h' || $arg eq '--host') {
	$host = shift;
  }
  elsif ($arg eq '-p' || $arg eq '--port') {
	$port = shift;
  }
  elsif ($arg eq '-c' || $arg eq '--channel') {
	$channel = shift;
  }
  elsif ($arg eq '-a' || $arg eq '--altuser') {
	$altuser = shift;
  }
  elsif ($arg eq '-l' || $arg eq '--maxlen') {
	$maxlen = shift;
  }
  elsif ($arg eq '-f' || $arg eq '--file') {
	$file = shift;
  }
  else {
    print_help;
    exit 0;
  }
}
if ($qmgr eq "" || $queue eq "") {
	print_help;
	exit 0;
}

#
# Get message
#
$msg = "";
if ($file eq "") {
   # Read from file
   while (defined($line=<STDIN>)) {
      $msg .= $line;
   }
}
else {
   # Read from stdin
   open(SRC, $file) or die ("Unable to open source file\n");
   while ($line = <SRC>) {
      $msg .= $line;
   }
   close(SRC);
}

#
# Connect QMGR
#
$hostport = "$host($port)";
$copts = { 'ChannelName' => $channel,
        'TransportType' => 'TCP',
	'MaxMsgLength' => $maxlen,
                'ConnectionName' => $hostport,
};
$conn = MQCONNX( $qmgr, { 'ClientConn' => $copts }, $code, $reason);
die MQReasonToText($reason) if $code == MQCC_FAILED;

#
# MQ setup
#

if ($altuser eq "") {
   $od = {
	ObjectName => $queue,
   };
   $opt=MQOO_OUTPUT | MQOO_FAIL_IF_QUIESCING;
}
else {
   $od = {
	ObjectName => $queue,
	AlternateUserId => $altuser,
   };
   $opt=MQOO_OUTPUT | MQOO_FAIL_IF_QUIESCING | MQOO_ALTERNATE_USER_AUTHORITY;
}

$pmo = {
   Options => MQPMO_NEW_MSG_ID | MQPMO_NEW_CORREL_ID,
};

$md = {
   Encoding => MQENC_NATIVE,
   CodedCharSetId => 819,
   MsgType => MQMT_DATAGRAM,
   Format => MQFMT_STRING,
};

#
# Open queue
#
$obj = MQOPEN $conn, $od, $opt, $code, $reason;
die MQReasonToText($reason) if $code == MQCC_FAILED;

#
# Put Message
#
MQPUT $conn, $obj, $md, $pmo, $msg, $code, $reason;
die $reason,MQReasonToText($reason) if $code == MQCC_FAILED;
       
$opt=0;
MQCLOSE($conn,$obj,$opt,$code,$reason);
MQDISC($conn,$CompCode,$Reason);

# Help text
sub print_help {
        printf STDOUT "#\n";
        printf STDOUT "# What:     Put a message on an MQ queue\n";
	printf STDOUT "#           Takes input from STDIN by default\n";
        printf STDOUT "# Name:     mqput.pl\n";
        printf STDOUT "# Ver:      1.1\n";
        printf STDOUT "# \n";
        printf STDOUT "# Args provided are:\n";
        printf STDOUT "#    --help      prints this text \n";
	printf STDOUT "#  -m|--qmgr qmgr  [queue manager]\n";
	printf STDOUT "#  -q|--queue queue  [queue to read]\n";
        printf STDOUT "# Optional params: \n";
	printf STDOUT "#  -h|--host host  [MQ server host to connect to]\n";
	printf STDOUT "#          default: taramajima\n";
	printf STDOUT "#  -p|--port port  [MQ server port to connect to]\n";
	printf STDOUT "#          default: 1415\n";
	printf STDOUT "#  -c|--channel channel  [client channel]\n";
	printf STDOUT "#          default: SYSTEM.DEF.SVRCONN\n";
        printf STDOUT "#  -a|--altuser altuser  [Alternate User Id]\n";
        printf STDOUT "#  -l|--maxlen bytes  [Default 4194304]\n";
        printf STDOUT "#  -f|--file filename  [Read message from file]\n";
        printf STDOUT "#\n";
}
