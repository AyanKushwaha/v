#!/bin/env perl
# $Header$
#
# Tool to visualize dependencies between menus.
#

use strict;
use warnings;

# Global variables ======================================================={{{1
my $all = 0;
my $debug = 0;
my $max_reclevel = 100;
my %menunames;
my @menus;
my $reclevel = 0;
my %referred_from;
my %refers_to;

# Functions =============================================================={{{1

# scanfile($filename) ----------------------------------------------------{{{2
sub scanfile {
    my $fn = shift;
    local *FH;
    open(FH, "<$fn") or do {
        warn "Can't open $fn";
        return;
    };
    my $currmenu;
    my @localmenu;
    while (<FH>) {
        /^\s*Menu\s+(\S+)/ && do {
            $currmenu = $1;
            push @menus, $currmenu;
        };
        /f\.menu\s+(.+)/ && do {
            push @localmenu, $1;
            push @{ $referred_from{$currmenu} }, $1;
            push @{ $refers_to{$1} }, $currmenu;
            print "got menu $1\n" if $debug;
        };
        /^\s*(.*)\s+f\.title/ && do {
            $menunames{$currmenu} = $1;
            print "got title $1\n" if $debug;
        };
        /^include -\s+(\S+)/ && do {
            scanfile($1);
        };
    }
    close(FH);
}


# Procedures ============================================================={{{1

# dump_plain -------------------------------------------------------------{{{2
sub dump_plain {
    print <<__print__;
------------------------------------------------------------------------------
Menu tree, shows order of callers
------------------------------------------------------------------------------
__print__
    my $zm;
    foreach $zm (sort @menus) {
        show_forwards($zm) if ($all || !exists($refers_to{$zm}));
    }
}


# dump_reversed ----------------------------------------------------------{{{2
sub dump_reversed {
    print <<__print__;
------------------------------------------------------------------------------
Reversed menu tree, shows order of called menus
------------------------------------------------------------------------------
__print__
    my $zm;
    foreach $zm (sort @menus) {
        show_backwards($zm) if ($all || !exists($referred_from{$zm}));
    }
}


# show_backwards ---------------------------------------------------------{{{2
sub show_backwards {
    my $me = shift;

    print " "x(3*$reclevel) . "$me";
    print " ($menunames{$me})" if ($menunames{$me});
    print "\n";

    my $them;

    if (exists($refers_to{$me})) {
        foreach $them (sort @{$refers_to{$me}}) {
            $reclevel++;
            return if $reclevel > $max_reclevel;
            show_backwards($them);
            $reclevel--;
        }
    }
}


# show_forwards ----------------------------------------------------------{{{2
sub show_forwards {
    my $me = shift;

    print " "x(3*$reclevel) . "$me";
    print " ($menunames{$me})" if ($menunames{$me});
    print "\n";

    my $them;

    if (exists($referred_from{$me})) {
        foreach $them (sort @{$referred_from{$me}}) {
            $reclevel++;
            return if $reclevel > $max_reclevel;
            show_forwards($them);
            $reclevel--;
        }
    }
}


# main ==================================================================={{{1
my $noplain = 0;
my $reversed = 0;
my $short_opt = 0;

use Getopt::Long;
GetOptions(
        "all" => \$all, 
        "debug" => \$debug, 
        "noplain" => \$noplain,
        "reversed" => \$reversed,
) or die "usage: $0 [--debug] [--all] [--reversed] [--noplain]";

if ($noplain && !$reversed) {
    warn "NOTE: The '--noplain' flag implicitely implies the '--reversed' flag, which was added automatically.";
    $reversed = 1;
}

my $file;
foreach $file (@ARGV) {
    scanfile($file);
}

dump_plain() unless $noplain;
print "\n\n\n" if ($reversed and !$noplain);
dump_reversed() if $reversed;

exit 0;
__END__

# modeline ==============================================================={{{1
# vim: set fdm=marker ts=4 sw=4 et:
# eof
