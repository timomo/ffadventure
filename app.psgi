# app.psgi
use Plack::Builder;
use Plack::App::WrapCGI;
use Plack::App::Directory;
use Plack::App::File;

builder {
    mount '/chara/' => Plack::App::Directory->new(root => './chara/')->to_app;
    mount '/bg.gif' => Plack::App::File->new(file => './bg.gif')->to_app;
    mount '/pochi5.gif' => Plack::App::File->new(file => './pochi5.gif')->to_app;
    mount '/title.gif' => Plack::App::File->new(file => './title.gif')->to_app;
    mount '/' => Plack::App::WrapCGI->new(script => './ffadventure.cgi', execute => 1)->to_app;
};
