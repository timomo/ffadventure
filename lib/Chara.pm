package Chara;

use Mojo::Base -base;
use SQL::Maker;

has 'parameter' => sub {
    return [qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date/];
};
has [qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date/];
has 'in_storage' => 0;
has 'dbh';
has 'maker' => sub {
    return SQL::Maker->new( driver => 'mysql' );
};
has 'table' => 'chara';

sub convertArray2ref {
    my $this = shift;
    my $ref = {};
    @$ref{@{$this->parameter}} = @_;
    return $ref;
}

sub toArray {
    my $this = shift;
    my $ref = {};
    for my $key (@{$this->parameter}) {
        $ref->{$key} = $this->$key;
    }
    return $ref;
}

sub load {
    my $this = shift;
    my ($sql, @binds) = $this->maker->select($this->table, ['*'], { id => $this->id });
    my $sth = $this->dbh->prepare($sql);
    $sth->execute(@binds);
    my $row = $sth->fetchrow_hashref();
    if (!defined($row)) {
        return 0;
    }
    for my $key (keys %$row) {
        $this->$key($row->{$key});
    }
    $this->in_storage(1);
    return 1;
}

sub save {
    my $this = shift;
    my $ref = shift || $this->toArray();
    my ($sql, @binds);
    if ($this->in_storage == 0) {
        ($sql, @binds) = $this->maker->insert($this->table, $ref);
    } else {
        ($sql, @binds) = $this->maker->update($this->table, $ref, { id => $this->id });
    }
    my $sth = $this->dbh->prepare($sql);
    $sth->execute(@binds);
print $sth->errstr;
    return 1;
}

1;
