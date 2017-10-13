# app.psgi
use Plack::Builder;
use Plack::App::WrapCGI;
use Plack::App::File;

builder {
    mount "/" => Plack::App::WrapCGI->new(script => './ffadventure.cgi', execute => 1)->to_app;
    mount "/chara/"          => Plack::App::File->new(root => './chara/')->to_app;
};
