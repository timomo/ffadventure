#!/usr/bin/perl --

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

#================================================================#
#┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓#
#┃ これより下はCGIに自信のある方以外は扱わないほうが無難です　┃#
#┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛#
#================================================================#

#--------------#
#　メイン処理　#
#--------------#
if($mente) { &error("現在メンテナンス中です。しばらくお待ちください。"); }
&decode;
if($mode eq "") { &html_top; }
elsif($mode eq 'log_in') { &log_in; }
elsif($mode eq 'chara_make') { &chara_make; }
elsif($mode eq 'make_end') { &make_end; }
elsif($mode eq 'regist') { &regist; }
elsif($mode eq 'battle') { &battle; }
elsif($mode eq 'tensyoku') { &tensyoku; }
elsif($mode eq 'monster') { &monster; }
elsif($mode eq 'ranking') { &ranking; }
elsif($mode eq 'yado') { &yado; }
elsif($mode eq 'message') { &message; }
elsif($mode eq 'item_shop') { &item_shop; }
elsif($mode eq 'item_buy') { &item_buy; }
&html_top;

#-----------------#
#  TOPページ表示  #
#-----------------#
sub html_top {
    &read_winner;

    &get_cookie;

    &class;

    if($wkati) { $ritu = int(($wkati / $wtotal) * 100); }
    else { $ritu = 0; }

    open(IN,"$recode_file");
    @recode = <IN>;
    close(IN);

    ($rcount,$rname,$rsite,$rurl) = split(/<>/,$recode[0]);

    if($wsex) { $esex = "男"; } else { $esex = "女"; }
    $next_ex = $wlv * $lv_up;

    if($witem){
        open(IN,"$item_file");
        @battle_item = <IN>;
        close(IN);

        foreach(@battle_item){
            ($wi_no,$wi_name,$wi_dmg) = split(/<>/);
            if($witem eq $wi_no) { last; }
        }
    }else{ $wi_name = "なし"; }

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
    <td><input type="text" size="10" name="id" value="$c_id"></td>
    <td class=b1>パスワード</td>
    <td><input type="password" size="10" name="pass" value="$c_pass"></td>
    <td><input type="submit" value="ログイン"></td>
    </tr>
    </table>
</td>
</tr>
</table>
<hr size=0>
<small>
/ <a href="$homepage">$home_title</a> / <a href="$script_url?mode=item_shop">武器屋</a> / <a href="$script_url?mode=ranking">英雄たちの記録</a> / <a href="$syoku_html">各職業に必要な特性値</a> / <a href="http://cgi.members.interq.or.jp/sun/cumro/cgi-bin/idea/wwwlng.cgi">アイデア募集</a> /
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
    if($rurl eq "$wurl") {
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
    <td colspan=5 align="center">$lname の <A HREF=\"http\:\/\/$lurl\" TARGET=\"_blank\">$lsite</A> に勝利！！</td>
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
    open(IN,"$chara_file");
    @RANKING = <IN>;
    close(IN);

    $sousu = @RANKING;

    @tmp1 = @tmp2 = ();
    foreach (@RANKING) {
         my ($aa,$bb,$cc,$dd,$ee,$ff,$gg,$hh,$ii,$jj,$kk,$ll,$mm,$nn,$oo,$pp,$qq,$second,$first) = split /<>/;
         push(@tmp1, $first);
         push(@tmp2, $second);
    }
    @RANKING = @RANKING[sort {$tmp1[$b] <=> $tmp1[$a] or
            $tmp2[$b] <=> $tmp2[$a]} 0 .. $#tmp1];

    $ima = time();

    &header;

    print <<"EOM";
<h1>英雄たちの記録</h1><hr size=0>
現在登録されているキャラクター<b>$sousu</b>人中レベルTOP<b>$rank_top</b>を表\示しています。
<p>
<table border=1>
<tr>
<th></th><th>なまえ</th><th>職業</th><th>ホームページ</th><th>レベル</th><th>経験値</th><th>HP</th><th>力</th><th>削除まで</th>
</tr>
EOM

    $i=1;
    foreach(@RANKING){
        ($rid,$rpass,$rsite,$rurl,$rname,$rsex,$rchara,$rn_0,$rn_1,$rn_2,$rn_3,$rn_4,$rn_5,$rn_6,$rsyoku,$rhp,$rmaxhp,$rex,$rlv,$rgold,$rlp,$rtotal,$rkati,$rwaza,$ritem,$rmons,$rhost,$rdate) = split(/<>/);
        if($i > $rank_top) { last; }
        $rdate = $rdate + (60*60*24*$limit);
        $niti = $rdate - $ima;
        $niti = int($niti / (60*60*24));
        print "<tr>\n";
        print "<td align=center>$i</td><td>$rname</td><td>$chara_syoku[$rsyoku]</td><td><a href=\"http\:\/\/$rurl\">$rsite</a></td><td align=center>$rlv</td><td align=center>$rex</td><td align=center>$rhp\/$rmaxhp</td><td align=center>$rn_0</td><td align=center>あと$niti日</td>\n";
        print "</tr>\n";
        $i++;
    }

    print "</table><p>\n";

    &footer;

    exit;
}

#----------------#
#  アイテム表示  #
#----------------#
sub item_shop {
    open(IN,"$item_file");
    @item_array = <IN>;
    close(IN);

    &header;

    print <<"EOM";
<h1>アイテムショップ</h1>
<hr size=0>
<p>
<form action="$script_url" method="post">
買いたいアイテムをチェックし、あなたのIDとパスワードを入力してください。
<table border=1>
<tr>
<th></th><th>No.</th><th>なまえ</th><th>威力</th><th>価格</th>
EOM

    foreach(@item_array){
        ($ino,$iname,$idmg,$igold) = split(/<>/);
        print "<tr>\n";
        print "<td><input type=radio name=item_no value=\"$ino\"></td><td align=right>$ino</td><td>$iname</td><td align=center>$idmg</td><td align=center>$igold</td>\n";
        print "</tr>\n";
    }

    print <<"EOM";
</tr>
</table>
<p>
あなたのキャラクターのIDとパスワードを入力してボタンを押してください。<br>
ID：<input type=text name=id size=10>
PASS：<input type=text name=pass size=10>
<input type=hidden name=mode value=item_buy>
<input type=submit value="アイテムを買う">
</form>
EOM

    &footer;

    exit;
}

#----------------#
#  アイテム買う  #
#----------------#
sub item_buy {
    if($in{'id'} eq "") {
        &error("IDが入力されていません。");
    }elsif($in{'pass'} eq ""){
        &error("パスワードが入力されていません。");
    }elsif($in{'item_no'} eq ""){
        &error("アイテムを選んでください。");
    }
    $item_id = $in{'id'};
    $item_pass = $in{'pass'};

    open(IN,"$item_file");
    @item_array = <IN>;
    close(IN);

    $hit=0;
    foreach(@item_array){
        ($i_no,$i_name,$i_dmg,$i_gold) = split(/<>/);
        if($in{'item_no'} eq "$i_no") { $hit=1;last; }
    }
    if(!$hit) { &error("そんなアイテムは存在しません"); }

    &get_host;

    $date = time();

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$chara_file");
    @item_chara = <IN>;
    close(IN);

    $hit=0;@item_new=();
    foreach(@item_chara){
        ($iid,$ipass,$isite,$iurl,$iname,$isex,$ichara,$in_0,$in_1,$in_2,$in_3,$in_4,$in_5,$in_6,$isyoku,$ihp,$imaxhp,$iex,$ilv,$igold,$ilp,$itotal,$ikati,$iwaza,$iitem,$imons,$ihost,$idate) = split(/<>/);
        if($iid eq "$item_id") {
            if($igold < $i_gold) { &error("お金が足りません"); }
            else { $igold = $igold - $i_gold; }
            unshift(@item_new,"$iid<>$ipass<>$isite<>$iurl<>$iname<>$isex<>$ichara<>$in_0<>$in_1<>$in_2<>$in_3<>$in_4<>$in_5<>$in_6<>$isyoku<>$imaxhp<>$imaxhp<>$iex<>$ilv<>$igold<>$ilp<>$itotal<>$ikati<>$iwaza<>$i_no<>$imons<>$host<>$idate<>\n");
            $hit=1;
        }else{
            push(@item_new,"$_");
        }
    }

    if(!$hit) { &error("キャラクターが見つかりません"); }

    open(OUT,">$chara_file");
    print OUT @item_new;
    close(OUT);

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    &header;

    print <<"EOM";
<h1>アイテムを買いました</h1>
<hr size=0>
<p>
<form action="$script_url" method="post">
<input type=hidden name=id value="$item_id">
<input type=hidden name=pass value="$item_pass">
<input type=hidden name=mode value=log_in>
<input type=submit value="ステータス画面へ">
</form>
EOM

    &footer;

    exit;
}

#------------#
#  体力回復  #
#------------#
sub yado {
    &get_host;

    $date = time();

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$chara_file");
    @YADO = <IN>;
    close(IN);

    $hit=0;@yado_new=();
    foreach(@YADO){
        ($yid,$ypass,$ysite,$yurl,$yname,$ysex,$ychara,$yn_0,$yn_1,$yn_2,$yn_3,$yn_4,$yn_5,$yn_6,$ysyoku,$yhp,$ymaxhp,$yex,$ylv,$ygold,$ylp,$ytotal,$ykati,$ywaza,$yitem,$ymons,$yhost,$ydate) = split(/<>/);
        if($in{'id'} eq "$yid") {
            $yado_gold = $yado_dai * $ylv;
            if($ygold < $yado_gold) { &error("お金が足りません"); }
            else { $ygold = $ygold - $yado_gold; }
            unshift(@yado_new,"$yid<>$ypass<>$ysite<>$yurl<>$yname<>$ysex<>$ychara<>$yn_0<>$yn_1<>$yn_2<>$yn_3<>$yn_4<>$yn_5<>$yn_6<>$ysyoku<>$ymaxhp<>$ymaxhp<>$yex<>$ylv<>$ygold<>$ylp<>$ytotal<>$ykati<>$ywaza<>$yitem<>$ymons<>$host<>$ydate<>\n");
        }else{
            push(@yado_new,"$_");
        }
    }

    open(OUT,">$chara_file");
    print OUT @yado_new;
    close(OUT);

    &read_winner;

    if($wid eq "$in{'id'}") {
        open(OUT,">$winner_file");
        print OUT "$wid<>$wpass<>$wsite<>$wurl<>$wname<>$wsex<>$wchara<>$wn_0<>$wn_1<>$wn_2<>$wn_3<>$wn_4<>$wn_5<>$wn_6<>$wsyoku<>$wmaxhp<>$wmaxhp<>$wex<>$wlv<>$wgold<>$wlp<>$wtotal<>$wkati<>$wwaza<>$witem<>$wmons<>$host<>$ydate<>$wcount<>$lsite<>$lurl<>$lname<>\n";
        close(OUT);
    }

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    &header;

    print <<"EOM";
<h1>体力を回復しました</h1>
<hr size=0>
<form action="$script_url" method="post">
<input type=hidden name=mode value=log_in>
<input type=hidden name=id value="$in{'id'}">
<input type=hidden name=pass value="$in{'pass'}">
<input type=submit value="ステータス画面へ">
</form>
EOM

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

    $i=0;
    foreach(@chara_name){
        print "<option value=\"$i\">$chara_name[$i]\n";
        $i++;
    }

    print <<"EOM";
</select><br><small>△作成するキャラクターの性別を選択してください。</small></td>
</tr>
<tr>
<td class="b1">キャラクターの能\力</td>
<td>
    <table border=1>
    <tr>
    <td class="b2" width="70">力</td><td class="b2" width="70">知能\</td><td class="b2" width="70">信仰心</td><td class="b2" width="70">生命力</td><td class="b2" width="70">器用さ</td><td class="b2" width="70">速さ</td><td class="b2" width="70">魅力</td>
    </tr>
    <tr>
EOM

    $point = int(rand(10));
    $point+=4;

    $i=0;$j=0;
    foreach(0..6){
        print "<td>$kiso_nouryoku[$i] + <select name=n_$i>\n";
        foreach(0..$point){
            print "<option value=\"$j\">$j\n";
            $j++;
        }
        print "</select>\n";
        print "</td>\n";
        $i++;$j=0;
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
<input type="hidden" name=point value="$point">
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
    if($chara_stop){ &error("現在キャラクターの作成登録はできません"); }
    if ($in{'id'} =~ m/[^0-9a-zA-Z]/)
    {&error("IDに半角英数字以外の文字が含まれています。"); }
    if ($in{'pass'} =~ m/[^0-9a-zA-Z]/)
    {&error("パスワードに半角英数字以外の文字が含まれています。"); }
    # 職業未選択の場合
        if($in{'syoku'} eq "") {
        if($in{'id'} eq "" or length($in{'id'}) < 4 or length($in{'id'}) > 8) { &error("IDは、4文字以上、8文字以下で入力して下さい。"); }
        elsif($in{'pass'} eq "" or length($in{'pass'}) < 4 or length($in{'pass'}) > 8) { &error("パスワードは、4文字以上、8文字以下で入力して下さい。"); }
        elsif($in{'site'} eq "") { &error("ホームページ名が未記入です"); }
        elsif($in{'url'} eq "") { &error("URLが未記入です"); }
        elsif($in{'c_name'} eq "") { &error("キャラクターの名前が未記入です"); }
        elsif($in{'sex'} eq "") { &error("性別が選択されていません"); }

        $g = $in{'n_0'} + $in{'n_1'} + $in{'n_2'} + $in{'n_3'} + $in{'n_4'} + $in{'n_5'} + $in{'n_6'};

        if($g > $in{'point'}) { &error("ポイントの振り分けが多すぎます。振り分けの合計を、$in{'point'}以下にしてください。"); }

        &header;

        print "<h1>職業選択画面</h1><hr size=0>\n";
        print "あなたがなることができる職業は以下のとおりです。<p>\n";
        print "<form action=\"$script_url\" method=\"post\">\n";
        print "<input type=hidden name=mode value=regist>\n";
        print "<select name=syoku>\n";
        print "<option value=0>$chara_syoku[0]\n";

        if($in{'n_1'} + $kiso_nouryoku[1] > 11) {
            print "<option value=1>$chara_syoku[1]\n";
        }
        if($in{'n_2'} + $kiso_nouryoku[2] > 11 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=2>$chara_syoku[2]\n";
        }
        if($in{'n_4'} + $kiso_nouryoku[4] > 11 and $in{'n_5'} + $kiso_nouryoku[5] > 7) {
            print "<option value=3>$chara_syoku[3]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 9 and $in{'n_1'} + $kiso_nouryoku[1] > 7 and $in{'n_2'} + $kiso_nouryoku[2] > 7 and $in{'n_3'} + $kiso_nouryoku[3] > 10 and $in{'n_4'} + $kiso_nouryoku[4] > 9 and $in{'n_5'} + $kiso_nouryoku[5] > 7 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=4>$chara_syoku[4]\n";
        }
        if($in{'n_1'} + $kiso_nouryoku[1] > 12 and $in{'n_4'} + $kiso_nouryoku[4] > 12) {
            print "<option value=5>$chara_syoku[5]\n";
        }
        if($in{'n_1'} + $kiso_nouryoku[1] > 9 and $in{'n_4'} + $kiso_nouryoku[4] > 11 and $in{'n_5'} + $kiso_nouryoku[5] > 7 and $in{'n_6'} + $kiso_nouryoku[6] > 11) {
            print "<option value=6>$chara_syoku[6]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 9 and $in{'n_1'} + $kiso_nouryoku[1] > 13 and $in{'n_3'} + $kiso_nouryoku[3] > 13 and $in{'n_6'} + $kiso_nouryoku[6] > 9) {
            print "<option value=7>$chara_syoku[7]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 9 and $in{'n_2'} + $kiso_nouryoku[2] > 10 and $in{'n_3'} + $kiso_nouryoku[3] > 10 and $in{'n_4'} + $kiso_nouryoku[4] > 9 and $in{'n_5'} + $kiso_nouryoku[5] > 10 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=8>$chara_syoku[8]\n";
        }
        if($in{'n_1'} + $kiso_nouryoku[1] > 14 and $in{'n_2'} + $kiso_nouryoku[2] > 14 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=9>$chara_syoku[9]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 11 and $in{'n_1'} + $kiso_nouryoku[1] > 8 and $in{'n_2'} + $kiso_nouryoku[2] > 11 and $in{'n_3'} + $kiso_nouryoku[3] > 11 and $in{'n_4'} + $kiso_nouryoku[4] > 8 and $in{'n_5'} + $kiso_nouryoku[5] > 8 and $in{'n_6'} + $kiso_nouryoku[6] > 13) {
            print "<option value=10>$chara_syoku[10]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 11 and $in{'n_1'} + $kiso_nouryoku[1] > 10 and $in{'n_3'} + $kiso_nouryoku[3] > 8 and $in{'n_4'} + $kiso_nouryoku[4] > 11 and $in{'n_5'} + $kiso_nouryoku[5] > 13 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=11>$chara_syoku[11]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 12 and $in{'n_1'} + $kiso_nouryoku[1] > 7 and $in{'n_2'} + $kiso_nouryoku[2] > 12 and $in{'n_4'} + $kiso_nouryoku[4] > 9 and $in{'n_5'} + $kiso_nouryoku[5] > 12 and $in{'n_6'} + $kiso_nouryoku[6] > 7) {
            print "<option value=12>$chara_syoku[12]\n";
        }
        if($in{'n_0'} + $kiso_nouryoku[0] > 11 and $in{'n_1'} + $kiso_nouryoku[1] > 9 and $in{'n_2'} + $kiso_nouryoku[2] > 9 and $in{'n_3'} + $kiso_nouryoku[3] > 11 and $in{'n_4'} + $kiso_nouryoku[4] > 11 and $in{'n_5'} + $kiso_nouryoku[5] > 11) {
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
    }else{
        if($in{'sex'}) { $esex = "男"; } else { $esex = "女"; }
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
    &set_cookie;

    &get_host;

    $date = time();

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$chara_file");
    @regist = <IN>;
    close(IN);

    $hit=0;@new=();
    foreach(@regist){
        ($cid,$cpass,$csite,$curl,$cname,$csex,$cchara,$cn_0,$cn_1,$cn_2,$cn_3,$cn_4,$cn_5,$cn_6,$csyoku,$chp,$cmaxhp,$cex,$clv,$cgold,$clp,$ctotal,$ckati,$cwaza,$citem,$cmons,$chost,$cdate) = split(/<>/);
        if($cid eq "$in{'id'}" and $in{'new'} eq 'new') {
            &error("そのIDはすでに登録されています");
        }elsif($curl eq "$in{'url'}" and $in{'new'} eq 'new'){
            &error("そのURLはすでに登録されています");
        }elsif($host eq "$chost" and $in{'new'} eq 'new'){
            &error("一人り一キャラクターです。守れない場合アクセス制限をかけさせていただきます。このエラーを出したあなたのIPアドレスを保存しています。");
        }elsif($cid eq "$kid"){
            unshift(@new,"$kid<>$kpass<>$ksite<>$kurl<>$kname<>$ksex<>$kchara<>$kn_0<>$kn_1<>$kn_2<>$kn_3<>$kn_4<>$kn_5<>$kn_6<>$ksyoku<>$khp<>$kmaxhp<>$kex<>$klv<>$kgold<>$klp<>$ktotal<>$kkati<>$kwaza<>$kitem<>$kmons<>$host<>$date<>\n");
            $hit=1;
        }else{
            if(($date - $cdate) > (60 * 60 * 24 * $limit)) { next; }
            push(@new,"$_");
        }
    }

    if(!$hit and $in{'new'} eq 'new'){
        $lp=int(rand(15));
        $hp = int(($in{'n_3'} + $kiso_nouryoku[3]) + (rand($lp) + 1)) + $kiso_hp;
        $ex=0;
        $lv=1;
        $gold=0;
        $n_0 = $kiso_nouryoku[0] + $in{'n_0'};
        $n_1 = $kiso_nouryoku[1] + $in{'n_1'};
        $n_2 = $kiso_nouryoku[2] + $in{'n_2'};
        $n_3 = $kiso_nouryoku[3] + $in{'n_3'};
        $n_4 = $kiso_nouryoku[4] + $in{'n_4'};
        $n_5 = $kiso_nouryoku[5] + $in{'n_5'};
        $n_6 = $kiso_nouryoku[6] + $in{'n_6'};
        $c_syoku = $in{'syoku'};
        unshift(@new,"$in{'id'}<>$in{'pass'}<>$in{'site'}<>$in{'url'}<>$in{'c_name'}<>$in{'sex'}<>$in{'chara'}<>$n_0<>$n_1<>$n_2<>$n_3<>$n_4<>$n_5<>$n_6<>$c_syoku<>$hp<>$hp<>$ex<>$lv<>$gold<>$lp<>$total<>$kati<>$waza<>$item<>$mons<>$host<>$date<>\n");
    }

    open(OUT,">$chara_file");
    print OUT @new;
    close(IN);

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    if($in{'new'}) { &make_end; }
}

#----------------#
#  ログイン画面  #
#----------------#
sub log_in {
    $chara_flag=1;

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$chara_file");
    @log_in = <IN>;
    close(IN);

    $hit=0;
    foreach(@log_in){
        ($kid,$kpass,$ksite,$kurl,$kname,$ksex,$kchara,$kn_0,$kn_1,$kn_2,$kn_3,$kn_4,$kn_5,$kn_6,$ksyoku,$khp,$kmaxhp,$kex,$klv,$kgold,$klp,$ktotal,$kkati,$kwaza,$kitem,$kmons,$khost,$kdate) = split(/<>/);
        if($in{'id'} eq "$kid" and $in{'pass'} eq "$kpass") {
            $hit=1; last;
        }
    }

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    if(!$hit) { &error("入力されたIDは登録されていません。又はパスワードが違います。"); }

    &class;

    if($ksex) { $esex = "男"; } else { $esex = "女"; }
    $next_ex = $klv * $lv_up;

    open(IN,"$item_file");
    @log_item = <IN>;
    close(IN);

    $hit=0;
    foreach(@log_item){
        ($i_no,$i_name,$i_dmg,$i_gold) = split(/<>/);
        if($kitem eq "$i_no"){ $hit=1;last; }
    }
    if(!$hit) { $i_name=""; }

    &header;

    print <<"EOM";
<h1>$knameさん用ステータス画面</h1>
<hr size=0>
EOM
    if($ltime < $b_time or !$ktotal){
    print <<"EOM";
<FORM NAME="form1">
チャンプと闘えるまで残り<INPUT TYPE="text" NAME="clock" SIZE="3" VALUE="$vtime">秒です。0になると、自動的に更新しますのでブラウザの更新は押さないで下さい。
</FORM>
EOM
    }
    print <<"EOM";
<form action="$script_url" method="post">
<table border=0>
<tr>
<td valign=top width='50%'>
<table border=1>
<tr>
<td colspan="5" class="b2" align="center">ホームページデータ</td>
</tr>
<tr>
<td class="b1">ホームページ名</td>
<td colspan="4"><input type="text" name=site value="$ksite" size=50></td>
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
<td><input type="text" name=c_name value="$kname" size=10></td>
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
<td>$klv</td>
<td class="b1">経験値</td>
<td>$kex/$next_ex</td>
</tr>
<tr>
<td class="b1">お金</td>
<td>$kgold</td>
<td class="b1">HP</td>
<td>$khp\/$kmaxhp</td>
</tr>
<tr>
<td class="b1">力</td>
<td>$kn_0</td>
<td class="b1">知能\</td>
<td>$kn_1</td>
</tr>
<tr>
<td class="b1">信仰心</td>
<td>$kn_2</td>
<td class="b1">生命力</td>
<td>$kn_3</td>
</tr>
<tr>
<td class="b1">器用さ</td>
<td>$kn_4</td>
<td class="b1">速さ</td>
<td>$kn_5</td>
</tr>
<tr>
<td class="b1">魅力</td>
<td>$kn_6</td>
<td class="b1">カルマ</td>
<td>$klp</td>
</tr>
<tr>
<td class="b1">技発動時コメント</td>
<td colspan="4"><input type="text" name=waza value="$kwaza" size=50></td>
</tr>
<tr>
<td colspan="5" align="center">
<input type="hidden" name=mode value=battle>
<input type="hidden" name=id value="$kid">
<input type="hidden" name=pass value="$kpass">
EOM
    if($ltime >= $b_time or !$ktotal) {
        print "<input type=\"submit\" value=\"チャンプに挑戦\">\n";
    }else{
        print "$vtime秒後闘えるようになります。\n";
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

    open(IN,"$syoku_file");
    @syoku = <IN>;
    close(IN);

    $i=0;$hit=0;
    foreach(@syoku){
        ($a,$b,$c,$d,$e,$f,$g) = split(/<>/);
        if($kn_0 >= $a and $kn_1 >= $b and $kn_2 >= $c and $kn_3 >= $d and $kn_4 >= $e and $kn_5 >= $f and $kn_6 >= $g and $ksyoku != $i) {
            print "<option value=\"$i\">$chara_syoku[$i]\n";
            $hit=1;
        }
        $i++;
    }
    print <<"EOM";
</select>
<input type=hidden name=id value=$kid>
<input type=hidden name=pass value=$kpass>
<input type=hidden name=mode value=tensyoku>
EOM

    if(!$hit) { print "現在転職できる職業はありません"; }
    else { print "<input type=submit value=\"転職する\">\n"; }

    print <<"EOM";
<br>
　<small>※ 転職すると、全ての能\力値が転職した職業の初期値になります。また、LVも1になります。</small>
</form>
<form action="$script_url" method="post">
【魔物と戦い修行できます】<br>
<input type=hidden name=id value=$kid>
<input type=hidden name=pass value=$kpass>
<input type=hidden name=mode value=monster>
EOM

    if($ltime >= $m_time or !$ktotal) {
        print "<input type=submit value=\"モンスターと闘う\"><br>\n";
    }else{
        print "$mtime秒後闘えるようになります。<br>\n";
    }

    $yado_gold = $yado_dai * $klv;

    print <<"EOM";
　<small>※修行の旅にいけます。</small>
</form>
<form action="$script_url" method="post">
【旅の宿】<br>
<input type=hidden name=id value=$kid>
<input type=hidden name=pass value=$kpass>
<input type=hidden name=mode value=yado>
<input type=submit value="体力を回復"><br>
　<small>※体力を回復することができます。<b>$yado_gold</b>G必要です。現在チャンプの方も回復できます。こまめに回復すれば連勝記録も・・・。</small>
</form>
<form action="$script_url" method="post">
【他のキャラクターへメッセージを送る】<br>
<input type="text" name=mes size=50><br>
<select name=mesid>
<option value="">送る相手を選択
EOM

    open(IN,"$chara_file");
    @MESSAGE = <IN>;
    close(IN);

    foreach(@MESSAGE) {
        ($did,$dpass,$dsite,$durl,$dname) = split(/<>/);
        if($kid eq $did) { next; }
        print "<option value=$did>$dnameさんへ\n";
    }

    print <<"EOM";
</select>
<input type=hidden name=id value=$kid>
<input type=hidden name=name value=$kname>
<input type=hidden name=pass value=$kpass>
<input type=hidden name=mode value=message>
<input type=submit value="メッセージを送る"><br>
　<small>※他のキャラクターへメッセージを送ることができます。</small>
</form>
</td>
</tr>
</table>
【届いているメッセージ】表\示数<b>$max_gyo</b>件まで<br>
EOM

    open(IN,"$message_file");
    @MESSAGE_LOG = <IN>;
    close(IN);

    $hit=0;$i=1;
    foreach(@MESSAGE_LOG){
        ($pid,$hid,$hname,$hmessage,$hhname,$htime) = split(/<>/);
        if($kid eq "$pid"){
            if($max_gyo < $i) { last; }
            print "<hr size=0><small><b>$hnameさん</b>　＞ 「<b>$hmessage</b>」($htime)</small><br>\n";
            $hit=1;$i++;
        }elsif($kid eq "$hid"){
            print "<hr size=0><small>$knameさんから$hhnameさんへ　＞ 「$hmessage」($htime)</small><br>\n";
        }
    }
    if(!$hit){ print "<hr size=0>$knameさん宛てのメッセージはありません<p>\n"; }
    print "<hr size=0><p>";

    &footer;

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    $chara_flag=0;

    exit;
}

#--------------#
#  メッセージ  #
#--------------#
sub message {
    if($in{'mes'} eq "") { &error("メッセージが記入されていません"); }
    if($in{'mesid'} eq "") { &error("相手が指定されていません"); }

    &get_time;

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$message_file");
    @mes_regist = <IN>;
    close(IN);

    open(IN,"$chara_file");
    @MESSAGE = <IN>;
    close(IN);

    foreach(@MESSAGE) {
        ($did,$dpass,$dsite,$durl,$dname) = split(/<>/);
        if($in{'mesid'} eq "$did") { last; }
    }

    $mes_max = @mes_regist;

    if($mes_max > $max) { pop(@mes_regist); }

    unshift(@mes_regist,"$in{'mesid'}<>$in{'id'}<>$in{'name'}<>$in{'mes'}<>$dname<>$gettime<>\n");

    open(OUT,">$message_file");
    print OUT @mes_regist;
    close(OUT);

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    &header;

    print <<"EOM";
<h1>$dnameさんへメッセージを送りました。</h1>
<hr size=0>
<form action="$script_url" method="post">
<input type=hidden name=mode value=log_in>
<input type=hidden name=id value="$in{'id'}">
<input type=hidden name=pass value="$in{'pass'}">
<input type=submit value="ログイン画面へ戻る">
</form>
EOM

    &footer;

    exit;
}

#--------#
#  転職  #
#--------#
sub tensyoku {
    if($in{'syoku'} eq 'no') { &error("職業を選択してください。"); }
    $syoku = $in{'syoku'};
    $id = $in{'id'};

    &get_host;

    $date = time();

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    open(IN,"$chara_file");
    @tensyoku = <IN>;
    close(IN);

    open(IN,"$syoku_file");
    @syokudate = <IN>;
    close(IN);

    ($a,$b,$c,$d,$e,$f,$g) = split(/<>/,$syokudate[$in{'syoku'}]);

    if(!$a) { $a = $kiso_nouryoku[0]; }
    if(!$b) { $b = $kiso_nouryoku[1]; }
    if(!$c) { $c = $kiso_nouryoku[2]; }
    if(!$d) { $d = $kiso_nouryoku[3]; }
    if(!$e) { $e = $kiso_nouryoku[4]; }
    if(!$f) { $f = $kiso_nouryoku[5]; }
    if(!$g) { $g = $kiso_nouryoku[6]; }

    $lv = 1;
    $ex = 0;

    @ten_new = ();
    foreach(@tensyoku) {
        ($tid,$tpass,$tsite,$turl,$tname,$tsex,$tchara,$tn_0,$tn_1,$tn_2,$tn_3,$tn_4,$tn_5,$tn_6,$tsyoku,$thp,$tmaxhp,$tex,$tlv,$tgold,$tlp,$ttotal,$tkati,$twaza,$titem,$tmons,$thost,$tdate) = split(/<>/);
        if($id eq $tid) {
            unshift(@ten_new,"$tid<>$tpass<>$tsite<>$turl<>$tname<>$tsex<>$tchara<>$a<>$b<>$c<>$d<>$e<>$f<>$g<>$syoku<>$thp<>$tmaxhp<>$ex<>$lv<>$tgold<>$tlp<>$ttotal<>$tkati<>$twaza<>$titem<>$tmons<>$host<>$date<>\n");
        }else{
            push(@ten_new,"$_");
        }
    }

    open(OUT,">$chara_file");
    print OUT @ten_new;
    close(IN);

    &read_winner;

    if($id eq $wid) {
        open(OUT,">$winner_file");
        print OUT "$wid<>$wpass<>$wsite<>$wurl<>$wname<>$wsex<>$wchara<>$a<>$b<>$c<>$d<>$e<>$f<>$g<>$syoku<>$wmaxhp<>$wmaxhp<>$ex<>$lv<>$wgold<>$wlp<>$wtotal<>$wkati<>$wwaza<>$witem<>$wmons<>$host<>$date<>$wcount<>$lsite<>$lurl<>$lname<>\n";
        close(OUT);
    }

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    &header;

    print <<"EOM";
<h1>転職しました</h1><hr size=0>
<p>
<form action="$script_url" method="post">
<input type="hidden" name=id value="$in{'id'}">
<input type="hidden" name=pass value="$in{'pass'}">
<input type="hidden" name=mode value=log_in>
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
    if($battle_flag) { &error("現在戦闘中です。少しお待ちになってから戦闘してください。"); }

    $battle_flag=1;

    open(IN,"$chara_file");
    @battle = <IN>;
    close(IN);

    foreach(@battle){
        ($kid,$kpass,$ksite,$kurl,$kname,$ksex,$kchara,$kn_0,$kn_1,$kn_2,$kn_3,$kn_4,$kn_5,$kn_6,$ksyoku,$khp,$kmaxhp,$kex,$klv,$kgold,$klp,$ktotal,$kkati,$kwaza,$kitem,$kmons,$khost,$kdate) = split(/<>/);
        if($in{'id'} eq "$kid") { last; }
    }

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    if($ltime < $b_time and $ktotal) {
        &error("$vtime秒後闘えるようになります。\n");
    }

    &read_winner;

    if($wid eq $kid) { &error("現在チャンプなので闘えません。"); }

    if($chanp_milit) {
        if($kurl eq $lurl) { &error("チャンプが変わるまで闘えません。"); }
    }

    if($kitem){
        open(IN,"$item_file");
        @battle_item = <IN>;
        close(IN);

        foreach(@battle_item){
            ($ci_no,$ci_name,$ci_dmg) = split(/<>/);
            if($kitem eq $ci_no) { last; }
        }
    }
    if($witem){
        open(IN,"$item_file");
        @battle_item = <IN>;
        close(IN);

        foreach(@battle_item){
            ($wi_no,$wi_name,$wi_dmg) = split(/<>/);
            if($witem eq $wi_no) { last; }
        }
    }

    if($in{'site'}) { $ksite = $in{'site'}; }
    if($in{'url'}) { $kurl = $in{'url'}; }
    if($in{'waza'}) { $kwaza = $in{'waza'}; }
    if($in{'c_name'}) { $kname = $in{'c_name'}; }
    $khp_flg = $khp;
    $whp_flg = $whp;

    $i=1;$j=0;@battle_date=();
    foreach(1..$turn) {
        $dmg1 = $klv * (int(rand(3)) + 1);
        $dmg2 = $wlv * (int(rand(3)) + 1);
        $clit1 = "";
        $clit2 = "";
        $com1 = "";
        $com2 = "";
        $kawasi1 = "";
        $kawasi2 = "";

            # 挑戦者ダメージ計算
            if($ksyoku == 0){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[0]</b></font>\n";
                    $dmg1 = $dmg1 * 5;
                }
                $dmg1 = $dmg1 + int(rand($kn_0)) + $ci_dmg;
            }elsif($ksyoku == 1){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[1]</b></font>\n";
                    $dmg1 = $dmg1 * 5;
                }
                $dmg1 = $dmg1 + int(rand($kn_1)) + $ci_dmg;
            }elsif($ksyoku == 2){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[2]</b></font>\n";
                    $dmg1 = $dmg1 * 5;
                }
                $dmg1 = $dmg1 + int(rand($kn_2)) + $ci_dmg;
            }elsif($ksyoku == 3){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[3]</b></font>\n";
                    $dmg1 = $dmg1 * 5;
                }
                $dmg1 = $dmg1 + int(rand($kn_3)) + $ci_dmg;
            }elsif($ksyoku == 4){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[4]</b></font>\n";
                    $dmg1 = $dmg1 * 5;
                }
                $dmg1 = $dmg1 + int(rand($kn_3)) + int(rand($kn_0)) + $ci_dmg;
            }elsif($ksyoku == 5){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[5]</b></font>\n";
                    $dmg1 = $dmg1 * 6;
                }
                $dmg1 = $dmg1 + (int(rand($kn_1)) + int(rand($kn_4))) + $ci_dmg;
            }elsif($ksyoku == 6){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[6]</b></font>\n";
                    $dmg1 = $dmg1 * 6;
                }
                $dmg1 = $dmg1 + (int(rand($kn_1)) + int(rand($kn_4))) + $ci_dmg;
            }elsif($ksyoku == 7){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand(7))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[7]</b></font>\n";
                    $dmg1 = $dmg1 * 6;
                }
                $dmg1 = $dmg1 + (int(rand($kn_1)) + int(rand($kn_3))) + $ci_dmg;
            }elsif($ksyoku == 9){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[9]</b></font>\n";
                    $dmg1 = $dmg1 * 8;
                }
                $dmg1 = $dmg1 * (int(rand($kn_1)) + int(rand($kn_2))) + $ci_dmg;
            }elsif($ksyoku == 8){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[8]</b></font>\n";
                    $dmg1 = $dmg1 * 8;
                }
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2)) + $ci_dmg;
            }elsif($ksyoku == 10){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[10]</b></font>\n";
                    $dmg1 = $dmg1 * 9;
                }
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2)) + $ci_dmg;
            }elsif($ksyoku == 11){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[11]</b></font>\n";
                    $dmg1 = $dmg1 * 9;
                }
                $dmg1 = $dmg1 + int(rand($kn_4)) + int(rand($kn_5)) + $ci_dmg;
            }elsif($ksyoku == 12){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[12]</b></font>\n";
                    $dmg1 = $dmg1 * 9;
                }
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2)) + $ci_dmg;
            }elsif($ksyoku == 13){
                if($kitem) { $com1 = "$knameは$ci_nameで攻撃！！<p>"; }
                else { $com1 = "$knameの攻撃！！<p>"; }
                if(0 == int(rand($waza_ritu))) {
                    $com1 .= "<font size=5>$kname「<b>$kwaza</b>」</font><p><font color=\"#CC6699\" size=5><b>$hissatu[13]</b></font>\n";
                    $dmg1 = $dmg1 * 9;
                }
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2)) + $ci_dmg;
            }

            # チャンプダメージ計算
            if($wsyoku == 0){
                $dmg2 = $dmg2 + int(rand($wn_0)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 1){
                $dmg2 = $dmg2 + int(rand($wn_1)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 2){
                $dmg2 = $dmg2 + int(rand($wn_2)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 3){
                $dmg2 = $dmg2 + int(rand($wn_4)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 4){
                $dmg2 = $dmg2 + int(rand($wn_3)) + int(rand($wn_0)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 5){
                $dmg2 = $dmg2 + (int(rand($wn_1)) + int(rand($wn_4))) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 6){
                $dmg2 = $dmg2 + int(rand($wn_1)) + int(rand($wn_4)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 7){
                $dmg2 = $dmg2 + (int(rand($wn_1)) + int(rand($wn_3))) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 8){
                $dmg2 = $dmg2 + (int(rand($wn_1)) + int(rand($wn_2))) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 9){
                $dmg2 = $dmg2 + int(rand($wn_0)) + int(rand($wn_2)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 10){
                $dmg2 = $dmg2 + int(rand($wn_0)) + int(rand($wn_2)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 11){
                $dmg2 = $dmg2 + int(rand($wn_4)) + int(rand($wn_5)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 12){
                $dmg2 = $dmg2 + int(rand($wn_0)) + int(rand($wn_2)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }elsif($wsyoku == 13){
                $dmg2 = $dmg2 + int(rand($wn_0)) + int(rand($wn_2)) + $wi_dmg;
                if($witem){ $com2 = "$wnameは、$wi_nameで攻撃！！"; }
                else{ $com2 = "$wnameの攻撃！！<p>"; }
            }

            if(int(rand(20)) == 0) {
                $clit1 = "<b class=\"clit\">クリティカル！！</b>";
                $dmg1 = $dmg1 * 2;
            }

            if(int(rand(30)) == 0) {
                $clit2 = "<font size=5>$wname「<b>$wwaza</b>」</font><p><b class=\"clit\">クリティカル！！</b>";
                $dmg2 = int($dmg2 * 1.5);
            }

            if(($wlv - $klv) >= $level_sa and $i == 1) {
                $sa = $wlv - $klv;
                $clit1 .= "<p><font size=5><b>$knameの体から青い炎のようなものが湧き上がる・・・。</b></font>";
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

        if($whp_flg <= 0) { $win = 1; last; }
        elsif($khp_flg <= 0) { $win = 0; last; }

        $i++;
        $j++;
    }

    if($win) {
        $ktotal += 1;
        $kkati += 1;
        $exp = int($wlv * $kiso_exp + (rand($klp) + 1));
        $kex = $kex + $exp;
        $gold = $wlv * 10 + int(rand($klp));
        $kmons = $sentou_limit;
        $comment = "<b><font size=5>$knameは、戦闘に勝利した！！</font></b><p>";
    }else{
        $ktotal += 1;
        $exp = int($wlv * (rand($klp) + 1));
        $kex = $kex + $exp;
        $gold = int(rand($klp));
        $kmons = $sentou_limit;
        $comment = "<b><font size=5>$knameは、戦闘に負けた・・・。</font></b><p>";
    }

    if($kex > ($klv * $lv_up)) {
        $comment .= "$knameは、レベルが上がった！！<p>";
        $kmaxhp = $kmaxhp + int(rand($kn_3)) + 1;
        $khp = $kmaxhp;
        $kex = 0;
        $klv += 1;
        if(int(rand(5)) == 0) { $kn_0 += 1; $t1 = 1;}
        if(int(rand(5)) == 0) { $kn_1 += 1; $t2 = 1;}
        if(int(rand(5)) == 0) { $kn_2 += 1; $t3 = 1;}
        if(int(rand(5)) == 0) { $kn_3 += 1; $t4 = 1;}
        if(int(rand(5)) == 0) { $kn_4 += 1; $t5 = 1;}
        if(int(rand(5)) == 0) { $kn_5 += 1; $t6 = 1;}
        if(int(rand(5)) == 0) { $kn_6 += 1; $t7 = 1;}
        if($t1) { $comment .= "力が上がった。"; }
        if($t2) { $comment .= "知力が上がった。"; }
        if($t3) { $comment .= "信仰心が上がった。"; }
        if($t4) { $comment .= "生命力が上がった。"; }
        if($t5) { $comment .= "器用さが上がった。"; }
        if($t6) { $comment .= "速さが上がった。"; }
        if($t7) { $comment .= "魅力が上がった。"; }
    }

    $khp = $khp_flg + int(rand($kn_3));
    if($khp > $kmaxhp) { $khp = $kmaxhp; }
    $whp = $whp_flg + int(rand($wn_3));
    if($whp > $wmaxhp) { $whp = $wmaxhp; }
    if($khp <= 0) { $khp = $kmaxhp; }
    if($whp <= 0) { $whp = $wmaxhp; }
    $kgold = $kgold + $gold;

    # ファイルロック
    if ($lockkey == 1) { &lock1; }
    elsif ($lockkey == 2) { &lock2; }
    elsif ($lockkey == 3) { &file'lock; }

    if($win){
        @new=();
        open(IN,">$winner_file");
        @winnew = <IN>;
        unshift(@new,"$kid<>$kpass<>$ksite<>$kurl<>$kname<>$ksex<>$kchara<>$kn_0<>$kn_1<>$kn_2<>$kn_3<>$kn_4<>$kn_5<>$kn_6<>$ksyoku<>$khp<>$kmaxhp<>$kex<>$klv<>$kgold<>$klp<>$ktotal<>$kkati<>$kwaza<>$kitem<>$kmons<>$host<>$date<>$win<>$wsite<>$wurl<>$wname<>\n");
        print IN @new;
        close(IN);

    }else{
        $wcount += 1;
        @new=();
        open(IN,">$winner_file");
        @winnew = <IN>;
        unshift(@new,"$wid<>$wpass<>$wsite<>$wurl<>$wname<>$wsex<>$wchara<>$wn_0<>$wn_1<>$wn_2<>$wn_3<>$wn_4<>$wn_5<>$wn_6<>$wsyoku<>$whp<>$wmaxhp<>$wex<>$wlv<>$wgold<>$wlp<>$wtotal<>$wkati<>$wwaza<>$witem<>$wmons<>$host<>$date<>$wcount<>$ksite<>$kurl<>$kname<>\n");
        print IN @new;
        close(IN);

        open(IN,"$recode_file");
        @recode = <IN>;
        close(IN);

        ($count,$name) = split(/<>/,$recode[0]);

        if($wcount > $count) {
            open(OUT,">$recode_file");
            print OUT "$wcount<>$wname<>$wsite<>$wurl<>\n";
            close(IN);
        }
    }

    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }

    &regist;

    if($refresh and !$win) { &header2; } else { &header; }

    print "<h1>$knameは、$wnameに戦いを挑んだ！！</h1><hr size=0><p>\n";

    $i=0;
    foreach(@battle_date){
        print "$battle_date[$i]";
        $i++;
    }
    
    print "$comment<p>$knameは、<b>$exp</b>の経験値を手に入れた。<b>$gold</b>G手に入れた。<p>\n";

    &footer;

    $battle_flag=0;

    exit;
}

#--------------------#
#  チャンプ読み込み  #
#--------------------#
sub read_winner {
    open(IN,"$winner_file");
    @winner = <IN>;
    close(IN);

    ($wid,$wpass,$wsite,$wurl,$wname,$wsex,$wchara,$wn_0,$wn_1,$wn_2,$wn_3,$wn_4,$wn_5,$wn_6,$wsyoku,$whp,$wmaxhp,$wex,$wlv,$wgold,$wlp,$wtotal,$wkati,$wwaza,$witem,$wmons,$whost,$wdate,$wcount,$lsite,$lurl,$lname) = split(/<>/,$winner[0]);
}

#--------------#
#  クラス設定  #
#--------------#
sub class {
    if($chara_flag){
        if($ksyoku == 0){
            if($klv > 42) {
                $class = $FIGHTER[6];
            }elsif($klv < 7){
                $class = $FIGHTER[0];
            }elsif($klv < 14){
                $class = $FIGHTER[1];
            }elsif($klv < 21){
                $class = $FIGHTER[2];
            }elsif($klv < 28){
                $class = $FIGHTER[3];
            }elsif($klv < 35){
                $class = $FIGHTER[4];
            }elsif($klv < 42){
                $class = $FIGHTER[5];
            }
        }elsif($ksyoku == 1){
            if($klv > 42) {
                $class = $MAGE[6];
            }elsif($klv < 7){
                $class = $MAGE[0];
            }elsif($klv < 14){
                $class = $MAGE[1];
            }elsif($klv < 21){
                $class = $MAGE[2];
            }elsif($klv < 28){
                $class = $MAGE[3];
            }elsif($klv < 35){
                $class = $MAGE[4];
            }elsif($klv < 42){
                $class = $MAGE[5];
            }
        }elsif($ksyoku == 2){
            if($klv > 42) {
                $class = $PRIEST[6];
            }elsif($klv < 7){
                $class = $PRIEST[0];
            }elsif($klv < 14){
                $class = $PRIEST[1];
            }elsif($klv < 21){
                $class = $PRIEST[2];
            }elsif($klv < 28){
                $class = $PRIEST[3];
            }elsif($klv < 35){
                $class = $PRIEST[4];
            }elsif($klv < 42){
                $class = $PRIEST[5];
            }
        }elsif($ksyoku == 3){
            if($klv > 42) {
                $class = $THIEF[6];
            }elsif($klv < 7){
                $class = $THIEF[0];
            }elsif($klv < 14){
                $class = $THIEF[1];
            }elsif($klv < 21){
                $class = $THIEF[2];
            }elsif($klv < 28){
                $class = $THIEF[3];
            }elsif($klv < 35){
                $class = $THIEF[4];
            }elsif($klv < 42){
                $class = $THIEF[5];
            }
        }elsif($ksyoku == 4){
            if($klv > 42) {
                $class = $RANGER[6];
            }elsif($klv < 7){
                $class = $RANGER[0];
            }elsif($klv < 14){
                $class = $RANGER[1];
            }elsif($klv < 21){
                $class = $RANGER[2];
            }elsif($klv < 28){
                $class = $RANGER[3];
            }elsif($klv < 35){
                $class = $RANGER[4];
            }elsif($klv < 42){
                $class = $RANGER[5];
            }
        }elsif($ksyoku == 5){
            if($klv > 42) {
                $class = $ALCHEMIST[6];
            }elsif($klv < 7){
                $class = $ALCHEMIST[0];
            }elsif($klv < 14){
                $class = $ALCHEMIST[1];
            }elsif($klv < 21){
                $class = $ALCHEMIST[2];
            }elsif($klv < 28){
                $class = $ALCHEMIST[3];
            }elsif($klv < 35){
                $class = $ALCHEMIST[4];
            }elsif($klv < 42){
                $class = $ALCHEMIST[5];
            }
        }elsif($ksyoku == 6){
            if($klv > 42) {
                $class = $BARD[6];
            }elsif($klv < 7){
                $class = $BARD[0];
            }elsif($klv < 14){
                $class = $BARD[1];
            }elsif($klv < 21){
                $class = $BARD[2];
            }elsif($klv < 28){
                $class = $BARD[3];
            }elsif($klv < 35){
                $class = $BARD[4];
            }elsif($klv < 42){
                $class = $BARD[5];
            }
        }elsif($ksyoku == 7){
            if($klv > 42) {
                $class = $PSIONIC[6];
            }elsif($klv < 7){
                $class = $PSIONIC[0];
            }elsif($klv < 14){
                $class = $PSIONIC[1];
            }elsif($klv < 21){
                $class = $PSIONIC[2];
            }elsif($klv < 28){
                $class = $PSIONIC[3];
            }elsif($klv < 35){
                $class = $PSIONIC[4];
            }elsif($klv < 42){
                $class = $PSIONIC[5];
            }
        }elsif($ksyoku == 8){
            if($klv > 42) {
                $class = $VALKYRIE[6];
            }elsif($klv < 7){
                $class = $VALKYRIE[0];
            }elsif($klv < 14){
                $class = $VALKYRIE[1];
            }elsif($klv < 21){
                $class = $VALKYRIE[2];
            }elsif($klv < 28){
                $class = $VALKYRIE[3];
            }elsif($klv < 35){
                $class = $VALKYRIE[4];
            }elsif($klv < 42){
                $class = $VALKYRIE[5];
            }
        }elsif($ksyoku == 9){
            if($klv > 42) {
                $class = $BISHOP[6];
            }elsif($klv < 7){
                $class = $BISHOP[0];
            }elsif($klv < 14){
                $class = $BISHOP[1];
            }elsif($klv < 21){
                $class = $BISHOP[2];
            }elsif($klv < 28){
                $class = $BISHOP[3];
            }elsif($klv < 35){
                $class = $BISHOP[4];
            }elsif($klv < 42){
                $class = $BISHOP[5];
            }
        }elsif($ksyoku == 10){
            if($klv > 42) {
                $class = $LORD[6];
            }elsif($klv < 7){
                $class = $LORD[0];
            }elsif($klv < 14){
                $class = $LORD[1];
            }elsif($klv < 21){
                $class = $LORD[2];
            }elsif($klv < 28){
                $class = $LORD[3];
            }elsif($klv < 35){
                $class = $LORD[4];
            }elsif($klv < 42){
                $class = $LORD[5];
            }
        }elsif($ksyoku == 11){
            if($klv > 42) {
                $class = $SAMURAI[6];
            }elsif($klv < 7){
                $class = $SAMURAI[0];
            }elsif($klv < 14){
                $class = $SAMURAI[1];
            }elsif($klv < 21){
                $class = $SAMURAI[2];
            }elsif($klv < 28){
                $class = $SAMURAI[3];
            }elsif($klv < 35){
                $class = $SAMURAI[4];
            }elsif($klv < 42){
                $class = $SAMURAI[5];
            }
        }elsif($ksyoku == 12){
            if($klv > 42) {
                $class = $MONK[6];
            }elsif($klv < 7){
                $class = $MONK[0];
            }elsif($klv < 14){
                $class = $MONK[1];
            }elsif($klv < 21){
                $class = $MONK[2];
            }elsif($klv < 28){
                $class = $MONK[3];
            }elsif($klv < 35){
                $class = $MONK[4];
            }elsif($klv < 42){
                $class = $MONK[5];
            }
        }elsif($ksyoku == 13){
            if($klv > 42) {
                $class = $NINJA[6];
            }elsif($klv < 7){
                $class = $NINJA[0];
            }elsif($klv < 14){
                $class = $NINJA[1];
            }elsif($klv < 21){
                $class = $NINJA[2];
            }elsif($klv < 28){
                $class = $NINJA[3];
            }elsif($klv < 35){
                $class = $NINJA[4];
            }elsif($klv < 42){
                $class = $NINJA[5];
            }
        }
    }else{
        if($wsyoku == 0){
            if($wlv > 42) {
                $class = $FIGHTER[6];
            }elsif($wlv < 7){
                $class = $FIGHTER[0];
            }elsif($wlv < 14){
                $class = $FIGHTER[1];
            }elsif($wlv < 21){
                $class = $FIGHTER[2];
            }elsif($wlv < 28){
                $class = $FIGHTER[3];
            }elsif($wlv < 35){
                $class = $FIGHTER[4];
            }elsif($wlv < 42){
                $class = $FIGHTER[5];
            }
        }elsif($wsyoku == 1){
            if($wlv > 42) {
                $class = $MAGE[6];
            }elsif($wlv < 7){
                $class = $MAGE[0];
            }elsif($wlv < 14){
                $class = $MAGE[1];
            }elsif($wlv < 21){
                $class = $MAGE[2];
            }elsif($wlv < 28){
                $class = $MAGE[3];
            }elsif($wlv < 35){
                $class = $MAGE[4];
            }elsif($wlv < 42){
                $class = $MAGE[5];
            }
        }elsif($wsyoku == 2){
            if($wlv > 42) {
                $class = $PRIEST[6];
            }elsif($wlv < 7){
                $class = $PRIEST[0];
            }elsif($wlv < 14){
                $class = $PRIEST[1];
            }elsif($wlv < 21){
                $class = $PRIEST[2];
            }elsif($wlv < 28){
                $class = $PRIEST[3];
            }elsif($wlv < 35){
                $class = $PRIEST[4];
            }elsif($wlv < 42){
                $class = $PRIEST[5];
            }
        }elsif($wsyoku == 3){
            if($wlv > 42) {
                $class = $THIEF[6];
            }elsif($wlv < 7){
                $class = $THIEF[0];
            }elsif($wlv < 14){
                $class = $THIEF[1];
            }elsif($wlv < 21){
                $class = $THIEF[2];
            }elsif($wlv < 28){
                $class = $THIEF[3];
            }elsif($wlv < 35){
                $class = $THIEF[4];
            }elsif($wlv < 42){
                $class = $THIEF[5];
            }
        }elsif($wsyoku == 4){
            if($wlv > 42) {
                $class = $RANGER[6];
            }elsif($wlv < 7){
                $class = $RANGER[0];
            }elsif($wlv < 14){
                $class = $RANGER[1];
            }elsif($wlv < 21){
                $class = $RANGER[2];
            }elsif($wlv < 28){
                $class = $RANGER[3];
            }elsif($wlv < 35){
                $class = $RANGER[4];
            }elsif($wlv < 42){
                $class = $RANGER[5];
            }
        }elsif($wsyoku == 5){
            if($wlv > 42) {
                $class = $ALCHEMIST[6];
            }elsif($wlv < 7){
                $class = $ALCHEMIST[0];
            }elsif($wlv < 14){
                $class = $ALCHEMIST[1];
            }elsif($wlv < 21){
                $class = $ALCHEMIST[2];
            }elsif($wlv < 28){
                $class = $ALCHEMIST[3];
            }elsif($wlv < 35){
                $class = $ALCHEMIST[4];
            }elsif($wlv < 42){
                $class = $ALCHEMIST[5];
            }
        }elsif($wsyoku == 6){
            if($wlv > 42) {
                $class = $BARD[6];
            }elsif($wlv < 7){
                $class = $BARD[0];
            }elsif($wlv < 14){
                $class = $BARD[1];
            }elsif($wlv < 21){
                $class = $BARD[2];
            }elsif($wlv < 28){
                $class = $BARD[3];
            }elsif($wlv < 35){
                $class = $BARD[4];
            }elsif($wlv < 42){
                $class = $BARD[5];
            }
        }elsif($wsyoku == 7){
            if($wlv > 42) {
                $class = $PSIONIC[6];
            }elsif($wlv < 7){
                $class = $PSIONIC[0];
            }elsif($wlv < 14){
                $class = $PSIONIC[1];
            }elsif($wlv < 21){
                $class = $PSIONIC[2];
            }elsif($wlv < 28){
                $class = $PSIONIC[3];
            }elsif($wlv < 35){
                $class = $PSIONIC[4];
            }elsif($wlv < 42){
                $class = $PSIONIC[5];
            }
        }elsif($wsyoku == 8){
            if($wlv > 42) {
                $class = $VALKYRIE[6];
            }elsif($wlv < 7){
                $class = $VALKYRIE[0];
            }elsif($wlv < 14){
                $class = $VALKYRIE[1];
            }elsif($wlv < 21){
                $class = $VALKYRIE[2];
            }elsif($wlv < 28){
                $class = $VALKYRIE[3];
            }elsif($wlv < 35){
                $class = $VALKYRIE[4];
            }elsif($wlv < 42){
                $class = $VALKYRIE[5];
            }
        }elsif($wsyoku == 9){
            if($wlv > 42) {
                $class = $BISHOP[6];
            }elsif($wlv < 7){
                $class = $BISHOP[0];
            }elsif($wlv < 14){
                $class = $BISHOP[1];
            }elsif($wlv < 21){
                $class = $BISHOP[2];
            }elsif($wlv < 28){
                $class = $BISHOP[3];
            }elsif($wlv < 35){
                $class = $BISHOP[4];
            }elsif($wlv < 42){
                $class = $BISHOP[5];
            }
        }elsif($wsyoku == 10){
            if($wlv > 42) {
                $class = $LORD[6];
            }elsif($wlv < 7){
                $class = $LORD[0];
            }elsif($wlv < 14){
                $class = $LORD[1];
            }elsif($wlv < 21){
                $class = $LORD[2];
            }elsif($wlv < 28){
                $class = $LORD[3];
            }elsif($wlv < 35){
                $class = $LORD[4];
            }elsif($wlv < 42){
                $class = $LORD[5];
            }
        }elsif($wsyoku == 11){
            if($wlv > 42) {
                $class = $SAMURAI[6];
            }elsif($wlv < 7){
                $class = $SAMURAI[0];
            }elsif($wlv < 14){
                $class = $SAMURAI[1];
            }elsif($wlv < 21){
                $class = $SAMURAI[2];
            }elsif($wlv < 28){
                $class = $SAMURAI[3];
            }elsif($wlv < 35){
                $class = $SAMURAI[4];
            }elsif($wlv < 42){
                $class = $SAMURAI[5];
            }
        }elsif($wsyoku == 12){
            if($wlv > 42) {
                $class = $MONK[6];
            }elsif($wlv < 7){
                $class = $MONK[0];
            }elsif($wlv < 14){
                $class = $MONK[1];
            }elsif($wlv < 21){
                $class = $MONK[2];
            }elsif($wlv < 28){
                $class = $MONK[3];
            }elsif($wlv < 35){
                $class = $MONK[4];
            }elsif($wlv < 42){
                $class = $MONK[5];
            }
        }elsif($wsyoku == 13){
            if($wlv > 42) {
                $class = $NINJA[6];
            }elsif($wlv < 7){
                $class = $NINJA[0];
            }elsif($wlv < 14){
                $class = $NINJA[1];
            }elsif($wlv < 21){
                $class = $NINJA[2];
            }elsif($wlv < 28){
                $class = $NINJA[3];
            }elsif($wlv < 35){
                $class = $NINJA[4];
            }elsif($wlv < 42){
                $class = $NINJA[5];
            }
        }
    }
}

#----------------------#
#  モンスターとの戦闘  #
#----------------------#
sub monster {
    if($battle_flag) { &error("現在戦闘中です。少しお待ちになってから戦闘してください。"); }

    $battle_flag=1;

    open(IN,"$chara_file");
    @battle = <IN>;
    close(IN);

    foreach(@battle){
        ($kid,$kpass,$ksite,$kurl,$kname,$ksex,$kchara,$kn_0,$kn_1,$kn_2,$kn_3,$kn_4,$kn_5,$kn_6,$ksyoku,$khp,$kmaxhp,$kex,$klv,$kgold,$klp,$ktotal,$kkati,$kwaza,$kitem,$kmons,$khost,$kdate) = split(/<>/);
        if($in{'id'} eq "$kid") { last; }
    }

    $ltime = time();
    $ltime = $ltime - $kdate;
    $vtime = $b_time - $ltime;
    $mtime = $m_time - $ltime;

    if($ltime < $m_time and $ktotal) {
        &error("$mtime秒後闘えるようになります。<br>\n");
    }

    if(!$kmons) { &error("一度キャラクターと闘ってください"); }

    open(IN,"$monster_file");
    @MONSTER = <IN>;
    close(IN);

    $r_no = @MONSTER;

    $r_no = int(rand($r_no));

    ($mname,$mex,$mhp,$msp,$mdmg) = split(/<>/,$MONSTER[$r_no]);

    if($in{'site'}) { $ksite = $in{'site'}; }
    if($in{'url'}) { $kurl = $in{'url'}; }
    if($in{'waza'}) { $kwaza = $in{'waza'}; }
    if($in{'c_name'}) { $kname = $in{'c_name'}; }
    $khp_flg = $khp;
    $mhp = int(rand($mhp)) + $msp;
    $mhp_flg = $mhp;

    $i=1;$j=0;@battle_date=();
    foreach(1..$turn) {
        $dmg1 = $klv * (int(rand(5)) + 1);
        $dmg2 = (int(rand($mdmg)) + 1) + $mdmg;
        $clit1 = "";
        $clit2 = "";
        $com1 = "";
        $com2 = "$mnameが襲いかかった！！";
        $kawasi1 = "";
        $kawasi2 = "";

            # 挑戦者ダメージ計算
            if($ksyoku == 0){
                $dmg1 = $dmg1 + int(rand($kn_0));
                $com1 = "$knameは、剣で切りつけた！！<p>";
            }elsif($ksyoku == 1){
                $dmg1 = $dmg1 * int(rand($kn_1));
                $com1 = "$knameは、魔法を唱えた！！<p>";
            }elsif($ksyoku == 2){
                $dmg1 = $dmg1 * int(rand($kn_2));
                $com1 = "$knameは、魔法を唱えた！！<p>";
            }elsif($ksyoku == 3){
                $dmg1 = $dmg1 + int(rand($kn_4));
                $com1 = "$knameは、背後から切りつけた！！<p>";
            }elsif($ksyoku == 4){
                $dmg1 = $dmg1 + int(rand($kn_3)) + int(rand($kn_0));
                $com1 = "$knameは、弓で攻撃！！<p>";
            }elsif($ksyoku == 5){
                $dmg1 = $dmg1 * (int(rand($kn_1)) + int(rand($kn_4)));
                $com1 = "$knameは、魔法を唱えた！！<p>";
            }elsif($ksyoku == 6){
                $dmg1 = $dmg1 * (int(rand($kn_1)) + int(rand($kn_4)));
                $com1 = "$knameは、呪歌を歌った！！<p>";
            }elsif($ksyoku == 7){
                $dmg1 = $dmg1 * (int(rand($kn_1)) + int(rand($kn_3)));
                $com1 = "$knameは、超能力を使った！！<p>";
            }elsif($ksyoku == 8){
                $dmg1 = $dmg1 * (int(rand($kn_1)) + int(rand($kn_2)));
                $com1 = "$knameは、精霊魔法と、神聖魔法を同時に唱えた！！<p>";
            }elsif($ksyoku == 9){
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2));
                $com1 = "$knameは、槍を突き刺した！！<p>";
            }elsif($ksyoku == 10){
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2));
                $com1 = "$knameは、神聖魔法を唱えつつ、剣で切りつけた！！<p>";
            }elsif($ksyoku == 11){
                $dmg1 = $dmg1 + int(rand($kn_4)) + int(rand($kn_5));
                $com1 = "$knameは、見えない速さで切りつけた！！<p>";
            }elsif($ksyoku == 12){
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2));
                $com1 = "$knameは、殴りつけた！！<p>";
            }elsif($ksyoku == 13){
                $dmg1 = $dmg1 + int(rand($kn_0)) + int(rand($kn_2));
                $com1 = "$knameは、蹴りつけた！！<p>";
            }

            if(int(rand(20)) == 0) {
                $clit1 = "<font size=5>$kname「<b>$kwaza</b>」</font><p><b class=\"clit\">クリティカル！！</b>";
                $dmg1 = $dmg1 * 2;
            }

            if(int(rand(30)) == 0) {
                $clit2 = "<b class=\"clit\">クリティカル！！</b>";
                $dmg2 = int($dmg2 * 1.5);
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
        $mhp = $mhp - $dmg1;

        if($mhp <= 0) { $win = 1; last; }
        elsif($khp_flg <= 0) { $win = 0; last; }

        $i++;
        $j++;
    }

    if($win) {
        $ktotal += 1;
        $kkati += 1;
        $kex = $kex + $mex;
        $kmons -= 1;
        $gold = $klv * 10 + int(rand($klp));
        $kgold = $kgold + $gold;
        $comment = "<b><font size=5>$knameは、戦闘に勝利した！！</font></b><p>";
    }else{
        $ktotal += 1;
        $mex = int(rand($klp));
        $kex = $kex + $mex;
        $kmons -= 1;
        if($kgold) { $kgold = int($kgold / 2); }
        else { $kgold = 0; }
        $comment = "<b><font size=5>$knameは、戦闘に負けた・・・。</font></b><p>";
    }

    if($kex > ($klv * $lv_up)) {
        $comment .= "$knameは、レベルが上がった！！<p>";
        $kmaxhp = $kmaxhp + int(rand($kn_3)) + 1;
        $khp = $kmaxhp;
        $kex = 0;
        $klv += 1;
        if(int(rand(5)) == 0) { $kn_0 += 1; $t1 = 1;}
        if(int(rand(5)) == 0) { $kn_1 += 1; $t2 = 1;}
        if(int(rand(5)) == 0) { $kn_2 += 1; $t3 = 1;}
        if(int(rand(5)) == 0) { $kn_3 += 1; $t4 = 1;}
        if(int(rand(5)) == 0) { $kn_4 += 1; $t5 = 1;}
        if(int(rand(5)) == 0) { $kn_5 += 1; $t6 = 1;}
        if(int(rand(5)) == 0) { $kn_6 += 1; $t7 = 1;}
        if($t1) { $comment .= "力が上がった。"; }
        if($t2) { $comment .= "知力が上がった。"; }
        if($t3) { $comment .= "信仰心が上がった。"; }
        if($t4) { $comment .= "生命力が上がった。"; }
        if($t5) { $comment .= "器用さが上がった。"; }
        if($t6) { $comment .= "速さが上がった。"; }
        if($t7) { $comment .= "魅力が上がった。"; }
    }

    $khp = $khp_flg + int(rand($kn_3));
    if($khp > $kmaxhp) { $khp = $kmaxhp; }
    if($khp <= 0) { $khp = $kmaxhp; }

    &regist;

    &header;

    print "<h1>$knameは、$mnameに戦いを挑んだ！！</h1><hr size=0><p>\n";

    $i=0;
    foreach(@battle_date){
        print "$battle_date[$i]";
        $i++;
    }
    
    if($win) { print "$comment<p>$knameは、$mexの経験値を手に入れた。<b>$gold</b>G手に入れた。<p>\n"; }
    else { print "$comment<p>$knameは、$mexの経験値を手に入れた。お金が半分になった。<p>\n"; }

    &footer;

    $battle_flag=0;

    exit;
}

#----------------#
#  ホスト名取得  #
#----------------#
sub get_host {
    $host = $ENV{'REMOTE_HOST'};
    $addr = $ENV{'REMOTE_ADDR'};

    if ($get_remotehost) {
        if ($host eq "" || $host eq "$addr") {
            $host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
        }
    }
    if ($host eq "") { $host = $addr; }
}

#--------------#
#  エラー処理  #
#--------------#
sub error {
    # ロック解除
    if ($lockkey == 3) { &file'unlock; }
    else { if(-e $lockfile) { unlink($lockfile); } }
    $battle_flag=0;

    &header;
    print "<center><hr width=400><h3>ERROR !</h3>\n";
    print "<P><font color=red><B>$_[0]</B></font>\n";
    print "<P><hr width=400></center>\n";
    print "</body></html>\n";
    exit;
}

#------------------#
#　HTMLのフッター　#
#------------------#
sub footer {
    if($refresh and !$win and $mode eq 'battle') {
        print "【<b><a href=\"http\:\/\/$wurl\">チャンプのホームページへ</a></b>】\n";
    }else{
        if($mode ne ""){
            print "<a href=\"$script_url\">TOPページへ</a>\n";
        }
        if($kid and $mode ne 'log_in' and $mode ne 'tensyoku' and $mode ne 'yado') { 
            print " / <a href=\"$script_url?mode=log_in&id=$kid&pass=$kpass\">ステータス画面へ</a>\n";
        }
    }
    print "<HR SIZE=0 WIDTH=\"100%\"><DIV align=right class=small>\n";
    print "$ver by <a href=\"http://www.interq.or.jp/sun/cumro/\">D.Takamiya(CUMRO)</a><br>\n";
        print "Character Image by <a href=\"http://www.aas.mtci.ne.jp/~hiji/9ff/9ff.html\">9-FFいっしょにTALK</a><br>\n";
    print "cooperation site by <a href=\"http://webooo.csidenet.com/asvyweb/\">FFADV推奨委員会</a>\n";
    print "</DIV>\n";

    if($mode eq 'log_in' and $ltime < $b_time and $ktotal){
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
    print "Cache-Control: no-cache\n";
    print "Pragma: no-cache\n";
    print "Content-type: text/html\n\n";
    print <<"EOM";
<html>
<head>
<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=Shift_JIS">
EOM

if($mode eq 'log_in' and $ltime < $b_time and $ktotal){
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
            location.href="$script_url?mode=log_in&id=$kid&pass=$kpass"
        }
    }
//-->
</SCRIPT>
EOM
}
    print <<"EOM";
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
EOM
    print "<title>$main_title</title></head>\n";
    print "<body background=\"$backgif\" bgcolor=\"$bgcolor\" text=\"$text\" link=\"$link\" vlink=\"$vlink\" alink=\"$alink\">\n";
}

#--------------#
#  強制送還用  #
#--------------#
sub header2 {
    print "Content-type: text/html\n\n";
    print <<"EOM";
<html>
<head>
<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=Shift_JIS">
<META http-equiv="refresh" content="$refresh;URL=http\:\/\/$wurl"> 
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
EOM
    print "<title>$main_title</title></head>\n";
    print "<body background=\"$backgif\" bgcolor=\"$bgcolor\" text=\"$text\" link=\"$link\" vlink=\"$vlink\" alink=\"$alink\">\n";
}

#----------------#
#  デコード処理  #
#----------------#
sub decode {
    if ($ENV{'REQUEST_METHOD'} eq "POST") {
        if ($ENV{'CONTENT_LENGTH'} > 51200) { &error("投稿量が大きすぎます"); }
        read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
    } else { $buffer = $ENV{'QUERY_STRING'}; }
    @pairs = split(/&/, $buffer);
    foreach (@pairs) {
        ($name,$value) = split(/=/, $_);
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
        if ($name eq 'del') { push(@DEL,$value); }

        $in{$name} = $value;
    }
    $mode = $in{'mode'};
    $in{'url'} =~ s/^http\:\/\///;
    $cookie_pass = $in{'pass'};
    $cookie_id = $in{'id'};
}

#-------------------------------#
#  ロックファイル：symlink関数  #
#-------------------------------#
sub lock1 {
    local($retry) = 5;
    while (!symlink(".", $lockfile)) {
        if (--$retry <= 0) { &error("LOCK is BUSY"); }
        sleep(1);
    }
}

#----------------------------#
#  ロックファイル：open関数  #
#----------------------------#
sub lock2 {
    local($retry) = 0;
    foreach (1 .. 5) {
        if (-e $lockfile) { sleep(1); }
        else {
            open(LOCK,">$lockfile") || &error("Can't Lock");
            close(LOCK);
            $retry = 1;
            last;
        }
    }
    if (!$retry) { &error("しばらくお待ちになってください(^^;)"); }
}

#------------------#
#  クッキーの発行  #
#------------------#
sub set_cookie {
    # クッキーは60日間有効
    local($sec,$min,$hour,$mday,$mon,$year,$wday) = gmtime(time+60*24*60*60);

    @month=('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
    $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
            $week[$wday],$mday,$month[$mon],$year+1900,$hour,$min,$sec);
    $cook="id<>$cookie_id\,pass<>$cookie_pass";
    print "Set-Cookie: FFADV=$cook; expires=$gmt\n";
}

#------------------#
#  クッキーを取得  #
#------------------#
sub get_cookie {
    @pairs = split(/;/, $ENV{'HTTP_COOKIE'});
    foreach (@pairs) {
        local($key,$val) = split(/=/);
        $key =~ s/\s//g;
        $GET{$key} = $val;
    }
    @pairs = split(/,/, $GET{'FFADV'});
    foreach (@pairs) {
        local($key,$val) = split(/<>/);
        $COOK{$key} = $val;
    }
    $c_id  = $COOK{'id'};
    $c_pass = $COOK{'pass'};
}

#--------------#
#  時間を取得  #
#--------------#
sub get_time {
    $ENV{'TZ'} = "JST-9";
    ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
    @week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');

    # 日時のフォーマット
    $gettime = sprintf("%04d/%02d/%02d %02d:%02d",
            $year+1900,$mon+1,$mday,$hour,$min);
}

#ファイルのロック
sub file'lock
{
    local($lockfile, $locktest) = @_;
    $locktest = ($locktest > 0 ? $locktest : 4);    #０以下なら標準で４回
    $locktest = ($locktest < 8 ? $locktest : 8);    #最大で８回までとする

    $file'lockflag = 0;
    $file'lockfile = $lockfile;        #本来のロックファイルの名前
    $file'lock_sw0 = $lockfile . ".sw0";    #最新日時のロックファイル作成用
    $file'lock_sw1 = $lockfile . ".sw1";    #ロックされている状態の名前

    (-l $lockfile) && &file'error(0);
    (-d $lockfile) && &file'error(0);

    #ロックファイルを置くサーバーの現在時刻を取得(timeではだめ)
    $locktemp = $lockfile . ".$$";
    open(LOCK, ">$locktemp") || return (0);    close(LOCK);
    $time = (stat($locktemp))[9];
    unlink($locktemp);

    #作成されてから$lock_limit秒以上経過しているロックファイルの名前を戻す
    if ((-f $file'lock_sw1) && ($time - (stat($file'lock_sw1))[9] > $lock_limit)) {
        rename($file'lock_sw1, $file'lockfile) || return (0);
    }

    #ロックファイルの作成日時更新
    open(LOCK, ">$file'lock_sw0") || &file'error(2);
    close(LOCK);
    rename($file'lock_sw0, $file'lockfile) || return (0);

    (-f $file'lock_sw1) && return (0);

    #ロック権の取得
    while (($file'lockflag = rename($file'lockfile, $file'lock_sw1)) == 0 && $lock_try) {
        #0.03, [0.07, 0.13, 0.17], 0.23
        select(undef, undef, undef, 0.13);
        $lock_try--;
    }
    $file'lockflag;
}

#ファイルのアンロック
sub file'unlock
{
    if ($file'lockflag) {
        rename($file'lock_sw1, $file'lockfile);

        #0.03, [0.07, 0.13, 0.17], 0.23
        select(undef, undef, undef, 0.03);
    }
}

sub file'error
{
    local(@error) = (
        "ロックシンボルの作成を中止しました<br>\n(ロックシンボル以外で同名称が存在)<br>\n",
        "ロックシンボルの作成に失敗しました<br>\n",
        "ロックシンボルの更新に失敗しました<br>\n",
        "ロックシンボルの削除に失敗しました<br>\n",
        $_[1],
    );

    select(STDOUT);    $| = 1;
    print "$error[$_[0]]\n";
    exit;
}
