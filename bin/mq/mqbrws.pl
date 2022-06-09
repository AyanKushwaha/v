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
$altuser = "";
$qmgr = "";
$queue = "";
$timeout = 0;
$buflen = 32768;
$showmsgid = 0;
while ($arg = shift) {
  if ($arg eq '-t' || $arg eq '--timeout') {
	$timeout = shift;
	$timeout *= 1000;
  }
  elsif ($arg eq '-l' || $arg eq '--buflen') {
	$buflen = shift;
  }
  elsif ($arg eq '-v' || $arg eq '--dspid') {
	$showmsgid = 1;
  }
  elsif ($arg eq '-m' || $arg eq '--qmgr') {
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
die MQReasonToText($reason) if $code == MQCC_FAILED;

#
# MQ setup
#
if ($altuser eq "") {
   $od = {
        ObjectName => $queue,
   };
   $opt=MQOO_INPUT_AS_Q_DEF | MQOO_FAIL_IF_QUIESCING | MQOO_BROWSE;
}
else {
   $od = {
        ObjectName => $queue,
        AlternateUserId => $altuser,
   };
   $opt=MQOO_INPUT_AS_Q_DEF | MQOO_FAIL_IF_QUIESCING | MQOO_BROWSE | MQOO_ALTERNATE_USER_AUTHORITY;
}

#
# Open queue
#
$obj = MQOPEN $conn, $od, $opt, $code, $reason;
die MQReasonToText($reason) if $code == MQCC_FAILED;

                                                                                       
$nMsg = 0;
while($code != MQCC_FAILED){

        #
        # Set browse parameters
        #
        if ($timeout == 0) {
                $gmo = {
                Version => MQGMO_VERSION_2,
                MatchOptions =>  MQMO_NONE,
                Options => MQGMO_CONVERT | MQGMO_BROWSE_NEXT | MQGMO_ACCEPT_TRUNCATED_MSG,
                };
        }
        else {
                $gmo = {
                Version => MQGMO_VERSION_2,
                MatchOptions =>  MQMO_NONE,
                Options => MQGMO_CONVERT | MQGMO_WAIT | MQGMO_BROWSE_NEXT | MQGMO_ACCEPT_TRUNCATED_MSG,
                WaitInterval => $timeout,
                };
        }

        $md = {
                Encoding => MQENC_NATIVE,
                CodedCharSetId => MQCCSI_Q_MGR,
              };
       
        #
        # Browse queue
        #
        $len = $buflen;
        $msg = MQGET $conn, $obj, $md, $gmo, $len, $code, $reason;
        die MQReasonToText($reason) if $code == MQCC_FAILED && $reason != MQRC_NO_MSG_AVAILABLE;
       
        #
        # If no more messages...
        #
        if($reason == MQRC_NO_MSG_AVAILABLE){
		last;
        }
        $nMsg++;

        if ($showmsgid) {
                $msgid = encode_base64($md->{MsgId});
                $crlid = encode_base64($md->{CorrelId});
                chomp($msgid);
                chomp($crlid);
                print STDERR "---------- message id: " . $msgid . " -----------------------\n";
                print STDERR "---------- correl id:  " . $crlid . " -----------------------\n";
        }
	if ($md->{Format} ne MQFMT_STRING) {
		open(LOG, ">>mqbrws.out$nMsg") or die "Failed open output file for binary msg\n";
		print LOG $msg;
		close (LOG);
		print STDERR "Non-string message written to mqbrws.out$nMsg\n";
	}
	else {
       		print STDOUT $msg;
		print STDERR "\n";
	}
	if ($reason == MQRC_TRUNCATED_MSG_ACCEPTED) {
		printf STDERR "The message was truncated. Actual size is $len bytes...\n";
	}


}

$opt=0;
MQCLOSE($conn,$obj,$opt,$code,$reason);
MQDISC($conn,$CompCode,$Reason);
printf STDERR "\n $nMsg messages found\n";

# Help text
sub print_help {
        printf STDOUT "#\n";
        printf STDOUT "# What:     Browse contents of an MQ queue\n";
        printf STDOUT "# Name:     mqbrws.pl\n";
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
        printf STDOUT "#  -t|--timeout timeout  [wait for timeout seconds]\n";
        printf STDOUT "#  -l|--buflen bytes  [Max length, truncated if longer]\n";
	printf STDOUT "#          default: 32786\n";
        printf STDOUT "#  -v|--dspid  [Display message id (base64 encoded)]\n";
        printf STDOUT "#\n";
}
