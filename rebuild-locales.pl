#!/usr/bin/perl
use strict;

my @languages = qw(ar bn bg ca cs cy da de el en es et eu fa fi fr ga gl 
                    hu he hi hr is it ja ka ko km kn lv lt mk nl no pl pt 
                    pt-br ro ru sk sl sr sv ta te th tr uk zh-cn zh-tw);

for my $lang (@languages){
    system("python manage.py makemessages -l $lang -e html,py,txt");
}
