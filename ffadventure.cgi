#!/usr/bin/perl --

use 5.010001;
use CGI qw|:standard|;
use CGI::Session;
use lib qw(lib);
use DBI;
use Data::Dumper;
use FFAdventure::Chara;
use FFAdventure::Monster;
use FFAdventure::Winner;
use utf8;
use Encode;
use Data::WeightedRoundRobin;
use FFAdventure::Schema;

#--- [注意事項] ------------------------------------------------#
# 1. このスクリプトはフリーソフトです。このスクリプトを使用した    #
#    いかなる損害に対して作者は一切の責任を負いません。        #
# 2. 設置に関する質問はサポート掲示板にお願いいたします。    #
#    直接メールによる質問は一切お受けいたしておりません。    #
#---------------------------------------------------------------#

# 日本語ライブラリの読み込み
# require 'jcode.pl';

# 初期設定ファイルの読み込み
require 'ini/ffadventure.ini';
require 'ini/dsn.ini';

#================================================================#
#┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓#
#┃ これより下はCGIに自信のある方以外は扱わないほうが無難です　┃#
#┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛#
#================================================================#

#--------------#
#　メイン処理　#
#--------------#
my $dbh = DBI->connect( $dsn, $dbuser, $dbpass, $dbopts )
  or &error("DBエラー");
my $cgi     = CGI->new();
my $session = CGI::Session->load( 'driver:mysql', $cgi, { Handle => $dbh } );
my %in      = ();
my $schema  = FFAdventure::Schema->connect( $dsn, $dbuser, $dbpass, $dbopts );

if ($mente) {
    &error(
"現在メンテナンス中です。しばらくお待ちください。"
    );
}
&decode2();

if ( $session->is_empty() ) {
    $session = $session->new();
}
else {
    # $in{id}   = $session->param('id');
    # $in{pass} = $session->param('pass');
}
$session->expire('+1h');

given ( $cgi->param('mode') ) {
    when ('log_out')    { &log_out(); }
    when ('log_in')     { &log_in(); }
    when ('chara_make') { &chara_make(); }
    when ('make_end')   { &make_end(); }
    when ('regist')     { &regist(); }
    when ('battle')     { &battle(); }
    when ('tensyoku')   { &tensyoku(); }
    when ('monster')    { &monster(); }
    when ('ranking')    { &ranking(); }
    when ('yado')       { &yado(); }
    when ('message')    { &message(); }
    when ('item_shop')  { &item_shop(); }
    when ('item_buy')   { &item_buy(); }
    when ('top')        { &top(); }
    default             { &html_top(); }
}
$session->flush();
exit(0);

sub chara_load {
    my $id   = shift;
    my $cond = {};
    if ( ref $id eq 'HASH' ) {
        $cond = $id;
    }
    else {
        $cond = { id => $id };
    }
    my $rs  = $schema->resultset('Chara')->search($cond);
    my $row = $rs->next;
    return $row;
}

sub chara_array {
    return (
        qw/id pass site url name sex chara n_0 n_1 n_2 n_3 n_4 n_5 n_6 syoku hp maxhp ex lv gold lp total kati waza item mons host date/
    );
}

sub chara_convert {
    my $ref = {};
    my @key = &chara_array();
    @$ref{@key} = @_;
    return $ref;
}

sub chara_set {
    my $chara = shift;
    if ( !defined($chara) ) {
        return 0;
    }
    my @key = &chara_array();
    for my $key (@key) {
        ${ 'main::k' . $key } = $chara->$key;
    }
    return 1;
}

sub winner_load {
    my $rs = $schema->resultset('Winner')
      ->search( {}, { order_by => { -desc => 'no' } } );
    my $row = $rs->next;
    return $row;
}

sub winner_array {
    my @key = &chara_array();
    return ( @key, qw/count lsite lurl lname/ );
}

sub winner_set {
    my $chara = shift;
    if ( !defined($chara) ) {
        return 0;
    }
    my @key = &winner_array();
    for my $key (@key) {
        ${ 'main::w' . $key } = $chara->$key;
    }
    return 1;
}

sub log_in {
    my $id    = $cgi->param('id');
    my $pass  = $cgi->param('pass');
    my $chara = &chara_load($id);
    if ( defined($chara) && $chara->pass == $pass ) {
        $session->param( 'id',   $id );
        $session->param( 'pass', $pass );
    }
    &header();
    print
"<META http-equiv=\"refresh\" content=\"$refresh;URL=$script_url?mode=top\">";
}

sub log_out {
    if ( $session->is_empty() ) {

        # noop
    }
    else {
        $session->clear( [ 'id', 'pass' ] );
        $session->close;
        $session->delete;
    }
    &header();
    print "<META http-equiv=\"refresh\" content=\"$refresh;URL=$script_url\">";
}

#-----------------#
#  TOPページ表示  #
#-----------------#
sub html_top {
    my $winner = &winner_load();
    &winner_set($winner);

    &class;

    if ($wkati) { $ritu = int( ( $wkati / $wtotal ) * 100 ); }
    else        { $ritu = 0; }

    open( IN, "$recode_file" );
    @recode = <IN>;
    close(IN);

    ( $rcount, $rname, $rsite, $rurl ) = split( /<>/, $recode[0] );

    if   ($wsex) { $esex = "男"; }
    else         { $esex = "女"; }
    $next_ex = $wlv * $lv_up;

    if ($witem) {
        open( IN, "$item_file" );
        @battle_item = <IN>;
        close(IN);

        foreach (@battle_item) {
            ( $wi_no, $wi_name, $wi_dmg ) = split(/<>/);
            if ( $witem eq $wi_no ) { last; }
        }
    }
    else { $wi_name = "なし"; }

    # ヘッダー表示
    &header;

    # HTMLの表示
    print <<"EOM";
<form action="$script_url" method="POST">
<input type="hidden" name="mode" value="log_in">
<table border=0 width='100%'>
<tr>
<td><img src="$title_img"></td>
<td align="right" valign="top">
    <table border=1>
    <tr>
    <td align=center colspan=5 class=b2>キャラクターを作成済みの方はこちらから</td>
    </tr>
    <tr>
    <td class=b1>I D</td>
    <td><input type="text" size="10" name="id" value="$in{id}"></td>
    <td class=b1>パスワード</td>
    <td><input type="password" size="10" name="pass" value="$in{pass}"></td>
    <td><input type="submit" value="ログイン"></td>
    </tr>
    </table>
</td>
</tr>
</table>
<hr size=0>
<small>
/ <a href="$homepage">$home_title</a> / <a href="$script_url?mode=ranking">英雄たちの記録</a> / <a href="$syoku_html">各職業に必要な特性値</a> / <a href="http://cgi.members.interq.or.jp/sun/cumro/cgi-bin/idea/wwwlng.cgi">アイデア募集</a> /
</form>
$kanri_message
<p>
現在の連勝記録は、$rnameさんの「<A HREF=\"http\:\/\/$rurl\" TARGET=\"_blank\"><FONT SIZE=\"3\" COLOR=\"#6666BB\">$rsite</FONT></A>」、$rcount連勝です。新記録を出したサイト名の横には、<IMG SRC="$mark">マークがつきます。
<table border=0 width='100%'>
<tr>
<td width="500" valign="top">
    <table border=1 width="100%">
    <tr>
    <td colspan=5 align="center" class="b2"><font color="#FFFFFF">$wcount連勝中</font></td>
    </tr>
    <tr>
    <td align="center" class="b1">ホームページ</td>
    <td colspan="4"><a href="http\:\/\/$wurl"><b>$wsite</b></a>
EOM
    if ( $rurl eq "$wurl" ) {
        print "<IMG SRC=\"$mark\" border=0>\n";
    }
    print <<"EOM";
    </td>
    </tr>
    <tr>
    <td align="center" rowspan="8"><img src="$img_path/$chara_img[$wchara]"><p>勝率：$ritu\%<br>武器：$wi_name</td>
    <td align="center" class="b1">なまえ</td><td><b>$wname</b></td>
    <td align="center" class="b1">性別</td><td><b>$esex</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">職業</td><td><b>$chara_syoku[$wsyoku]</b></td>
    <td align="center" class="b1">クラス</td><td><b>$class</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">レベル</td><td><b>$wlv</b></td>
    <td align="center" class="b1">経験値</td><td><b>$wex/$next_ex</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">お金</td><td><b>$wgold</b></td>
    <td align="center" class="b1">HP</td><td><b>$whp\/$wmaxhp</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">力</td><td><b>$wn_0</b></td>
    <td align="center" class="b1">知能\</td><td><b>$wn_1</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">信仰心</td><td><b>$wn_2</b></td>
    <td align="center" class="b1">生命力</td><td><b>$wn_3</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">器用さ</td><td><b>$wn_4</b></td>
    <td align="center" class="b1">速さ</td><td><b>$wn_5</b></td>
    </tr>
    <tr>
    <td align="center" class="b1">魅力</td><td><b>$wn_6</b></td>
    <td align="center" class="b1">カルマ</td><td><b>$wlp</b></td>
    </tr>
    <tr>
    <td colspan=5 align="center">$wlname の <A HREF=\"http\:\/\/$wlurl\" TARGET=\"_blank\">$wlsite</A> に勝利！！</td>
    </tr>
    </table>
</td>
<td valign="top" class=small>
[<B><FONT COLOR="#FF9933">$main_title の遊び方</FONT></B>]
<OL>
<LI>まず、「新規キャラクター登録」ボタンを押して、キャラクターを作成します。
<LI>キャラクターの作成が完了したら、このページの右上にあるところからログインして、あなた専用のステータス画面に入ります。
<LI>そこであなたの行動を選択することができます。
<LI>一度キャラクターを作成したら、右上のところからログインして遊びます。新規にキャラクターを作れるのは、一人に一つのキャラクターのみです。
<LI>これは、HPバトラーではなく、キャラバトラーです。キャラクターを育てていくゲームです。
<LI>能\力を振り分けることができキャラクターの能\力をご自分で決めることができます。(ここで決めた能\力はごくまれにしか上昇しないので、慎重に)
<LI><b>$limit日</b>以上闘わなければ、キャラクターのデータが削除されます。
<LI>一度戦闘すると<b>$b_time</b>秒経過しないと再び戦闘できません。
</OL>
[<B><FONT COLOR="#FF9933">新規キャラクタ作成</FONT></B>]<BR>
下のボタンを押して、あなたのキャラクターを作成します。
<FORM ACTION="$script_url" METHOD="POST">
<INPUT TYPE="hidden" NAME="mode" VALUE="chara_make">
<INPUT TYPE="submit" VALUE="新規キャラクター作成">
</FORM>
</td>
</tr>
</table>
</small>
EOM

    # フッター表示
    &footer;

    exit;
}

