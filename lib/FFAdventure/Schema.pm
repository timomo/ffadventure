package FFAdventure::Schema;

use base qw/DBIx::Class::Schema::Loader/;

__PACKAGE__->loader_options(
    # constraint => '^ffa.*',
    # debug      => 1,
);
