package FFAdventure::Winner;

use Mojo::Base -base;
use base 'FFAdventure::Base';

has 'parameter' => sub {
    return [qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date count lsite lurl lname/];
};
has [qw/no id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date count lsite lurl lname/];
has 'table' => 'winner';
has 'primaryKey' => 'no';

sub convertArray2ref {
    my $this = shift;
    my $ref = {};
    @$ref{@{$this->parameter}} = @_;
    return $ref;
}

sub last {
    my $this = shift;
    my ($sql, @binds) = $this->maker->select($this->table, ['*'], {}, { order_by => $this->primaryKey. ' desc' } );
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

1;