#------------------#
#  ランキング画面  #
#------------------#
sub ranking {
    my $rs =
      $schema->resultset('Chara')
      ->search( {},
        { limit => $rank_top, order_by => { -desc => [qw/lv ex/] } } );
    my $sousu = $rs->count();

    &header;

    print <<"EOM";
<h1>英雄たちの記録</h1><hr size=0>
現在登録されているキャラクター<b>$sousu</b>人中レベルTOP<b>$rank_top</b>を表\示しています。
<p>
<table class="table">
<tr>
<th></th><th>なまえ</th><th>職業</th><th>ホームページ</th><th>レベル</th><th>経験値</th><th>HP</th><th>力</th><th>削除まで</th>
</tr>
EOM

    my $i = 1;
    while ( my $chara = $rs->next ) {
        my $rdate = $chara->date + ( 60 * 60 * 24 * $limit );
        my $niti = $rdate - time;
        $niti = int( $niti / ( 60 * 60 * 24 ) );
        say '<tr>';
        say sprintf(
"<td align=center>%d</td><td>%s</td><td>%s</td><td><a href=\"http\:\/\/%s\">%s</a></td><td align=center>%s</td><td align=center>%s</td><td align=center>%d\/%d</td><td align=center>%s</td><td align=center>あと %d 日</td>",
            $i,                            $chara->name,
            $chara_syoku[ $chara->syoku ], $chara->url,
            $chara->site,                  $chara->lv,
            $chara->ex,                    $chara->hp,
            $chara->maxhp,                 $chara->n_0,
            $niti
        );
        say '</tr>';
        $i += 1;
    }

    print "</table><p>\n";

    &footer;

    exit;
}

#----------------#
#  アイテム表示  #
#----------------#
sub item_shop {
    open( IN, "$item_file" );
    @item_array = <IN>;
    close(IN);

    &header;

    print <<"EOM";
<h1>アイテムショップ</h1>
<hr size=0>
<p>
<form action="$script_url" method="post">
買いたいアイテムをチェックし、あなたのIDとパスワードを入力してください。
<table class="table">
<tr>
<th></th><th>No.</th><th>なまえ</th><th>威力</th><th>価格</th>
EOM

    foreach (@item_array) {
        ( $ino, $iname, $idmg, $igold ) = split(/<>/);
        print "<tr>\n";
        print
"<td><input type=radio name=item_no value=\"$ino\"></td><td align=right>$ino</td><td>$iname</td><td align=center>$idmg</td><td align=center>$igold</td>\n";
        print "</tr>\n";
    }

    print <<"EOM";
</tr>
</table>
<p>
<input type="hidden" name="mode" value="item_buy" />
<input type="submit" value="アイテムを買う">
</form>
EOM

    &footer;

    exit;
}

#----------------#
#  アイテム買う  #
#----------------#
sub item_buy {
    my $chara =
      &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    if ( $in{'item_no'} eq "" ) {
        &error("アイテムを選んでください。");
    }

    open( IN, "$item_file" );
    @item_array = <IN>;
    close(IN);

    $hit = 0;
    foreach (@item_array) {
        ( $i_no, $i_name, $i_dmg, $i_gold ) = split(/<>/);
        if ( $in{'item_no'} eq "$i_no" ) { $hit = 1; last; }
    }
    if ( !$hit ) { &error("そんなアイテムは存在しません"); }

    &get_host;

    $date = time();

    if   ( $chara->gold < $i_gold ) { &error("お金が足りません"); }
    else                            { $chara->gold( $chara->gold - $i_gold ); }
    $chara->host($host);
    $chara->date($date);
    $chara->item($i_no);
    $chara->update();

    &header;

    say '<h1>アイテムを買いました</h1>';

    &footer;

    exit;
}

#------------#
#  体力回復  #
#------------#
sub yado {
    &get_host;

    $date = time();

    my $chara =
      &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    my $yado_gold = $yado_dai * $chara->lv;
    if ( $chara->gold < $yado_gold ) { &error("お金が足りません"); }
    $chara->gold( $chara->gold - $yado_gold );
    $chara->hp( $chara->maxhp );
    $chara->update();

    my $winner = &winner_load();
    if ( defined($winner) && $winner->id eq $chara->id ) {
        $winner->hp( $winner->maxhp );
        $winner->update();
    }

    &header;

    say '<h1>体力を回復しました</h1>';

    &footer;

    exit;
}

#----------------------#
#  キャラクタ作成画面  #
#----------------------#
sub chara_make {

    # ヘッダー表示
    &header;

    print <<"EOM";
<h1>キャラクタ作成画面</h1>
<hr size=0>
<form action="$script_url" method="post">
<input type="hidden" name="mode" value="make_end">
<table border=1>
<tr>
<td class="b1">ID</td>
<td><input type="text" name="id" size="10"><br><small>△お好きな半角英数字を4～8文字以内でご記入ください。</small></td>
</tr>
<tr>
<td class="b1">パスワード</td>
<td><input type="password" name="pass" size="10"><br><small>△お好きな半角英数字を4～8文字以内でご記入ください。</small></td>
</tr>
<tr>
<td class="b1">ホームページ名</td>
<td><input type="text" name="site" size="40"><br><small>△あなたのホームページの名前を入力してください。</small></td>
</tr>
<tr>
<td class="b1">URL</td>
<td><input type="text" name="url" size="50" value="http://"><br><small>△あなたのホームページのアドレスを記入してください。</small></td>
</tr>
<tr>
<td class="b1">キャラクターの名前</td>
<td><input type="text" name="c_name" size="30"><br><small>△作成するキャラクターの名前を入力してください。</small></td>
</tr>
<tr>
<td class="b1">キャラクターの性別</td>
<td><input type="radio" name="sex" value="0">女　<input type="radio" name="sex" value="1">男<br><small>△作成するキャラクターの性別を選択してください。</small></td>
</tr>
<tr>
<td class="b1">キャラクターのイメージ</td>
<td><select name="chara">
EOM

    foreach my $i ( 0 .. $#chara_name ) {
        print "<option value=\"$i\">$chara_name[$i]</option>";
    }

    print <<"EOM";
</select><br><small>△作成するキャラクターの性別を選択してください。</small></td>
</tr>
<tr>
<td class="b1">キャラクターの能力</td>
<td>
    <table border=1>
    <tr>
    <td class="b2" width="70">力</td><td class="b2" width="70">知能</td><td class="b2" width="70">信仰心</td><td class="b2" width="70">生命力</td><td class="b2" width="70">器用さ</td><td class="b2" width="70">速さ</td><td class="b2" width="70">魅力</td>
    </tr>
    <tr>
EOM

    $point = int( rand(10) );
    $point += 4;

    $i = 0;
    $j = 0;
    foreach ( 0 .. 6 ) {
        print "<td>$kiso_nouryoku[$i] + <select name=n_$i>\n";
        foreach ( 0 .. $point ) {
            print "<option value=\"$j\">$j</option>";
            $j++;
        }
        print "</select>\n";
        print "</td>\n";
        $i++;
        $j = 0;
    }

    print <<"EOM";
    </tr>
    </table>
<small>△ボーナスポイント「<b>$point</b>」をそれぞれに振り分けてください。(振り分けた合計が、$point以下になるように。<br>又どれかが最低12以上になるように。最高は18までです)</small>
</td>
</tr>
<tr>
<td colspan="2" align="center"><input type="submit" value="これで登録"></td>
</tr>
</table>
<input type="hidden" name="point" value="$point">
</form>
EOM

    # フッター表示
    &footer;

    exit;
}

