Summary:	A set of documentation tools: man, apropos and whatis
Name:		man
Version:	1.6e
Release:	%mkrel 6
License:	GPL
Group:		System/Base
Url:		http://primates.ximian.com/~flucifredi/man/
Source0:	http://primates.ximian.com/~flucifredi/man/%{name}-%{version}.tar.gz
Source1:	makewhatis.cronweekly
Source2:	makewhatis.crondaily
Patch1:		man-1.5k-confpath.patch
Patch4:		man-1.5h1-make.patch
Patch5:		man-1.5k-nonascii.patch
Patch6:		man-1.6e-security.patch
Patch7:		man-1.6e-mandirs.patch
Patch8:		man-1.5m2-bug11621.patch
Patch9:		man-1.5k-sofix.patch
Patch10:	man-1.5m2-buildroot.patch
Patch12:	man-1.6e-ro_usr.patch
Patch14:	man-1.5i2-newline.patch
Patch17:	man-1.5j-utf8.patch
Patch19:	man-1.5i2-overflow.patch
Patch22:	man-1.5j-nocache.patch
Patch24:	man-1.5i2-initial.patch
Patch25:	man-1.6e-use_i18n_vars_in_a_std_way.patch
Patch26:	man-1.5m2-no-color-for-printing.patch
# ignore SIGPIPE signals, so no error messages are displayed
# when the pipe is broken before the formatting of the man page
# (which may take some time) is finished.
# the typical case is "man foo | head -1"
Patch27:	man-1.5m2-sigpipe.patch

# Japanese patches
Patch51:	man-1.5h1-gencat.patch
Patch102:	man-1.5g-nonrootbuild.patch
Patch104:	man-1.5m2-tv_fhs.patch
Patch105:	man-1.5j-i18n.patch
Patch107:	man-1.6e-whatis2.patch

# avoid adding a manpage already in the list
Patch200:	man-1.5m2-multiple.patch
# i18n fixes for whatis and makewhatis
Patch201:	man-1.6e-i18n_whatis.patch
Patch300:	man-1.6e-new_sections.patch

#(peroyvind)
Patch500:	man-1.6e-lzma-support.patch

Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires:	groff-for-man
BuildRequires:	lzma

%description
The man package includes three tools for finding information and/or
documentation about your Linux system: man, apropos and whatis. The man
system formats and displays on-line manual pages about commands or
functions on your system. Apropos searches the whatis database
(containing short descriptions of system commands) for a string. Whatis
searches its own database for a complete word.

The man package should be installed on your system because it is the
primary way for find documentation on a Mandriva Linux system.

%prep
%setup -q
%patch1 -p0 -b .confpath
%patch4 -p1 -b .make
%patch5 -p1 -b .nonascii
%patch6 -p1 -b .security
%patch7 -p1 -b .mandirs
%patch8 -p1 -b .ad
%patch9 -p1 -b .sofix
%patch10 -p1 -b .less
%patch12 -p1 -b .ro_usr
%patch14 -p1 -b .newline
%patch51 -p1 -b .jp2
%patch17 -p1 -b .utf8
%patch19 -p1 -b .overflow
%patch22 -p1 -b .nocache
%patch24 -p1 -b .initial
%patch25 -p1 -b .use_i18n_vars_in_a_std_way
%patch26 -p1 -b .color
%patch27 -p1 -b .sigpipe

%patch102 -p1
%patch104 -p1 -b .tv_fhs
%patch105 -p1 -b .i18n
%patch107 -p1 -b .whatis2
%patch200 -p1 -b .multiple
%patch201 -p1 -b .i18n_whatis

%patch300 -p1 -b .new_sections

%patch500 -p1 -b .lzma_support

