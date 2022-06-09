#! /usr/bin/perl

use MQSeries;
use Benchmark;
use Time::HiRes qw(gettimeofday tv_interval);
use MIME::Base64;
sub print_help;

if (@ARGV[0] eq "--help") {
  print_help;
  exit 0;
}

$qmgr =  "";
$qsend =  "";
$qreply =  "";
$filename = "";
$host = "taramajima";
$port = "1415";
$channel = "SYSTEM.DEF.SVRCONN";
$altuser = "";
$async = 0;
$delay = 0;
$match = 1;
$onetoone = 1;
$syncpointput = 0;
while ($arg = shift) {
    if ($arg eq '-m' || $arg eq '--qmgr') {
        $qmgr = uc(shift);
    }
    elsif ($arg eq '-s' || $arg eq '--qsend') {
        $qsend = uc(shift);
    }
    elsif ($arg eq '-r' || $arg eq '--qreply') {
        $qreply = uc(shift);
    }
    elsif ($arg eq '-h' || $arg eq '--host') {
        $host = shift;
    }
    elsif ($arg eq '-p' || $arg eq '--port') {
        $port = uc(shift);
    }
    elsif ($arg eq '-c' || $arg eq '--channel') {
        $channel = uc(shift);
    }
    elsif ($arg eq '-a' || $arg eq '--altuser') {
        $altuser = shift;
    }
    elsif ($arg eq '-f' || $arg eq '--file') {
        $filename = shift;
    }
    elsif ($arg eq '-d' || $arg eq '--delay') {
        $delay = shift;
    }
    elsif ($arg eq '--async') {
        $async = 1;
    }
    elsif ($arg eq '-n' || $arg eq '--nomatch') {
        $match = 0;
    }
    elsif ($arg eq '--no11') {
        $onetoone = 0;
    }
    elsif ($arg eq '--syncpointput') {
        $syncpointput = 1;
    }
    else {
        print_help;
        exit(0);
    }
}
if ($async && $match && !$onetoone) {
    print "crlid match disabled when --async and --no11\n";
    $match = 0;
}