#----------------#
#  登録完了画面  #
#----------------#
sub make_end {
    if ($chara_stop) {
        &error("現在キャラクターの作成登録はできません");
    }
    if ( $in{'id'} =~ m/[^0-9a-zA-Z]/ ) {
        &error(
            "IDに半角英数字以外の文字が含まれています。");
    }
    if ( $in{'pass'} =~ m/[^0-9a-zA-Z]/ ) {
        &error(
"パスワードに半角英数字以外の文字が含まれています。"
        );
    }

    # 職業未選択の場合
    if ( $in{'syoku'} eq "" ) {
        if (   $in{'id'} eq ""
            or length( $in{'id'} ) < 4
            or length( $in{'id'} ) > 8 )
        {
            &error(
"IDは、4文字以上、8文字以下で入力して下さい。"
            );
        }
        elsif ($in{'pass'} eq ""
            or length( $in{'pass'} ) < 4
            or length( $in{'pass'} ) > 8 )
        {
            &error(
"パスワードは、4文字以上、8文字以下で入力して下さい。"
            );
        }
        elsif ( $in{'site'} eq "" ) {
            &error("ホームページ名が未記入です");
        }
        elsif ( $in{'url'} eq "" ) { &error("URLが未記入です"); }
        elsif ( $in{'c_name'} eq "" ) {
            &error("キャラクターの名前が未記入です");
        }
        elsif ( $in{'sex'} eq "" ) {
            &error("性別が選択されていません");
        }

        $g =
          $in{'n_0'} +
          $in{'n_1'} +
          $in{'n_2'} +
          $in{'n_3'} +
          $in{'n_4'} +
          $in{'n_5'} +
          $in{'n_6'};

        if ( $g > $in{'point'} ) {
            &error(
"ポイントの振り分けが多すぎます。振り分けの合計を、$in{'point'}以下にしてください。"
            );
        }

        &header;

        print "<h1>職業選択画面</h1><hr size=0>\n";
        print
"あなたがなることができる職業は以下のとおりです。<p>\n";
        print "<form action=\"$script_url\" method=\"post\">\n";
        print "<input type=hidden name=mode value=regist>\n";
        print "<select name=syoku>\n";
        print "<option value=0>$chara_syoku[0]\n";

        if ( $in{'n_1'} + $kiso_nouryoku[1] > 11 ) {
            print "<option value=1>$chara_syoku[1]\n";
        }
        if (    $in{'n_2'} + $kiso_nouryoku[2] > 11
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=2>$chara_syoku[2]\n";
        }
        if (    $in{'n_4'} + $kiso_nouryoku[4] > 11
            and $in{'n_5'} + $kiso_nouryoku[5] > 7 )
        {
            print "<option value=3>$chara_syoku[3]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 9
            and $in{'n_1'} + $kiso_nouryoku[1] > 7
            and $in{'n_2'} + $kiso_nouryoku[2] > 7
            and $in{'n_3'} + $kiso_nouryoku[3] > 10
            and $in{'n_4'} + $kiso_nouryoku[4] > 9
            and $in{'n_5'} + $kiso_nouryoku[5] > 7
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=4>$chara_syoku[4]\n";
        }
        if (    $in{'n_1'} + $kiso_nouryoku[1] > 12
            and $in{'n_4'} + $kiso_nouryoku[4] > 12 )
        {
            print "<option value=5>$chara_syoku[5]\n";
        }
        if (    $in{'n_1'} + $kiso_nouryoku[1] > 9
            and $in{'n_4'} + $kiso_nouryoku[4] > 11
            and $in{'n_5'} + $kiso_nouryoku[5] > 7
            and $in{'n_6'} + $kiso_nouryoku[6] > 11 )
        {
            print "<option value=6>$chara_syoku[6]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 9
            and $in{'n_1'} + $kiso_nouryoku[1] > 13
            and $in{'n_3'} + $kiso_nouryoku[3] > 13
            and $in{'n_6'} + $kiso_nouryoku[6] > 9 )
        {
            print "<option value=7>$chara_syoku[7]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 9
            and $in{'n_2'} + $kiso_nouryoku[2] > 10
            and $in{'n_3'} + $kiso_nouryoku[3] > 10
            and $in{'n_4'} + $kiso_nouryoku[4] > 9
            and $in{'n_5'} + $kiso_nouryoku[5] > 10
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=8>$chara_syoku[8]\n";
        }
        if (    $in{'n_1'} + $kiso_nouryoku[1] > 14
            and $in{'n_2'} + $kiso_nouryoku[2] > 14
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=9>$chara_syoku[9]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 11
            and $in{'n_1'} + $kiso_nouryoku[1] > 8
            and $in{'n_2'} + $kiso_nouryoku[2] > 11
            and $in{'n_3'} + $kiso_nouryoku[3] > 11
            and $in{'n_4'} + $kiso_nouryoku[4] > 8
            and $in{'n_5'} + $kiso_nouryoku[5] > 8
            and $in{'n_6'} + $kiso_nouryoku[6] > 13 )
        {
            print "<option value=10>$chara_syoku[10]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 11
            and $in{'n_1'} + $kiso_nouryoku[1] > 10
            and $in{'n_3'} + $kiso_nouryoku[3] > 8
            and $in{'n_4'} + $kiso_nouryoku[4] > 11
            and $in{'n_5'} + $kiso_nouryoku[5] > 13
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=11>$chara_syoku[11]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 12
            and $in{'n_1'} + $kiso_nouryoku[1] > 7
            and $in{'n_2'} + $kiso_nouryoku[2] > 12
            and $in{'n_4'} + $kiso_nouryoku[4] > 9
            and $in{'n_5'} + $kiso_nouryoku[5] > 12
            and $in{'n_6'} + $kiso_nouryoku[6] > 7 )
        {
            print "<option value=12>$chara_syoku[12]\n";
        }
        if (    $in{'n_0'} + $kiso_nouryoku[0] > 11
            and $in{'n_1'} + $kiso_nouryoku[1] > 9
            and $in{'n_2'} + $kiso_nouryoku[2] > 9
            and $in{'n_3'} + $kiso_nouryoku[3] > 11
            and $in{'n_4'} + $kiso_nouryoku[4] > 11
            and $in{'n_5'} + $kiso_nouryoku[5] > 11 )
        {
            print "<option value=13>$chara_syoku[13]\n";
        }

        print "</select>\n";
        print "<input type=hidden name=new value=new>\n";
        print "<input type=hidden name=id value=\"$in{'id'}\">\n";
        print "<input type=hidden name=pass value=\"$in{'pass'}\">\n";
        print "<input type=hidden name=site value=\"$in{'site'}\">\n";
        print "<input type=hidden name=url value=\"$in{'url'}\">\n";
        print "<input type=hidden name=c_name value=\"$in{'c_name'}\">\n";
        print "<input type=hidden name=sex value=\"$in{'sex'}\">\n";
        print "<input type=hidden name=chara value=\"$in{'chara'}\">\n";
        print "<input type=hidden name=n_0 value=\"$in{'n_0'}\">\n";
        print "<input type=hidden name=n_1 value=\"$in{'n_1'}\">\n";
        print "<input type=hidden name=n_2 value=\"$in{'n_2'}\">\n";
        print "<input type=hidden name=n_3 value=\"$in{'n_3'}\">\n";
        print "<input type=hidden name=n_4 value=\"$in{'n_4'}\">\n";
        print "<input type=hidden name=n_5 value=\"$in{'n_5'}\">\n";
        print "<input type=hidden name=n_6 value=\"$in{'n_6'}\">\n";
        print "<input type=submit value=\"この職業でOK\"></form>\n";

        &footer;

        exit;
    }
    else {
        if   ( $in{'sex'} ) { $esex = "男"; }
        else                { $esex = "女"; }
        $next_ex = $lv * $lv_up;

        &header;

        print <<"EOM";
<h1>登録完了画面</h1>
以下の内容で登録が完了しました。
<hr size=0>
<p>
<table border=1>
<tr>
<td class="b1">ホームページ</td>
<td colspan="4"><a href="http\:\/\/$in{'url'}">$in{'site'}</a></td>
</tr>
<tr>
<td rowspan="8" align="center"><img src="$img_path/$chara_img[$in{'chara'}]"></td>
<td class="b1">なまえ</td>
<td>$in{'c_name'}</td>
<td class="b1">性別</td>
<td>$esex</td>
</tr>
<tr>
<td class="b1">職業</td>
<td>$chara_syoku[$in{'syoku'}]</td>
<td class="b1">お金</td>
<td>$gold</td>
</tr>
<tr>
<td class="b1">レベル</td>
<td>$lv</td>
<td class="b1">経験値</td>
<td>$ex/$next_ex</td>
</tr>
<tr>
<td class="b1">HP</td>
<td>$hp</td>
<td class="b1"></td>
<td></td>
</tr>
<tr>
<td class="b1">力</td>
<td>$n_0</td>
<td class="b1">知能\</td>
<td>$n_1</td>
</tr>
<tr>
<td class="b1">信仰心</td>
<td>$n_2</td>
<td class="b1">生命力</td>
<td>$n_3</td>
</tr>
<tr>
<td class="b1">器用さ</td>
<td>$n_4</td>
<td class="b1">速さ</td>
<td>$n_5</td>
</tr>
<tr>
<td class="b1">魅力</td>
<td>$n_6</td>
<td class="b1">カルマ</td>
<td>$lp</td>
</tr>
</table>
<form action="$script_url" method="post">
<input type="hidden" name=mode value=log_in>
<input type="hidden" name=id value="$in{'id'}">
<input type="hidden" name=pass value="$in{'pass'}">
<input type="submit" value="ステータス画面へ">
</form>
EOM

        &footer;

        exit;
    }
}

#----------------#
#  書き込み処理  #
#----------------#
sub regist {
    &get_host;

    $date = time();

    if ( $in{'new'} eq 'new' ) {
        $lp = int( rand(15) );
        $hp = int( ( $in{'n_3'} + $kiso_nouryoku[3] ) + ( rand($lp) + 1 ) ) +
          $kiso_hp;
        $ex      = 0;
        $lv      = 1;
        $gold    = 0;
        $n_0     = $kiso_nouryoku[0] + $in{'n_0'};
        $n_1     = $kiso_nouryoku[1] + $in{'n_1'};
        $n_2     = $kiso_nouryoku[2] + $in{'n_2'};
        $n_3     = $kiso_nouryoku[3] + $in{'n_3'};
        $n_4     = $kiso_nouryoku[4] + $in{'n_4'};
        $n_5     = $kiso_nouryoku[5] + $in{'n_5'};
        $n_6     = $kiso_nouryoku[6] + $in{'n_6'};
        $c_syoku = $in{'syoku'};
        $item  ||= '0000';
        $mons  ||= 0;
        $kati  ||= 0;
        $total ||= 0;
        $waza  ||= 'コメントなし';

        my $chara = &chara_load( $in{id} );
        $chara = $schema->resultset('Chara')->new( {} );
        my $attr = &chara_convert(
            $in{id},  $in{pass},  $in{site}, $in{url}, $in{c_name},
            $in{sex}, $in{chara}, $n_0,      $n_1,     $n_2,
            $n_3,     $n_4,       $n_5,      $n_6,     $c_syoku,
            $hp,      $hp,        $ex,       $lv,      $gold,
            $lp,      $total,     $kati,     $waza,    $item,
            $mons,    $host,      $date
        );
        eval {
            $chara->set_columns($attr);
            $chara->insert();
        };
        if ($@) {
            &error($@);
        }
    }
    else {
        my $chara = &chara_load( $session->param('id') );
        $ksyoku ||= 0;
        $kn_0   ||= 0;
        $kn_1   ||= 0;
        $kn_2   ||= 0;
        $kn_3   ||= 0;
        $kn_4   ||= 0;
        $kn_5   ||= 0;
        $kn_6   ||= 0;
        $klp    ||= 0;
        $kitem  ||= '0000';
        my $attr = &chara_convert(
            $kid,    $kpass, $ksite,  $kurl,  $kname, $ksex,  $kchara,
            $kn_0,   $kn_1,  $kn_2,   $kn_3,  $kn_4,  $kn_5,  $kn_6,
            $ksyoku, $khp,   $kmaxhp, $kex,   $klv,   $kgold, $klp,
            $ktotal, $kkati, $kwaza,  $kitem, $kmons, $host,  $date
        );
        eval {
            $chara->set_columns($attr);
            $chara->update();
        };
        if ($@) {
            &error($@);
        }
    }

    if ( $in{'new'} ) { &make_end; }
}

