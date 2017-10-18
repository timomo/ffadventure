package FFAdventure::Monster;

use Mojo::Base -base;
use base 'FFAdventure::Base';

has 'parameter' => sub {
    return [qw/name ex hp sp dmg/];
};
has [qw/id name ex hp sp dmg maxhp/];
has 'table' => 'monster';
has 'primaryKey' => 'id';

1;
