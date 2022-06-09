#!/bin/env perl
# @(#) $Header: /opt/Carmen/CVS/sk_cms_user/bin/mqcapture.pl,v 1.5 2007/05/08 11:21:27 acosta Exp $
#
# Uses MQSeries to fetch messages from a queue and write the sequentially to a
# file with a separating header line.
#
# DIG's 'sklogfilter' keeps a timestamp of the time when the message was read
# from the queue, not when it was put there, something this script tries to
# correct.
#
# changelog {{{2
# [acosta:07/038@15:09] First version
# [acosta:07/053@09:56] Roland updated 'altuser', on site installation this
#          row might be useful (MQ not installed as 'root'):
#          use lib qw(/users/ade409/perl/lib64/perl5 /users/ade409/perl/lib64/perl5/site_perl);
# }}}


# imports ================================================================{{{1
use strict;
use warnings;

use Getopt::Long;
use Pod::Usage;

use MQSeries qw(:functions);
use MQSeries::QueueManager;
use MQSeries::Queue;
use MQSeries::Message;

# Force flush of output buffer (default value of $| is 0).
$|++;

my $ver = q($Revision: 1.5 $);
($::VERSION) = ($ver =~ /\$\S+: (\S+) \$/);

# Get basename of this script
my $script = ($0 =~ m#/?([^/]+)$#)[0];
my $usage = "\t$script -help, for help.";


# subroutines ============================================================{{{1

# feedback ---------------------------------------------------------------{{{2
# For error messages
# NOTE: We will bail out for warnings too, that is intended.
sub feedback {
	my ($msg, $obj) = @_; 
    my $c = $obj->CompCode();
    my $r = $obj->Reason();
    my $rc = "$script: ";

	my ($text, $macro) = MQReasonToStrings($r);
	if ($c == MQSeries::MQCC_WARNING) {
		$rc .= "WARNING:";
	} elsif ($c == MQSeries::MQCC_FAILED) {
		$rc .= "ERROR:";
	} else {
		$rc .= "UNKNOWN:";
	}
	return $rc . " $msg (Completion code = $c).\n\t$macro: $text (Reason = $r).\n\tStopped";
}


# missing ----------------------------------------------------------------{{{2
sub missing {
    my (@opts) = @_;
    my $s;
    $s = ($#opts > 0) ? "s" : "";
    return "$script: ERROR: The option$s '" . join("', '", @opts) . "' must be specified.\n" .
        "$usage\n\tStopped";
}


# main ==================================================================={{{1
our $opt_altuser = '';
our $opt_channel = 'SYSTEM.DEF.SVRCONN';
our $opt_manager = '';
our $opt_queue = '';
our $opt_host = '';
our $opt_output = '';
our $opt_port = 1414;
our ($verbose, $help, $man);
our $wait = 1;

# Some options are undocumented :-)
our $msgs_per_mark = 100;
our $msgs_per_row = 5000;

GetOptions(
    'altuser=s',
    'channel=s',
    'host=s',
    'manager=s',
    'output=s',
    'port=i',
    'queue=s',
    'verbose!' => \$verbose,
    'wait!' => \$wait,
    'help|?' => \$help,
    'man' => \$man,
    'msgs_per_mark' => \$msgs_per_mark,
    'msgs_per_row' => \$msgs_per_row,
) or pod2usage(2);

pod2usage(1) if $help;
pod2usage(-exitstatus => 0, -verbose => 2) if $man;

print STDERR "$script - version $::VERSION.\n" if $verbose;

my @missing_options = (); 
push @missing_options, "host" unless $opt_host;
push @missing_options, "manager" unless $opt_manager;
push @missing_options, "queue" unless $opt_queue;
die missing(@missing_options) if @missing_options;

# Open output file or redirect output to stdout.
if ($opt_output) {
    open(OUTPUT, ">>$opt_output")
        or die "$script: ERROR: Could not open file '$opt_output'.\n\tStopped";
    print STDERR "$script: NOTE: Will put output in file '$opt_output'.\n" if $verbose;
} else {
    open(OUTPUT, ">-")
        or die "$script: ERROR: Could not open 'stdout'.\n\tStopped";
    print STDERR "$script: NOTE: output will go to stdout.\n" if $verbose;
}

my $qmgr = MQSeries::QueueManager->new(
    QueueManager => $opt_manager,
    AutoConnect => 0,
    ClientConn => {
        ChannelName => $opt_channel,
        ConnectionName => "$opt_host($opt_port)",
    },
) or die "$script: ERROR: Unable to instantiate MQSeries::QueueManager object.\n\tStopped";

$qmgr->Connect() or die feedback("Cannot connect to QueueManager $opt_manager.", $qmgr);

my $queue = ($opt_altuser)
    ? MQSeries::Queue->new(
        QueueManager => $qmgr,
        Options => MQSeries::MQOO_INPUT_AS_Q_DEF | MQSeries::MQOO_FAIL_IF_QUIESCING
            | MQSeries::MQOO_ALTERNATE_USER_AUTHORITY,
        ObjDesc => {
            AlternateUserId => $opt_altuser,
            ObjectName => $opt_queue,
            ObjectType => MQSeries::MQOT_Q
        })
    : MQSeries::Queue->new(
        QueueManager => $qmgr,
        Queue => $opt_queue,
        Mode => 'input',
    )
    or die "$script: ERROR: Unable to open queue $opt_queue.\n\tStopped";

print STDERR "$script: NOTE: Connected to $opt_manager, queue $opt_queue.\n" .
    "\tWaiting for messages ($msgs_per_mark messages per marker).\n\tCapturing:  "
    if $verbose;

my $wait_time = ($wait) ? MQSeries::MQWI_UNLIMITED : 1000;
my $counter;

for ($counter = 1;; $counter++) {
    my $msgobj = MQSeries::Message -> new();

    $queue->Get(Message => $msgobj, Sync => 1, Wait => $wait_time)
        or die feedback("Unable to get message from queue $opt_queue.", $queue);
    
    if ($queue->CompCode()) {
        print STDERR "\n" if $verbose;
        last if !$wait && $queue->Reason() == 2033; # MQRC_NO_MSG_AVAILABLE
        die feedback("Could not get message data", $queue);
    }

    my $data = $msgobj->Data();

    my ($yy, $mm, $dd) =  ($msgobj->MsgDesc('PutDate') =~ /^(....)(..)(..)/);
    my ($HH, $MM, $SS) =  ($msgobj->MsgDesc('PutTime') =~ /^(..)(..)(..)/);

    print OUTPUT "SKLogEntry;$yy-$mm-${dd}T$HH:$MM:$SS\n$data\n"
        and ($qmgr->Commit() or die feedback("Could not commit.", $qmgr));

    print STDERR "." if $verbose and ($counter % $msgs_per_mark == 0);
    printf(STDERR "   (%06d)\n\tCapturing:  ", $counter) if $verbose and ($counter % $msgs_per_row == 0);
}

close OUTPUT if $opt_output;
print STDERR "$script: NOTE: Leaving.\n" if $verbose;
    
__END__


# pod ===================================================================={{{2

=head1 NAME

mqcapture.pl - Capture messages from Message Queue to file.

Each message will have a header with a timestamp (the time and date when the
message was placed on the queue).

=head1 SYNOPSIS

B<mqcapture.pl> B<-host> I<host> B<-manager> I<manager> B<-queue> I<queue> [options] 

options:
    B<-altuser> I<altuser>
    B<-channel> I<channel>
    B<-port> I<port>
    B<-output> I<output_file>
    B<-verbose>
    B<-nowait>
    B<-help>|B<-?>
    B<-man>

=head1 OPTIONS

=over 8

=item B<-host> I<host>

Use MQ Manager on I<host>. Mandatory option, no default value.

=item B<-manager> I<manager>

Use this MQ manager. Mandatory option, no default value.

=item B<-queue> I<queue>

Read messages from the Message Queue I<queue>. Mandatory option, no default
value.

=item B<-altuser> I<altuser>

Use the alternate user ID I<altuser> for opening the queue.

=item B<-channel> I<channel>

Use this channel. The default value is I<SYSTEM.DEF.SVRCONN>.

=item B<-port> I<port>

Use this port for the connection, the default value is I<1414>.

=item B<-output> I<output_file>

Print output to file I<output_file>. If no output file is specified, the
program will write to I<stdout>.

=item B<-verbose>

Print progress information to I<stderr>. The opposite option B<-noverbose> is
enabled by default.

=item B<-nowait>

If this options is given, the program will not wait for more messages after the
queue is exhausted. The default behaviour is to use B<-wait> (wait for unlimited time).

=item B<-help> |  B<-?>

Prints a brief help message and exits. B<-?> is a synonym for B<-help>.

=item B<-man>

Prints the manual page and exits.

=back

=head1 DESCRIPTION

B<mqcapture.pl> will get messages from a IBM MQSeries message queue and append
them to an output file (or to I<stdout> if no output file was specified).

Each message will start with a header that contains a timestamp. The time
displayed is the time and date the message was placed on the queue.

=cut


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