#----------------#
#  ログイン画面  #
#----------------#
sub top {
    $chara_flag = 1;

    # ファイルロック
    if    ( $lockkey == 1 ) { &lock1; }
    elsif ( $lockkey == 2 ) { &lock2; }
    elsif ( $lockkey == 3 ) { &file'lock; }

    my $chara = &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    &chara_set($chara);

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    &class;

    if   ($ksex) { $esex = "男"; }
    else         { $esex = "女"; }
    $next_ex = $klv * $lv_up;

    open( IN, "$item_file" );
    @log_item = <IN>;
    close(IN);

    $hit = 0;
    foreach (@log_item) {
        ( $i_no, $i_name, $i_dmg, $i_gold ) = split(/<>/);
        if ( $kitem eq "$i_no" ) { $hit = 1; last; }
    }
    if ( !$hit ) { $i_name = ""; }

    &header;
    my $site = $ksite;
    my $name = $kname;

    if ( $ltime < $b_time or !$ktotal ) {
        print <<"EOM";
<FORM NAME="form1">
チャンプと闘えるまで残り<INPUT TYPE="text" NAME="clock" SIZE="3" VALUE="$vtime">秒です。0になると、自動的に更新しますのでブラウザの更新は押さないで下さい。
</FORM>
EOM
    }
    print <<"EOM";
<form action="$script_url" method="post">
<table border=0 class="">
<tr>
<td valign=top width='50%'>
<table border=1 class="table table-striped">
<tr>
<td colspan="5" class="b2" align="center">ホームページデータ</td>
</tr>
<tr>
<td class="b1">ホームページ名</td>
<td colspan="4"><input type="text" name=site value="$site" size=50></td>
</tr>
<tr>
<td class="b1">ホームページのURL</td>
<td colspan="4"><input type="text" name=url value="http\:\/\/$kurl" size=60></td>
</tr>
<tr>
<td colspan="5" class="b2" align="center">キャラクターデータ</td>
</tr>
<tr>
<td rowspan="8" align="center"><img src="$img_path/$chara_img[$kchara]"><br>武器：$i_name</td>
<td class="b1">なまえ</td>
<td><input type="text" name=c_name value="$name" size=10></td>
<td class="b1">性別</td>
<td>$esex</td>
</tr>
<tr>
<td class="b1">職業</td>
<td>$chara_syoku[$ksyoku]</td>
<td class="b1">クラス</td>
<td>$class</td>
</tr>
<tr>
<td class="b1">レベル</td>
<td class="int">$klv</td>
<td class="b1">経験値</td>
<td class="int">$kex/$next_ex</td>
</tr>
<tr>
<td class="b1">お金</td>
<td class="int">$kgold</td>
<td class="b1">HP</td>
<td class="int">$khp\/$kmaxhp</td>
</tr>
<tr>
<td class="b1">力</td>
<td class="int">$kn_0</td>
<td class="b1">知能\</td>
<td class="int">$kn_1</td>
</tr>
<tr>
<td class="b1">信仰心</td>
<td class="int">$kn_2</td>
<td class="b1">生命力</td>
<td class="int">$kn_3</td>
</tr>
<tr>
<td class="b1">器用さ</td>
<td class="int">$kn_4</td>
<td class="b1">速さ</td>
<td class="int">$kn_5</td>
</tr>
<tr>
<td class="b1">魅力</td>
<td class="int">$kn_6</td>
<td class="b1">カルマ</td>
<td class="int">$klp</td>
</tr>
<tr>
<td class="b1">技発動時コメント</td>
<td colspan="4"><input type="text" name=waza value="$kwaza" size=50></td>
</tr>
<tr>
<td colspan="5" align="center">
<input type="hidden" name="mode" value="battle" />
EOM
    if ( $ltime >= $b_time or !$ktotal ) {
        say "<input type=\"submit\" value=\"チャンプに挑戦\">";
    }
    else {
        say $vtime. "秒後闘えるようになります。";
    }

    print <<"EOM";
</td>
</tr>
</table>
</form>
</td>
<td valign="top">
<form action="$script_url" method="post">
【現在転職できる職業一覧】<br>
<select name=syoku>
<option value="no">選択してください。
EOM

    open( IN, "$syoku_file" );
    @syoku = <IN>;
    close(IN);

    $i   = 0;
    $hit = 0;
    foreach (@syoku) {
        ( $a, $b, $c, $d, $e, $f, $g ) = split(/<>/);
        if (    $kn_0 >= $a
            and $kn_1 >= $b
            and $kn_2 >= $c
            and $kn_3 >= $d
            and $kn_4 >= $e
            and $kn_5 >= $f
            and $kn_6 >= $g
            and $ksyoku != $i )
        {
            print "<option value=\"$i\">$chara_syoku[$i]\n";
            $hit = 1;
        }
        $i++;
    }
    print <<"EOM";
</select>
<input type="hidden" name="mode" value="tensyoku" />
EOM

    if   ( !$hit ) { print "現在転職できる職業はありません"; }
    else           { print "<input type=submit value=\"転職する\">\n"; }

    print <<"EOM";
<br>
　<small>※ 転職すると、全ての能\力値が転職した職業の初期値になります。また、LVも1になります。</small>
</form>
<form action="$script_url" method="get">
【アイテムショップ】<br />
<input type="hidden" name="mode" value="item_shop" />
<input type="submit" value="アイテムショップに行く"><br />
</form>
<form action="$script_url" method="get">
【魔物と戦い修行できます】<br />
<input type="hidden" name="mode" value="monster" />
EOM

    if ( $ltime >= $m_time or !$ktotal ) {
        say "<input type=submit value=\"モンスターと闘う\"><br />";
    }
    else {
        say $mtime. " 秒後闘えるようになります。<br />";
    }

    $yado_gold = $yado_dai * $klv;

    print <<"EOM";
　<small>※修行の旅にいけます。</small>
</form>
<form action="$script_url" method="post">
【旅の宿】<br>
<input type="hidden" name="mode" value="yado" />
<input type="submit" value="体力を回復"><br />
　<small>※体力を回復することができます。<b>$yado_gold</b>G必要です。現在チャンプの方も回復できます。こまめに回復すれば連勝記録も・・・。</small>
</form>
<form action="$script_url" method="post">
【他のキャラクターへメッセージを送る】<br />
<input type="text" name="mes" size=50 /><br />
<select name="mesid">
<option value="">送る相手を選択
EOM

    my $rs = $schema->resultset('Chara')
      ->search( { id => { '!=' => $session->param('id') } } );
    while ( my $row = $rs->next ) {
        printf( qq|<option value="%d">%s さんへ</option>|,
            $row->no, $row->name );
    }

    print <<"EOM";
</select>
<input type="hidden" name="mode" value="message" />
<input type=submit value="メッセージを送る"><br>
　<small>※他のキャラクターへメッセージを送ることができます。</small>
</form>
</td>
</tr>
</table>
【届いているメッセージ】表示数<b>$max_gyo</b>件まで<br>
EOM

    my $rs =
      $schema->resultset('Message')
      ->search( [ { from => $chara->no }, { to => $chara->no } ],
        { limit => $max_gyo } );
    while ( my $mes = $rs->next ) {
        my $from = &chara_load( { no => $mes->from } );
        my $to   = &chara_load( { no => $mes->to } );
        printf(
"<hr size=0><small>%s さんから %s さんへ　＞ 「%s」(%s)</small><br>",
            $from->name, $to->name, $mes->mes, &get_time( $mes->date ) );
    }

    say '<hr size="0" />';

    &footer;

    # ロック解除
    if ( $lockkey == 3 ) { &file'unlock; }
    else {
        if ( -e $lockfile ) { unlink($lockfile); }
    }

    $chara_flag = 0;

    exit;
}

#--------------#
#  メッセージ  #
#--------------#
sub message {
    if ( $in{'mes'} eq "" ) {
        &error("メッセージが記入されていません");
    }
    if ( $in{'mesid'} eq "" ) {
        &error("相手が指定されていません");
    }
    my $from =
      &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    my $to = &chara_load( { no => $in{mesid} } )
      || &error("送信先がいません。");
    my $mes = $schema->resultset('Message')->new( {} );
    $mes->from( $from->no );
    $mes->to( $to->no );
    $mes->mes( $in{mes} );
    $mes->date(time);
    $mes->insert();

    &header;
    say 'メッセージを送りました。';
    &footer;

    exit;
}

#--------#
#  転職  #
#--------#
sub tensyoku {
    if ( $in{'syoku'} eq 'no' ) {
        &error("職業を選択してください。");
    }
    $syoku = $in{'syoku'};
    $id    = $in{'id'};

    &get_host;

    $date = time();

    open( IN, "$syoku_file" );
    my @syokudate = <IN>;
    close(IN);

    my ( $a, $b, $c, $d, $e, $f, $g ) =
      split( /<>/, $syokudate[ $in{'syoku'} ] );

    if ( !$a ) { $a = $kiso_nouryoku[0]; }
    if ( !$b ) { $b = $kiso_nouryoku[1]; }
    if ( !$c ) { $c = $kiso_nouryoku[2]; }
    if ( !$d ) { $d = $kiso_nouryoku[3]; }
    if ( !$e ) { $e = $kiso_nouryoku[4]; }
    if ( !$f ) { $f = $kiso_nouryoku[5]; }
    if ( !$g ) { $g = $kiso_nouryoku[6]; }

    $lv = 1;
    $ex = 0;

    my $chara =
      &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    $chara->n_0($a);
    $chara->n_1($b);
    $chara->n_2($c);
    $chara->n_3($d);
    $chara->n_4($e);
    $chara->n_5($f);
    $chara->n_6($g);
    $chara->syoku($syoku);
    $chara->ex($ex);
    $chara->lv($lv);
    $chara->host($host);
    $chara->date($date);
    $chara->update();
    my $winner = &winner_load();

    if ( defined($winner) && $chara->id == $winner->id ) {
        $winner->n_0( $chara->n_0 );
        $winner->n_1( $chara->n_1 );
        $winner->n_2( $chara->n_2 );
        $winner->n_3( $chara->n_3 );
        $winner->n_4( $chara->n_4 );
        $winner->n_5( $chara->n_5 );
        $winner->n_6( $chara->n_6 );
        $winner->syoku( $chara->syoku );
        $winner->ex( $chara->ex );
        $winner->lv( $chara->lv );
        $winner->host( $chara->host );
        $winner->date( $chara->date );
        $winner->update();
    }

    &header;
    my $id = $session->param('id');

    print <<"EOM";
<h1>転職しました</h1><hr size=0>
<p>
<form action="$script_url" method="post">
<input type="hidden" name=id value="$id">
<input type="submit" value="ステータス画面へ">
</form>
EOM

    &footer;

    exit;
}

#------------#
#  戦闘画面  #
#------------#
sub battle {
    if ($battle_flag) {
        &error(
"現在戦闘中です。少しお待ちになってから戦闘してください。"
        );
    }

    $battle_flag = 1;

    my $chara = &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    &chara_set($chara);

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    if ( $ltime < $b_time and $ktotal ) {
        &error("$vtime秒後闘えるようになります。\n");
    }

    my $winner = &winner_load();
    if ( !defined($winner) ) {
        $winner = $schema->resultset('Winner')->new( {} );
        my @keys = &chara_array();
        for my $key (@keys) {
            $winner->$key( $chara->$key );
        }
        $winner->lsite( $chara->site );
        $winner->lurl( $chara->url );
        $winner->lname( $chara->name );
        $winner->count(1);
        $winner->insert();
        &error(
"チャンプがいない為、自分がチャンプになりました。"
        );
    }
    &winner_set($winner);

    if ( $wid eq $kid ) {
        &error("現在チャンプなので闘えません。");
    }

    if ($chanp_milit) {
        if ( $kurl eq $lurl ) {
            &error("チャンプが変わるまで闘えません。");
        }
    }

    if ($kitem) {
        open( IN, "$item_file" );
        @battle_item = <IN>;
        close(IN);

        foreach (@battle_item) {
            ( $ci_no, $ci_name, $ci_dmg ) = split(/<>/);
            if ( $kitem eq $ci_no ) { last; }
        }
    }
    if ($witem) {
        open( IN, "$item_file" );
        @battle_item = <IN>;
        close(IN);

        foreach (@battle_item) {
            ( $wi_no, $wi_name, $wi_dmg ) = split(/<>/);
            if ( $witem eq $wi_no ) { last; }
        }
    }

    if ( $in{'site'} )   { $ksite = $in{'site'}; }
    if ( $in{'url'} )    { $kurl  = $in{'url'}; }
    if ( $in{'waza'} )   { $kwaza = $in{'waza'}; }
    if ( $in{'c_name'} ) { $kname = $in{'c_name'}; }
    $khp_flg = $khp;
    $whp_flg = $whp;

    $i           = 1;
    $j           = 0;
    @battle_date = ();
    foreach ( 1 .. $turn ) {
        $dmg1 = $klv * ( int( rand(3) ) + 1 );
        $dmg2 = $wlv * ( int( rand(3) ) + 1 );
        $clit1   = "";
        $clit2   = "";
        $com1    = "";
        $com2    = "";
        $kawasi1 = "";
        $kawasi2 = "";

        # 挑戦者ダメージ計算
        if ( $ksyoku == 0 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[0]</b></font>\n";
                $dmg1 = $dmg1 * 5;
            }
            $dmg1 = $dmg1 + int( rand($kn_0) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 1 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[1]</b></font>\n";
                $dmg1 = $dmg1 * 5;
            }
            $dmg1 = $dmg1 + int( rand($kn_1) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 2 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[2]</b></font>\n";
                $dmg1 = $dmg1 * 5;
            }
            $dmg1 = $dmg1 + int( rand($kn_2) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 3 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[3]</b></font>\n";
                $dmg1 = $dmg1 * 5;
            }
            $dmg1 = $dmg1 + int( rand($kn_3) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 4 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[4]</b></font>\n";
                $dmg1 = $dmg1 * 5;
            }
            $dmg1 = $dmg1 + int( rand($kn_3) ) + int( rand($kn_0) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 5 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[5]</b></font>\n";
                $dmg1 = $dmg1 * 6;
            }
            $dmg1 =
              $dmg1 + ( int( rand($kn_1) ) + int( rand($kn_4) ) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 6 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[6]</b></font>\n";
                $dmg1 = $dmg1 * 6;
            }
            $dmg1 =
              $dmg1 + ( int( rand($kn_1) ) + int( rand($kn_4) ) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 7 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand(7) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[7]</b></font>\n";
                $dmg1 = $dmg1 * 6;
            }
            $dmg1 =
              $dmg1 + ( int( rand($kn_1) ) + int( rand($kn_3) ) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 9 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[9]</b></font>\n";
                $dmg1 = $dmg1 * 8;
            }
            $dmg1 =
              $dmg1 * ( int( rand($kn_1) ) + int( rand($kn_2) ) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 8 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[8]</b></font>\n";
                $dmg1 = $dmg1 * 8;
            }
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 10 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[10]</b></font>\n";
                $dmg1 = $dmg1 * 9;
            }
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 11 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[11]</b></font>\n";
                $dmg1 = $dmg1 * 9;
            }
            $dmg1 = $dmg1 + int( rand($kn_4) ) + int( rand($kn_5) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 12 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[12]</b></font>\n";
                $dmg1 = $dmg1 * 9;
            }
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) ) + $ci_dmg;
        }
        elsif ( $ksyoku == 13 ) {
            if   ($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
            else          { $com1 = "$knameの攻撃！！<p>"; }
            if ( 0 == int( rand($waza_ritu) ) ) {
                $com1 .=
"<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[13]</b></font>\n";
                $dmg1 = $dmg1 * 9;
            }
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) ) + $ci_dmg;
        }

        # チャンプダメージ計算
        if ( $wsyoku == 0 ) {
            $dmg2 = $dmg2 + int( rand($wn_0) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 1 ) {
            $dmg2 = $dmg2 + int( rand($wn_1) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 2 ) {
            $dmg2 = $dmg2 + int( rand($wn_2) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 3 ) {
            $dmg2 = $dmg2 + int( rand($wn_4) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 4 ) {
            $dmg2 = $dmg2 + int( rand($wn_3) ) + int( rand($wn_0) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 5 ) {
            $dmg2 =
              $dmg2 + ( int( rand($wn_1) ) + int( rand($wn_4) ) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 6 ) {
            $dmg2 = $dmg2 + int( rand($wn_1) ) + int( rand($wn_4) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 7 ) {
            $dmg2 =
              $dmg2 + ( int( rand($wn_1) ) + int( rand($wn_3) ) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 8 ) {
            $dmg2 =
              $dmg2 + ( int( rand($wn_1) ) + int( rand($wn_2) ) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 9 ) {
            $dmg2 = $dmg2 + int( rand($wn_0) ) + int( rand($wn_2) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 10 ) {
            $dmg2 = $dmg2 + int( rand($wn_0) ) + int( rand($wn_2) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 11 ) {
            $dmg2 = $dmg2 + int( rand($wn_4) ) + int( rand($wn_5) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 12 ) {
            $dmg2 = $dmg2 + int( rand($wn_0) ) + int( rand($wn_2) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }
        elsif ( $wsyoku == 13 ) {
            $dmg2 = $dmg2 + int( rand($wn_0) ) + int( rand($wn_2) ) + $wi_dmg;
            if   ($witem) { $com2 = "$wnameは、$wi_nameで攻撃！！"; }
            else          { $com2 = "$wnameの攻撃！！<p>"; }
        }

        if ( int( rand(20) ) == 0 ) {
            $clit1 = "<b class=\"clit\">クリティカル！！</b>";
            $dmg1  = $dmg1 * 2;
        }

        if ( int( rand(30) ) == 0 ) {
            $clit2 =
"<font size=5>$wname「<b>$wwaza</b>」</font><p><b class=\"clit\">クリティカル！！</b>";
            $dmg2 = int( $dmg2 * 1.5 );
        }

        if ( ( $wlv - $klv ) >= $level_sa and $i == 1 ) {
            $sa = $wlv - $klv;
            $clit1 .=
"<p><font size=5><b>$knameの体から青い炎のようなものが湧き上がる・・・。</b></font>";
            $dmg1 = $dmg1 + $kmaxhp;
        }

        $battle_date[$j] = <<"EOM";
<TABLE BORDER=0>
<TR>
    <TD CLASS="b2" COLSPAN="3" ALIGN="center">
    $iターン
    </TD>
</TR>
<TR>
    <TD ALIGN="center">
    <IMG SRC="$img_path/$chara_img[$kchara]">
    </TD>
    <TD>
    </TD>
    <TD ALIGN="center">
    <IMG SRC="$img_path/$chara_img[$wchara]">
    </TR>
<TR>
<TD>
<TABLE BORDER=1>
<TR>
    <TD CLASS="b1">
    なまえ
    </TD>
    <TD CLASS="b1">
    HP
    </TD>
    <TD CLASS="b1">
    職業
    </TD>
    <TD CLASS="b1">
    LV
    </TD>
</TR>
<TR>
    <TD>
    $kname
    </TD>
    <TD>
    $khp_flg\/$kmaxhp
    </TD>
    <TD>
    $chara_syoku[$ksyoku]
    </TD>
    <TD>
    $klv
    </TD>
</TR>
</TABLE>
</TD>
<TD>
<FONT SIZE=5 COLOR="#9999DD">VS</FONT>
</TD>
<TD>
<TABLE BORDER=1>
<TR>
    <TD CLASS="b1">
    なまえ
    </TD>
    <TD CLASS="b1">
    HP
    </TD>
    <TD CLASS="b1">
    職業
    </TD>
    <TD CLASS="b1">
    LV
    </TD>
</TR>
<TR>
    <TD>
    $wname
    </TD>
    <TD>
    $whp_flg\/$wmaxhp
    </TD>
    <TD>
    $chara_syoku[$wsyoku]
    </TD>
    <TD>
    $wlv
    </TD>
</TR>
</TABLE>
</TD>
</TR>
</TABLE>
<p>
$com1 $clit1 $kawasi2 $wname に <font class="dmg"><b>$dmg1</b></font> のダメージを与えた。<p>
$com2 $clit2 $kawasi1 $kname に <font class="dmg"><b>$dmg2</b></font> のダメージを与えた。<p>
EOM

        $khp_flg = $khp_flg - $dmg2;
        $whp_flg = $whp_flg - $dmg1;

        if    ( $whp_flg <= 0 ) { $win = 1; last; }
        elsif ( $khp_flg <= 0 ) { $win = 0; last; }

        $i++;
        $j++;
    }

    if ($win) {
        $ktotal += 1;
        $kkati  += 1;
        $exp   = int( $wlv * $kiso_exp + ( rand($klp) + 1 ) );
        $kex   = $kex + $exp;
        $gold  = $wlv * 10 + int( rand($klp) );
        $kmons = $sentou_limit;
        $comment =
"<b><font size=5>$knameは、戦闘に勝利した！！</font></b><p>";
    }
    else {
        $ktotal += 1;
        $exp   = int( $wlv * ( rand($klp) + 1 ) );
        $kex   = $kex + $exp;
        $gold  = int( rand($klp) );
        $kmons = $sentou_limit;
        $comment =
"<b><font size=5>$knameは、戦闘に負けた・・・。</font></b><p>";
    }

    if ( $kex > ( $klv * $lv_up ) ) {
        $comment .= "$knameは、レベルが上がった！！<p>";
        $kmaxhp = $kmaxhp + int( rand($kn_3) ) + 1;
        $khp    = $kmaxhp;
        $kex    = 0;
        $klv += 1;
        if ( int( rand(5) ) == 0 ) { $kn_0 += 1; $t1 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_1 += 1; $t2 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_2 += 1; $t3 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_3 += 1; $t4 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_4 += 1; $t5 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_5 += 1; $t6 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_6 += 1; $t7 = 1; }
        if ($t1) { $comment .= "力が上がった。"; }
        if ($t2) { $comment .= "知力が上がった。"; }
        if ($t3) { $comment .= "信仰心が上がった。"; }
        if ($t4) { $comment .= "生命力が上がった。"; }
        if ($t5) { $comment .= "器用さが上がった。"; }
        if ($t6) { $comment .= "速さが上がった。"; }
        if ($t7) { $comment .= "魅力が上がった。"; }
    }

    $khp = $khp_flg + int( rand($kn_3) );
    if ( $khp > $kmaxhp ) { $khp = $kmaxhp; }
    $whp = $whp_flg + int( rand($wn_3) );
    if ( $whp > $wmaxhp ) { $whp = $wmaxhp; }
    if ( $khp <= 0 )      { $khp = $kmaxhp; }
    if ( $whp <= 0 )      { $whp = $wmaxhp; }
    $kgold = $kgold + $gold;

    # ファイルロック
    if    ( $lockkey == 1 ) { &lock1; }
    elsif ( $lockkey == 2 ) { &lock2; }
    elsif ( $lockkey == 3 ) { &file'lock; }

    if ($win) {
        @new = ();
        open( IN, ">$winner_file" );
        @winnew = <IN>;
        unshift( @new,
"$kid<>$kpass<>$ksite<>$kurl<>$kname<>$ksex<>$kchara<>$kn_0<>$kn_1<>$kn_2<>$kn_3<>$kn_4<>$kn_5<>$kn_6<>$ksyoku<>$khp<>$kmaxhp<>$kex<>$klv<>$kgold<>$klp<>$ktotal<>$kkati<>$kwaza<>$kitem<>$kmons<>$host<>$date<>$win<>$wsite<>$wurl<>$wname<>\n"
        );
        print IN @new;
        close(IN);

    }
    else {
        $wcount += 1;
        @new = ();
        open( IN, ">$winner_file" );
        @winnew = <IN>;
        unshift( @new,
"$wid<>$wpass<>$wsite<>$wurl<>$wname<>$wsex<>$wchara<>$wn_0<>$wn_1<>$wn_2<>$wn_3<>$wn_4<>$wn_5<>$wn_6<>$wsyoku<>$whp<>$wmaxhp<>$wex<>$wlv<>$wgold<>$wlp<>$wtotal<>$wkati<>$wwaza<>$witem<>$wmons<>$host<>$date<>$wcount<>$ksite<>$kurl<>$kname<>\n"
        );
        print IN @new;
        close(IN);

        open( IN, "$recode_file" );
        @recode = <IN>;
        close(IN);

        ( $count, $name ) = split( /<>/, $recode[0] );

        if ( $wcount > $count ) {
            open( OUT, ">$recode_file" );
            print OUT "$wcount<>$wname<>$wsite<>$wurl<>\n";
            close(IN);
        }
    }

    # ロック解除
    if ( $lockkey == 3 ) { &file'unlock; }
    else {
        if ( -e $lockfile ) { unlink($lockfile); }
    }

    &regist;

    if   ( $refresh and !$win ) { &header2; }
    else                        { &header; }

    print
      "<h1>$knameは、$wnameに戦いを挑んだ！！</h1><hr size=0><p>\n";

    $i = 0;
    foreach (@battle_date) {
        print "$battle_date[$i]";
        $i++;
    }

    print
"$comment<p>$knameは、<b>$exp</b>の経験値を手に入れた。<b>$gold</b>G手に入れた。<p>\n";

    &footer;

    $battle_flag = 0;

    exit;
}

#--------------#
#  クラス設定  #
#--------------#
sub class {
    if ($chara_flag) {
        if ( $ksyoku == 0 ) {
            if ( $klv > 42 ) {
                $class = $FIGHTER[6];
            }
            elsif ( $klv < 7 ) {
                $class = $FIGHTER[0];
            }
            elsif ( $klv < 14 ) {
                $class = $FIGHTER[1];
            }
            elsif ( $klv < 21 ) {
                $class = $FIGHTER[2];
            }
            elsif ( $klv < 28 ) {
                $class = $FIGHTER[3];
            }
            elsif ( $klv < 35 ) {
                $class = $FIGHTER[4];
            }
            elsif ( $klv < 42 ) {
                $class = $FIGHTER[5];
            }
        }
        elsif ( $ksyoku == 1 ) {
            if ( $klv > 42 ) {
                $class = $MAGE[6];
            }
            elsif ( $klv < 7 ) {
                $class = $MAGE[0];
            }
            elsif ( $klv < 14 ) {
                $class = $MAGE[1];
            }
            elsif ( $klv < 21 ) {
                $class = $MAGE[2];
            }
            elsif ( $klv < 28 ) {
                $class = $MAGE[3];
            }
            elsif ( $klv < 35 ) {
                $class = $MAGE[4];
            }
            elsif ( $klv < 42 ) {
                $class = $MAGE[5];
            }
        }
        elsif ( $ksyoku == 2 ) {
            if ( $klv > 42 ) {
                $class = $PRIEST[6];
            }
            elsif ( $klv < 7 ) {
                $class = $PRIEST[0];
            }
            elsif ( $klv < 14 ) {
                $class = $PRIEST[1];
            }
            elsif ( $klv < 21 ) {
                $class = $PRIEST[2];
            }
            elsif ( $klv < 28 ) {
                $class = $PRIEST[3];
            }
            elsif ( $klv < 35 ) {
                $class = $PRIEST[4];
            }
            elsif ( $klv < 42 ) {
                $class = $PRIEST[5];
            }
        }
        elsif ( $ksyoku == 3 ) {
            if ( $klv > 42 ) {
                $class = $THIEF[6];
            }
            elsif ( $klv < 7 ) {
                $class = $THIEF[0];
            }
            elsif ( $klv < 14 ) {
                $class = $THIEF[1];
            }
            elsif ( $klv < 21 ) {
                $class = $THIEF[2];
            }
            elsif ( $klv < 28 ) {
                $class = $THIEF[3];
            }
            elsif ( $klv < 35 ) {
                $class = $THIEF[4];
            }
            elsif ( $klv < 42 ) {
                $class = $THIEF[5];
            }
        }
        elsif ( $ksyoku == 4 ) {
            if ( $klv > 42 ) {
                $class = $RANGER[6];
            }
            elsif ( $klv < 7 ) {
                $class = $RANGER[0];
            }
            elsif ( $klv < 14 ) {
                $class = $RANGER[1];
            }
            elsif ( $klv < 21 ) {
                $class = $RANGER[2];
            }
            elsif ( $klv < 28 ) {
                $class = $RANGER[3];
            }
            elsif ( $klv < 35 ) {
                $class = $RANGER[4];
            }
            elsif ( $klv < 42 ) {
                $class = $RANGER[5];
            }
        }
        elsif ( $ksyoku == 5 ) {
            if ( $klv > 42 ) {
                $class = $ALCHEMIST[6];
            }
            elsif ( $klv < 7 ) {
                $class = $ALCHEMIST[0];
            }
            elsif ( $klv < 14 ) {
                $class = $ALCHEMIST[1];
            }
            elsif ( $klv < 21 ) {
                $class = $ALCHEMIST[2];
            }
            elsif ( $klv < 28 ) {
                $class = $ALCHEMIST[3];
            }
            elsif ( $klv < 35 ) {
                $class = $ALCHEMIST[4];
            }
            elsif ( $klv < 42 ) {
                $class = $ALCHEMIST[5];
            }
        }
        elsif ( $ksyoku == 6 ) {
            if ( $klv > 42 ) {
                $class = $BARD[6];
            }
            elsif ( $klv < 7 ) {
                $class = $BARD[0];
            }
            elsif ( $klv < 14 ) {
                $class = $BARD[1];
            }
            elsif ( $klv < 21 ) {
                $class = $BARD[2];
            }
            elsif ( $klv < 28 ) {
                $class = $BARD[3];
            }
            elsif ( $klv < 35 ) {
                $class = $BARD[4];
            }
            elsif ( $klv < 42 ) {
                $class = $BARD[5];
            }
        }
        elsif ( $ksyoku == 7 ) {
            if ( $klv > 42 ) {
                $class = $PSIONIC[6];
            }
            elsif ( $klv < 7 ) {
                $class = $PSIONIC[0];
            }
            elsif ( $klv < 14 ) {
                $class = $PSIONIC[1];
            }
            elsif ( $klv < 21 ) {
                $class = $PSIONIC[2];
            }
            elsif ( $klv < 28 ) {
                $class = $PSIONIC[3];
            }
            elsif ( $klv < 35 ) {
                $class = $PSIONIC[4];
            }
            elsif ( $klv < 42 ) {
                $class = $PSIONIC[5];
            }
        }
        elsif ( $ksyoku == 8 ) {
            if ( $klv > 42 ) {
                $class = $VALKYRIE[6];
            }
            elsif ( $klv < 7 ) {
                $class = $VALKYRIE[0];
            }
            elsif ( $klv < 14 ) {
                $class = $VALKYRIE[1];
            }
            elsif ( $klv < 21 ) {
                $class = $VALKYRIE[2];
            }
            elsif ( $klv < 28 ) {
                $class = $VALKYRIE[3];
            }
            elsif ( $klv < 35 ) {
                $class = $VALKYRIE[4];
            }
            elsif ( $klv < 42 ) {
                $class = $VALKYRIE[5];
            }
        }
        elsif ( $ksyoku == 9 ) {
            if ( $klv > 42 ) {
                $class = $BISHOP[6];
            }
            elsif ( $klv < 7 ) {
                $class = $BISHOP[0];
            }
            elsif ( $klv < 14 ) {
                $class = $BISHOP[1];
            }
            elsif ( $klv < 21 ) {
                $class = $BISHOP[2];
            }
            elsif ( $klv < 28 ) {
                $class = $BISHOP[3];
            }
            elsif ( $klv < 35 ) {
                $class = $BISHOP[4];
            }
            elsif ( $klv < 42 ) {
                $class = $BISHOP[5];
            }
        }
        elsif ( $ksyoku == 10 ) {
            if ( $klv > 42 ) {
                $class = $LORD[6];
            }
            elsif ( $klv < 7 ) {
                $class = $LORD[0];
            }
            elsif ( $klv < 14 ) {
                $class = $LORD[1];
            }
            elsif ( $klv < 21 ) {
                $class = $LORD[2];
            }
            elsif ( $klv < 28 ) {
                $class = $LORD[3];
            }
            elsif ( $klv < 35 ) {
                $class = $LORD[4];
            }
            elsif ( $klv < 42 ) {
                $class = $LORD[5];
            }
        }
        elsif ( $ksyoku == 11 ) {
            if ( $klv > 42 ) {
                $class = $SAMURAI[6];
            }
            elsif ( $klv < 7 ) {
                $class = $SAMURAI[0];
            }
            elsif ( $klv < 14 ) {
                $class = $SAMURAI[1];
            }
            elsif ( $klv < 21 ) {
                $class = $SAMURAI[2];
            }
            elsif ( $klv < 28 ) {
                $class = $SAMURAI[3];
            }
            elsif ( $klv < 35 ) {
                $class = $SAMURAI[4];
            }
            elsif ( $klv < 42 ) {
                $class = $SAMURAI[5];
            }
        }
        elsif ( $ksyoku == 12 ) {
            if ( $klv > 42 ) {
                $class = $MONK[6];
            }
            elsif ( $klv < 7 ) {
                $class = $MONK[0];
            }
            elsif ( $klv < 14 ) {
                $class = $MONK[1];
            }
            elsif ( $klv < 21 ) {
                $class = $MONK[2];
            }
            elsif ( $klv < 28 ) {
                $class = $MONK[3];
            }
            elsif ( $klv < 35 ) {
                $class = $MONK[4];
            }
            elsif ( $klv < 42 ) {
                $class = $MONK[5];
            }
        }
        elsif ( $ksyoku == 13 ) {
            if ( $klv > 42 ) {
                $class = $NINJA[6];
            }
            elsif ( $klv < 7 ) {
                $class = $NINJA[0];
            }
            elsif ( $klv < 14 ) {
                $class = $NINJA[1];
            }
            elsif ( $klv < 21 ) {
                $class = $NINJA[2];
            }
            elsif ( $klv < 28 ) {
                $class = $NINJA[3];
            }
            elsif ( $klv < 35 ) {
                $class = $NINJA[4];
            }
            elsif ( $klv < 42 ) {
                $class = $NINJA[5];
            }
        }
    }
    else {
        if ( $wsyoku == 0 ) {
            if ( $wlv > 42 ) {
                $class = $FIGHTER[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $FIGHTER[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $FIGHTER[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $FIGHTER[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $FIGHTER[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $FIGHTER[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $FIGHTER[5];
            }
        }
        elsif ( $wsyoku == 1 ) {
            if ( $wlv > 42 ) {
                $class = $MAGE[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $MAGE[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $MAGE[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $MAGE[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $MAGE[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $MAGE[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $MAGE[5];
            }
        }
        elsif ( $wsyoku == 2 ) {
            if ( $wlv > 42 ) {
                $class = $PRIEST[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $PRIEST[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $PRIEST[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $PRIEST[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $PRIEST[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $PRIEST[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $PRIEST[5];
            }
        }
        elsif ( $wsyoku == 3 ) {
            if ( $wlv > 42 ) {
                $class = $THIEF[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $THIEF[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $THIEF[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $THIEF[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $THIEF[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $THIEF[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $THIEF[5];
            }
        }
        elsif ( $wsyoku == 4 ) {
            if ( $wlv > 42 ) {
                $class = $RANGER[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $RANGER[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $RANGER[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $RANGER[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $RANGER[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $RANGER[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $RANGER[5];
            }
        }
        elsif ( $wsyoku == 5 ) {
            if ( $wlv > 42 ) {
                $class = $ALCHEMIST[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $ALCHEMIST[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $ALCHEMIST[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $ALCHEMIST[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $ALCHEMIST[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $ALCHEMIST[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $ALCHEMIST[5];
            }
        }
        elsif ( $wsyoku == 6 ) {
            if ( $wlv > 42 ) {
                $class = $BARD[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $BARD[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $BARD[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $BARD[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $BARD[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $BARD[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $BARD[5];
            }
        }
        elsif ( $wsyoku == 7 ) {
            if ( $wlv > 42 ) {
                $class = $PSIONIC[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $PSIONIC[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $PSIONIC[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $PSIONIC[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $PSIONIC[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $PSIONIC[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $PSIONIC[5];
            }
        }
        elsif ( $wsyoku == 8 ) {
            if ( $wlv > 42 ) {
                $class = $VALKYRIE[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $VALKYRIE[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $VALKYRIE[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $VALKYRIE[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $VALKYRIE[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $VALKYRIE[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $VALKYRIE[5];
            }
        }
        elsif ( $wsyoku == 9 ) {
            if ( $wlv > 42 ) {
                $class = $BISHOP[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $BISHOP[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $BISHOP[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $BISHOP[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $BISHOP[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $BISHOP[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $BISHOP[5];
            }
        }
        elsif ( $wsyoku == 10 ) {
            if ( $wlv > 42 ) {
                $class = $LORD[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $LORD[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $LORD[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $LORD[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $LORD[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $LORD[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $LORD[5];
            }
        }
        elsif ( $wsyoku == 11 ) {
            if ( $wlv > 42 ) {
                $class = $SAMURAI[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $SAMURAI[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $SAMURAI[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $SAMURAI[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $SAMURAI[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $SAMURAI[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $SAMURAI[5];
            }
        }
        elsif ( $wsyoku == 12 ) {
            if ( $wlv > 42 ) {
                $class = $MONK[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $MONK[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $MONK[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $MONK[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $MONK[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $MONK[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $MONK[5];
            }
        }
        elsif ( $wsyoku == 13 ) {
            if ( $wlv > 42 ) {
                $class = $NINJA[6];
            }
            elsif ( $wlv < 7 ) {
                $class = $NINJA[0];
            }
            elsif ( $wlv < 14 ) {
                $class = $NINJA[1];
            }
            elsif ( $wlv < 21 ) {
                $class = $NINJA[2];
            }
            elsif ( $wlv < 28 ) {
                $class = $NINJA[3];
            }
            elsif ( $wlv < 35 ) {
                $class = $NINJA[4];
            }
            elsif ( $wlv < 42 ) {
                $class = $NINJA[5];
            }
        }
    }
}

#----------------------#
#  モンスターとの戦闘  #
#----------------------#
sub monster {
    if ($battle_flag) {
        &error(
"現在戦闘中です。少しお待ちになってから戦闘してください。"
        );
    }

    $battle_flag = 1;

    my $chara = &chara_load( $session->param('id') )
      || &error(
"入力されたIDは登録されていません。又はパスワードが違います。"
      );
    &chara_set($chara);

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    if ( $ltime < $m_time and $ktotal ) {
        &error("$mtime秒後闘えるようになります。<br>\n");
    }

    if ( !$chara->mons ) {
        &error("一度キャラクターと闘ってください");
    }

    open( IN, "$monster_file" );
    @MONSTER = <IN>;
    close(IN);

    my $dwr = Data::WeightedRoundRobin->new();
    for my $no ( 0 .. $#MONSTER ) {
        my ( $mname, $mex, $mhp, $msp, $mdmg, $dummy ) =
          split( /<>/, $MONSTER[$no] );
        my $seed = $chara->maxhp / $mhp;
        $dwr->add( { value => $no, weight => $seed } );
    }

    $r_no = $dwr->next;

    my ( $mname, $mex, $mhp, $msp, $mdmg ) = split( /<>/, $MONSTER[$r_no] );

    if ( $in{'site'} )   { $ksite = $in{'site'}; }
    if ( $in{'url'} )    { $kurl  = $in{'url'}; }
    if ( $in{'waza'} )   { $kwaza = $in{'waza'}; }
    if ( $in{'c_name'} ) { $kname = $in{'c_name'}; }
    $khp_flg = $khp;
    $mhp     = int( rand($mhp) ) + $msp;
    $mhp_flg = $mhp;

    $i           = 1;
    $j           = 0;
    @battle_date = ();
    foreach ( 1 .. $turn ) {
        $dmg1    = $klv * ( int( rand(5) ) + 1 );
        $dmg2    = ( int( rand($mdmg) ) + 1 ) + $mdmg;
        $clit1   = "";
        $clit2   = "";
        $com1    = "";
        $com2    = "$mnameが襲いかかった！！";
        $kawasi1 = "";
        $kawasi2 = "";

        # 挑戦者ダメージ計算
        if ( $ksyoku == 0 ) {
            $dmg1 = $dmg1 + int( rand($kn_0) );
            $com1 = "$knameは、剣で切りつけた！！<p>";
        }
        elsif ( $ksyoku == 1 ) {
            $dmg1 = $dmg1 * int( rand($kn_1) );
            $com1 = "$knameは、魔法を唱えた！！<p>";
        }
        elsif ( $ksyoku == 2 ) {
            $dmg1 = $dmg1 * int( rand($kn_2) );
            $com1 = "$knameは、魔法を唱えた！！<p>";
        }
        elsif ( $ksyoku == 3 ) {
            $dmg1 = $dmg1 + int( rand($kn_4) );
            $com1 = "$knameは、背後から切りつけた！！<p>";
        }
        elsif ( $ksyoku == 4 ) {
            $dmg1 = $dmg1 + int( rand($kn_3) ) + int( rand($kn_0) );
            $com1 = "$knameは、弓で攻撃！！<p>";
        }
        elsif ( $ksyoku == 5 ) {
            $dmg1 = $dmg1 * ( int( rand($kn_1) ) + int( rand($kn_4) ) );
            $com1 = "$knameは、魔法を唱えた！！<p>";
        }
        elsif ( $ksyoku == 6 ) {
            $dmg1 = $dmg1 * ( int( rand($kn_1) ) + int( rand($kn_4) ) );
            $com1 = "$knameは、呪歌を歌った！！<p>";
        }
        elsif ( $ksyoku == 7 ) {
            $dmg1 = $dmg1 * ( int( rand($kn_1) ) + int( rand($kn_3) ) );
            $com1 = "$knameは、超能力を使った！！<p>";
        }
        elsif ( $ksyoku == 8 ) {
            $dmg1 = $dmg1 * ( int( rand($kn_1) ) + int( rand($kn_2) ) );
            $com1 =
"$knameは、精霊魔法と、神聖魔法を同時に唱えた！！<p>";
        }
        elsif ( $ksyoku == 9 ) {
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) );
            $com1 = "$knameは、槍を突き刺した！！<p>";
        }
        elsif ( $ksyoku == 10 ) {
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) );
            $com1 =
"$knameは、神聖魔法を唱えつつ、剣で切りつけた！！<p>";
        }
        elsif ( $ksyoku == 11 ) {
            $dmg1 = $dmg1 + int( rand($kn_4) ) + int( rand($kn_5) );
            $com1 = "$knameは、見えない速さで切りつけた！！<p>";
        }
        elsif ( $ksyoku == 12 ) {
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) );
            $com1 = "$knameは、殴りつけた！！<p>";
        }
        elsif ( $ksyoku == 13 ) {
            $dmg1 = $dmg1 + int( rand($kn_0) ) + int( rand($kn_2) );
            $com1 = "$knameは、蹴りつけた！！<p>";
        }

        if ( int( rand(20) ) == 0 ) {
            $clit1 =
"<font size=5>$kname「<b>$kwaza</b>」</font><p><b class=\"clit\">クリティカル！！</b>";
            $dmg1 = $dmg1 * 2;
        }

        if ( int( rand(30) ) == 0 ) {
            $clit2 = "<b class=\"clit\">クリティカル！！</b>";
            $dmg2  = int( $dmg2 * 1.5 );
        }

        $battle_date[$j] = <<"EOM";
<TABLE BORDER=0>
<TR>
    <TD CLASS="b2" COLSPAN="3" ALIGN="center">
    $iターン
    </TD>
</TR>
<TR>
<TD>
<TABLE BORDER=1>
<TR>
    <TD CLASS="b1">
    なまえ
    </TD>
    <TD CLASS="b1">
    HP
    </TD>
    <TD CLASS="b1">
    職業
    </TD>
    <TD CLASS="b1">
    LV
    </TD>
</TR>
<TR>
    <TD>
    $kname
    </TD>
    <TD>
    $khp_flg\/$kmaxhp
    </TD>
    <TD>
    $chara_syoku[$ksyoku]
    </TD>
    <TD>
    $klv
    </TD>
</TR>
</TABLE>
</TD>
<TD>
<FONT SIZE=5 COLOR="#9999DD">VS</FONT>
</TD>
<TD>
<TABLE BORDER=1>
<TR>
    <TD CLASS="b1">
    なまえ
    </TD>
    <TD CLASS="b1">
    HP
    </TD>
</TR>
<TR>
    <TD>
    $mname
    </TD>
    <TD>
    $mhp/$mhp_flg
    </TD>
</TR>
</TABLE>
</TD>
</TR>
</TABLE>
<p>
$com1 $clit1 $kawasi2 $mname に <font class="dmg"><b>$dmg1</b></font> のダメージを与えた。<p>
$com2 $clit2 $kawasi1 $kname に <font class="dmg"><b>$dmg2</b></font> のダメージを与えた。<p>
EOM

        $khp_flg = $khp_flg - $dmg2;
        $mhp     = $mhp - $dmg1;

        if    ( $mhp <= 0 )     { $win = 1; last; }
        elsif ( $khp_flg <= 0 ) { $win = 0; last; }

        $i++;
        $j++;
    }

    if ($win) {
        $ktotal += 1;
        $kkati  += 1;
        $kex = $kex + $mex;
        $kmons -= 1;
        $gold  = $klv * 10 + int( rand($klp) );
        $kgold = $kgold + $gold;
        $comment =
"<b><font size=5>$knameは、戦闘に勝利した！！</font></b><p>";
    }
    else {
        $ktotal += 1;
        $mex = int( rand($klp) );
        $kex = $kex + $mex;
        $kmons -= 1;
        if   ($kgold) { $kgold = int( $kgold / 2 ); }
        else          { $kgold = 0; }
        $comment =
"<b><font size=5>$knameは、戦闘に負けた・・・。</font></b><p>";
    }

    if ( $kex > ( $klv * $lv_up ) ) {
        $comment .= "$knameは、レベルが上がった！！<p>";
        $kmaxhp = $kmaxhp + int( rand($kn_3) ) + 1;
        $khp    = $kmaxhp;
        $kex    = 0;
        $klv += 1;
        if ( int( rand(5) ) == 0 ) { $kn_0 += 1; $t1 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_1 += 1; $t2 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_2 += 1; $t3 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_3 += 1; $t4 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_4 += 1; $t5 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_5 += 1; $t6 = 1; }
        if ( int( rand(5) ) == 0 ) { $kn_6 += 1; $t7 = 1; }
        if ($t1) { $comment .= "力が上がった。"; }
        if ($t2) { $comment .= "知力が上がった。"; }
        if ($t3) { $comment .= "信仰心が上がった。"; }
        if ($t4) { $comment .= "生命力が上がった。"; }
        if ($t5) { $comment .= "器用さが上がった。"; }
        if ($t6) { $comment .= "速さが上がった。"; }
        if ($t7) { $comment .= "魅力が上がった。"; }
    }

    $khp = $khp_flg + int( rand($kn_3) );
    if ( $khp > $kmaxhp ) { $khp = $kmaxhp; }
    if ( $khp <= 0 )      { $khp = $kmaxhp; }

    &regist;

    &header;

    print
      "<h1>$knameは、$mnameに戦いを挑んだ！！</h1><hr size=0><p>\n";

    $i = 0;
    foreach (@battle_date) {
        print "$battle_date[$i]";
        $i++;
    }

    if ($win) {
        print
"$comment<p>$knameは、$mexの経験値を手に入れた。<b>$gold</b>G手に入れた。<p>\n";
    }
    else {
        print
"$comment<p>$knameは、$mexの経験値を手に入れた。お金が半分になった。<p>\n";
    }

    &footer;

    $battle_flag = 0;

    exit;
}

#----------------#
#  ホスト名取得  #
#----------------#
sub get_host {
    $host = $ENV{'REMOTE_HOST'};
    $addr = $ENV{'REMOTE_ADDR'};

    if ($get_remotehost) {
        if ( $host eq "" || $host eq "$addr" ) {
            $host = gethostbyaddr( pack( "C4", split( /\./, $addr ) ), 2 );
        }
    }
    if ( $host eq "" ) { $host = $addr; }
}

#--------------#
#  エラー処理  #
#--------------#
sub error {

    # ロック解除
    if ( $lockkey == 3 ) { &file'unlock; }
    else {
        if ( -e $lockfile ) { unlink($lockfile); }
    }
    $battle_flag = 0;

    &header;
    print "<center><hr width=400><h3>ERROR !</h3>\n";
    print "<P><font color=red><B>$_[0]</B></font>\n";
    print "<P><hr width=400></center>\n";
    &footer();
    exit;
}

#------------------#
#　HTMLのフッター　#
#------------------#
sub footer {
    if ( $refresh and !$win and $mode eq 'battle' ) {
        print
"【<b><a href=\"http\:\/\/$wurl\">チャンプのホームページへ</a></b>】\n";
    }
    else {
        if ( $mode ne "" ) {
            print "<a href=\"$script_url\">TOPページへ</a>\n";
        }
        if ( !$session->is_empty() ) {
            print
" / <a href=\"$script_url?mode=log_in\">ステータス画面へ</a>\n";
            print
              " / <a href=\"$script_url?mode=log_out\">ログアウト</a>\n";
        }
    }
    print "<HR SIZE=0 WIDTH=\"100%\"><DIV align=right class=small>\n";
    print
"$ver by <a href=\"http://www.interq.or.jp/sun/cumro/\">D.Takamiya(CUMRO)</a><br>\n";
    print
"Character Image by <a href=\"http://www.aas.mtci.ne.jp/~hiji/9ff/9ff.html\">9-FFいっしょにTALK</a><br>\n";
    print
"cooperation site by <a href=\"http://webooo.csidenet.com/asvyweb/\">FFADV推奨委員会</a>\n";
    print "</DIV>\n";

    if ( $mode eq 'log_in' and $ltime < $b_time and $ktotal ) {
        print <<"EOM";
<SCRIPT language="JavaScript">
<!--
window.setTimeout('CountDown()',100);
//-->
</SCRIPT>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js" integrity="sha384-h0AbiXch4ZDo7tp9hKZ4TsHbi047NrKGLO3SEJAg45jXxnGIfYzk4Si90RDIqNm1" crossorigin="anonymous"></script>
EOM
    }
    print "</body></html>\n";
}

#------------------#
#  HTMLのヘッダー  #
#------------------#
sub header {
    print $session->header( '-charset' => 'UTF-8' );
    print <<"EOM";
<html>
<head>
<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=UTF-8">
EOM

    if ( $mode eq 'top' and $ltime < $b_time and $ktotal ) {
        print <<"EOM";
<META HTTP-EQUIV="Refresh" CONTENT="$vtime">
<SCRIPT LANGUAGE="JavaScript">
<!--
    var start=new Date();
    start=Date.parse(start)/1000;
    var counts=$vtime;
    function CountDown(){
        var now=new Date();
        now=Date.parse(now)/1000;
        var x=parseInt(counts-(now-start),10);
        if(document.form1){document.form1.clock.value = x;}
        if(x>0){
            timerID=setTimeout("CountDown()", 100)
        }else{
            location.href="$script_url?mode=top"
        }
    }
//-->
</SCRIPT>
EOM
    }
    print <<"EOM";
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
EOM
    say <<EOF;
<style>
.int { text-align: right }
</style>
EOF
    print "<title>$main_title</title></head>\n";
    print
"<body background=\"$backgif\" bgcolor=\"$bgcolor\" text=\"$text\" link=\"$link\" vlink=\"$vlink\" alink=\"$alink\">\n";
}

#--------------#
#  強制送還用  #
#--------------#
sub header2 {
    print $session->header( '-charset' => 'UTF-8' );
    print <<"EOM";
<html>
<head>
<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=UTF-8">
<META http-equiv="refresh" content="$refresh;URL=http\:\/\/$wurl"> 
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
EOM
    print "<title>$main_title</title></head>\n";
    print
"<body background=\"$backgif\" bgcolor=\"$bgcolor\" text=\"$text\" link=\"$link\" vlink=\"$vlink\" alink=\"$alink\">\n";
}

#----------------#
#  デコード処理  #
#----------------#
sub decode2 {
    for my $key ( $cgi->param() ) {
        $in{$key} = $cgi->param($key);
    }
    if ( $ENV{'REQUEST_METHOD'} eq "POST" ) {
        if ( $ENV{'CONTENT_LENGTH'} > 51200 ) {
            &error("投稿量が大きすぎます");
        }
        read( STDIN, $buffer, $ENV{'CONTENT_LENGTH'} );
    }
    else { $buffer = $ENV{'QUERY_STRING'}; }
    @pairs = split( /&/, $buffer );
    foreach (@pairs) {
        ( $name, $value ) = split( /=/, $_ );
        $value =~ tr/+/ /;
        $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

        # 文字コードをシフトJIS変換
        # &jcode'convert(*value, "sjis", "", "z");

        # タグ処理
        $value =~ s/</&lt;/g;
        $value =~ s/>/&gt;/g;
        $value =~ s/\"/&quot;/g;

        # 改行等処理
        $value =~ s/\r//g;
        $value =~ s/\n//g;

        # 一括削除用
        if ( $name eq 'del' ) { push( @DEL, $value ); }

        $in{$name} = $value;
    }
    $mode = $in{'mode'};
    $in{'url'} =~ s/^http\:\/\///;
    $cookie_pass = $in{'pass'};
    $cookie_id   = $in{'id'};
}

#-------------------------------#
#  ロックファイル：symlink関数  #
#-------------------------------#
sub lock1 {
    local ($retry) = 5;
    while ( !symlink( ".", $lockfile ) ) {
        if ( --$retry <= 0 ) { &error("LOCK is BUSY"); }
        sleep(1);
    }
}

#----------------------------#
#  ロックファイル：open関数  #
#----------------------------#
sub lock2 {
    local ($retry) = 0;
    foreach ( 1 .. 5 ) {
        if ( -e $lockfile ) { sleep(1); }
        else {
            open( LOCK, ">$lockfile" ) || &error("Can't Lock");
            close(LOCK);
            $retry = 1;
            last;
        }
    }
    if ( !$retry ) {
        &error("しばらくお待ちになってください(^^;)");
    }
}

#--------------#
#  時間を取得  #
#--------------#
sub get_time {
    my $time = shift || time;
    $ENV{TZ} = 'JST-9';
    my ( $sec, $min, $hour, $mday, $mon, $year, $wday ) = localtime($time);
    my @week = ( 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' );

    # 日時のフォーマット
    my $gettime = sprintf(
        "%04d/%02d/%02d %02d:%02d",
        $year + 1900,
        $mon + 1, $mday, $hour, $min
    );
    return $gettime;
}

#ファイルのロック
sub file'lock {
    local ( $lockfile, $locktest ) = @_;
    $locktest =
      ( $locktest > 0 ? $locktest : 4 );    #０以下なら標準で４回
    $locktest =
      ( $locktest < 8 ? $locktest : 8 );    #最大で８回までとする

    $file'lockflag = 0;
    $file'lockfile = $lockfile;    #本来のロックファイルの名前
    $file'lock_sw0 =
      $lockfile . ".sw0";    #最新日時のロックファイル作成用
    $file'lock_sw1 =
      $lockfile . ".sw1";    #ロックされている状態の名前

    ( -l $lockfile ) && &file'error(0);
    ( -d $lockfile ) && &file'error(0);

#ロックファイルを置くサーバーの現在時刻を取得(timeではだめ)
    $locktemp = $lockfile . ".$$";
    open( LOCK, ">$locktemp" ) || return (0);
    close(LOCK);
    $time = ( stat($locktemp) )[9];
    unlink($locktemp);

#作成されてから$lock_limit秒以上経過しているロックファイルの名前を戻す
    if (   ( -f $file'lock_sw1 )
        && ( $time - ( stat($file'lock_sw1) )[9] > $lock_limit ) )
    {
        rename( $file'lock_sw1, $file'lockfile ) || return (0);
    }

    #ロックファイルの作成日時更新
    open( LOCK, ">$file'lock_sw0" ) || &file'error(2);
    close(LOCK);
    rename( $file'lock_sw0, $file'lockfile ) || return (0);

    ( -f $file'lock_sw1 ) && return (0);

    #ロック権の取得
    while ( ( $file'lockflag = rename( $file'lockfile, $file'lock_sw1 ) ) == 0
        && $lock_try )
    {
        #0.03, [0.07, 0.13, 0.17], 0.23
        select( undef, undef, undef, 0.13 );
        $lock_try--;
    }
    $file'lockflag;
}

#ファイルのアンロック
sub file'unlock {
    if ($file'lockflag) {
        rename( $file'lock_sw1, $file'lockfile );

        #0.03, [0.07, 0.13, 0.17], 0.23
        select( undef, undef, undef, 0.03 );
    }
}

sub file'error {
    local (@error) = (
"ロックシンボルの作成を中止しました<br>\n(ロックシンボル以外で同名称が存在)<br>\n",
        "ロックシンボルの作成に失敗しました<br>\n",
        "ロックシンボルの更新に失敗しました<br>\n",
        "ロックシンボルの削除に失敗しました<br>\n",
        $_[1],
    );

    select(STDOUT);
    $| = 1;
    print "$error[$_[0]]\n";
    exit;
}
