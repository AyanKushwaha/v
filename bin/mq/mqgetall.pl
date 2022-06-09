#! /usr/bin/perl

use MQSeries;
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
$altuser = "";
$qmgr = "";
$queue = "";
$printit = 1;
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
  elsif ($arg eq '-d' || $arg eq '--discard') {
	  $printit = 0;
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
# Connect QMGR
#
$hostport = "$host($port)";
$copts = { 'ChannelName' => $channel,
	'TransportType' => 'TCP',
	'ConnectionName' => $hostport,
};
$conn = MQCONNX( $qmgr, { 'ClientConn' => $copts }, $code, $reason);
if ($code == MQCC_FAILED){
  print STDERR "MQCONN failed: rc=$reason (".MQReasonToText($reason).")\n"; die;
} elsif ($code == MQCC_WARN && $reason != 0) {
  print STDERR "MQCONN warning: rc=$reason (".MQReasonToText($reason).")\n";
}


#
# MQ setup
#
$opt=MQOO_INPUT_AS_Q_DEF | MQOO_FAIL_IF_QUIESCING | MQOO_BROWSE;

$od = {
  ObjectName => $queue,
};

if ($altuser ne "") {
  $od->{AlternateUserId} = $altuser;
  $opt |= MQOO_ALTERNATE_USER_AUTHORITY;
}

#
# Open queue
#
$obj = MQOPEN $conn, $od, $opt, $code, $reason;
if ($code == MQCC_FAILED){
  print STDERR "MQOPEN failed: rc=$reason (".MQReasonToText($reason).")\n";
  exit 1;
} elsif ($code == MQCC_WARN && $reason != 0) {
  print STDERR "MQOPEN warning: rc=$reason (".MQReasonToText($reason).")\n";
}

$nmsg = 0;
if (!$printit) {
  print STDOUT "\nWorking... ";
}
while (TRUE) {
#
# Browse queue in order to get message length
#
$gmo = {
  Version => MQGMO_VERSION_2,
  MatchOptions =>  MQMO_NONE,
  Options =>  MQGMO_CONVERT | MQGMO_ACCEPT_TRUNCATED_MSG| MQGMO_BROWSE_FIRST,
};
$md = {
  Encoding => MQENC_NATIVE,
  CodedCharSetId => MQCCSI_Q_MGR,
};

$len=0;       
$msg = MQGET $conn, $obj, $md, $gmo, $len, $code, $reason;
if($code == MQCC_FAILED and $reason != MQRC_NO_MSG_AVAILABLE) {
  print STDERR "MQGET failed: rc=$reason (".MQReasonToText($reason).")\n";
  exit 1;
} elsif ($code == MQCC_WARN && $reason != 0) {
  print STDERR "MQGET warning: rc=$reason (".MQReasonToText($reason).")\n";
}
if ($reason == MQRC_NO_MSG_AVAILABLE) {
  last;
}

#
# Get message
#
$gmo = {
  Version => MQGMO_VERSION_2,
  MatchOptions =>  MQMO_NONE,
  Options =>  MQGMO_SYNCPOINT | MQGMO_CONVERT | MQGMO_ACCEPT_TRUNCATED_MSG | MQGMO_MSG_UNDER_CURSOR ,
};
$md = {
  Encoding => MQENC_NATIVE,
  CodedCharSetId => MQCCSI_Q_MGR,
};

$msg = MQGET $conn, $obj, $md, $gmo, $len, $code, $reason;
if($code == MQCC_FAILED and $reason != MQRC_NO_MSG_AVAILABLE) {
  print STDERR "MQGET failed: rc=$reason (".MQReasonToText($reason).")\n";
  exit 1;
} elsif ($code == MQCC_WARN && $reason != 0) {
  print STDERR "MQGET warning: rc=$reason (".MQReasonToText($reason).")\n";
}
$nmsg++;
if ($nmsg % 100 == 0) {
  if (!$printit) {
    print STDOUT ".";
  }
  MQCMIT($conn,$code,$reason);
}

if ($printit) {
  if ($md->{Format} ne MQFMT_STRING) {
    open(LOG, ">>mqget.out") or die "Failed opening output file for binary msg\n";
    print LOG $msg;
    close (LOG);
    print STDERR "Non-string message stored in file mqget.out\n";
  }
  else {
    print STDOUT $msg;
    print STDOUT "\n";
  }
}
}

if ($nmsg == 0) {
  print STDERR "No message available...\n";
}
else { 
  print STDOUT "\n$nmsg messages found...\n";
}
$opt=0;
MQCMIT($conn,$code,$reason);
MQCLOSE($conn,$obj,$opt,$code,$reason);
MQDISC($conn,$CompCode,$reason);

exit 0;

# Help text
sub print_help {
        printf STDERR "#\n";
        printf STDERR "# What:     Get all messages from an MQ queue\n";
        printf STDERR "# Name:     mqgetall.pl\n";
        printf STDERR "# Ver:      1.0\n";
        printf STDERR "# \n";
        printf STDERR "# Args provided are:\n";
        printf STDERR "#    --help      prints this text \n";
        printf STDERR "#  -m|--qmgr qmgr  [queue manager]\n";
        printf STDERR "#  -q|--queue queue  [queue to read]\n";
        printf STDERR "# Optional params: \n";
	printf STDERR "#  -h|--host host  [MQ server host to connect to]\n";
	printf STDERR "#          default: taramajima\n";
	printf STDERR "#  -p|--port port  [MQ server port to connect to]\n";
	printf STDERR "#          default: 1415\n";
	printf STDERR "#  -c|--channel channel  [client channel]\n";
	printf STDERR "#          default: SYSTEM.DEF.SVRCONN\n";
	printf STDOUT "#  -a|--altuser altuser  [Alternate User Id]\n";
	printf STDOUT "#  -d|--discard  [Do not print messages]\n";
        printf STDERR "#\n";
}
