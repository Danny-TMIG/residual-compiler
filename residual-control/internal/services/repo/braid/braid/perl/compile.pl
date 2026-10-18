#!/usr/bin/env perl
use strict;
use warnings;
use JSON::PP;

sub read_json {
    my ($path) = @_;
    open my $fh, '<', $path or die "open $path: $!";
    local $/;
    my $data = <$fh>;
    close $fh;
    return JSON::PP->new->decode($data);
}

my $schema = read_json('schema.json');
my $symbols = read_json('symbols.json');
my $intent  = read_json('intent.json');


my @resolved = map { $symbols->{$_} } grep { exists $symbols->{$_} } @{ $intent->{symbols} };
my @ops = map { @{ $_->{expands_to}{operators} } } @resolved;

my @nodes = map {
    {
        id       => sprintf("n-%d-%d", time, int(rand(1000000))),
        operator => $_,
        inputs   => {},
        outputs  => {},
        status   => 'PENDING',
    }
} @ops;

my @edges = map {
    {
        from      => $nodes[$_]{id},
        to        => $nodes[$_ + 1]{id},
        condition => {},
    }
} (0 .. $#nodes - 1);

my $graph = { nodes => \@nodes, edges => \@edges };
print JSON::PP->new->pretty->canonical->encode($graph);
open my $out, '>', 'graph-perl.json' or die $!;
print $out JSON::PP->new->pretty->encode($graph);
close $out;