#
# read message data from file or stdin
#
if ($filename eq "") {
    while (defined($line=<STDIN>)) {
        $msg .= $line;
    }
}
else {
    open(SRC, "<$filename") or die ("Unable to open source file\n");
    while ($line = <SRC>) {
        $msg .= $line;
    }
    close(SRC);
}
@lines0 = split(/\n/,$msg);
# Skip comment lines
@lines = ();
foreach $line (@lines0) {
	if (!($line =~ /^#/)) {
		push(@lines,$line);
	}
}

#
# Connect QMGR
#
print "Connecting to qmgr $qmgr\n";
$hostport = "$host($port)";
$copts = { 'ChannelName' => $channel,
	'TransportType' => 'TCP',
	'ConnectionName' => $hostport,
	};
$conn =  MQCONNX( $qmgr, { 'ClientConn' => $copts }, $code, $reason);
if ($code ==  MQCC_FAILED){
  print STDERR "MQCONN failed: rc= $reason (".MQReasonToText($reason).")\n"; die;
}

#
# MQ setup
#
$od =  {MQOD_DEFAULT};
$od =  {
  ObjectName => $qsend,
};
$opt=  MQOO_OUTPUT | MQOO_FAIL_IF_QUIESCING | MQOO_BIND_AS_Q_DEF;

$od_reply =  {MQOD_DEFAULT};
$od_reply =  {
  ObjectName => $qreply,
};
$opt_reply= MQOO_INPUT_AS_Q_DEF | MQOO_FAIL_IF_QUIESCING;

if ($altuser ne "") {
   $od->{AlternateUserId} = $altuser;
   $od_reply->{AlternateUserId} = $altuser;
   $opt += MQOO_ALTERNATE_USER_AUTHORITY;
   $opt_reply += MQOO_ALTERNATE_USER_AUTHORITY;
}

#
# Open Queue for sending
#
$obj =  MQOPEN $conn, $od, $opt, $code, $reason;
if ($code ==  MQCC_FAILED){
  print STDERR "MQOPEN failed: rc= $reason (".MQReasonToText($reason).")\n"; die;
}

#
# Open Queue for reply
#
$obj_reply =  MQOPEN $conn, $od_reply, $opt_reply, $code, $reason;
if ($code ==  MQCC_FAILED){
  print STDERR "MQOPEN failed: rc= $reason (".MQReasonToText($reason).")\n"; die;
}

$gmo =  {MQGMO_DEFAULT};
$pmo =  {MQPMO_DEFAULT};
$md =  {MQMD_DEFAULT};
$md_reply =  {MQMD_DEFAULT};
$md =  {
    Encoding => MQENC_NATIVE,
    CodedCharSetId => MQCCSI_Q_MGR,
    ReplyToQ => $qreply,
    MsgType => MQMT_REQUEST,
    Report => MQRO_COPY_MSG_ID_TO_CORREL_ID,
};
$md_reply =  {
    Encoding => MQENC_NATIVE,
    CodedCharSetId => MQCCSI_Q_MGR,
};
$pmo =  {
  Options => MQPMO_NEW_MSG_ID | MQPMO_NEW_CORREL_ID,
};
if ($syncpointput) {
  $pmo{Options} += MQPMO_SYNCPOINT;
}
$gmo =  {
    Version => MQGMO_VERSION_2,
    Options => MQGMO_SYNCPOINT | MQGMO_WAIT | MQGMO_CONVERT | MQGMO_ACCEPT_TRUNCATED_MSG,
    WaitInterval => MQWI_UNLIMITED,
};
if ($match && !$async) {
    $gmo{MatchOptions} = MQMO_MATCH_CORREL_ID;
}

$t0 =  new Benchmark;

$nReq = 0;
$nRep = 0;
$nombretotaledellarequesti = @lines;
foreach $request (@lines) {
  $nReq++;
  #
  # Send mq-request
  #
  $trq0 = [gettimeofday];
  print "Sending message $nReq \n";
  MQPUT $conn ,$obj,$md ,$pmo,$request, $code, $reason;
  if ($code ==  MQCC_FAILED){
    print STDERR "MQPUT failed: rc= $reason (".MQReasonToText($reason).")\n"; die;
  }
  if ($syncpointput) {
    MQCMIT($conn,$code,$reason);
  }
  $crlid =  $md->{CorrelId};
  $crlidstr = encode_base64($crlid);
  chomp($crlidstr);
  $msgid =  $md->{MsgId};
  $msgidstr = encode_base64($msgid);
  chomp($msgidstr);
  push(@mids,$msgidstr);
  print "Sent msg with correlId= ".$crlidstr."\n";
  print "              msgId=    ".$msgidstr."\n";

  if (!$async) {
      #
      # Get reply message
      #
      readreply();
  }

  if ($delay && $nReq < $nombretotaledellarequesti) {
      sleep $delay;
  }
}

if ($async) {
    while (@mids) {
        readreply();
	if ($onetoone) {
            if ($nRep == $nReq) {
                last;
            }
        }
	if ($match) {
       	    $offset = 0;
            foreach $mid (@mids) {
                if ($mid eq $crlid_replystr) {
                    splice(@mids,$offset,1);
                }
	        $offset++;
            }
        }
    }
}
	
$t1 =  new Benchmark;
$tdiff =  timediff($t1,$t0);
print "\nTotal number of requests: $nReq\n";
print "Total number of replies: $nRep\n";
print "Total elapsed time: ", timestr($tdiff), "\n";

MQCLOSE($conn,$obj,$Copt,$code,$reason);
MQCLOSE($conn,$obj_reply,$Copt,$code,$reason);
MQDISC($conn,$code,$Reason);

sub readreply {
  print "\nWaiting for reply message ... \n";
  $md_reply =  {
    Encoding => MQENC_NATIVE,
    CodedCharSetId => MQCCSI_Q_MGR,
  };
  if ($match && !$async) {
      $md_reply{CorrelId} = $msgid;
  }
  $len= 1000000;  # message max length
  $mqmsg =  MQGET $conn, $obj_reply, $md_reply, $gmo, $len, $code, $reason;
  if ($code ==  MQCC_FAILED){
    print STDERR "MQGET failed: rc= $reason (".MQReasonToText($reason).")\n";
  }
  MQCMIT($conn,$code,$reason);
  $nRep++;
  $trq1 = [gettimeofday];
  $elapsed = tv_interval($trq0,$trq1);
  $elapsedStr = sprintf("%.06f",$elapsed);
  $crlid_reply =  $md_reply->{CorrelId};
  $crlid_replystr = encode_base64($crlid_reply);
  chomp($crlid_replystr);
  $msgid_reply =  $md_reply->{MsgId};
  $msgid_replystr = encode_base64($msgid_reply);
  chomp($msgid_replystr);
  print "Rcv. msg with correlId= ".$crlid_replystr."\n";
  print "              msgId=    ".$msgid_replystr."\n";
  if ($md_reply->{Format} ne MQFMT_STRING) {
      open(LOG, ">>mqrequest.out$nRep") or die "Failed open output file for binary msg\n";
      print LOG $mqmsg;
      close (LOG);
      print STDERR "Non-string message written to mqrequest.out$nRep\n";
  }
  else {
      print "=== Msg content === \n$mqmsg\n================== \n";
  }
  if ($reason == MQRC_TRUNCATED_MSG_ACCEPTED) {
      printf STDERR "The message was truncated. Actual size is $len bytes...\n";
  }
  print "Elapsed time: ", $elapsedStr, " (reply nr. $nRep)\n";
}


# Help text
sub print_help {
        printf STDOUT "#\n";
        printf STDOUT "# What:     Sends message on request queue and waits for response to\n";
        printf STDOUT "#           arrive on reply queue. Msgid and correlid are automatically\n";
        printf STDOUT "#           generated. Correlid of reply message is expected to correspond\n";
        printf STDOUT "#           to msgid of request message unless --nomatch is used.\n";
	printf STDOUT "#           Also, in asynchronous mode, reply messages are always read \n";
	printf STDOUT "#           regardless of correlid but if --nomatch is not used, the program \n";
	printf STDOUT "#           continues reading until one of each expected correlid has been read.\n";
        printf STDOUT "# Purpose:  Primarily to test MQ request-reply\n";
        printf STDOUT "# Name:     mqrequest.pl\n";
        printf STDOUT "# Ver:      2.2\n";
        printf STDOUT "# \n";
        printf STDOUT "# Args provided are:\n";
        printf STDOUT "#    --help         prints this text \n";
        printf STDOUT "#  -m | --qmgr      qmgr\n";
        printf STDOUT "#  -s | --qsend     queue to put request messages\n";
        printf STDOUT "#  -r | --qreply    queue to read reply messages\n";
        printf STDOUT "#  [-h | --host]    mq host name (Default taramajima)\n";
        printf STDOUT "#  [-p | --port]    mq port (Default 1415)\n";
        printf STDOUT "#  [-c | --channel] mq channel (Default SYSTEM.DEF.SVRCONN)\n";
        printf STDOUT "#  [-a | --altuser] mq altuser (Default '')\n";
        printf STDOUT "#  [-f | --file]    file to read request message. Default STDIN\n";
        printf STDOUT "#  [-d | --delay]   delay in seconds between requests\n";
        printf STDOUT "#  [-n | --nomatch] get any message regardless of correlid\n";
        printf STDOUT "#  [--async]        asynchronous mode\n";
        printf STDOUT "#  [--no11]         await possibly more than one reply\n";
	printf STDOUT "#                   per request in async mode.\n";
        printf STDOUT "#  [--syncpointput] put reply with syncpoint\n";
        printf STDOUT "#\n";
}

sub gettimestr {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst,$totsec,$microsec,$result);
	if (@$ == 0) {
		($totsec, $microsec) = gettimeofday;
	}
	else {
		$totsec = $_[0];
		$microsec = $_[1];
	}
	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($totsec);
	$result = sprintf("%04d-%02d-%02d %02d:%02d:%02d.%06d", $year + 1900, $mon + 1, $mday,$hour,$min,$sec,$microsec);
	return $result;
}