# fixing the encodings to utf-8
for i in msgs/mess.* man/*/*.man
do
	if iconv -f utf-8 -t utf-8 -o /dev/null $i 2> /dev/null ; then continue ; fi
    lang=`echo $i | cut -d'/' -f2 | sed 's/mess.//'`
    case $lang in
    	bg) encoding=cp1251 ;;
    	cs|hu|hr|pl|ro|sk|sl) encoding=iso-8859-2 ;;
    	eo) encoding=iso-8859-3 ;;
    	el) encoding=iso-8859-7 ;;
    	ja) encoding=euc-jp ;;
    	ko) encoding=euc-kr ;;
    	ru) encoding=koi8-r ;;
    	uk) encoding=koi8-u ;;
    	*) encoding=iso-8859-1 ;;
    esac
    iconv -f $encoding -t utf-8 -o tmpfile $i && mv tmpfile $i
done

cd man;
    for i in `find -name man.conf.man`; do
        sed -e 's/MAN\.CONF/MAN\.CONFIG/g' \
            -e 's/man\.conf/man\.config/g' \
            -i $i
        mv $i `echo $i|sed -e 's/conf.man/config.man/g'`
    done
cd ..

%build
./configure -default -confdir %{_sysconfdir} +sgid +fhs +lang all 
#	-compatibility_mode_for_colored_groff
make CC="gcc -g %{optflags} -D_GNU_SOURCE" MANDIR=%{_mandir}
# it seems for some reason make rpm is building with LC_ALL=C
# which breaks gencat (as the input is utf-8); forcing a clean rebuild
(cd msgs/ ; rm -f *.cat ; LC_ALL=en_US.UTF-8 make)

%install
rm -rf %{buildroot}
perl -pi -e 's!mandir = .*$!mandir ='"%{_mandir}"'!g' man2html/Makefile
make install PREFIX=%{buildroot} mandir=%{buildroot}%{_mandir}

install -m755 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/cron.weekly/makewhatis.cron
install -m755 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/cron.daily/makewhatis.cron

for i in 1 2 3 4 5 6 7 8 9 n; do
	mkdir -p %{buildroot}/var/cache/man/cat$i
	mkdir -p %{buildroot}/var/cache/man/local/cat$i
	mkdir -p %{buildroot}/var/cache/man/X11R6/cat$i
done

# symlinks for manpath
pushd %{buildroot}
  ln -s man .%{_bindir}/manpath
  ln -s man.1%{_extension} .%{_mandir}/man1/manpath.1%{_extension}
popd

# those are provided in the man-pages-xx packages
rm -rf %{buildroot}%{_mandir}/{de,fr,it,pl}

# Fix makewhatis perms
chmod 755 %{buildroot}%{_sbindir}/makewhatis

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/cron.weekly/makewhatis.cron
%{_sysconfdir}/cron.daily/makewhatis.cron
%attr(2755,root,man) %{_bindir}/man
%{_bindir}/manpath
%{_bindir}/apropos
%{_bindir}/whatis
%{_bindir}/man2dvi
%{_sbindir}/makewhatis
%config(noreplace) %{_sysconfdir}/man.config
%{_mandir}/man8/*
%{_mandir}/man5/*
%{_mandir}/man1/*
# translated man pages
%lang(bg) %{_mandir}/bg/man?/*
%lang(cs) %{_mandir}/cs/man?/*
%lang(da) %{_mandir}/da/man?/*
%lang(el) %{_mandir}/el/man?/*
%lang(es) %{_mandir}/es/man?/*
%lang(fi) %{_mandir}/fi/man?/*
%lang(hr) %{_mandir}/hr/man?/*
%lang(ja) %{_mandir}/ja/man?/*
%lang(ko) %{_mandir}/ko/man?/*
%lang(nl) %{_mandir}/nl/man?/*
%lang(pt) %{_mandir}/pt/man?/*
%lang(ro) %{_mandir}/ro/man?/*
%lang(sl) %{_mandir}/sl/man?/*
%{_bindir}/man2html

%attr(0775,root,man) %dir /var/cache/man/cat[123456789n]
%attr(0775,root,man) %dir /var/cache/man/local
%attr(0775,root,man) %dir /var/cache/man/local/cat[123456789n]
%attr(0775,root,man) %dir /var/cache/man/X11R6
%attr(0775,root,man) %dir /var/cache/man/X11R6/cat[123456789n]

# translation of man program. It doesn't use gettext format, so
# find_lang doesn't find them... manual setting is needed
%lang(bg) %{_datadir}/locale/bg/man
%lang(cs) %{_datadir}/locale/cs/man
%lang(da) %{_datadir}/locale/da/man
%lang(de) %{_datadir}/locale/de/man
%lang(el) %{_datadir}/locale/el/man
%lang(en) %{_datadir}/locale/en/man
%lang(es) %{_datadir}/locale/es/man
%lang(fi) %{_datadir}/locale/fi/man
%lang(fr) %{_datadir}/locale/fr/man
%lang(hr) %{_datadir}/locale/hr/man
%lang(it) %{_datadir}/locale/it/man
%lang(ja) %{_datadir}/locale/ja/man
%lang(ko) %{_datadir}/locale/ko/man
%lang(nl) %{_datadir}/locale/nl/man
%lang(pl) %{_datadir}/locale/pl/man
%lang(pt) %{_datadir}/locale/pt/man
%lang(ro) %{_datadir}/locale/ro/man
%lang(ru) %{_datadir}/locale/ru/man
%lang(sl) %{_datadir}/locale/sl/man
