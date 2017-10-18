package FFAdventure::Base;

use Mojo::Base -base;
use SQL::Maker;

has 'in_storage' => 0;
has 'dbh';
has 'maker' => sub {
    return SQL::Maker->new( driver => 'mysql' );
};

sub fill {
    my $this = shift;
    my $attributes = shift;
    for my $key (keys %$attributes) {
        if ($this->can($key)) {
            $this->$key($attributes->{$key});
        }
    }
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
    my ($sql, @binds) = $this->maker->select($this->table, ['*'], { $this->primaryKey => $this->id });
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
        ($sql, @binds) = $this->maker->update($this->table, $ref, { $this->primaryKey => $this->id });
    }
    my $sth = $this->dbh->prepare($sql) || die $this->dbh->errstr;
    $sth->execute(@binds) || die $sth->errstr;
    return 1;
}

1;
