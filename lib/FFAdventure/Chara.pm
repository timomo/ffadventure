package FFAdventure::Chara;

use Mojo::Base -base;
use base 'FFAdventure::Base';

has 'parameter' => sub {
    return [qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date/];
};
has [qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date/];
has 'table' => 'chara';

sub convertArray2ref {
    my $this = shift;
    my $ref = {};
    @$ref{@{$this->parameter}} = @_;
    return $ref;
}

1;
